"""UC-01: Kimlik doğrulama ve güvenli oturum yönetimi (FR-01, ADR-006).

Kurallar:
- Parolalar Argon2id ile özetlenir (`argon2-cffi` varsayılanı Argon2id'dir).
- Yanlış parola ve olmayan kullanıcı adı aynı mesajı alır (TC-01, TC-05).
- Hatalı deneme sayısı yalnızca `LoginAttempt` tablosundan, kullanıcı adına göre
  hesaplanır; var olan ve olmayan adlar aynı sayılır (KR-03, R-02).
- Son başarılı girişten bu yana 3 hatalı denemeden sonra CAPTCHA istenir (TC-04).
- CAPTCHA basit bir toplama sorusudur ve uygulamanın kendisinde üretilir.
"""

import secrets
from datetime import datetime
from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from servisflow.repository.models import LoginAttempt, User
from servisflow.services.clock import Clock
from servisflow.services.errors import (
    AuthenticationError,
    ConflictError,
    ValidationError,
)

CAPTCHA_AFTER = 3
USERNAME_MAX = 50
PASSWORD_MIN = 8  # NIST SP 800-63B
PASSWORD_MAX = 128  # Çok uzun parolayla özetleme maliyetini şişirmeyi önler
LOGIN_FAILED = "Kullanıcı adı veya parola hatalı."
CAPTCHA_FAILED = "Robot doğrulaması hatalı."

_hasher = PasswordHasher()


@cache
def _dummy_hash() -> str:
    """Olmayan kullanıcıda da aynı süre harcansın diye karşılaştırılacak özet."""
    return _hasher.hash(secrets.token_urlsafe(16))


def _clean_username(username: str | None) -> str:
    # Saldırganın gönderdiği çok uzun ad tabloyu şişirmesin diye kırpılır (R-11).
    return (username or "").strip()[:USERNAME_MAX]


def create_owner(session: Session, username: str, password: str) -> User:
    """İşletme sorumlusu hesabını oluşturur; sistemde tek hesap olur (RV-08)."""
    name = (username or "").strip()
    if not 1 <= len(name) <= USERNAME_MAX:
        raise ValidationError(f"Kullanıcı adı 1–{USERNAME_MAX} karakter olmalıdır.")
    if not PASSWORD_MIN <= len(password or "") <= PASSWORD_MAX:
        raise ValidationError(
            f"Parola {PASSWORD_MIN}–{PASSWORD_MAX} karakter olmalıdır."
        )
    if session.scalar(select(func.count()).select_from(User)):
        raise ConflictError("İşletme sorumlusu hesabı zaten var.")
    user = User(username=name, password_hash=_hasher.hash(password))
    session.add(user)
    session.flush()
    return user


def ensure_owner(session: Session, username: str, password: str) -> bool:
    """Hiç hesap yoksa sorumlu hesabını oluşturur; varsa dokunmaz (Faz 4 - iv).

    Bulut kurulumunda kabuk yoktur, `create_owner` betiği çalıştırılamaz.
    Var olan hesap ezilmez: sırlardaki parola değişse bile mevcut parola geçerli
    kalır. Hesap oluşturulduysa True döner.
    """
    if session.scalar(select(func.count()).select_from(User)):
        return False
    create_owner(session, username, password)
    return True


def _last_success_id(session: Session, username: str) -> int:
    last = session.scalar(
        select(func.max(LoginAttempt.id)).where(
            LoginAttempt.username == username, LoginAttempt.success.is_(True)
        )
    )
    return last or 0


def captcha_required(session: Session, username: str) -> bool:
    """Son başarılı girişten bu yana bu ad için en az 3 hatalı deneme var mı?"""
    name = _clean_username(username)
    failures = session.scalar(
        select(func.count()).where(
            LoginAttempt.username == name,
            LoginAttempt.success.is_(False),
            LoginAttempt.id > _last_success_id(session, name),
        )
    )
    return failures >= CAPTCHA_AFTER


def _password_ok(user: User | None, password: str) -> bool:
    try:
        _hasher.verify(user.password_hash if user else _dummy_hash(), password or "")
    except (VerificationError, InvalidHashError):
        return False
    return user is not None


def authenticate(
    session: Session,
    clock: Clock,
    username: str,
    password: str,
    captcha_passed: bool,
) -> User:
    """Girişi doğrular ve her denemeyi kaydeder.

    CAPTCHA gerekiyorsa ve geçilmediyse doğru parola da kabul edilmez (TC-04).
    """
    name = _clean_username(username)
    now = clock.now()
    if captcha_required(session, name) and not captcha_passed:
        session.add(LoginAttempt(username=name, attempted_at=now, success=False))
        session.flush()
        raise AuthenticationError(CAPTCHA_FAILED)
    user = session.scalar(select(User).where(User.username == name))
    ok = _password_ok(user, password)
    session.add(LoginAttempt(username=name, attempted_at=now, success=ok))
    if not ok:
        session.flush()
        raise AuthenticationError(LOGIN_FAILED)
    if _hasher.check_needs_rehash(user.password_hash):
        user.password_hash = _hasher.hash(password)
    user.last_login_at = now
    session.flush()
    return user


def failed_attempts_since_last_login(session: Session, username: str) -> list[datetime]:
    """Bu girişten önceki başarılı girişten beri yapılan hatalı denemeler (TC-32).

    `authenticate` başarılı döndükten sonra çağrılır.
    """
    name = _clean_username(username)
    successes = session.scalars(
        select(LoginAttempt.id)
        .where(LoginAttempt.username == name, LoginAttempt.success.is_(True))
        .order_by(LoginAttempt.id.desc())
        .limit(2)
    ).all()
    if not successes:
        return []
    previous = successes[1] if len(successes) == 2 else 0
    return list(
        session.scalars(
            select(LoginAttempt.attempted_at)
            .where(
                LoginAttempt.username == name,
                LoginAttempt.success.is_(False),
                LoginAttempt.id > previous,
                LoginAttempt.id < successes[0],
            )
            .order_by(LoginAttempt.id)
        )
    )


def new_captcha() -> tuple[str, int]:
    """Sunucuda üretilen toplama sorusu ve cevabı (ADR-006 açık konusu)."""
    a, b = 2 + secrets.randbelow(18), 2 + secrets.randbelow(18)
    return f"{a} + {b} kaç eder?", a + b


def check_captcha(expected: int, given: str | None) -> bool:
    try:
        return int((given or "").strip()) == expected
    except ValueError:
        return False
