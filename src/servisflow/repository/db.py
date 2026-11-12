"""Veritabanı bağlantısı ve oturum fabrikası (ADR-002)."""

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_URL = "sqlite:///servisflow.db"


class Base(DeclarativeBase):
    pass


def make_engine(url: str = DEFAULT_URL) -> Engine:
    engine = create_engine(url)

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
