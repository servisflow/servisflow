"""Devreye alma (Faz 4 - iv): bulut giriş noktası ve sırlardan hesap oluşturma.

Streamlit Community Cloud depoyu paket olarak kurmaz ve kabuk vermez. Kök
dizindeki `streamlit_app.py` çalışmalı; sorumlu hesabı sır ayarından gelmeli.
"""

import logging
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import (
    DB_URL_ENV,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.repository.models import User
from servisflow.services import auth
from servisflow.services.clock import SystemClock

ROOT = Path(__file__).parents[1]
CLOUD_ENTRY = str(ROOT / "streamlit_app.py")
APP = str(ROOT / "src" / "servisflow" / "ui" / "app.py")
PAROLA = "bulut-parola-123"


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'bulut.db'}"
    monkeypatch.setenv(DB_URL_ENV, url)
    return url


def _users(url):
    engine = make_engine(url)
    init_db(engine)
    with make_session_factory(engine)() as s:
        rows = [u.username for u in s.query(User)]
    engine.dispose()
    return rows


def _login_ok(url, username, password):
    engine = make_engine(url)
    with make_session_factory(engine).begin() as s:
        user = auth.authenticate(s, SystemClock(), username, password, False)
    engine.dispose()
    return user is not None


def _app(path, owner=None):
    at = AppTest.from_file(path, default_timeout=30)
    if owner is not None:
        at.secrets["owner"] = owner
    return at.run()


def test_bulut_giris_noktasi_giris_ekranini_acar(db_url):
    at = _app(CLOUD_ENTRY)
    assert not at.exception
    assert [b.label for b in at.button] == ["Giriş yap"]


def test_sirlardan_hesap_olusur_ve_giris_yapilir(db_url):
    at = _app(CLOUD_ENTRY, {"username": "sorumlu", "password": PAROLA})
    assert not at.exception
    assert _users(db_url) == ["sorumlu"]
    assert _login_ok(db_url, "sorumlu", PAROLA)
    at.run()  # her yeniden çizimde ikinci hesap açılmaz
    assert _users(db_url) == ["sorumlu"]


def test_sir_yoksa_hesap_olusmaz(db_url):
    """Yerel kurulum: hesap yine `create_owner` betiğiyle açılır."""
    at = _app(APP)
    assert not at.exception
    assert _users(db_url) == []


def test_gecersiz_sir_kullaniciya_gosterilmez_gunluge_yazilir(db_url, caplog):
    with caplog.at_level(logging.ERROR, logger="servisflow"):
        at = _app(APP, {"username": "sorumlu", "password": "kisa"})
    assert not at.exception and not at.error
    assert _users(db_url) == []
    assert any("Parola" in r.getMessage() for r in caplog.records)
    assert not any("kisa" in r.getMessage() for r in caplog.records)
