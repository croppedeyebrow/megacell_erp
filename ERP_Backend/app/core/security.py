import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:
        return False


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def utcnow() -> datetime:
    return datetime.now(UTC)


def session_expiry() -> datetime:
    return utcnow() + timedelta(hours=settings.session_ttl_hours)
