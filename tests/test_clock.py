"""Saat sağlayıcısı testleri (RV-10, ADR-004)."""

from datetime import datetime, timedelta, timezone

import pytest

from servisflow.services.clock import ISTANBUL, FixedClock, SystemClock


def test_sistem_saati_utc_ve_saat_dilimli():
    now = SystemClock().now()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


def test_sabit_saat_istanbul_zamanini_utcye_cevirir():
    clock = FixedClock(datetime(2026, 10, 22, 23, 59, 59, tzinfo=ISTANBUL))
    assert clock.now() == datetime(2026, 10, 22, 20, 59, 59, tzinfo=timezone.utc)


def test_sabit_saat_ilerletilebilir():
    clock = FixedClock(datetime(2026, 10, 22, 23, 59, 59, tzinfo=ISTANBUL))
    clock.advance(timedelta(seconds=1))
    assert clock.now().astimezone(ISTANBUL) == datetime(
        2026, 10, 23, 0, 0, 0, tzinfo=ISTANBUL
    )


def test_sabit_saat_saat_dilimsiz_zamani_reddeder():
    with pytest.raises(ValueError):
        FixedClock(datetime(2026, 10, 22, 10, 0))
