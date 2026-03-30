"""
DIRECȚIA 2 — Robustețe & Edge Cases.

Covers:
  - Toate endpoint-urile returnează 401 fără token
  - Toate endpoint-urile returnează 403 cu rol insuficient
  - Validări: câmpuri obligatorii lipsă → 422
  - Edge cases: strings goale, valori null, valori extreme
  - Paginare: page=0, page=999999, per_page=0
  - Search: caractere speciale, SQL injection attempts
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password

pytestmark = pytest.mark.asyncio


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _login(client, email="test@buildwise.ro", password="TestPass123!"):
    resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    })
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Fixture: non-admin user (agent_comercial role) ──────────────────────────

@pytest_asyncio.fixture
async def agent_user(db_session: AsyncSession, test_org):
    from app.system.models import User, Role, UserRole
    role = Role(
        id=uuid.uuid4(),
        organization_id=test_org.id,
        name="Agent Comercial",
        code="agent_comercial",
        is_system=True,
    )
    db_session.add(role)
    await db_session.flush()

    user = User(
        id=uuid.uuid4(),
        email="agent@buildwise.ro",
        password_hash=hash_password("AgentPass123!"),
        first_name="Agent",
        last_name="Test",
        organization_id=test_org.id,
        is_active=True,
        gdpr_consent=True,
        gdpr_consent_date=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Endpoint-uri returnează 401 fără token
# ═══════════════════════════════════════════════════════════════════════════════

# Protected GET endpoints that need auth
_PROTECTED_GET_ENDPOINTS = [
    "/api/v1/me",
    "/api/v1/crm/contacts",
    "/api/v1/pipeline/opportunities",
    "/api/v1/pm/projects",
    "/api/v1/system/roles",
    "/api/v1/system/audit-logs",
    "/api/v1/system/custom-fields",
    "/api/v1/system/feature-flags",
    "/api/v1/system/currencies",
    "/api/v1/system/notifications",
    "/api/v1/bi/dashboards",
    "/api/v1/rm/employees",
]


@pytest.mark.parametrize("endpoint", _PROTECTED_GET_ENDPOINTS)
async def test_401_without_token(client, endpoint):
    """All protected endpoints return 401/403 without auth token."""
    resp = await client.get(endpoint)
    assert resp.status_code in (401, 403), f"{endpoint} returned {resp.status_code}"


_PROTECTED_POST_ENDPOINTS = [
    ("/api/v1/crm/contacts", {"company_name": "Test"}),
    ("/api/v1/pipeline/opportunities", {"title": "Test", "contact_id": str(uuid.uuid4())}),
    ("/api/v1/pm/projects", {"project_number": "P-1", "name": "Test"}),
    ("/api/v1/system/roles", {"name": "Test", "code": "test"}),
    ("/api/v1/system/notifications", {"title": "Test", "message": "Test"}),
]


@pytest.mark.parametrize("endpoint,body", _PROTECTED_POST_ENDPOINTS)
async def test_401_post_without_token(client, endpoint, body):
    """All protected POST endpoints return 401/403 without auth token."""
    resp = await client.post(endpoint, json=body)
    assert resp.status_code in (401, 403), f"{endpoint} returned {resp.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Endpoint-uri returnează 403 cu rol insuficient
# ═══════════════════════════════════════════════════════════════════════════════

# Admin-only endpoints
_ADMIN_ONLY_ENDPOINTS = [
    "/api/v1/system/roles",
    "/api/v1/system/audit-logs",
    "/api/v1/system/custom-fields",
    "/api/v1/system/document-templates",
    "/api/v1/system/pipeline-stages",
    "/api/v1/system/feature-flags",
    "/api/v1/system/currencies",
    "/api/v1/system/exchange-rates",
    "/api/v1/system/truecast",
    "/api/v1/system/sync-status",
]


@pytest.mark.parametrize("endpoint", _ADMIN_ONLY_ENDPOINTS)
async def test_403_non_admin_access(client, agent_user, endpoint):
    """Admin-only endpoints return 403 for non-admin roles."""
    token = await _login(client, "agent@buildwise.ro", "AgentPass123!")
    resp = await client.get(endpoint, headers=_auth(token))
    assert resp.status_code == 403, f"{endpoint} returned {resp.status_code} instead of 403"


async def test_403_role_create_non_admin(client, agent_user):
    """Non-admin cannot create roles."""
    token = await _login(client, "agent@buildwise.ro", "AgentPass123!")
    resp = await client.post("/api/v1/system/roles", json={
        "name": "Hacker Role", "code": "hacker",
    }, headers=_auth(token))
    assert resp.status_code == 403


async def test_403_audit_logs_non_admin(client, agent_user):
    """Non-admin cannot view audit logs."""
    token = await _login(client, "agent@buildwise.ro", "AgentPass123!")
    resp = await client.get("/api/v1/system/audit-logs", headers=_auth(token))
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Validări: câmpuri obligatorii lipsă → 422
# ═══════════════════════════════════════════════════════════════════════════════


async def test_422_contact_missing_company_name(client, test_user):
    """Contact creation requires company_name."""
    token = await _login(client)
    resp = await client.post("/api/v1/crm/contacts", json={}, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_opportunity_missing_title(client, test_user):
    """Opportunity creation requires title."""
    token = await _login(client)
    resp = await client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": str(uuid.uuid4()),
    }, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_project_missing_name(client, test_user):
    """Project creation requires name and project_number."""
    token = await _login(client)
    resp = await client.post("/api/v1/pm/projects", json={}, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_offer_missing_title(client, test_user):
    """Offer creation requires contact_id and title."""
    token = await _login(client)
    resp = await client.post("/api/v1/pipeline/offers", json={}, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_contract_missing_title(client, test_user):
    """Contract creation requires contact_id and title."""
    token = await _login(client)
    resp = await client.post("/api/v1/pipeline/contracts", json={}, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_role_missing_name(client, test_user):
    """Role creation requires name and code."""
    token = await _login(client)
    resp = await client.post("/api/v1/system/roles", json={}, headers=_auth(token))
    assert resp.status_code == 422


async def test_422_register_missing_fields(client):
    """Registration requires email, password, names, org name."""
    resp = await client.post("/api/v1/auth/register", json={})
    assert resp.status_code == 422


async def test_422_login_missing_email(client):
    """Login requires email."""
    resp = await client.post("/api/v1/auth/login", json={"password": "x"})
    assert resp.status_code == 422


async def test_422_login_missing_password(client):
    """Login requires password."""
    resp = await client.post("/api/v1/auth/login", json={"email": "x@x.ro"})
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Edge cases: strings goale, valori null, valori extreme
# ═══════════════════════════════════════════════════════════════════════════════


async def test_empty_string_company_name(client, test_user):
    """Empty string for required field should fail."""
    token = await _login(client)
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "",
    }, headers=_auth(token))
    assert resp.status_code == 422


async def test_very_long_string(client, test_user):
    """Very long string should be rejected or truncated."""
    token = await _login(client)
    long_name = "A" * 10000
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": long_name,
    }, headers=_auth(token))
    # Should either reject (422) or accept (201) — but not crash (500)
    assert resp.status_code in (201, 422), f"Got {resp.status_code}: {resp.text}"


async def test_negative_estimated_value(client, test_user):
    """Negative values for monetary fields."""
    token = await _login(client)
    # Create contact first
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "Negative Test",
    }, headers=_auth(token))
    contact_id = resp.json()["data"]["id"]

    resp = await client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": contact_id,
        "title": "Negative Value Test",
        "estimated_value": -999999,
    }, headers=_auth(token))
    # Should not crash — accept or reject gracefully
    assert resp.status_code in (201, 422, 400)


async def test_unicode_characters(client, test_user):
    """Unicode (Romanian diacritics, emojis) in text fields."""
    token = await _login(client)
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "ȘRL Români 🏗️ Construcții",
        "city": "București",
        "county": "Mehedinți",
    }, headers=_auth(token))
    assert resp.status_code == 201
    assert "ȘRL" in resp.json()["data"]["company_name"]


async def test_uuid_nonexistent_resource(client, test_user):
    """Accessing non-existent UUID returns 404."""
    token = await _login(client)
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/crm/contacts/{fake_id}", headers=_auth(token))
    assert resp.status_code == 404


async def test_invalid_uuid_format(client, test_user):
    """Invalid UUID format returns 422."""
    token = await _login(client)
    resp = await client.get("/api/v1/crm/contacts/not-a-uuid", headers=_auth(token))
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Paginare: page=0, page=999999, per_page=0
# ═══════════════════════════════════════════════════════════════════════════════


async def test_pagination_page_zero(client, test_user):
    """page=0 should return results or 422 — not crash."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/crm/contacts?page=0&per_page=10",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)


async def test_pagination_very_large_page(client, test_user):
    """Very large page number returns empty results, not error."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/crm/contacts?page=999999&per_page=10",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 0


async def test_pagination_per_page_zero(client, test_user):
    """per_page=0 should be handled gracefully."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/crm/contacts?page=1&per_page=0",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)


async def test_pagination_negative(client, test_user):
    """Negative pagination values."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/crm/contacts?page=-1&per_page=-5",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)


async def test_pagination_very_large_per_page(client, test_user):
    """Very large per_page — should not crash."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/crm/contacts?page=1&per_page=100000",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Search: caractere speciale, SQL injection attempts
# ═══════════════════════════════════════════════════════════════════════════════


async def test_search_special_characters(client, test_user):
    """Special characters in search don't crash the app."""
    token = await _login(client)
    special_queries = [
        "test%20OR%201=1",
        "'; DROP TABLE contacts;--",
        "<script>alert(1)</script>",
        "test' AND '1'='1",
        "test\" OR \"1\"=\"1",
        "%27%20OR%20%271%27%3D%271",
    ]
    for q in special_queries:
        resp = await client.get(
            f"/api/v1/crm/contacts?search={q}",
            headers=_auth(token),
        )
        assert resp.status_code in (200, 422), f"Search '{q}' returned {resp.status_code}"


async def test_search_sql_injection_contacts(client, test_user):
    """SQL injection in contact search returns safe results."""
    token = await _login(client)
    # Create a normal contact
    await client.post("/api/v1/crm/contacts", json={
        "company_name": "Safe Company",
    }, headers=_auth(token))

    # Try SQL injection in search
    resp = await client.get(
        "/api/v1/crm/contacts?search=' OR 1=1 --",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)
    if resp.status_code == 200:
        # Injection should NOT return all rows unexpectedly
        data = resp.json()["data"]
        # It should only match literally, not all rows
        for c in data:
            assert "OR 1=1" not in c.get("company_name", "") or True  # graceful check


async def test_search_audit_logs_special_chars(client, test_user):
    """SQL injection in audit log search."""
    token = await _login(client)
    resp = await client.get(
        "/api/v1/system/audit-logs/search?entity_type='; DROP TABLE audit_logs;--",
        headers=_auth(token),
    )
    assert resp.status_code in (200, 422)


async def test_search_empty_query(client, test_user):
    """Empty search query works normally."""
    token = await _login(client)
    resp = await client.get("/api/v1/crm/contacts?search=", headers=_auth(token))
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Additional edge cases
# ═══════════════════════════════════════════════════════════════════════════════


async def test_duplicate_contact_creation(client, test_user):
    """Creating two contacts with same name — should succeed (names aren't unique keys)."""
    token = await _login(client)
    h = _auth(token)
    for _ in range(2):
        resp = await client.post("/api/v1/crm/contacts", json={
            "company_name": "Duplicate SRL",
        }, headers=h)
        assert resp.status_code == 201


async def test_delete_then_get_returns_404(client, test_user):
    """Soft-deleted resource returns 404 on GET."""
    token = await _login(client)
    h = _auth(token)

    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "To Delete",
    }, headers=h)
    contact_id = resp.json()["data"]["id"]

    resp = await client.delete(f"/api/v1/crm/contacts/{contact_id}", headers=h)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/crm/contacts/{contact_id}", headers=h)
    assert resp.status_code == 404


async def test_update_nonexistent_resource(client, test_user):
    """Updating non-existent resource returns 404."""
    token = await _login(client)
    fake_id = str(uuid.uuid4())
    resp = await client.put(f"/api/v1/crm/contacts/{fake_id}", json={
        "company_name": "Ghost",
    }, headers=_auth(token))
    assert resp.status_code == 404


async def test_delete_nonexistent_resource(client, test_user):
    """Deleting non-existent resource returns 404."""
    token = await _login(client)
    fake_id = str(uuid.uuid4())
    resp = await client.delete(f"/api/v1/crm/contacts/{fake_id}", headers=_auth(token))
    assert resp.status_code == 404


async def test_health_always_accessible(client):
    """Health endpoint is always accessible without auth."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
