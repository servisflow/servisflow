"""Veritabanı bağlantısı ve oturum fabrikası (ADR-002)."""

import os
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_URL_ENV = "SERVISFLOW_DB_URL"
# Proje kökü: src/servisflow/repository/db.py -> üç üst dizin
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Base(DeclarativeBase):
    pass


def default_url() -> str:
    """Ortam değişkeni verilmemişse proje kökündeki servisflow.db.

    Uygulamanın hangi dizinden başlatıldığından bağımsızdır (PR #10 incelemesi).
    """
    return os.environ.get(DB_URL_ENV) or f"sqlite:///{PROJECT_ROOT / 'servisflow.db'}"


def make_engine(url: str | None = None) -> Engine:
    engine = create_engine(url or default_url())

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record) -> None:
        # SQLite yabancı anahtarları varsayılan olarak denetlemez.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    from . import models  # noqa: F401  (tabloların metadata'ya kaydı için)

    Base.metadata.create_all(engine)
