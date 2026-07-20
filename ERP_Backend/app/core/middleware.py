from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": {"code": code, "message": message}},
    )


def _client_ip(scope: Scope) -> str:
    headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
    cf_ip = headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    forwarded = headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    real_ip = headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    client = scope.get("client")
    if client:
        return str(client[0])
    return "unknown"


class RequestGuardMiddleware:
    """Reject obviously abusive requests before they reach routers or DB code."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                body_size = int(content_length)
            except ValueError:
                body_size = 0
            if body_size > settings.max_request_body_bytes:
                response = _error_response(413, "REQUEST_TOO_LARGE", "Request body is too large.")
                await response(scope, receive, send)
                return

        query = scope.get("query_string", b"")
        if len(query) > settings.max_query_string_bytes:
            response = _error_response(414, "QUERY_TOO_LONG", "Query string is too long.")
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


class RateLimitMiddleware:
    """Small in-process fixed-window rate limiter for local/single-host deployments."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _limit_for_path(self, path: str) -> int:
        if path.startswith("/api/v1/auth"):
            return settings.auth_rate_limit_requests_per_window
        if path.startswith("/api/v1/imports") or "/imports/" in path:
            return settings.import_rate_limit_requests_per_window
        return settings.rate_limit_requests_per_window

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not settings.rate_limit_enabled:
            await self.app(scope, receive, send)
            return

        path = str(scope.get("path", ""))
        if path == "/health":
            await self.app(scope, receive, send)
            return

        now = time.monotonic()
        window = settings.rate_limit_window_seconds
        limit = self._limit_for_path(path)
        group = "auth" if path.startswith("/api/v1/auth") else "imports" if path.startswith("/api/v1/imports") else "default"
        key = f"{_client_ip(scope)}:{group}"
        hits = self._hits[key]
        while hits and now - hits[0] >= window:
            hits.popleft()

        if len(hits) >= limit:
            response = _error_response(429, "RATE_LIMITED", "Too many requests. Please try again later.")
            response.headers["Retry-After"] = str(window)
            await response(scope, receive, send)
            return

        hits.append(now)
        await self.app(scope, receive, send)


class SecurityHeadersMiddleware:
    """Attach defensive browser headers to reduce accidental data exposure."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("X-Frame-Options", "DENY")
                headers.setdefault("Referrer-Policy", "no-referrer")
                headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
                headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
                if str(scope.get("path", "")).startswith("/api/"):
                    headers.setdefault("Cache-Control", "no-store")
                if settings.environment != "local":
                    headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            await send(message)

        await self.app(scope, receive, send_with_headers)
