from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.permissions import permissions_for_role
from app.core.security import (
    generate_session_token,
    hash_password,
    needs_rehash,
    session_expiry,
    utcnow,
    verify_password,
)
from app.domains.identity.models import SessionToken, User


class AuthError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    name: str,
    department: str,
) -> User:
    if len(password) < settings.password_min_length:
        raise AuthError(
            "WEAK_PASSWORD",
            f"비밀번호는 {settings.password_min_length}자 이상이어야 합니다.",
        )

    normalized = _normalize_email(email)
    existing = db.scalar(select(User).where(User.email == normalized))
    if existing:
        raise AuthError("EMAIL_TAKEN", "이미 등록된 이메일입니다.", status_code=409)

    user_count = db.scalar(select(func.count()).select_from(User)) or 0
    role = "admin" if user_count == 0 else "staff"

    user = User(
        email=normalized,
        name=name.strip(),
        department=(department or "").strip(),
        role=role,
        password_hash=hash_password(password),
        permissions=permissions_for_role(role),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(
    db: Session,
    *,
    email: str,
    password: str,
    user_agent: str | None,
) -> tuple[User, str]:
    normalized = _normalize_email(email)
    user = db.scalar(select(User).where(User.email == normalized))
    if not user:
        raise AuthError("INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.", 401)

    now = utcnow()
    if user.locked_until and _as_utc(user.locked_until) > now:
        raise AuthError(
            "ACCOUNT_LOCKED",
            "로그인 시도가 많아 잠시 잠겼습니다. 잠시 후 다시 시도하세요.",
            423,
        )

    if not user.is_active:
        raise AuthError("ACCOUNT_INACTIVE", "비활성화된 계정입니다. 관리자에게 문의하세요.", 403)

    if not verify_password(user.password_hash, password):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.login_max_attempts:
            user.locked_until = now + timedelta(minutes=settings.login_lock_minutes)
            user.failed_login_count = 0
        db.commit()
        raise AuthError("INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.", 401)

    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)

    user.failed_login_count = 0
    user.locked_until = None

    raw_token = generate_session_token()
    session = SessionToken(
        user_id=user.id,
        token_hash=_token_hash(raw_token),
        expires_at=session_expiry(),
        user_agent=(user_agent or "")[:512] or None,
    )
    db.add(session)
    db.commit()
    db.refresh(user)
    return user, raw_token


def get_user_by_session(db: Session, raw_token: str | None) -> User | None:
    if not raw_token:
        return None
    session = db.scalar(
        select(SessionToken).where(SessionToken.token_hash == _token_hash(raw_token))
    )
    if not session or session.revoked_at is not None:
        return None
    if _as_utc(session.expires_at) <= utcnow():
        return None
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        return None
    return user


def logout_session(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    session = db.scalar(
        select(SessionToken).where(SessionToken.token_hash == _token_hash(raw_token))
    )
    if session and session.revoked_at is None:
        session.revoked_at = utcnow()
        db.commit()


def change_password(
    db: Session,
    *,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    if len(new_password) < settings.password_min_length:
        raise AuthError(
            "WEAK_PASSWORD",
            f"새 비밀번호는 {settings.password_min_length}자 이상이어야 합니다.",
        )
    if not verify_password(user.password_hash, current_password):
        raise AuthError("INVALID_PASSWORD", "현재 비밀번호가 올바르지 않습니다.", 400)

    user.password_hash = hash_password(new_password)
    # 다른 세션 무효화는 선택 — 보안 변경 시 현재 제외 전부 폐기
    now = utcnow()
    for session in user.sessions:
        if session.revoked_at is None:
            session.revoked_at = now
    db.commit()
