"""UC-04 testleri: ziyaret açılışı (TC-13, TC-14)."""

from datetime import timedelta

import pytest

from servisflow.repository.models import Customer, ServiceVisit, Vehicle
from servisflow.services import visits
from servisflow.services.errors import NotFoundError, ValidationError
from servisflow.services.reports import vehicle_history


@pytest.fixture
def vehicle(session, clock):
    customer = Customer(full_name="Can GPT", created_at=clock.now())
    vehicle = Vehicle(
        customer=customer, plate_normalized="34BJK321", brand="Isuzu", model="10 Long"
    )
    session.add(vehicle)
    session.flush()
    return vehicle


def test_tc13_acilis_zamani_saat_saglayicidan(session, clock, vehicle):
    visit = visits.open_visit(session, clock, vehicle.id, "Ön sol tekerden ses")
    assert visit.id is not None
    assert visit.opened_at == clock.now()
    assert visit.complaint == "Ön sol tekerden ses"


def test_tc14_ayni_araca_farkli_gunlerde_ayri_ziyaret(session, clock, vehicle):
    first = visits.open_visit(session, clock, vehicle.id)
    clock.advance(timedelta(days=1))
    second = visits.open_visit(session, clock, vehicle.id)
    assert first.id != second.id
    assert [v.id for v in vehicle_history(session, vehicle.id)] == [second.id, first.id]


@pytest.mark.parametrize("complaint", [None, "", "  \n "])
def test_bos_aciklama_none_saklanir(session, clock, vehicle, complaint):
    assert visits.open_visit(session, clock, vehicle.id, complaint).complaint is None


def test_aciklama_siniri(session, clock, vehicle):
    assert (
        len(visits.open_visit(session, clock, vehicle.id, "x" * 500).complaint) == 500
    )
    with pytest.raises(ValidationError):
        visits.open_visit(session, clock, vehicle.id, "x" * 501)


def test_olmayan_araca_ziyaret_acilamaz(session, clock):
    with pytest.raises(NotFoundError):
        visits.open_visit(session, clock, 999)
    assert session.query(ServiceVisit).count() == 0
