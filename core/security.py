from __future__ import annotations

import hashlib
import hmac
import secrets


PASSWORD_ITERATIONS = 240_000


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
