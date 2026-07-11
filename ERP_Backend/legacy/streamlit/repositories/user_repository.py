from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from config import ADMIN_EMAILS, DB_PATH
from core.security import PASSWORD_ITERATIONS, hash_password


DEPARTMENTS = ["경영지원팀", "기술영업팀", "생산팀", "연구소"]
ROLES = ["관리자", "부서관리자", "일반사용자"]
DEFAULT_ADMIN_PASSWORD = os.getenv("MEGACELL_ADMIN_INITIAL_PASSWORD", "megacell1234!")


@dataclass(frozen=True)
class User:
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


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row["name"]) for row in rows}


def ensure_users_schema(conn: sqlite3.Connection) -> None:
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


def seed_admin_users(conn: sqlite3.Connection) -> None:
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
            VALUES (?, ?, '경영지원팀', '관리자', 1, 1, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                department='경영지원팀',
                role='관리자',
                can_create_documents=1,
                is_active=1,
                password_hash=COALESCE(NULLIF(users.password_hash, ''), excluded.password_hash),
                password_salt=COALESCE(NULLIF(users.password_salt, ''), excluded.password_salt),
                password_iterations=COALESCE(users.password_iterations, excluded.password_iterations),
                must_change_password=CASE
                    WHEN users.password_hash IS NULL OR users.password_hash = '' THEN 1
                    ELSE users.must_change_password
                END,
                updated_at=excluded.updated_at
            """,
            (email, email.split("@")[0], password_hash, password_salt, iterations, timestamp, timestamp),
        )


def ensure_users_table() -> None:
    with connect() as conn:
        ensure_users_schema(conn)
        seed_admin_users(conn)
        conn.commit()


def row_to_user(row: sqlite3.Row) -> User:
    return User(
        email=str(row["email"]).lower(),
        name=str(row["name"] or ""),
        department=str(row["department"] or ""),
        role=str(row["role"] or "일반사용자"),
        can_create_documents=bool(row["can_create_documents"]),
        is_active=bool(row["is_active"]),
        must_change_password=bool(row["must_change_password"]),
    )


def get_user(email: str) -> User | None:
    if not email:
        return None
    ensure_users_table()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip().lower(),)).fetchone()
    return row_to_user(row) if row else None


def get_user_auth_row(email: str) -> sqlite3.Row | None:
    ensure_users_table()
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip().lower(),)).fetchone()


def touch_login(email: str) -> None:
    if not email:
        return
    with connect() as conn:
        conn.execute(
            "UPDATE users SET last_login_at=?, updated_at=? WHERE lower(email)=lower(?)",
            (now_text(), now_text(), email.strip().lower()),
        )
        conn.commit()


def list_users() -> list[dict[str, Any]]:
    ensure_users_table()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                email,
                name,
                department,
                role,
                can_create_documents,
                is_active,
                must_change_password,
                last_login_at,
                updated_at
            FROM users
            ORDER BY is_active DESC, role ASC, department ASC, email ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


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


def update_password(email: str, password_hash: str, password_salt: str, iterations: int, must_change_password: bool) -> None:
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


def get_user_options() -> list[str]:
    ensure_users_table()
    with connect() as conn:
        rows = conn.execute("SELECT email FROM users ORDER BY email").fetchall()
    return [str(row["email"]) for row in rows]
