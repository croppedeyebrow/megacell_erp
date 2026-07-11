import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
email = f"u_{uuid.uuid4().hex[:8]}@example.com"

r = client.post(
    "/api/v1/auth/register",
    json={
        "email": email,
        "password": "password123",
        "name": "테스트",
        "department": "기술영업팀",
    },
)
print("register", r.status_code, r.json())
assert r.status_code == 201
assert "megacell_session" in r.cookies

r2 = client.get("/api/v1/auth/me")
print("me", r2.status_code, r2.json())
assert r2.status_code == 200

r3 = client.post("/api/v1/auth/logout")
print("logout", r3.status_code)

r4 = client.post(
    "/api/v1/auth/login",
    json={"email": email, "password": "password123"},
)
print("login", r4.status_code, r4.json().get("role"))
assert r4.status_code == 200
print("OK")
