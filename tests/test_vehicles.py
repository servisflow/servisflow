"""UC-03 testleri: plaka normalizasyonu ve tekillik (TC-10 – TC-12)."""

import pytest
from sqlalchemy.exc import IntegrityError

from servisflow.repository.models import Customer, Vehicle
from servisflow.services import vehicles
from servisflow.services.errors import ConflictError, NotFoundError, ValidationError


@pytest.fixture
def customer(session, clock):
    customer = Customer(full_name="Can GPT", created_at=clock.now())
    session.add(customer)
    session.flush()
    return customer


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("34 bjk 321", "34BJK321"),
        ("34BJK321", "34BJK321"),
        ("34 abi 12", "34ABI12"),  # TC-11: Latin büyük harf (i → I, İ değil)
        ("01 a 1234", "01A1234"),  # il kodu alt sınırı
        ("81 abc 12", "81ABC12"),  # il kodu üst sınırı
        ("\t06 ab\n123 ", "06AB123"),
    ],
)
def test_plaka_normalize_edilir(raw, expected):
    assert vehicles.normalize_plate(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "34 ŞK 123",  # TC-12: Türkçe karakter
        "82 AB 123",  # TC-12: il kodu 82
        "34 ABCD 12",  # TC-12: 4 harf
        "34 abı 12",  # ı.upper() == "I" tuzağı
        "00 AB 123",
        "34 AB 1",
        "34 AB 12345",
        "3 AB 123",
        "",
        None,
    ],
)
def test_gecersiz_plaka_reddedilir(raw):
    with pytest.raises(ValidationError):
        vehicles.normalize_plate(raw)


def test_arac_kaydedilir(session, customer):
    vehicle = vehicles.register_vehicle(
        session, customer.id, "34 bjk 321", " Isuzu ", "10  Long"
    )
    assert vehicle.id is not None
    assert (vehicle.plate_normalized, vehicle.brand, vehicle.model) == (
        "34BJK321",
        "Isuzu",
        "10 Long",
    )


def test_tc10_ayni_plaka_farkli_yazimla_reddedilir(session, customer):
    vehicles.register_vehicle(session, customer.id, "34BJK321", "Isuzu", "10 Long")
    with pytest.raises(ConflictError):
        vehicles.register_vehicle(session, customer.id, "34 bjk 321", "Ford", "Transit")
    assert session.query(Vehicle).count() == 1


def test_ayni_musteriye_iki_arac(session, customer):
    vehicles.register_vehicle(session, customer.id, "34BJK321", "Isuzu", "10 Long")
    vehicles.register_vehicle(session, customer.id, "06 AB 123", "Ford", "Transit")
    session.refresh(customer)
    assert len(customer.vehicles) == 2


def test_yaris_durumunda_tekil_kisit_conflict_doner(session, customer, monkeypatch):
    """Ön denetimden sonra başka bir istek aynı plakayı eklerse (TC-10)."""
    vehicles.register_vehicle(session, customer.id, "34BJK321", "Isuzu", "10 Long")
    monkeypatch.setattr(vehicles, "_by_plate", lambda *_: None)
    with pytest.raises(ConflictError) as info:
        vehicles.register_vehicle(session, customer.id, "34BJK321", "Ford", "Transit")
    assert isinstance(info.value.__cause__, IntegrityError)
    # Savepoint sayesinde oturum kullanılabilir kalır.
    assert session.query(Vehicle).count() == 1


@pytest.mark.parametrize(
    "brand, model", [("", "Transit"), ("Ford", " "), ("x" * 51, "T")]
)
def test_gecersiz_marka_model(session, customer, brand, model):
    with pytest.raises(ValidationError):
        vehicles.register_vehicle(session, customer.id, "06AB123", brand, model)


def test_olmayan_musteriye_arac_eklenemez(session):
    with pytest.raises(NotFoundError):
        vehicles.register_vehicle(session, 999, "06AB123", "Ford", "Transit")


def test_plakayla_arac_bulunur(session, customer):
    saved = vehicles.register_vehicle(session, customer.id, "34BJK321", "Isuzu", "X")
    assert vehicles.find_vehicle_by_plate(session, "34 bjk 321").id == saved.id


def test_kayitsiz_plaka_bulunamaz(session):
    with pytest.raises(NotFoundError):
        vehicles.find_vehicle_by_plate(session, "06AB123")
