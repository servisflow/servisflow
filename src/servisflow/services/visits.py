"""UC-04: Servis ziyareti açılışı ve otomatik zaman damgalama (FR-04)."""

from sqlalchemy.orm import Session

from servisflow.repository.models import ServiceVisit, Vehicle
from servisflow.services.clock import Clock
from servisflow.services.errors import NotFoundError, ValidationError

COMPLAINT_MAX = 500  # R-11


def open_visit(
    session: Session, clock: Clock, vehicle_id: int, complaint: str | None = None
) -> ServiceVisit:
    """Araca yeni ziyaret açar; `opened_at` yalnızca saat sağlayıcısından gelir.

    Kullanıcı tarih giremez: fonksiyonun tarih parametresi yoktur (UC-04).
    """
    cleaned = (complaint or "").strip()
    if len(cleaned) > COMPLAINT_MAX:
        raise ValidationError(f"Açıklama en fazla {COMPLAINT_MAX} karakter olabilir.")
    if session.get(Vehicle, vehicle_id) is None:
        raise NotFoundError("Araç bulunamadı.")
    visit = ServiceVisit(
        vehicle_id=vehicle_id, opened_at=clock.now(), complaint=cleaned or None
    )
    session.add(visit)
    session.flush()
    return visit
