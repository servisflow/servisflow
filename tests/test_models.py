"""Veri modeli ve veritabanı kısıtları (son savunma hattı) testleri."""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from servisflow.repository.models import (
    TASK_DONE,
    TASK_TODO,
    Customer,
    ServiceTask,
    ServiceVisit,
    Vehicle,
)
from servisflow.services import errors


def _visit(session, clock, plate="34BJK321"):
    customer = Customer(full_name="Can GPT", created_at=clock.now())
    vehicle = Vehicle(
        customer=customer, plate_normalized=plate, brand="Isuzu", model="10 Long"
    )
    visit = ServiceVisit(vehicle=vehicle, opened_at=clock.now())
    session.add(visit)
    session.flush()
    return visit


def _task(visit, clock, **overrides):
    values = {
        "visit": visit,
        "title": "Ön sol teker",
        "amount_kurus": 160000,
        "created_at": clock.now(),
    }
    values.update(overrides)
    return ServiceTask(**values)


def test_musteri_arac_ziyaret_is_zinciri_kaydedilir(session, clock):
    visit = _visit(session, clock)
    session.add(_task(visit, clock))
    session.commit()

    stored = session.get(ServiceTask, 1)
    assert stored.status == TASK_TODO
    assert stored.visit.vehicle.customer.full_name == "Can GPT"
    assert stored.created_at == clock.now()


def test_ayni_plaka_ikinci_kez_eklenemez(session, clock):
    _visit(session, clock)
    customer = session.get(Customer, 1)
    session.add(
        Vehicle(customer=customer, plate_normalized="34BJK321", brand="X", model="Y")
    )
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("amount", [0, 99, 150, 160_050, 100_000_100])
def test_tutar_sinirlarin_disinda_reddedilir(session, clock, amount):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, amount_kurus=amount))
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("amount", [100, 100_000_000])
def test_tutar_sinirlarinda_kabul_edilir(session, clock, amount):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, amount_kurus=amount))
    session.flush()


def test_done_is_tamamlanma_zamani_olmadan_kaydedilemez(session, clock):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, status=TASK_DONE))
    with pytest.raises(IntegrityError):
        session.flush()


def test_todo_is_tamamlanma_zamaniyla_kaydedilemez(session, clock):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, completed_at=clock.now()))
    with pytest.raises(IntegrityError):
        session.flush()


def test_olmayan_musteriye_arac_eklenemez(session):
    session.add(
        Vehicle(customer_id=999, plate_normalized="06AB123", brand="X", model="Y")
    )
    with pytest.raises(IntegrityError):
        session.flush()


def test_saat_dilimsiz_zaman_kaydedilemez(session):
    session.add(Customer(full_name="Can GPT", created_at=datetime(2026, 10, 22)))
    with pytest.raises(StatementError):
        session.flush()


def test_servis_hatalari_ortak_tabandan_turer():
    for error in (errors.ValidationError, errors.NotFoundError, errors.ConflictError):
        assert issubclass(error, errors.ServisFlowError)


# --- PR #10 kod incelemesi (Kerem Erden) bulgularına ait testler ----------


def test_kesirli_tutar_reddedilir(session, clock):
    """SQLite tür dayatmaz; 1600.5 kuruş `real` olarak saklanmamalı (ADR-003)."""
    visit = _visit(session, clock)
    session.add(_task(visit, clock, amount_kurus=1600.5))
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("title", ["", "   ", "x" * 101])
def test_gecersiz_is_basligi_reddedilir(session, clock, title):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, title=title))
    with pytest.raises(IntegrityError):
        session.flush()


def test_uzun_is_notu_reddedilir(session, clock):
    visit = _visit(session, clock)
    session.add(_task(visit, clock, note="x" * 501))
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("full_name", ["", "  ", "x" * 101])
def test_gecersiz_musteri_adi_reddedilir(session, clock, full_name):
    session.add(Customer(full_name=full_name, created_at=clock.now()))
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("phone", ["532123456", "53212345678", "532-123-456"])
def test_gecersiz_telefon_reddedilir(session, clock, phone):
    session.add(Customer(full_name="Can GPT", phone=phone, created_at=clock.now()))
    with pytest.raises(IntegrityError):
        session.flush()


@pytest.mark.parametrize("plate", ["34AB", "Y" * 21])
def test_gecersiz_uzunlukta_plaka_reddedilir(session, clock, plate):
    with pytest.raises(IntegrityError):
        _visit(session, clock, plate=plate)


def test_uzun_sikayet_reddedilir(session, clock):
    visit = _visit(session, clock)
    visit.complaint = "x" * 501
    with pytest.raises(IntegrityError):
        session.flush()
