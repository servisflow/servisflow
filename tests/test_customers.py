"""UC-02 testleri: müşteri kaydı, telefon normalizasyonu ve arama (TC-06 – TC-09)."""

import pytest

from servisflow.repository.models import Customer
from servisflow.services import customers
from servisflow.services.errors import NotFoundError, ValidationError


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0532 123 45 67", "5321234567"),  # TC-08
        ("(532) 123-4567", "5321234567"),  # TC-08
        ("5321234567", "5321234567"),
        (None, None),
        ("", None),
        ("   ", None),
    ],
)
def test_telefon_normalize_edilir(raw, expected):
    assert customers.normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "raw", ["212 123 4567", "53212", "05321234567 8", "+90 532 123 4567", "532abc4567"]
)
def test_gecersiz_telefon_reddedilir(raw):
    """TC-08: sabit hat ve eksik hane red; +90 BR-09'da tanımlı değil."""
    with pytest.raises(ValidationError):
        customers.normalize_phone(raw)


@pytest.mark.parametrize("length", [1, 100])
def test_tc07_ad_siniri_kabul(session, clock, length):
    assert len(customers.create_customer(session, clock, "x" * length).full_name) == (
        length
    )


@pytest.mark.parametrize("name", ["", "   ", "\t", "x" * 101])
def test_tc07_ad_siniri_red(session, clock, name):
    with pytest.raises(ValidationError):
        customers.create_customer(session, clock, name)
    assert session.query(Customer).count() == 0


def test_musteri_kaydedilir(session, clock):
    customer = customers.create_customer(
        session, clock, "  Can   GPT ", "0532 123 45 67"
    )
    assert customer.id is not None
    assert (customer.full_name, customer.phone) == ("Can GPT", "5321234567")
    assert customer.created_at == clock.now()


def test_ayni_adli_iki_musteri_ayri_kayit(session, clock):
    first = customers.create_customer(session, clock, "Can GPT")
    second = customers.create_customer(session, clock, "Can GPT")
    assert first.id != second.id


def test_musteri_guncellenir(session, clock):
    customer = customers.create_customer(session, clock, "Can GPT", "5321234567")
    updated = customers.update_customer(session, customer.id, "Can Claude", None)
    assert (updated.full_name, updated.phone) == ("Can Claude", None)


def test_gecersiz_guncelleme_kaydi_degistirmez(session, clock):
    customer = customers.create_customer(session, clock, "Can GPT", "5321234567")
    with pytest.raises(ValidationError):
        customers.update_customer(session, customer.id, "Can GPT", "212 123 4567")
    session.refresh(customer)
    assert customer.phone == "5321234567"


def test_olmayan_musteri_guncellenemez(session):
    with pytest.raises(NotFoundError):
        customers.update_customer(session, 999, "Can GPT", None)


@pytest.fixture
def kayitlar(session, clock):
    for name, phone in [
        ("Can GPT", "05321234567"),
        ("ŞÜKRÜ YILMAZ", None),
        ("Işıl Çağrı", "5449876543"),
        ("Ilgın İnce", None),
    ]:
        customers.create_customer(session, clock, name, phone)


def _names(result):
    return [c.full_name for c in result]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("can", ["Can GPT"]),  # TC-06
        ("şükrü", ["ŞÜKRÜ YILMAZ"]),  # TC-09
        ("yılmaz", ["ŞÜKRÜ YILMAZ"]),  # I → ı
        ("IŞIL", ["Işıl Çağrı"]),
        ("ince", ["Ilgın İnce"]),  # İ → i
        ("0544 987", ["Işıl Çağrı"]),  # telefonla
        ("123 45", ["Can GPT"]),
        ("yok", []),
    ],
)
def test_arama(session, kayitlar, text, expected):
    assert _names(customers.search_customers(session, text)) == expected


def test_bos_arama_hepsini_doner(session, kayitlar):
    assert len(customers.search_customers(session, "")) == 4
