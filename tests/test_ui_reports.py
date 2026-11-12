"""Rapor ekranı testleri (UC-07 arayüzü), Streamlit AppTest ile."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from servisflow.repository.db import (
    DB_URL_ENV,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.services import auth, completion, customers, tasks, vehicles, visits
from servisflow.services.clock import ISTANBUL, FixedClock

APP = str(Path(__file__).parents[1] / "src" / "servisflow" / "ui" / "app.py")


@pytest.fixture
def page(tmp_path, monkeypatch):
    """TC-25 verisi: 22 Ekim 1.600 TL, 23 Ekim 1.200 TL tamamlanır, bir iş açık."""
    url = f"sqlite:///{tmp_path / 'ui.db'}"
    monkeypatch.setenv(DB_URL_ENV, url)
    engine = make_engine(url)
    init_db(engine)
    clock = FixedClock(datetime(2026, 10, 22, 10, 0, tzinfo=ISTANBUL))
    with make_session_factory(engine).begin() as s:
        user_id = auth.create_owner(s, "sorumlu", "dogru-parola-123").id
        customer = customers.create_customer(s, clock, "Can GPT")
        vehicle = vehicles.register_vehicle(s, customer.id, "34BJK321", "Isuzu", "X")
        visit = visits.open_visit(s, clock, vehicle.id)
        teker = tasks.add_task(s, clock, visit.id, "Ön sol teker", Decimal("1600"))
        yag = tasks.add_task(s, clock, visit.id, "Yağ değişimi", Decimal("1200"))
        tasks.add_task(s, clock, visit.id, "Açık iş", Decimal("999"))
        completion.complete_task(s, clock, teker.id)
        clock.advance(datetime(2026, 10, 23, 9, 0, tzinfo=ISTANBUL) - clock.now())
        completion.complete_task(s, clock, yag.id)
    engine.dispose()
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["user_id"] = user_id
    at.run()
    return at.sidebar.radio(key="menu").set_value("Rapor").run()


def _show(at, kind, day):
    at.radio(key="donem").set_value(kind)
    return at.date_input(key="donem_gunu").set_value(day).run()


@pytest.mark.parametrize(
    "kind, day, total, rows",
    [
        ("gun", date(2026, 10, 22), "1.600 TL", 1),  # TC-25 günlük
        ("gun", date(2026, 10, 23), "1.200 TL", 1),
        ("hafta", date(2026, 10, 22), "2.800 TL", 2),  # TC-25 hafta
        ("ay", date(2026, 10, 1), "2.800 TL", 2),
        ("yil", date(2026, 1, 1), "2.800 TL", 2),
    ],
)
def test_donem_toplamlari(page, kind, day, total, rows):
    at = _show(page, kind, day)
    assert not at.exception
    assert at.metric[0].value == total
    assert len(at.dataframe[0].value) == rows


def test_bos_donem_sifir(page):
    """TC-27: boş dönem 0,00 TL; açık iş hiçbir dönemde sayılmaz."""
    at = _show(page, "gun", date(2026, 10, 24))
    assert at.metric[0].value == "0 TL"
    assert "tamamlanan iş yok" in at.caption[-1].value


def test_hafta_etiketi_son_gunu_gosterir(page):
    at = _show(page, "hafta", date(2026, 10, 22))
    assert "19.10.2026 – 25.10.2026" in at.metric[0].label
