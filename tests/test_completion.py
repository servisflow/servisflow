"""UC-06 testleri: idempotent tamamlama ve aynı gün geri alma (TC-18 – TC-21, TC-23)."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from servisflow.repository.db import init_db, make_engine, make_session_factory
from servisflow.repository.models import (
    TASK_DONE,
    TASK_TODO,
    Customer,
    ServiceTask,
    Vehicle,
)
from servisflow.services import completion
from servisflow.services.clock import ISTANBUL, FixedClock
from servisflow.services.errors import ConflictError, NotFoundError
from servisflow.services.reports import gross_total, period_bounds
from servisflow.services.tasks import add_task
from servisflow.services.visits import open_visit


def _task(session, clock, amount="1600"):
    customer = Customer(full_name="Can GPT", created_at=clock.now())
    vehicle = Vehicle(
        customer=customer, plate_normalized="34BJK321", brand="Isuzu", model="X"
    )
    session.add(vehicle)
    session.flush()
    visit = open_visit(session, clock, vehicle.id)
    return add_task(session, clock, visit.id, "Ön sol teker", Decimal(amount))


def _day_total(session, clock):
    return gross_total(
        session, *period_bounds("gun", clock.now().astimezone(ISTANBUL).date())
    )


@pytest.fixture
def task(session, clock):
    return _task(session, clock)


# --- complete_task: BR-02, BR-03 ---------------------------------------------


def test_is_tamamlanir_ve_zaman_saat_saglayicidan(session, clock, task):
    done = completion.complete_task(session, clock, task.id)
    assert (done.status, done.completed_at) == (TASK_DONE, clock.now())
    assert _day_total(session, clock) == 160_000


def test_tc18_iki_kez_tik_tek_tamamlama(session, clock, task):
    first = completion.complete_task(session, clock, task.id).completed_at
    clock.advance(timedelta(minutes=5))
    again = completion.complete_task(session, clock, task.id)
    assert again.completed_at == first  # completed_at değişmez
    assert _day_total(session, clock) == 160_000  # toplam ikiye katlanmaz


def test_olmayan_is_tamamlanamaz(session, clock):
    with pytest.raises(NotFoundError):
        completion.complete_task(session, clock, 999)


# --- undo_completion: BR-04 karar tablosu -------------------------------------


def test_tc19_k1_ayni_gun_geri_al_ve_yeniden_tik(session, clock, task):
    completion.complete_task(session, clock, task.id)
    clock.advance(timedelta(hours=1))
    undone = completion.undo_completion(session, clock, task.id)
    assert (undone.status, undone.completed_at) == (TASK_TODO, None)
    assert _day_total(session, clock) == 0  # rapordan düşer

    clock.advance(timedelta(hours=1))
    redone = completion.complete_task(session, clock, task.id)
    assert redone.completed_at == clock.now()  # yeni tamamlanma zamanı
    assert _day_total(session, clock) == 160_000  # toplamda bir kez


def test_tc20_k2_dunku_is_bugun_geri_alinamaz(session, clock, task):
    completion.complete_task(session, clock, task.id)
    completed_at = task.completed_at
    clock.advance(timedelta(days=1))
    with pytest.raises(ConflictError):
        completion.undo_completion(session, clock, task.id)
    session.refresh(task)
    assert (task.status, task.completed_at) == (TASK_DONE, completed_at)


def test_tc20_gun_siniri_istanbul_gece_yarisi(session):
    """23:59:59'da tamamlanan iş 00:00:00'da artık geri alınamaz (BR-04, BR-06)."""
    clock = FixedClock(datetime(2026, 10, 22, 23, 59, 59, tzinfo=ISTANBUL))
    task = _task(session, clock)
    completion.complete_task(session, clock, task.id)
    clock.advance(timedelta(seconds=1))
    with pytest.raises(ConflictError):
        completion.undo_completion(session, clock, task.id)


def test_tc20_utc_ile_ayni_gun_ama_istanbulda_farkli_gun(session):
    """UTC 21:30 (İstanbul 00:30) ile UTC 20:30 (İstanbul 23:30) aynı UTC günüdür."""
    clock = FixedClock(datetime(2026, 10, 22, 23, 30, tzinfo=ISTANBUL))
    task = _task(session, clock)
    completion.complete_task(session, clock, task.id)
    clock.advance(timedelta(hours=1))
    assert clock.now().date() == task.completed_at.date()  # UTC'de aynı gün
    with pytest.raises(ConflictError):
        completion.undo_completion(session, clock, task.id)


def test_tc21_k3_k4_todo_isi_geri_almak_degisiklik_yapmaz(session, clock, task):
    result = completion.undo_completion(session, clock, task.id)
    assert (result.status, result.completed_at) == (TASK_TODO, None)


def test_olmayan_is_geri_alinamaz(session, clock):
    with pytest.raises(NotFoundError):
        completion.undo_completion(session, clock, 999)


# --- TC-23: iki sekmeden aynı anda ✓ (NFR-04, R-07) ---------------------------


def test_tc23_eszamanli_tik_tek_tamamlama(tmp_path):
    """İki ayrı oturum (iki sekme) işi TODO olarak okumuşken ikisi de ✓ yapar.

    Önce oku sonra yaz yaklaşımında ikinci istek completed_at'i ezerdi; koşullu
    UPDATE'te ikinci istek hiçbir satırı değiştirmez.
    """
    engine = make_engine(f"sqlite:///{tmp_path / 'tc23.db'}")
    init_db(engine)
    factory = make_session_factory(engine)
    clock = FixedClock(datetime(2026, 10, 22, 10, 0, tzinfo=ISTANBUL))
    with factory.begin() as s:
        task_id = _task(s, clock).id

    tab_a, tab_b = factory(), factory()
    stale = tab_a.get(ServiceTask, task_id)
    assert stale.status == TASK_TODO  # A sekmesi işi açık görüyor
    completion.complete_task(tab_b, clock, task_id)
    tab_b.commit()
    first = clock.now()

    clock.advance(timedelta(seconds=2))
    result = completion.complete_task(tab_a, clock, task_id)
    tab_a.commit()
    assert result.completed_at == first
    with factory() as check:
        assert check.get(ServiceTask, task_id).completed_at == first
        assert _day_total(check, FixedClock(first)) == 160_000
    tab_a.close()
    tab_b.close()
    engine.dispose()
