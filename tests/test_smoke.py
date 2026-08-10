from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz():
    from backend.main import app

    with TestClient(app) as client:
        res = client.get("/healthz")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


def test_spa_index():
    from backend.main import app

    with TestClient(app) as client:
        res = client.get("/")
        assert res.status_code == 200
        assert "TG-SignPulse" in res.text


def test_login_and_me():
    from backend.main import app

    with TestClient(app) as client:
        res = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "AdminTest123!"},
        )
        assert res.status_code == 200, res.text
        token = res.json()["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["username"] == "admin"


def test_accounts_empty():
    from backend.main import app

    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "AdminTest123!"},
        )
        token = login.json()["access_token"]
        res = client.get("/api/accounts", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
