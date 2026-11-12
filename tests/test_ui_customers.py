"""Müşteri ve araç ekranı testleri (UC-02, UC-03 arayüzü), Streamlit AppTest ile."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import (
    DB_URL_ENV,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.repository.models import Customer, Vehicle
from servisflow.services import auth

APP = str(Path(__file__).parents[1] / "src" / "servisflow" / "ui" / "app.py")


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'ui.db'}"
    monkeypatch.setenv(DB_URL_ENV, url)
    engine = make_engine(url)
    init_db(engine)
    with make_session_factory(engine).begin() as session:
        user = auth.create_owner(session, "sorumlu", "dogru-parola-123")
        user_id = user.id
    engine.dispose()
    return url, user_id


def _rows(url, model):
    engine = make_engine(url)
    with make_session_factory(engine)() as s:
        rows = s.query(model).all()
        data = [
            (r.full_name, r.phone) if model is Customer else r.plate_normalized
            for r in rows
        ]
    engine.dispose()
    return data


@pytest.fixture
def page(db_url):
    """Giriş yapılmış kullanıcıyla müşteri ekranı."""
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["user_id"] = db_url[1]
    at.run()
    at.sidebar.radio(key="menu").set_value("Müşteriler ve araçlar").run()
    return at


def _new_customer(at, name, phone=""):
    at.text_input(key="yeni_ad").input(name)
    at.text_input(key="yeni_tel").input(phone)
    return at.button[0].click().run()  # "Kaydet" ilk form düğmesi


def test_oturumsuz_musteri_ekrani_acilmaz(db_url):
    """TC-03: oturum yoksa menü ve müşteri ekranı çizilmez."""
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.sidebar.radio
    assert "Müşteriler ve araçlar" not in [h.value for h in at.header]


def test_musteri_eklenir_ve_listelenir(page, db_url):
    at = _new_customer(page, "Can GPT", "0532 123 45 67")
    assert not at.exception
    assert at.success[0].value == "Müşteri kaydedildi."
    assert _rows(db_url[0], Customer) == [("Can GPT", "5321234567")]
    assert at.selectbox(key="musteri_sec").options == ["Can GPT (5321234567)"]


def test_gecersiz_telefon_alan_mesaji_ve_kayit_yok(page, db_url):
    at = _new_customer(page, "Can GPT", "212 123 4567")
    assert "5 ile başlayan" in at.error[0].value
    assert _rows(db_url[0], Customer) == []


def test_turkce_harfle_arama(page):
    at = _new_customer(page, "ŞÜKRÜ YILMAZ")
    at = _new_customer(at, "Can GPT")
    at = at.text_input(key="musteri_ara").input("şükrü").run()
    assert at.selectbox(key="musteri_sec").options == ["ŞÜKRÜ YILMAZ (-)"]


def _add_vehicle(at, plate, brand="Isuzu", model="10 Long"):
    at.text_input(key="arac_plaka").input(plate)
    at.text_input(key="arac_marka").input(brand)
    at.text_input(key="arac_model").input(model)
    return [b for b in at.button if b.label == "Aracı kaydet"][0].click().run()


def test_arac_eklenir_plaka_normalize(page, db_url):
    at = _new_customer(page, "Can GPT")
    at = _add_vehicle(at, "34 bjk 321")
    assert at.success[0].value == "Araç kaydedildi."
    assert _rows(db_url[0], Vehicle) == ["34BJK321"]


def test_ayni_plaka_ikinci_kez_reddedilir(page, db_url):
    """TC-10 arayüzde: farklı yazımla aynı plaka çakışma mesajı verir."""
    at = _new_customer(page, "Can GPT")
    at = _add_vehicle(at, "34BJK321")
    at = _add_vehicle(at, "34 bjk 321", "Ford", "Transit")
    assert "zaten kayıtlı" in at.error[0].value
    assert _rows(db_url[0], Vehicle) == ["34BJK321"]


def test_plakayla_arama_sahibini_gosterir(page):
    at = _new_customer(page, "Can GPT")
    at = _add_vehicle(at, "34BJK321")
    at = at.text_input(key="plaka_ara").input("34 bjk 321").run()
    assert "Can GPT" in at.info[0].value


def test_musteri_guncellenir(page, db_url):
    at = _new_customer(page, "Can GPT")
    at.text_input(key="duz_ad").input("Can Claude")
    at = [b for b in at.button if b.label == "Güncelle"][0].click().run()
    assert at.success[0].value == "Müşteri güncellendi."
    assert _rows(db_url[0], Customer) == [("Can Claude", None)]
