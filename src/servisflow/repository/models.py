"""Veri modeli (Faz 1 Raporu 3.9, Faz 2 incelemesiyle güncel hali).

Kayıtlar silinmez (BR-08), bu yüzden ilişkilerde silme zinciri yoktur.
İş kuralları `services` katmanında doğrulanır; buradaki kısıtlar son savunma hattıdır.
"""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

TASK_TODO = "TODO"
TASK_DONE = "DONE"
MIN_AMOUNT_KURUS = 1  # 0,01 TL (BR-01)
MAX_AMOUNT_KURUS = 100_000_000  # 1.000.000,00 TL (BR-01)


class UTCDateTime(TypeDecorator):
    """SQLite saat dilimi tutmaz: UTC'ye çevirip yazar, okurken UTC olarak işaretler."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Saat dilimi bilgisi olmayan zaman kaydedilemez")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        return None if value is None else value.replace(tzinfo=timezone.utc)


class User(Base):
    """Sistemin tek kullanıcısı: işletme sorumlusu (RV-08)."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    failed_attempts: Mapped[int] = mapped_column(default=0)
    last_login_at: Mapped[datetime | None] = mapped_column(UTCDateTime)


class LoginAttempt(Base):
    """Giriş denemeleri; başarılı girişte son hatalı denemeler listelenir (RV-07)."""

    __tablename__ = "login_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    attempted_at: Mapped[datetime] = mapped_column(UTCDateTime)
    success: Mapped[bool]


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="customer")


class Vehicle(Base):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    plate_normalized: Mapped[str] = mapped_column(String(10), unique=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))

    customer: Mapped[Customer] = relationship(back_populates="vehicles")
    visits: Mapped[list["ServiceVisit"]] = relationship(back_populates="vehicle")


class ServiceVisit(Base):
    __tablename__ = "service_visit"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"))
    opened_at: Mapped[datetime] = mapped_column(UTCDateTime)
    complaint: Mapped[str | None] = mapped_column(String(500))

    vehicle: Mapped[Vehicle] = relationship(back_populates="visits")
    tasks: Mapped[list["ServiceTask"]] = relationship(back_populates="visit")


class ServiceTask(Base):
    __tablename__ = "service_task"
    __table_args__ = (
        CheckConstraint(
            f"amount_kurus BETWEEN {MIN_AMOUNT_KURUS} AND {MAX_AMOUNT_KURUS}",
            name="ck_task_amount_range",
        ),
        CheckConstraint(
            f"(status = '{TASK_DONE}' AND completed_at IS NOT NULL)"
            f" OR (status = '{TASK_TODO}' AND completed_at IS NULL)",
            name="ck_task_status_completed_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("service_visit.id"))
    title: Mapped[str] = mapped_column(String(100))
    note: Mapped[str | None] = mapped_column(String(500))
    amount_kurus: Mapped[int]
    status: Mapped[str] = mapped_column(String(4), default=TASK_TODO)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    visit: Mapped[ServiceVisit] = relationship(back_populates="tasks")
