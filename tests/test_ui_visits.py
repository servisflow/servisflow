"""Servis ve işler ekranı testleri (UC-04 – UC-06 arayüzü), Streamlit AppTest ile."""

from datetime import timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import (
    DB_URL_ENV,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.repository.models import ServiceTask, ServiceVisit
from servisflow.services import auth, customers, vehicles
from servisflow.services.clock import SystemClock
from servisflow.ui.common import tl

APP = str(Path(__file__).parents[1] / "src" / "servisflow" / "ui" / "app.py")


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'ui.db'}"
    monkeypatch.setenv(DB_URL_ENV, url)
    engine = make_engine(url)
    init_db(engine)
    with make_session_factory(engine).begin() as s:
        user_id = auth.create_owner(s, "sorumlu", "dogru-parola-123").id
        customer = customers.create_customer(s, SystemClock(), "Can GPT")
        vehicles.register_vehicle(s, customer.id, "34BJK321", "Isuzu", "10 Long")
    engine.dispose()
    return url, user_id


def _query(url, fn):
    engine = make_engine(url)
    with make_session_factory(engine).begin() as s:
        result = fn(s)
    engine.dispose()
    return result


def _tasks(url):
    return _query(
        url,
        lambda s: [
            (t.title, t.amount_kurus, t.status)
            for t in s.query(ServiceTask).order_by(ServiceTask.id)
        ],
    )


@pytest.fixture
def page(db_url):
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["user_id"] = db_url[1]
    at.run()
    at.sidebar.radio(key="menu").set_value("Servis ve işler").run()
    return at.text_input(key="ziyaret_plaka").input("34 bjk 321").run()


def _button(at, label):
    return [b for b in at.button if b.label == label][0]


def _open_visit(at, complaint=""):
    at.text_area(key="sikayet").input(complaint)
    return _button(at, "Yeni servis ziyareti aç").click().run()


def _add_task(at, title, amount, note=""):
    title_box = [t for t in at.text_input if t.key.startswith("yeni_is_baslik_")][0]
    vid = title_box.key.rsplit("_", 1)[1]
    title_box.input(title)
    at.number_input(key=f"yeni_is_tutar_{vid}").set_value(amount)
    at.text_input(key=f"yeni_is_not_{vid}").input(note)
    return _button(at, "İşi ekle").click().run()


def test_plaka_ile_arac_bulunur(page):
    assert not page.exception
    assert "34BJK321" in page.subheader[0].value
    assert "Can GPT" in page.subheader[0].value


def test_kayitsiz_plaka_mesaji(page):
    at = page.text_input(key="ziyaret_plaka").input("06AB123").run()
    assert "kayıtlı araç yok" in at.error[0].value


def test_ziyaret_acilir_tarih_sistemce(page, db_url):
    at = _open_visit(page, "Ön sol tekerden ses")
    assert not at.exception
    assert "Ziyaret açıldı" in at.success[0].value
    visits = _query(db_url[0], lambda s: s.query(ServiceVisit).all())
    assert len(visits) == 1
    assert "Ön sol tekerden ses" in [c.value for c in at.caption]


def test_is_eklenir_tutar_kurusa_dogru_cevrilir(page, db_url):
    """1600,50 TL → 160050 kuruş; float → Decimal(str(x)) dönüşümü (TC-16)."""
    at = _add_task(_open_visit(page), "Ön sol teker", 1600.50, "Bilya, keçe")
    assert at.success[0].value == "İş eklendi."
    assert _tasks(db_url[0]) == [("Ön sol teker", 160050, "TODO")]
    text = " ".join(m.value for m in at.markdown)
    assert "Açık işler: **1.600,50 TL** · Tamamlanan: **0,00 TL**" in text


def test_float_tuzagi_1_15(page, db_url):
    """1.15 float olarak 1.1499... saklanır; arayüz yine 115 kuruş kaydetmeli."""
    _add_task(_open_visit(page), "Vida", 1.15)
    assert _tasks(db_url[0]) == [("Vida", 115, "TODO")]


def test_sifir_tutar_reddedilir(page, db_url):
    at = _add_task(_open_visit(page), "Yağ", 0.0)
    assert "0,01 TL" in at.error[0].value
    assert _tasks(db_url[0]) == []


def test_tik_tamamlar_ve_toplamlari_gunceller(page, db_url):
    at = _add_task(_open_visit(page), "Ön sol teker", 1600.0)
    at = _add_task(at, "Yağ değişimi", 1200.0)
    tid = _tasks_ids(db_url[0])[0]
    at = at.button(key=f"tik_{tid}").click().run()
    assert at.success[0].value == "İş tamamlandı."
    statuses = [s for *_, s in _tasks(db_url[0])]
    assert statuses == ["DONE", "TODO"]
    text = " ".join(m.value for m in at.markdown)
    assert "Açık işler: **1.200,00 TL** · Tamamlanan: **1.600,00 TL**" in text
    # Tamamlanan iş için ✓ ve düzenleme yok, yalnızca geri al var (BR-02)
    assert not [b for b in at.button if b.key == f"tik_{tid}"]
    assert not [b for b in at.button if b.key == f"sil_{tid}"]


def test_geri_al_ayni_gun(page, db_url):
    at = _add_task(_open_visit(page), "Ön sol teker", 1600.0)
    tid = _tasks_ids(db_url[0])[0]
    at = at.button(key=f"tik_{tid}").click().run()
    at = at.button(key=f"geri_{tid}").click().run()
    assert at.success[0].value == "✓ geri alındı."
    assert [s for *_, s in _tasks(db_url[0])] == ["TODO"]


def test_dunku_isin_geri_alinmasi_reddedilir(page, db_url):
    """TC-20 arayüzde: tamamlanma zamanı dün olan iş için hata mesajı."""
    at = _add_task(_open_visit(page), "Ön sol teker", 1600.0)
    tid = _tasks_ids(db_url[0])[0]
    at = at.button(key=f"tik_{tid}").click().run()

    def yesterday(s):
        task = s.get(ServiceTask, tid)
        task.completed_at = task.completed_at - timedelta(days=1)

    _query(db_url[0], yesterday)
    at = at.button(key=f"geri_{tid}").click().run()
    assert at.error[0].value == "Geçmiş günün işi geri alınamaz."
    assert [s for *_, s in _tasks(db_url[0])] == ["DONE"]


def test_todo_is_duzenlenir_ve_silinir(page, db_url):
    at = _add_task(_open_visit(page), "Yağ", 1200.0)
    tid = _tasks_ids(db_url[0])[0]
    at.text_input(key=f"is_baslik_{tid}").input("Yağ + filtre")
    at.number_input(key=f"is_tutar_{tid}").set_value(1350.5)
    at = _button(at, "Güncelle").click().run()
    assert at.success[0].value == "İş güncellendi."
    assert _tasks(db_url[0]) == [("Yağ + filtre", 135050, "TODO")]
    at = at.button(key=f"sil_{tid}").click().run()
    assert at.success[0].value == "İş silindi."
    assert _tasks(db_url[0]) == []


def test_tl_bicimi():
    assert (tl(160050), tl(1), tl(100_000_000)) == (
        "1.600,50 TL",
        "0,01 TL",
        "1.000.000,00 TL",
    )


def _tasks_ids(url):
    return _query(url, lambda s: [t.id for t in s.query(ServiceTask).order_by("id")])
