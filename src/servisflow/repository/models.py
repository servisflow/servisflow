"""Veri modeli (Faz 1 Raporu 3.9, Faz 2 incelemesiyle güncel hali).

Kayıtlar silinmez (BR-08), bu yüzden ilişkilerde silme zinciri yoktur.
İş kuralları `services` katmanında doğrulanır; buradaki kısıtlar son savunma hattıdır.
SQLite sütun türünü ve `String(n)` uzunluğunu dayatmaz; bu yüzden tür ve uzunluk
sınırları açık CHECK kısıtlarıyla yazılmıştır (ADR-002, PR #10 incelemesi).
"""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

TASK_TODO = "TODO"
TASK_DONE = "DONE"
MIN_AMOUNT_KURUS = 100  # 1 TL (BR-01 v1.4: yalnızca tam TL, KR-08)
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
    last_login_at: Mapped[datetime | None] = mapped_column(UTCDateTime)


class LoginAttempt(Base):
    """Giriş denemeleri; başarılı girişte son hatalı denemeler listelenir (RV-07).

    Hatalı deneme sayısı yalnızca buradan, kullanıcı adına göre hesaplanır; var olan
    ve olmayan kullanıcı adları aynı şekilde sayılır, böylece CAPTCHA'nın çıkması
    kullanıcı adının var olup olmadığını sızdırmaz (R-02, ADR-006).
    """

    __tablename__ = "login_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    attempted_at: Mapped[datetime] = mapped_column(UTCDateTime)
    success: Mapped[bool]


class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = (
        CheckConstraint(
            "length(trim(full_name)) BETWEEN 1 AND 100", name="ck_customer_name"
        ),
        CheckConstraint(
            "phone IS NULL OR (length(phone) = 10 AND phone NOT GLOB '*[^0-9]*')",
            name="ck_customer_phone",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="customer")


class Vehicle(Base):
    __tablename__ = "vehicle"
    __table_args__ = (
        CheckConstraint(
            "length(plate_normalized) BETWEEN 5 AND 9", name="ck_vehicle_plate"
        ),
        CheckConstraint(
            "length(brand) <= 50 AND length(model) <= 50", name="ck_vehicle_text"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    plate_normalized: Mapped[str] = mapped_column(String(10), unique=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))

    customer: Mapped[Customer] = relationship(back_populates="vehicles")
    visits: Mapped[list["ServiceVisit"]] = relationship(back_populates="vehicle")


class ServiceVisit(Base):
    __tablename__ = "service_visit"
    __table_args__ = (
        CheckConstraint(
            "complaint IS NULL OR length(complaint) <= 500", name="ck_visit_complaint"
        ),
    )

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
            f"typeof(amount_kurus) = 'integer'"
            f" AND amount_kurus BETWEEN {MIN_AMOUNT_KURUS} AND {MAX_AMOUNT_KURUS}"
            " AND amount_kurus % 100 = 0",
            name="ck_task_amount_range",
        ),
        CheckConstraint("length(trim(title)) BETWEEN 1 AND 100", name="ck_task_title"),
        CheckConstraint("note IS NULL OR length(note) <= 500", name="ck_task_note"),
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
