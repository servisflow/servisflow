"""TC-30 (NFR-08, R-08): veritabanına erişilemezken genel hata mesajı.

Veritabanı adresi var olmayan bir klasörü gösterir; SQLite dosyayı açamaz
(bağlantı kesilmiş gibi). Kullanıcı yalnızca genel mesajı görmeli: yığın izi,
dosya yolu ve SQL ayrıntısı tarayıcıya gitmemeli (ADR-007).
"""

import logging
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import DB_URL_ENV
from servisflow.ui.common import DB_ERROR_MESSAGE

APP = str(Path(__file__).parents[1] / "src" / "servisflow" / "ui" / "app.py")


@pytest.fixture
def broken_db(tmp_path, monkeypatch):
    missing = tmp_path / "olmayan-klasor" / "servisflow.db"
    monkeypatch.setenv(DB_URL_ENV, f"sqlite:///{missing}")
    return missing


def _page_text(at) -> str:
    parts = [e.value for e in at.error] + [m.value for m in at.markdown]
    return " ".join(str(p) for p in parts)


def _assert_generic_only(at, missing: Path):
    assert not at.exception  # Streamlit'in hata kutusu (yığın izi) yok
    assert [e.value for e in at.error] == [DB_ERROR_MESSAGE]
    text = _page_text(at)
    for leak in ("Traceback", "sqlite3", "OperationalError", str(missing.parent)):
        assert leak not in text


def test_tc30_giris_ekrani_veritabani_yokken_genel_mesaj(broken_db, caplog):
    with caplog.at_level(logging.ERROR, logger="servisflow"):
        at = AppTest.from_file(APP, default_timeout=30)
        at.session_state["last_username"] = "sorumlu"  # CAPTCHA kontrolü DB'ye gider
        at.run()
    _assert_generic_only(at, broken_db)
    # Ayrıntı yalnızca sunucu günlüğüne yazılır (ADR-007).
    assert any("OperationalError" in r.exc_text for r in caplog.records if r.exc_text)


def test_tc30_oturum_acikken_islem_sirasinda_genel_mesaj(broken_db):
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["user_id"] = 1
    at.run()
    at = at.sidebar.radio(key="menu").set_value("Müşteriler ve araçlar").run()
    _assert_generic_only(at, broken_db)
