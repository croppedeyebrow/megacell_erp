from collections.abc import Generator

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.domains.identity import service as auth_service
from app.domains.identity.models import User


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db_session),
) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    user = auth_service.get_user_by_session(db, token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHENTICATED", "message": "로그인이 필요합니다."},
        )
    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db_session),
) -> User | None:
    token = request.cookies.get(settings.session_cookie_name)
    return auth_service.get_user_by_session(db, token)
