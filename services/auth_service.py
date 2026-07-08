from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import streamlit as st

from config import ADMIN_EMAILS, DB_PATH


DEPARTMENTS = ["경영지원팀", "기술영업팀", "생산팀", "연구소"]
ROLES = ["관리자", "부서관리자", "일반사용자"]
DEFAULT_ADMIN_PASSWORD = os.getenv("MEGACELL_ADMIN_INITIAL_PASSWORD", "megacell1234!")
PASSWORD_ITERATIONS = 240_000


@dataclass(frozen=True)
class CurrentUser:
    email: str
    name: str
    department: str
    role: str
    can_create_documents: bool
    is_active: bool
    must_change_password: bool

    @property
    def is_admin(self) -> bool:
        return self.role == "관리자"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: str | None = None, iterations: int = PASSWORD_ITERATIONS) -> tuple[str, str, int]:
    if not password:
        raise ValueError("비밀번호를 입력해 주세요.")
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(password_salt),
        iterations,
    ).hex()
    return digest, password_salt, iterations


def verify_password(password: str, password_hash: str, password_salt: str, iterations: int) -> bool:
    if not password or not password_hash or not password_salt:
        return False
    digest, _, _ = hash_password(password, password_salt, iterations)
    return hmac.compare_digest(digest, password_hash)


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row["name"]) for row in rows}


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
                password_hash TEXT,
                password_salt TEXT,
                password_iterations INTEGER NOT NULL DEFAULT 240000,
                must_change_password INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )
        columns = table_columns(conn, "users")
        migrations = {
            "password_hash": "ALTER TABLE users ADD COLUMN password_hash TEXT",
            "password_salt": "ALTER TABLE users ADD COLUMN password_salt TEXT",
            "password_iterations": "ALTER TABLE users ADD COLUMN password_iterations INTEGER NOT NULL DEFAULT 240000",
            "must_change_password": "ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0",
        }
        for column, sql in migrations.items():
            if column not in columns:
                conn.execute(sql)

        timestamp = now_text()
        for email in sorted(ADMIN_EMAILS):
            password_hash, password_salt, iterations = hash_password(DEFAULT_ADMIN_PASSWORD)
            conn.execute(
                """
                INSERT INTO users (
                    email, name, department, role, can_create_documents,
                    is_active, password_hash, password_salt, password_iterations,
                    must_change_password, created_at, updated_at
                )
                VALUES (?, ?, ?, '관리자', 1, 1, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    role='관리자',
                    can_create_documents=1,
                    is_active=1,
                    password_hash=COALESCE(users.password_hash, excluded.password_hash),
                    password_salt=COALESCE(users.password_salt, excluded.password_salt),
                    password_iterations=COALESCE(users.password_iterations, excluded.password_iterations),
                    must_change_password=CASE
                        WHEN users.password_hash IS NULL OR users.password_hash = '' THEN 1
                        ELSE users.must_change_password
                    END,
                    updated_at=excluded.updated_at
                """,
                (email, email.split("@")[0], "경영지원팀", password_hash, password_salt, iterations, timestamp, timestamp),
            )
        conn.commit()


def row_to_user(row: sqlite3.Row) -> CurrentUser:
    return CurrentUser(
        email=str(row["email"]).lower(),
        name=str(row["name"] or ""),
        department=str(row["department"] or ""),
        role=str(row["role"] or "일반사용자"),
        can_create_documents=bool(row["can_create_documents"]),
        is_active=bool(row["is_active"]),
        must_change_password=bool(row["must_change_password"]),
    )


def get_user(email: str) -> CurrentUser | None:
    if not email:
        return None
    ensure_users_table()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
    return row_to_user(row) if row else None


def touch_login(email: str) -> None:
    if not email:
        return
    with connect() as conn:
        conn.execute(
            "UPDATE users SET last_login_at=?, updated_at=? WHERE lower(email)=lower(?)",
            (now_text(), now_text(), email),
        )
        conn.commit()


def authenticate(email: str, password: str) -> tuple[CurrentUser | None, str | None]:
    ensure_users_table()
    clean_email = email.strip().lower()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (clean_email,)).fetchone()
    if row is None:
        return None, "등록되지 않은 이메일입니다. 관리자에게 사용자 등록을 요청해 주세요."
    if not bool(row["is_active"]):
        return None, "비활성 또는 승인 대기 계정입니다. 관리자에게 문의해 주세요."
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
    with connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET password_hash=?,
                password_salt=?,
                password_iterations=?,
                must_change_password=?,
                updated_at=?
            WHERE lower(email)=lower(?)
            """,
            (
                password_hash,
                password_salt,
                iterations,
                int(must_change_password),
                now_text(),
                email.strip().lower(),
            ),
        )
        conn.commit()


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
                must_change_password AS 비밀번호변경,
                last_login_at AS 최근로그인,
                updated_at AS 수정일
            FROM users
            ORDER BY is_active DESC, role ASC, department ASC, email ASC
            """,
            conn,
        )
    if not df.empty:
        df["문서생성"] = df["문서생성"].map(lambda value: "가능" if int(value or 0) else "불가")
        df["활성"] = df["활성"].map(lambda value: "사용" if int(value or 0) else "비활성")
        df["비밀번호변경"] = df["비밀번호변경"].map(lambda value: "필요" if int(value or 0) else "")
    return df


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

    ensure_users_table()
    timestamp = now_text()
    existing = get_user(clean_email)
    if existing is None and not new_password:
        raise ValueError("새 사용자는 초기 비밀번호를 입력해야 합니다.")

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

    if new_password:
        change_password(clean_email, new_password, must_change_password=force_password_change)


def get_user_options() -> list[str]:
    ensure_users_table()
    with connect() as conn:
        rows = conn.execute("SELECT email FROM users ORDER BY email").fetchall()
    return [str(row["email"]) for row in rows]
