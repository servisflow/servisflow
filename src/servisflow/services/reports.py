"""UC-07: Araç servis geçmişi ve zaman dilimi duyarlı dönemsel raporlama.

Dönem sınırları İstanbul takvimine göre hesaplanır, sorgu UTC ile yapılır
(BR-06, ADR-004). Toplam bir sayaçta tutulmaz; her seferinde tamamlanan
işlerden hesaplanır (BR-05, ADR-005).
"""

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from servisflow.repository.models import TASK_DONE, ServiceTask, ServiceVisit, Vehicle
from servisflow.services.clock import ISTANBUL
from servisflow.services.errors import NotFoundError, ValidationError

PERIOD_DAY = "gun"
PERIOD_WEEK = "hafta"
PERIOD_MONTH = "ay"
PERIOD_YEAR = "yil"
PERIODS = (PERIOD_DAY, PERIOD_WEEK, PERIOD_MONTH, PERIOD_YEAR)


def _local_period(kind: str, day: date) -> tuple[date, date]:
    """Dönemin İstanbul takvimindeki ilk günü ve bir sonraki dönemin ilk günü."""
    if kind == PERIOD_DAY:
        return day, day + timedelta(days=1)
    if kind == PERIOD_WEEK:
        start = day - timedelta(days=day.weekday())  # Hafta Pazartesi başlar
        return start, start + timedelta(days=7)
    if kind == PERIOD_MONTH:
        start = day.replace(day=1)
        return start, (start + timedelta(days=32)).replace(day=1)
    if kind == PERIOD_YEAR:
        return date(day.year, 1, 1), date(day.year + 1, 1, 1)
    raise ValidationError(f"Geçersiz dönem: {kind!r}. Seçenekler: {', '.join(PERIODS)}")


def _istanbul_midnight_utc(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=ISTANBUL).astimezone(timezone.utc)


def period_bounds(kind: str, day: date) -> tuple[datetime, datetime]:
    """`day` gününü içeren dönemin UTC sınırları: [başlangıç, bitiş)."""
    start, end = _local_period(kind, day)
    return _istanbul_midnight_utc(start), _istanbul_midnight_utc(end)


def _done_in_period(start: datetime, end: datetime):
    return (
        ServiceTask.status == TASK_DONE,
        ServiceTask.completed_at >= start,
        ServiceTask.completed_at < end,
    )


def gross_total(session: Session, start: datetime, end: datetime) -> int:
    """[start, end) aralığında tamamlanan işlerin brüt bedeli (kuruş)."""
    total = session.scalar(
        select(func.coalesce(func.sum(ServiceTask.amount_kurus), 0)).where(
            *_done_in_period(start, end)
        )
    )
    return int(total)


def completed_tasks(
    session: Session, start: datetime, end: datetime
) -> list[ServiceTask]:
    """Rapor dökümü: aralıkta tamamlanan işler, tamamlanma sırasıyla."""
    query = (
        select(ServiceTask)
        .where(*_done_in_period(start, end))
        .order_by(ServiceTask.completed_at, ServiceTask.id)
    )
    return list(session.scalars(query))


def open_work(session: Session) -> tuple[int, int]:
    """Henüz tamamlanmamış (TODO) işlerin sayısı ve toplam tutarı (kuruş).

    Ana sayfadaki özet içindir; brüt iş bedeline girmez (BR-05).
    """
    count, total = session.execute(
        select(
            func.count(ServiceTask.id),
            func.coalesce(func.sum(ServiceTask.amount_kurus), 0),
        ).where(ServiceTask.status != TASK_DONE)
    ).one()
    return int(count), int(total)


def vehicle_history(session: Session, vehicle_id: int) -> list[ServiceVisit]:
    """Aracın ziyaretleri işleriyle birlikte, en yeniden en eskiye (FR-07).

    İşler tek ek sorguyla yüklenir; ziyaret başına ayrı sorgu (N+1) oluşmaz.
    """
    if session.get(Vehicle, vehicle_id) is None:
        raise NotFoundError("Araç bulunamadı.")
    query = (
        select(ServiceVisit)
        .options(selectinload(ServiceVisit.tasks))
        .where(ServiceVisit.vehicle_id == vehicle_id)
        .order_by(ServiceVisit.opened_at.desc(), ServiceVisit.id.desc())
    )
    return list(session.scalars(query))
