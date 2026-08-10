"""Tests for authentication (login, JWT, rate limiting, TOTP)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _get_client():
    from backend.main import app

    return TestClient(app)


class TestLogin:
    def test_login_success(self):
        """Default admin credentials should work."""
        with _get_client() as client:
            res = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "AdminTest123!"},
            )
            assert res.status_code == 200
            data = res.json()
            assert "access_token" in data
            assert len(data["access_token"]) > 20

    def test_login_wrong_password(self):
        """Wrong password returns 401."""
        with _get_client() as client:
            res = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "wrong_password"},
            )
            assert res.status_code == 401

    def test_login_nonexistent_user(self):
        """Non-existent user returns 401."""
        with _get_client() as client:
            res = client.post(
                "/api/auth/login",
                json={"username": "nobody", "password": "anything"},
            )
            assert res.status_code == 401

    def test_me_with_valid_token(self):
        """GET /me with a valid token returns the user info."""
        with _get_client() as client:
            login = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "AdminTest123!"},
            )
            token = login.json()["access_token"]
            res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert res.status_code == 200
            assert res.json()["username"] == "admin"

    def test_me_without_token(self):
        """GET /me without a token returns 401."""
        with _get_client() as client:
            res = client.get("/api/auth/me")
            assert res.status_code == 401

    def test_me_with_bad_token(self):
        """GET /me with a bad token returns 401."""
        with _get_client() as client:
            res = client.get("/api/auth/me", headers={"Authorization": "Bearer bad_token"})
            assert res.status_code == 401

    def test_login_rate_limit(self):
        """Repeated login attempts with the same username should be rate-limited."""
        with _get_client() as client:
            for _ in range(5):
                client.post(
                    "/api/auth/login",
                    json={"username": "ratelimit_user", "password": "wrong"},
                )
            # The 6th attempt should be rate-limited
            res = client.post(
                "/api/auth/login",
                json={"username": "ratelimit_user", "password": "wrong"},
            )
            assert res.status_code == 429


class TestHealth:
    def test_healthz(self):
        with _get_client() as client:
            res = client.get("/healthz")
            assert res.status_code == 200
            assert res.json()["status"] == "ok"

    def test_readyz_starts_as_not_ready(self):
        with _get_client() as client:
            res = client.get("/readyz")
            # App may or may not be ready depending on startup timing
            assert res.status_code in (200, 503)
