"""UC-07 testleri: dönem sınırları, brüt toplam ve araç geçmişi (TC-24 – TC-29)."""

from datetime import date, datetime, timezone

import pytest

from servisflow.repository.models import (
    TASK_DONE,
    Customer,
    ServiceTask,
    ServiceVisit,
    Vehicle,
)
from servisflow.services import reports
from servisflow.services.clock import ISTANBUL
from servisflow.services.errors import NotFoundError, ValidationError


def ist(*args) -> datetime:
    return datetime(*args, tzinfo=ISTANBUL)


@pytest.fixture
def vehicle(session):
    customer = Customer(full_name="Can GPT", created_at=ist(2026, 10, 1, 9, 0))
    vehicle = Vehicle(
        customer=customer, plate_normalized="34BJK321", brand="Isuzu", model="10 Long"
    )
    session.add(vehicle)
    session.flush()
    return vehicle


def add_visit(session, vehicle, opened_at):
    visit = ServiceVisit(vehicle=vehicle, opened_at=opened_at)
    session.add(visit)
    session.flush()
    return visit


def add_task(session, visit, amount_tl, created_at, completed_at=None):
    task = ServiceTask(
        visit=visit,
        title="İş",
        amount_kurus=amount_tl * 100,
        created_at=created_at,
        status=TASK_DONE if completed_at else "TODO",
        completed_at=completed_at,
    )
    session.add(task)
    session.flush()
    return task


def total_tl(session, kind, day):
    return reports.gross_total(session, *reports.period_bounds(kind, day)) / 100


# --- Dönem sınırları -------------------------------------------------------


def test_gun_sinirlari_istanbul_gece_yarisindan_utcye_cevrilir():
    start, end = reports.period_bounds(reports.PERIOD_DAY, date(2026, 10, 23))
    assert start == datetime(2026, 10, 22, 21, 0, tzinfo=timezone.utc)
    assert end == datetime(2026, 10, 23, 21, 0, tzinfo=timezone.utc)


def test_hafta_pazartesi_baslar_ve_yedi_gun_surer():
    start, end = reports.period_bounds(reports.PERIOD_WEEK, date(2026, 10, 25))  # Pazar
    assert start.astimezone(ISTANBUL) == ist(2026, 10, 19)  # Pazartesi
    assert end.astimezone(ISTANBUL) == ist(2026, 10, 26)


def test_ay_ve_yil_sinirlari():
    start, end = reports.period_bounds(reports.PERIOD_MONTH, date(2026, 12, 15))
    assert (start.astimezone(ISTANBUL), end.astimezone(ISTANBUL)) == (
        ist(2026, 12, 1),
        ist(2027, 1, 1),
    )
    start, end = reports.period_bounds(reports.PERIOD_YEAR, date(2026, 6, 1))
    assert (start.astimezone(ISTANBUL), end.astimezone(ISTANBUL)) == (
        ist(2026, 1, 1),
        ist(2027, 1, 1),
    )


def test_subat_artik_yilda_29_gun():
    """TC-29 (ay sınırı): 29 Şubat 2028 Şubat ayına aittir."""
    start, end = reports.period_bounds(reports.PERIOD_MONTH, date(2028, 2, 29))
    assert (start.astimezone(ISTANBUL), end.astimezone(ISTANBUL)) == (
        ist(2028, 2, 1),
        ist(2028, 3, 1),
    )


def test_gecersiz_donem_reddedilir():
    with pytest.raises(ValidationError):
        reports.period_bounds("ceyrek", date(2026, 10, 23))


# --- Brüt toplam ------------------------------------------------------------


def test_tc24_dun_acilip_bugun_tamamlanan_is_bugune_yazilir(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 10, 22, 9, 0))
    add_task(session, visit, 1600, ist(2026, 10, 22, 9, 30), ist(2026, 10, 23, 11, 0))

    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 22)) == 0
    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 23)) == 1600


def test_tc25_gunluk_ve_haftalik_toplam(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 10, 22, 9, 0))
    add_task(session, visit, 1600, ist(2026, 10, 22, 9, 0), ist(2026, 10, 22, 15, 0))
    add_task(session, visit, 1200, ist(2026, 10, 22, 9, 0), ist(2026, 10, 23, 10, 0))

    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 22)) == 1600
    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 23)) == 1200
    assert total_tl(session, reports.PERIOD_WEEK, date(2026, 10, 22)) == 2800


def test_tc26_gece_yarisi_siniri(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 10, 22, 9, 0))
    add_task(
        session, visit, 100, ist(2026, 10, 22, 9, 0), ist(2026, 10, 22, 23, 59, 59)
    )
    add_task(session, visit, 200, ist(2026, 10, 22, 9, 0), ist(2026, 10, 23, 0, 0, 0))

    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 22)) == 100
    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 23)) == 200


def test_tc27_acik_is_bos_ve_gelecek_donem(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 10, 22, 9, 0))
    add_task(session, visit, 1600, ist(2026, 10, 22, 9, 0))  # açık iş

    assert total_tl(session, reports.PERIOD_DAY, date(2026, 10, 22)) == 0
    assert total_tl(session, reports.PERIOD_MONTH, date(2026, 9, 1)) == 0
    assert total_tl(session, reports.PERIOD_YEAR, date(2030, 1, 1)) == 0


def test_tc29_yil_sonu_siniri(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 12, 31, 9, 0))
    add_task(
        session, visit, 500, ist(2026, 12, 31, 9, 0), ist(2026, 12, 31, 23, 59, 59)
    )
    add_task(session, visit, 700, ist(2026, 12, 31, 9, 0), ist(2027, 1, 1, 0, 0, 0))

    assert total_tl(session, reports.PERIOD_YEAR, date(2026, 6, 1)) == 500
    assert total_tl(session, reports.PERIOD_YEAR, date(2027, 6, 1)) == 700


def test_tamamlanan_isler_dokumu_sirali_ve_acik_isler_haric(session, vehicle):
    visit = add_visit(session, vehicle, ist(2026, 10, 22, 9, 0))
    later = add_task(
        session, visit, 300, ist(2026, 10, 22, 9, 0), ist(2026, 10, 22, 16, 0)
    )
    earlier = add_task(
        session, visit, 200, ist(2026, 10, 22, 9, 0), ist(2026, 10, 22, 12, 0)
    )
    add_task(session, visit, 900, ist(2026, 10, 22, 9, 0))

    bounds = reports.period_bounds(reports.PERIOD_DAY, date(2026, 10, 22))
    assert reports.completed_tasks(session, *bounds) == [earlier, later]


# --- Araç geçmişi -----------------------------------------------------------


def test_tc28_arac_gecmisi_yeniden_eskiye(session, vehicle):
    first = add_visit(session, vehicle, ist(2026, 9, 1, 9, 0))
    third = add_visit(session, vehicle, ist(2026, 11, 1, 9, 0))
    second = add_visit(session, vehicle, ist(2026, 10, 1, 9, 0))

    assert reports.vehicle_history(session, vehicle.id) == [third, second, first]


def test_olmayan_aracin_gecmisi_istenemez(session):
    with pytest.raises(NotFoundError):
        reports.vehicle_history(session, 999)
