"""
Tests for authentication endpoints — Task 3.

Covers:
  - GET /api/health
  - POST /api/auth/login (success + failure)
  - POST /api/auth/refresh (success + invalid)
  - POST /api/auth/logout
  - POST /api/auth/register
  - GET /api/v1/me (authenticated)
  - RBAC: protected endpoints reject unauthorized users
"""

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


# ─── Health Check ─────────────────────────────────────────────────────────────


async def test_health_check(client):
    """GET /api/health returns status ok."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "prototype" in data


# ─── Login ────────────────────────────────────────────────────────────────────


async def test_login_success(client, test_user):
    """POST /api/auth/login with valid credentials returns tokens."""
    resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "TestPass123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


async def test_login_wrong_password(client, test_user):
    """POST /api/auth/login with wrong password returns 401."""
    resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "WrongPassword",
    })
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


async def test_login_nonexistent_user(client):
    """POST /api/auth/login with unknown email returns 401."""
    resp = await client.post("/api/auth/login", json={
        "email": "nobody@buildwise.ro",
        "password": "SomePass123",
    })
    assert resp.status_code == 401


# ─── Token Refresh ────────────────────────────────────────────────────────────


async def test_refresh_success(client, test_user):
    """POST /api/auth/refresh with valid refresh token returns new tokens."""
    # Login first
    login_resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "TestPass123!",
    })
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    resp = await client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_invalid_token(client):
    """POST /api/auth/refresh with invalid token returns 401."""
    resp = await client.post("/api/auth/refresh", json={
        "refresh_token": "invalid.token.here",
    })
    assert resp.status_code == 401


# ─── Logout ───────────────────────────────────────────────────────────────────


async def test_logout(client, test_user):
    """POST /api/auth/logout invalidates refresh token."""
    # Login
    login_resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "TestPass123!",
    })
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]

    # Logout
    resp = await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 204

    # Refresh should now fail
    resp = await client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 401


# ─── Register ─────────────────────────────────────────────────────────────────


async def test_register_success(client):
    """POST /api/auth/register creates user + organization."""
    resp = await client.post("/api/auth/register", json={
        "email": "new@buildwise.ro",
        "password": "NewPass123!",
        "first_name": "New",
        "last_name": "User",
        "organization_name": "New Corp",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["email"] == "new@buildwise.ro"
    assert data["first_name"] == "New"
    assert "admin" in data["roles"]


async def test_register_duplicate_email(client):
    """POST /api/auth/register with duplicate email returns 400."""
    payload = {
        "email": "dup@buildwise.ro",
        "password": "DupPass123!",
        "first_name": "Dup",
        "last_name": "User",
        "organization_name": "Dup Corp",
    }
    resp1 = await client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 400
    assert "already registered" in resp2.json()["detail"]


# ─── Current User (GET /me) ──────────────────────────────────────────────────


async def test_get_me_authenticated(client, test_user):
    """GET /api/v1/me returns current user when authenticated."""
    login_resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "TestPass123!",
    })
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == "test@buildwise.ro"
    assert data["first_name"] == "Test"


async def test_get_me_unauthenticated(client):
    """GET /api/v1/me without token returns 401/403."""
    resp = await client.get("/api/v1/me")
    assert resp.status_code in (401, 403)


# ─── RBAC: Admin-only endpoints ──────────────────────────────────────────────


async def test_roles_endpoint_requires_auth(client):
    """GET /api/v1/system/roles without auth returns 401/403."""
    resp = await client.get("/api/v1/system/roles")
    assert resp.status_code in (401, 403)


async def test_audit_logs_endpoint_requires_auth(client):
    """GET /api/v1/system/audit-logs without auth returns 401/403."""
    resp = await client.get("/api/v1/system/audit-logs")
    assert resp.status_code in (401, 403)
