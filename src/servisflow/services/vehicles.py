"""UC-03: Araç kaydı, plaka normalizasyonu ve tekillik denetimi (FR-03, BR-07)."""

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from servisflow.repository.models import Customer, Vehicle
from servisflow.services.errors import ConflictError, NotFoundError, ValidationError

TEXT_MAX = 50
SUGGEST_LIMIT = 10
SUGGEST_MIN = 2
_PLATE_CHARS = re.compile(r"[0-9A-Z]+")
_TURKISH = set("çğıöşüÇĞİÖŞÜ")
# BR-07: il kodu 01–81, 1–3 harf, 2–4 rakam.
_PLATE = re.compile(r"(0[1-9]|[1-7]\d|8[01])[A-Z]{1,3}\d{2,4}")


def normalize_plate(raw: str) -> str:
    """Boşlukları atar, Latin büyük harfe çevirir ve BR-07 biçimini denetler.

    Türkçe karakter büyük harfe çevrilmeden reddedilir: Python'da `"ı".upper()`
    `"I"` döndürdüğü için önce çevirmek `34 abı 12` girişini sessizce geçirirdi.
    """
    text = "".join((raw or "").split())
    if _TURKISH & set(text):
        raise ValidationError("Plakada Türkçe karakter (Ç, Ğ, İ, Ö, Ş, Ü) olamaz.")
    plate = text.upper()
    if not _PLATE.fullmatch(plate):
        raise ValidationError(
            "Plaka biçimi geçersiz: il kodu (01–81), 1–3 harf, 2–4 rakam olmalıdır."
        )
    return plate


def _clean_text(value: str, label: str) -> str:
    cleaned = " ".join((value or "").split())
    if not 1 <= len(cleaned) <= TEXT_MAX:
        raise ValidationError(f"{label} 1–{TEXT_MAX} karakter olmalıdır.")
    return cleaned


def register_vehicle(
    session: Session, customer_id: int, plate: str, brand: str, model: str
) -> Vehicle:
    """Müşteriye araç ekler; normalize plaka sistemde tekildir (TC-10)."""
    vehicle = Vehicle(
        customer_id=customer_id,
        plate_normalized=normalize_plate(plate),
        brand=_clean_text(brand, "Marka"),
        model=_clean_text(model, "Model"),
    )
    if session.get(Customer, customer_id) is None:
        raise NotFoundError("Müşteri bulunamadı.")
    duplicate = ConflictError(f"{vehicle.plate_normalized} plakası zaten kayıtlı.")
    if _by_plate(session, vehicle.plate_normalized) is not None:
        raise duplicate
    try:
        # Ön denetim ile kayıt arasında aynı plaka eklenirse tekil kısıt yakalar;
        # iç işlem (savepoint) yalnızca bu eklemeyi geri alır.
        with session.begin_nested():
            session.add(vehicle)
    except IntegrityError as exc:
        raise duplicate from exc
    return vehicle


def _by_plate(session: Session, plate_normalized: str) -> Vehicle | None:
    return session.scalar(
        select(Vehicle).where(Vehicle.plate_normalized == plate_normalized)
    )


def find_vehicle_by_plate(session: Session, plate: str) -> Vehicle:
    vehicle = _by_plate(session, normalize_plate(plate))
    if vehicle is None:
        raise NotFoundError("Bu plakayla kayıtlı araç yok.")
    return vehicle


def suggest_plates(session: Session, text: str) -> list[Vehicle]:
    """Yazılan plakanın başıyla eşleşen araçlar (KR-09: `06 b` → `06BUM00`).

    Girdi tam plaka gibi normalize edilir ama biçim denetlenmez, çünkü yarım
    plaka henüz BR-07'ye uymaz. Yalnızca rakam ve Latin büyük harf kabul edilir;
    böylece `%` ve `_` LIKE sorgusunda joker karakter olarak çalışamaz.
    """
    prefix = "".join((text or "").split())
    if _TURKISH & set(prefix):
        return []
    prefix = prefix.upper()
    if len(prefix) < SUGGEST_MIN or not _PLATE_CHARS.fullmatch(prefix):
        return []
    return list(
        session.scalars(
            select(Vehicle)
            .where(Vehicle.plate_normalized.startswith(prefix, autoescape=True))
            .order_by(Vehicle.plate_normalized)
            .limit(SUGGEST_LIMIT)
        )
    )
