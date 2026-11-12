"""Giriş ekranı testleri (UC-01 arayüzü): TC-03, TC-22, TC-04 ve TC-32 sistem seviyesi.

Streamlit AppTest uygulamayı tarayıcısız çalıştırır; form doldurulup gönderilir.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import (
    DB_URL_ENV,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.repository.models import LoginAttempt
from servisflow.services import auth

APP = str(Path(__file__).parents[1] / "src" / "servisflow" / "ui" / "app.py")
PAROLA = "dogru-parola-123"


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'ui.db'}"
    monkeypatch.setenv(DB_URL_ENV, url)
    engine = make_engine(url)
    init_db(engine)
    with make_session_factory(engine).begin() as session:
        auth.create_owner(session, "sorumlu", PAROLA)
    yield url
    engine.dispose()


def _app():
    return AppTest.from_file(APP, default_timeout=30).run()


def _login(at, username="sorumlu", password=PAROLA, captcha=None):
    at.text_input[0].input(username)
    at.text_input[1].input(password)
    if captcha is not None:
        at.text_input[2].input(captcha)
    return at.button[0].click().run()


def _attempts(url):
    engine = make_engine(url)
    with make_session_factory(engine)() as s:
        rows = [a.success for a in s.query(LoginAttempt).order_by(LoginAttempt.id)]
    engine.dispose()
    return rows


def test_tc03_oturumsuz_yalnizca_giris_ekrani(db_url):
    at = _app()
    assert not at.exception
    assert [s.value for s in at.subheader] == ["Giriş"]
    assert len(at.text_input) == 2  # kullanıcı adı + parola, CAPTCHA yok
    assert "Giriş yapıldı" not in [i.value for i in at.info][:1]


def test_dogru_giris_ana_ekrana_gecer(db_url):
    at = _login(_app())
    assert not at.exception
    assert at.session_state["user_id"] is not None
    assert "Giriş yapıldı" in at.info[0].value


def test_yanlis_parola_genel_mesaj_ve_tek_kayit(db_url):
    """Hatalı deneme bir kez kaydedilir (çift sayım hatası için regresyon testi)."""
    at = _login(_app(), password="yanlis")
    assert at.error[0].value == auth.LOGIN_FAILED
    assert _attempts(db_url) == [False]


def test_tc04_uc_hatadan_sonra_captcha_alani_cikar(db_url):
    at = _app()
    for _ in range(2):
        at = _login(at, password="yanlis")
    assert len(at.text_input) == 2  # 2 hatadan sonra CAPTCHA yok
    at = _login(at, password="yanlis")
    assert len(at.text_input) == 3  # 3. hatadan sonra CAPTCHA alanı
    assert _attempts(db_url) == [False, False, False]

    question_answer = at.session_state["captcha"][1]
    at = _login(at, captcha=str(question_answer + 1))  # CAPTCHA yanlış
    assert at.error[0].value == auth.CAPTCHA_FAILED
    assert "user_id" not in at.session_state  # doğru parola da kabul edilmedi


def test_tc04_dogru_captcha_ile_giris_ve_tc32_listesi(db_url):
    at = _app()
    for _ in range(3):
        at = _login(at, password="yanlis")
    answer = at.session_state["captcha"][1]
    at = _login(at, captcha=str(answer))
    assert not at.exception
    assert "3 hatalı deneme" in at.warning[0].value  # TC-32


def test_tc22_cikis_sonrasi_giris_ekrani(db_url):
    at = _login(_app())
    at = at.sidebar.button[0].click().run()
    assert "user_id" not in at.session_state
    assert [s.value for s in at.subheader] == ["Giriş"]
    at = at.run()  # sayfayı yenileme / geri dönme
    assert [s.value for s in at.subheader] == ["Giriş"]
