from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MegaCell ERP API"
    app_version: str = "0.1.0"
    environment: str = "local"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 로컬 기본은 SQLite. 운영은 DATABASE_URL로 PostgreSQL 지정.
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parents[2] / 'instance' / 'megacell.db').as_posix()}"

    session_cookie_name: str = "megacell_session"
    session_ttl_hours: int = 12
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    password_min_length: int = 8

    api_docs_enabled: bool = True
    max_request_body_bytes: int = 10 * 1024 * 1024
    max_query_string_bytes: int = 4096
    rate_limit_enabled: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_requests_per_window: int = 120
    auth_rate_limit_requests_per_window: int = 20
    import_rate_limit_requests_per_window: int = 10
    sqlite_busy_timeout_seconds: int = 15


settings = Settings()
