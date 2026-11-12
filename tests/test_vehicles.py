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


# --- Plaka önerisi: KR-09 (Faz 3 incelemesi, Selim ve Kerem) ------------------


@pytest.fixture
def plakalar(session, customer):
    for plate in ["06BUM00", "06BA1234", "06AB123", "34BJK321"]:
        vehicles.register_vehicle(session, customer.id, plate, "Ford", "Transit")


def _plates(result):
    return [v.plate_normalized for v in result]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("06 b", ["06BA1234", "06BUM00"]),  # inceleme örneği
        ("06 bu", ["06BUM00"]),
        ("06bum00", ["06BUM00"]),  # tam plaka da bulunur
        ("06", ["06AB123", "06BA1234", "06BUM00"]),
        ("34 bjk", ["34BJK321"]),
        ("35", []),
    ],
)
def test_plaka_basindan_oneri(session, plakalar, text, expected):
    assert _plates(vehicles.suggest_plates(session, text)) == expected


@pytest.mark.parametrize("text", ["", "  ", "0", "%", "06_", "06 ş"])
def test_oneri_icin_gecersiz_veya_kisa_girdi_bos_doner(session, plakalar, text):
    """En az 2 karakter; % ve _ joker karakter gibi davranmaz; Türkçe harf eşleşmez."""
    assert vehicles.suggest_plates(session, text) == []


def test_oneri_sayisi_sinirli(session, customer):
    for n in range(15):
        vehicles.register_vehicle(session, customer.id, f"06AB{100 + n}", "F", "T")
    assert len(vehicles.suggest_plates(session, "06")) == vehicles.SUGGEST_LIMIT


# --- Plaka seçim listesi: arayüzde yazdıkça süzülen liste (KR-09 devamı) ------


@pytest.mark.parametrize(
    "plate, shown",
    [
        ("06BUM00", "06 BUM 00"),
        ("06BA1234", "06 BA 1234"),
        ("01A1234", "01 A 1234"),
        ("34BJK321", "34 BJK 321"),
    ],
)
def test_plaka_bosluklu_gosterilir(plate, shown):
    assert vehicles.format_plate(plate) == shown


def test_bicime_uymayan_plaka_oldugu_gibi_gosterilir():
    assert vehicles.format_plate("ESKI-KAYIT") == "ESKI-KAYIT"


def test_araclar_plakaya_gore_sirali(session, plakalar):
    assert _plates(vehicles.list_vehicles(session)) == [
        "06AB123",
        "06BA1234",
        "06BUM00",
        "34BJK321",
    ]
