"""UC-06: İdempotent görev tamamlama ve tutar kilitleme (FR-06, BR-02 – BR-04).

Her iki işlem de tek bir koşullu UPDATE'tir (ADR-005). Önce okuyup sonra yazmak,
iki sekmeden gelen eşzamanlı ✓'de ikinci isteğin `completed_at`'i ezmesine yol
açardı (R-07, TC-23). Koşul sağlanmazsa hiçbir satır değişmez; ardından işin
güncel hali okunarak sonuç belirlenir.
"""

from datetime import datetime, time, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from servisflow.repository.models import TASK_DONE, TASK_TODO, ServiceTask
from servisflow.services.clock import ISTANBUL, Clock
from servisflow.services.errors import ConflictError, NotFoundError


def _istanbul_day_start_utc(now: datetime) -> datetime:
    day = now.astimezone(ISTANBUL).date()
    return datetime.combine(day, time.min, tzinfo=ISTANBUL).astimezone(timezone.utc)


def _current(session: Session, task_id: int) -> ServiceTask:
    task = session.get(ServiceTask, task_id)
    if task is None:
        raise NotFoundError("İş bulunamadı.")
    session.refresh(task)  # başka bir oturumun yazdığı güncel hali al
    return task


def complete_task(session: Session, clock: Clock, task_id: int) -> ServiceTask:
    """İşi `DONE` yapar; zaten `DONE` ise hiçbir şey değişmez (BR-03, TC-18)."""
    session.execute(
        update(ServiceTask)
        .where(ServiceTask.id == task_id, ServiceTask.status == TASK_TODO)
        .values(status=TASK_DONE, completed_at=clock.now())
        .execution_options(synchronize_session=False)
    )
    return _current(session, task_id)


def undo_completion(session: Session, clock: Clock, task_id: int) -> ServiceTask:
    """✓'yi yalnızca tamamlandığı İstanbul günü içinde geri alır (BR-04).

    Karar tablosu (Faz 2, 3.4): K1 aynı gün → `TODO`; K2 geçmiş gün → red;
    K3–K4 iş zaten `TODO` → değişiklik yok.
    """
    result = session.execute(
        update(ServiceTask)
        .where(
            ServiceTask.id == task_id,
            ServiceTask.status == TASK_DONE,
            ServiceTask.completed_at >= _istanbul_day_start_utc(clock.now()),
        )
        .values(status=TASK_TODO, completed_at=None)
        .execution_options(synchronize_session=False)
    )
    task = _current(session, task_id)
    if result.rowcount == 0 and task.status == TASK_DONE:
        raise ConflictError("Geçmiş günün işi geri alınamaz.")
    return task
