"""Basic smoke tests for the hosting platform API."""

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _suffix():
    return uuid.uuid4().hex[:8]


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login():
    s = _suffix()
    email = f"u{s}@test.com"
    username = f"u{s}"
    r = client.post("/api/v1/auth/register", json={"email": email, "username": username, "password": "Passw0rd!"})
    assert r.status_code == 201
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "Passw0rd!"})
    assert r.status_code == 200
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == username


def test_plans_require_admin():
    s = _suffix()
    r = client.post("/api/v1/auth/register", json={"email": f"u{s}@test.com", "username": f"u{s}", "password": "Passw0rd!"})
    assert r.status_code == 201
    csrf = r.cookies.get("csrf_token")
    headers = {"X-CSRF-TOKEN": csrf} if csrf else {}
    r = client.post("/api/v1/plans", json={"category_id": 1, "name": "X", "slug": f"x{s}", "price": 1.0}, headers=headers)
    assert r.status_code in (401, 403)


def test_csrf_protection():
    s = _suffix()
    r = client.post("/api/v1/auth/register", json={"email": f"u{s}@test.com", "username": f"u{s}", "password": "Passw0rd!"})
    assert r.status_code == 201
    # Missing CSRF token on state-changing request -> 403
    r = client.post("/api/v1/orders", json={"plan_id": 1})
    assert r.status_code == 403
