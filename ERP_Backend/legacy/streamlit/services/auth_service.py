from __future__ import annotations

import pandas as pd
import streamlit as st

from core.security import PASSWORD_ITERATIONS, hash_password, verify_password
from repositories.user_repository import (
    DEPARTMENTS,
    ROLES,
    User as CurrentUser,
    get_user,
    get_user_auth_row,
    get_user_options,
    list_users as list_user_rows,
    touch_login,
    update_password,
    upsert_user as save_user,
)


def authenticate(email: str, password: str) -> tuple[CurrentUser | None, str | None]:
    clean_email = email.strip().lower()
    row = get_user_auth_row(clean_email)
    if row is None:
        return None, "등록되지 않은 이메일입니다. 관리자에게 사용자 등록을 요청해 주세요."
    if not bool(row["is_active"]):
        return None, "비활성 계정입니다. 관리자에게 문의해 주세요."
    if not verify_password(
        password,
        str(row["password_hash"] or ""),
        str(row["password_salt"] or ""),
        int(row["password_iterations"] or PASSWORD_ITERATIONS),
    ):
        return None, "이메일 또는 비밀번호가 올바르지 않습니다."
    touch_login(clean_email)
    return get_user(clean_email), None


def login(email: str, password: str) -> tuple[bool, str | None]:
    user, error = authenticate(email, password)
    if error or user is None:
        return False, error
    st.session_state["auth_user_email"] = user.email
    return True, None


def logout() -> None:
    for key in ["auth_user_email", "selected_department", "selected_page"]:
        st.session_state.pop(key, None)


def get_current_user() -> CurrentUser | None:
    email = st.session_state.get("auth_user_email", "")
    if not email:
        return None
    user = get_user(str(email))
    if user is None or not user.is_active:
        logout()
        return None
    return user


def change_password(email: str, new_password: str, must_change_password: bool = False) -> None:
    if len(new_password) < 8:
        raise ValueError("비밀번호는 8자 이상으로 입력해 주세요.")
    password_hash, password_salt, iterations = hash_password(new_password)
    update_password(email, password_hash, password_salt, iterations, must_change_password)


def list_users() -> pd.DataFrame:
    rows = list_user_rows()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["이메일", "이름", "부서", "역할", "문서생성", "활성", "비밀번호변경", "최근로그인", "수정일"]
        )
    df = df.rename(
        columns={
            "email": "이메일",
            "name": "이름",
            "department": "부서",
            "role": "역할",
            "can_create_documents": "문서생성",
            "is_active": "활성",
            "must_change_password": "비밀번호변경",
            "last_login_at": "최근로그인",
            "updated_at": "수정일",
        }
    )
    df["문서생성"] = df["문서생성"].map(lambda value: "가능" if int(value or 0) else "불가")
    df["활성"] = df["활성"].map(lambda value: "사용" if int(value or 0) else "비활성")
    df["비밀번호변경"] = df["비밀번호변경"].map(lambda value: "필요" if int(value or 0) else "")
    return df[["이메일", "이름", "부서", "역할", "문서생성", "활성", "비밀번호변경", "최근로그인", "수정일"]]


def upsert_user(
    *,
    email: str,
    name: str,
    department: str,
    role: str,
    can_create_documents: bool,
    is_active: bool,
    new_password: str = "",
    force_password_change: bool = False,
) -> None:
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise ValueError("올바른 이메일을 입력해 주세요.")
    if department and department not in DEPARTMENTS:
        raise ValueError("부서를 다시 선택해 주세요.")
    if role not in ROLES:
        raise ValueError("역할을 다시 선택해 주세요.")

    existing = get_user(clean_email)
    if existing is None and not new_password:
        raise ValueError("새 사용자는 초기 비밀번호를 입력해야 합니다.")

    save_user(
        email=clean_email,
        name=name,
        department=department,
        role=role,
        can_create_documents=can_create_documents,
        is_active=is_active,
    )
    if new_password:
        change_password(clean_email, new_password, must_change_password=force_password_change)
