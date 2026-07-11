from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.core.config import settings
from app.domains.identity import service as auth_service
from app.domains.identity.models import User
from app.domains.identity.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from app.domains.identity.service import AuthError

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
        max_age=settings.session_ttl_hours * 3600,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        samesite="lax",
        secure=settings.environment != "local",
    )


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        department=user.department,
        role=user.role,
        permissions=list(user.permissions or []),
        is_active=user.is_active,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    body: RegisterRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db_session),
) -> UserResponse:
    try:
        user = auth_service.register_user(
            db,
            email=str(body.email),
            password=body.password,
            name=body.name,
            department=body.department,
        )
        user, token = auth_service.authenticate(
            db,
            email=str(body.email),
            password=body.password,
            user_agent=request.headers.get("user-agent"),
        )
    except AuthError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc

    _set_session_cookie(response, token)
    return _to_user_response(user)


@router.post("/login", response_model=UserResponse)
def login(
    body: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db_session),
) -> UserResponse:
    try:
        user, token = auth_service.authenticate(
            db,
            email=str(body.email),
            password=body.password,
            user_agent=request.headers.get("user-agent"),
        )
    except AuthError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc

    _set_session_cookie(response, token)
    return _to_user_response(user)


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db_session),
) -> MessageResponse:
    token = request.cookies.get(settings.session_cookie_name)
    auth_service.logout_session(db, token)
    _clear_session_cookie(response)
    return MessageResponse(message="로그아웃되었습니다.")


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return _to_user_response(user)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    try:
        auth_service.change_password(
            db,
            user=user,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    except AuthError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc

    # 비밀번호 변경 후 재로그인 유도
    token = request.cookies.get(settings.session_cookie_name)
    auth_service.logout_session(db, token)
    _clear_session_cookie(response)
    return MessageResponse(message="비밀번호가 변경되었습니다. 다시 로그인해 주세요.")
