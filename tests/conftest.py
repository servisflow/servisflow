"""Ortak test hazırlıkları: her test temiz bir bellek veritabanı ve sabit saat alır."""

from datetime import datetime

import pytest

from servisflow.repository.db import init_db, make_engine, make_session_factory
from servisflow.services.clock import ISTANBUL, FixedClock


@pytest.fixture
def session():
    engine = make_engine("sqlite://")
    init_db(engine)
    with make_session_factory(engine)() as s:
        yield s
    engine.dispose()


@pytest.fixture
def clock():
    return FixedClock(datetime(2026, 10, 22, 10, 0, tzinfo=ISTANBUL))
