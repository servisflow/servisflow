"""Zaman sağlayıcısı (RV-10, ADR-004).

Servisler saati doğrudan sistemden okumaz; dışarıdan bir `Clock` alır.
Böylece testlerde zaman sabitlenebilir (ör. TC-26 gece yarısı sınırı).
"""

from datetime import datetime, timedelta, timezone
from typing import Protocol
from zoneinfo import ZoneInfo

ISTANBUL = ZoneInfo("Europe/Istanbul")


class Clock(Protocol):
    def now(self) -> datetime:
        """Şu anki zamanı UTC ve saat dilimi bilgisiyle döndürür."""


class SystemClock:
    """Uygulamada kullanılan gerçek saat."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock:
    """Testler için sabitlenmiş, elle ilerletilebilen saat."""

    def __init__(self, at: datetime) -> None:
        if at.tzinfo is None:
            raise ValueError("FixedClock saat dilimi bilgisi olan bir zaman ister")
        self._at = at.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._at

    def advance(self, delta: timedelta) -> None:
        self._at += delta
