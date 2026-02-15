import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.config import get_settings

settings = get_settings()


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "securepass",
            "display_name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["display_name"] == "New User"
        assert data["is_pro"] is False
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        resp = client.post("/api/auth/register", json={
            "email": "teacher@example.com",
            "password": "anotherpass",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    def test_register_invalid_email(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "securepass",
        })
        assert resp.status_code == 422

    def test_register_missing_password(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, test_user):
        resp = client.post("/api/auth/login", data={
            "username": "teacher@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid JWT
        payload = jwt.decode(
            data["access_token"],
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload["sub"] == str(test_user.id)

    def test_login_wrong_password(self, client, test_user):
        resp = client.post("/api/auth/login", data={
            "username": "teacher@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401
        assert "Incorrect email or password" in resp.json()["detail"]

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", data={
            "username": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestTokenValidation:
    def test_expired_token(self, client):
        expired_token = jwt.encode(
            {"sub": "some-id", "exp": datetime.utcnow() - timedelta(hours=1)},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        resp = client.get("/api/users/me", headers={
            "Authorization": f"Bearer {expired_token}",
        })
        assert resp.status_code == 401

    def test_malformed_token(self, client):
        resp = client.get("/api/users/me", headers={
            "Authorization": "Bearer not-a-valid-token",
        })
        assert resp.status_code == 401

    def test_missing_sub_claim(self, client):
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(hours=1)},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        resp = client.get("/api/users/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 401
