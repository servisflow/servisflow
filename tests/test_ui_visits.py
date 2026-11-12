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
from servisflow.repository.models import ServiceTask, ServiceVisit, Vehicle
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
    return _choose(at, db_url[0], "34BJK321")


def _vehicle_id(url, plate):
    return _query(
        url,
        lambda s: s.query(Vehicle).filter_by(plate_normalized=plate).one().id,
    )


def _choose(at, url, plate):
    """Listeden plakayı seçer (tarayıcıda yazıp tıklamanın karşılığı)."""
    return at.selectbox(key="ziyaret_arac").set_value(_vehicle_id(url, plate)).run()


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
    assert page.subheader[0].value.startswith("34 BJK 321 · ")
    assert "Can GPT" in page.subheader[0].value


@pytest.fixture
def unselected(db_url):
    """Servis ve işler ekranı, henüz araç seçilmemiş."""

    def add(s):
        owner = customers.create_customer(s, SystemClock(), "Işıl Çağrı")
        for plate in ("06BUM00", "06BA1234"):
            vehicles.register_vehicle(s, owner.id, plate, "Ford", "Transit")

    _query(db_url[0], add)
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["user_id"] = db_url[1]
    at.run()
    at = at.sidebar.radio(key="menu").set_value("Servis ve işler").run()
    return at, db_url[0]


def test_kr09_secim_yapilana_kadar_arac_acilmaz(unselected):
    """Kullanıcı listeden seçene kadar araç bilgileri ve ziyaret formu gelmez."""
    at, _ = unselected
    assert at.selectbox(key="ziyaret_arac").value is None
    assert not at.subheader
    assert not [b for b in at.button if b.label == "Yeni servis ziyareti aç"]


def test_kr09_liste_bosluklu_plakayla_baslar_ve_sirali(unselected):
    """Tarayıcıdaki "prefix" süzgeci etiketin başına bakar: "06 b" → 06 BA, 06 BUM."""
    at, _ = unselected
    box = at.selectbox(key="ziyaret_arac")
    assert [o.split(" · ")[0] for o in box.options] == [
        "06 BA 1234",
        "06 BUM 00",
        "34 BJK 321",
    ]


def test_kr09_listeden_secilen_arac_acilir(unselected):
    at = _choose(*unselected, "06BUM00")
    assert at.subheader[0].value.startswith("06 BUM 00 · ")
    assert "Işıl Çağrı" in at.subheader[0].value


def test_ziyaret_acilir_tarih_sistemce(page, db_url):
    at = _open_visit(page, "Ön sol tekerden ses")
    assert not at.exception
    assert "Ziyaret açıldı" in at.success[0].value
    visits = _query(db_url[0], lambda s: s.query(ServiceVisit).all())
    assert len(visits) == 1
    assert "Ön sol tekerden ses" in [c.value for c in at.caption]


def test_is_eklenir_tutar_kurusa_dogru_cevrilir(page, db_url):
    """1600 TL → 160000 kuruş (TC-16, BR-01 v1.4)."""
    at = _add_task(_open_visit(page), "Ön sol teker", 1600, "Bilya, keçe")
    assert at.success[0].value == "İş eklendi."
    assert _tasks(db_url[0]) == [("Ön sol teker", 160000, "TODO")]
    text = " ".join(m.value for m in at.markdown)
    assert "Açık işler: **1.600 TL** · Tamamlanan: **0 TL**" in text


def test_tutar_alani_tam_tl_ve_bir_tl_adim(page):
    """KR-08: kuruş girilmez; alan tam sayı tutar ve 1 TL adımla artar."""
    at = _open_visit(page)
    box = [n for n in at.number_input if n.key.startswith("yeni_is_tutar_")][0]
    assert box.step == 1
    assert isinstance(box.value, int)


def test_sifir_tutar_reddedilir(page, db_url):
    at = _add_task(_open_visit(page), "Yağ", 0)
    assert "1 TL ile 1.000.000 TL" in at.error[0].value
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
    assert "Açık işler: **1.200 TL** · Tamamlanan: **1.600 TL**" in text
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
    at.number_input(key=f"is_tutar_{tid}").set_value(1350)
    at = _button(at, "Güncelle").click().run()
    assert at.success[0].value == "İş güncellendi."
    assert _tasks(db_url[0]) == [("Yağ + filtre", 135000, "TODO")]
    at = at.button(key=f"sil_{tid}").click().run()
    assert at.success[0].value == "İş silindi."
    assert _tasks(db_url[0]) == []


def test_tl_bicimi():
    assert (tl(160000), tl(100), tl(100_000_000), tl(160050)) == (
        "1.600 TL",
        "1 TL",
        "1.000.000 TL",
        "1.600,50 TL",
    )


def _tasks_ids(url):
    return _query(url, lambda s: [t.id for t in s.query(ServiceTask).order_by("id")])
