from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from config import ADMIN_EMAILS, DB_PATH


DEPARTMENTS = ["경영지원팀", "기술영업팀", "생산팀", "연구소"]
ROLES = ["관리자", "부서관리자", "일반사용자"]


@dataclass(frozen=True)
class CurrentUser:
    email: str
    name: str
    department: str
    role: str
    can_create_documents: bool
    is_active: bool

    @property
    def is_admin(self) -> bool:
        return self.role == "관리자"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_users_table() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL DEFAULT '',
                department TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT '일반사용자',
                can_create_documents INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )
        for email in sorted(ADMIN_EMAILS):
            conn.execute(
                """
                INSERT INTO users (
                    email, name, department, role, can_create_documents,
                    is_active, created_at, updated_at
                )
                VALUES (?, ?, ?, '관리자', 1, 1, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    role='관리자',
                    can_create_documents=1,
                    is_active=1,
                    updated_at=excluded.updated_at
                """,
                (email, email.split("@")[0], "경영지원팀", now_text(), now_text()),
            )
        conn.commit()


def get_login_email() -> str:
    """Read the authenticated email forwarded by Cloudflare Access.

    Local development usually has no Cloudflare headers, so we fall back to
    MEGACELL_DEV_EMAIL or the first configured admin email.
    """
    headers: dict[str, Any] = {}
    try:
        headers = dict(st.context.headers)
    except Exception:
        headers = {}

    normalized_headers = {str(key).lower(): str(value).strip() for key, value in headers.items()}
    for key in [
        "cf-access-authenticated-user-email",
        "x-forwarded-email",
        "x-authenticated-user-email",
    ]:
        value = normalized_headers.get(key, "")
        if value:
            return value.lower()

    host = normalized_headers.get("host", "")
    is_localhost = host.startswith("localhost") or host.startswith("127.0.0.1")
    dev_email = os.getenv("MEGACELL_DEV_EMAIL", "").strip().lower()
    if is_localhost and dev_email:
        return dev_email
    if is_localhost and os.getenv("MEGACELL_LOCAL_ADMIN_FALLBACK", "1") == "1" and ADMIN_EMAILS:
        return sorted(ADMIN_EMAILS)[0]
    return ""


def row_to_user(row: sqlite3.Row) -> CurrentUser:
    return CurrentUser(
        email=str(row["email"]).lower(),
        name=str(row["name"] or ""),
        department=str(row["department"] or ""),
        role=str(row["role"] or "일반사용자"),
        can_create_documents=bool(row["can_create_documents"]),
        is_active=bool(row["is_active"]),
    )


def get_user(email: str) -> CurrentUser | None:
    if not email:
        return None
    ensure_users_table()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
    return row_to_user(row) if row else None


def register_pending_user(email: str) -> CurrentUser:
    ensure_users_table()
    timestamp = now_text()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                email, name, department, role, can_create_documents,
                is_active, created_at, updated_at, last_login_at
            )
            VALUES (?, ?, '', '일반사용자', 0, 0, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                last_login_at=excluded.last_login_at
            """,
            (email.lower(), email.split("@")[0], timestamp, timestamp, timestamp),
        )
        conn.commit()
    return get_user(email)  # type: ignore[return-value]


def touch_login(email: str) -> None:
    if not email:
        return
    ensure_users_table()
    with connect() as conn:
        conn.execute(
            "UPDATE users SET last_login_at=?, updated_at=? WHERE lower(email)=lower(?)",
            (now_text(), now_text(), email),
        )
        conn.commit()


def get_current_user() -> CurrentUser | None:
    email = get_login_email()
    if not email:
        return None
    user = get_user(email)
    if user is None:
        user = register_pending_user(email)
    elif user.is_active:
        touch_login(email)
    return user


def list_users() -> pd.DataFrame:
    ensure_users_table()
    with connect() as conn:
        df = pd.read_sql(
            """
            SELECT
                email AS 이메일,
                name AS 이름,
                department AS 부서,
                role AS 역할,
                can_create_documents AS 문서생성,
                is_active AS 활성,
                last_login_at AS 최근로그인,
                updated_at AS 수정일
            FROM users
            ORDER BY is_active DESC, role ASC, department ASC, email ASC
            """,
            conn,
        )
    if not df.empty:
        df["문서생성"] = df["문서생성"].map(lambda value: "가능" if int(value or 0) else "불가")
        df["활성"] = df["활성"].map(lambda value: "사용" if int(value or 0) else "승인대기/비활성")
    return df


def upsert_user(
    *,
    email: str,
    name: str,
    department: str,
    role: str,
    can_create_documents: bool,
    is_active: bool,
) -> None:
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise ValueError("올바른 이메일을 입력해 주세요.")
    if department and department not in DEPARTMENTS:
        raise ValueError("부서를 다시 선택해 주세요.")
    if role not in ROLES:
        raise ValueError("역할을 다시 선택해 주세요.")

    ensure_users_table()
    timestamp = now_text()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO users (
                email, name, department, role, can_create_documents,
                is_active, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                name=excluded.name,
                department=excluded.department,
                role=excluded.role,
                can_create_documents=excluded.can_create_documents,
                is_active=excluded.is_active,
                updated_at=excluded.updated_at
            """,
            (
                clean_email,
                name.strip() or clean_email.split("@")[0],
                department,
                role,
                int(can_create_documents),
                int(is_active),
                timestamp,
                timestamp,
            ),
        )
        conn.commit()


def get_user_options() -> list[str]:
    ensure_users_table()
    with connect() as conn:
        rows = conn.execute("SELECT email FROM users ORDER BY email").fetchall()
    return [str(row["email"]) for row in rows]
