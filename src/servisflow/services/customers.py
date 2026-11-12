"""UC-02: Müşteri kaydı, girdi doğrulama ve arama (FR-02, BR-09)."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from servisflow.repository.models import Customer
from servisflow.services.clock import Clock
from servisflow.services.errors import NotFoundError, ValidationError

NAME_MAX = 100  # R-11
_PHONE_SEPARATORS = re.compile(r"[\s\-()]")
_MOBILE = re.compile(r"5\d{9}")


def normalize_phone(raw: str | None) -> str | None:
    """BR-09: boşluk, tire ve parantez atılır, baştaki 0 düşer; 5 ile başlayan 10 hane.

    Boş giriş telefon yok demektir (isteğe bağlı alan).
    """
    digits = _PHONE_SEPARATORS.sub("", raw or "")
    if not digits:
        return None
    if digits.startswith("0"):
        digits = digits[1:]
    if not _MOBILE.fullmatch(digits):
        raise ValidationError("Telefon 5 ile başlayan 10 haneli bir numara olmalıdır.")
    return digits


def _clean_name(full_name: str) -> str:
    cleaned = " ".join((full_name or "").split())
    if not 1 <= len(cleaned) <= NAME_MAX:
        raise ValidationError(f"Ad soyad 1–{NAME_MAX} karakter olmalıdır.")
    return cleaned


def _fold(text: str) -> str:
    """Türkçe küçük harf: `I → ı`, `İ → i`.

    Python'un lower() fonksiyonu `I` harfini `i` yapar, `ı` değil.
    """
    return text.replace("I", "ı").replace("İ", "i").lower()


def create_customer(
    session: Session, clock: Clock, full_name: str, phone: str | None = None
) -> Customer:
    customer = Customer(
        full_name=_clean_name(full_name),
        phone=normalize_phone(phone),
        created_at=clock.now(),
    )
    session.add(customer)
    session.flush()
    return customer


def update_customer(
    session: Session, customer_id: int, full_name: str, phone: str | None
) -> Customer:
    name, normalized = _clean_name(full_name), normalize_phone(phone)
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError("Müşteri bulunamadı.")
    customer.full_name, customer.phone = name, normalized
    session.flush()
    return customer


def search_customers(session: Session, text: str) -> list[Customer]:
    """Ad (Türkçe büyük/küçük harf duyarsız) veya telefonda geçen metinle arar.

    SQLite'ın lower() fonksiyonu yalnızca ASCII harfleri çevirdiği için eşleştirme
    Python'da yapılır; tek şubeli bir serviste müşteri sayısı bunu kaldırır.
    """
    query = _fold(" ".join((text or "").split()))
    digits = _PHONE_SEPARATORS.sub("", text or "").lstrip("0")
    customers = session.scalars(select(Customer).order_by(Customer.id))
    return [
        c
        for c in customers
        if query in _fold(c.full_name)
        or (digits.isdigit() and c.phone is not None and digits in c.phone)
    ]
