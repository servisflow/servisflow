"""UC-05: Görev tabanlı iş listesi yönetimi (FR-05, BR-01, BR-02, BR-08).

Servisler `flush` yapar, `commit` yapmaz: işlem sınırını çağıran (arayüz) belirler.
"""

from decimal import Decimal

from sqlalchemy import case, delete, func, select, update
from sqlalchemy.orm import Session

from servisflow.repository.models import (
    MAX_AMOUNT_KURUS,
    MIN_AMOUNT_KURUS,
    TASK_DONE,
    TASK_TODO,
    ServiceTask,
    ServiceVisit,
)
from servisflow.services.clock import Clock
from servisflow.services.errors import ConflictError, NotFoundError, ValidationError

TITLE_MAX = 100  # R-11
NOTE_MAX = 500  # R-11
_KURUS = Decimal("0.01")


def to_kurus(amount: Decimal | int) -> int:
    """TL tutarını tamsayı kuruşa çevirir (BR-01, ADR-003).

    `float` kabul edilmez: 1.15 bellekte 1.1499999... olarak durur. Arayüz
    sayıyı `Decimal(str(deger))` ile çevirip gönderir. Metin ayrıştırılmaz (RV-05).
    """
    if isinstance(amount, bool) or not isinstance(amount, (Decimal, int)):
        raise ValidationError("Tutar sayı olarak girilmelidir.")
    value = Decimal(amount)
    if not value.is_finite():
        raise ValidationError("Tutar geçerli bir sayı olmalıdır.")
    if value != value.quantize(_KURUS):
        raise ValidationError("Tutar en fazla 2 ondalık basamak içerebilir.")
    kurus = int(value / _KURUS)
    if not MIN_AMOUNT_KURUS <= kurus <= MAX_AMOUNT_KURUS:
        raise ValidationError("Tutar 0,01 TL ile 1.000.000,00 TL arasında olmalıdır.")
    return kurus


def _clean_title(title: str) -> str:
    # str.strip() sekme ve satır sonunu da kırpar; SQLite trim() yalnızca boşluğu.
    cleaned = (title or "").strip()
    if not 1 <= len(cleaned) <= TITLE_MAX:
        raise ValidationError(f"İş başlığı 1–{TITLE_MAX} karakter olmalıdır.")
    return cleaned


def _clean_note(note: str | None) -> str | None:
    cleaned = (note or "").strip()
    if len(cleaned) > NOTE_MAX:
        raise ValidationError(f"Not en fazla {NOTE_MAX} karakter olabilir.")
    return cleaned or None


def _fields(title: str, amount: Decimal | int, note: str | None) -> dict:
    """Tüm girdiyi veritabanına dokunmadan önce doğrular."""
    return {
        "title": _clean_title(title),
        "amount_kurus": to_kurus(amount),
        "note": _clean_note(note),
    }


def _raise_missing_or_done(session: Session, task_id: int) -> None:
    if session.get(ServiceTask, task_id) is None:
        raise NotFoundError("İş bulunamadı.")
    raise ConflictError("Tamamlanan iş düzenlenemez veya silinemez.")


def add_task(
    session: Session,
    clock: Clock,
    visit_id: int,
    title: str,
    amount: Decimal | int,
    note: str | None = None,
) -> ServiceTask:
    """Ziyarete `TODO` durumunda iş ekler; `created_at` saat sağlayıcısından gelir."""
    fields = _fields(title, amount, note)
    if session.get(ServiceVisit, visit_id) is None:
        raise NotFoundError("Servis ziyareti bulunamadı.")
    task = ServiceTask(
        visit_id=visit_id, status=TASK_TODO, created_at=clock.now(), **fields
    )
    session.add(task)
    session.flush()
    return task


def update_task(
    session: Session,
    task_id: int,
    title: str,
    amount: Decimal | int,
    note: str | None,
) -> ServiceTask:
    """Yalnızca `TODO` işi günceller (BR-02).

    Durum kontrolü ve yazma tek koşullu UPDATE'tir (ADR-005 ile aynı yaklaşım):
    okuma ile yazma arasında iş tamamlanırsa güncelleme hiçbir satırı etkilemez.
    """
    fields = _fields(title, amount, note)
    result = session.execute(
        update(ServiceTask)
        .where(ServiceTask.id == task_id, ServiceTask.status == TASK_TODO)
        .values(**fields)
        .execution_options(synchronize_session="fetch")
    )
    if result.rowcount == 0:
        _raise_missing_or_done(session, task_id)
    return session.get(ServiceTask, task_id)


def delete_task(session: Session, task_id: int) -> None:
    """Yalnızca `TODO` işi siler (BR-08); koşullu DELETE ile."""
    result = session.execute(
        delete(ServiceTask)
        .where(ServiceTask.id == task_id, ServiceTask.status == TASK_TODO)
        .execution_options(synchronize_session="fetch")
    )
    if result.rowcount == 0:
        _raise_missing_or_done(session, task_id)


def visit_totals(session: Session, visit_id: int) -> tuple[int, int]:
    """Ziyaretin (açık, tamamlanan) iş toplamları, kuruş (UC-05 ana akış)."""
    if session.get(ServiceVisit, visit_id) is None:
        raise NotFoundError("Servis ziyareti bulunamadı.")

    def _sum(status: str):
        return func.coalesce(
            func.sum(case((ServiceTask.status == status, ServiceTask.amount_kurus))),
            0,
        )

    open_total, done_total = session.execute(
        select(_sum(TASK_TODO), _sum(TASK_DONE)).where(ServiceTask.visit_id == visit_id)
    ).one()
    return int(open_total), int(done_total)
