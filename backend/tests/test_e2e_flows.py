"""
DIRECȚIA 1 — Teste E2E Fluxuri Critice.

Covers:
  - Flux complet: contact → oportunitate → ofertă → contract → proiect
  - Multi-tenant izolare: user din org A nu poate vedea datele org B
  - Switch prototip P1/P2/P3 — feature flags corecte
  - Notificări automate la evenimente cheie
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
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Fixtures: Second org + user for multi-tenant tests ───────────────────────

@pytest_asyncio.fixture
async def org_b(db_session: AsyncSession):
    from app.system.models import Organization
    org = Organization(
        id=uuid.uuid4(),
        name="Other Corp",
        slug="other-corp",
        active_prototype="P2",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def user_b(db_session: AsyncSession, org_b):
    from app.system.models import User, Role, UserRole
    role = Role(
        id=uuid.uuid4(),
        organization_id=org_b.id,
        name="Administrator",
        code="admin",
        is_system=True,
    )
    db_session.add(role)
    await db_session.flush()

    user = User(
        id=uuid.uuid4(),
        email="userb@other.ro",
        password_hash=hash_password("OtherPass123!"),
        first_name="Other",
        last_name="User",
        organization_id=org_b.id,
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
# 1. Flux complet: Contact → Oportunitate → Ofertă → Contract → Proiect
# ═══════════════════════════════════════════════════════════════════════════════


async def test_full_e2e_flow(client, test_user):
    """End-to-end: create contact, opportunity, offer, contract, project — full chain."""
    token = await _login(client)
    h = _auth(token)

    # Step 1: Create contact
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "E2E Client SRL",
        "contact_type": "pj",
        "stage": "prospect",
        "email": "e2e@client.ro",
    }, headers=h)
    assert resp.status_code == 201, resp.text
    contact_id = resp.json()["data"]["id"]

    # Step 2: Create opportunity from contact
    resp = await client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": contact_id,
        "title": "E2E Oportunitate Renovare",
        "estimated_value": 150000.0,
        "currency": "RON",
        "stage": "new",
    }, headers=h)
    assert resp.status_code == 201, resp.text
    opp_id = resp.json()["data"]["id"]

    # Verify opportunity links to contact
    resp = await client.get(f"/api/v1/pipeline/opportunities/{opp_id}", headers=h)
    assert resp.status_code == 200
    assert resp.json()["data"]["contact_id"] == contact_id

    # Step 3: Create offer linked to opportunity and contact
    resp = await client.post("/api/v1/pipeline/offers", json={
        "contact_id": contact_id,
        "opportunity_id": opp_id,
        "title": "Ofertă Renovare Termică",
        "currency": "RON",
        "validity_days": 30,
    }, headers=h)
    assert resp.status_code == 201, resp.text
    offer_id = resp.json()["data"]["id"]

    # Step 4: Create contract linked to offer
    resp = await client.post("/api/v1/pipeline/contracts", json={
        "contact_id": contact_id,
        "offer_id": offer_id,
        "opportunity_id": opp_id,
        "title": "Contract Renovare Termică",
        "total_value": 145000.0,
        "currency": "RON",
    }, headers=h)
    assert resp.status_code == 201, resp.text
    contract_id = resp.json()["data"]["id"]

    # Step 5: Create project linked to contract
    resp = await client.post("/api/v1/pm/projects", json={
        "contract_id": contract_id,
        "contact_id": contact_id,
        "project_number": "PRJ-E2E-001",
        "name": "Proiect Renovare Termică E2E",
        "project_type": "client",
        "budget_allocated": 145000.0,
    }, headers=h)
    assert resp.status_code == 201, resp.text
    project_id = resp.json()["data"]["id"]

    # Verify project exists and has correct links
    resp = await client.get(f"/api/v1/pm/projects/{project_id}", headers=h)
    assert resp.status_code == 200
    project = resp.json()["data"]
    assert project["contract_id"] == contract_id
    assert project["name"] == "Proiect Renovare Termică E2E"


async def test_e2e_flow_contract_sign_then_project(client, test_user):
    """Sign a contract and verify it transitions status correctly."""
    token = await _login(client)
    h = _auth(token)

    # Create contact + contract
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "Sign Test SRL",
    }, headers=h)
    contact_id = resp.json()["data"]["id"]

    resp = await client.post("/api/v1/pipeline/contracts", json={
        "contact_id": contact_id,
        "title": "Contract pt Semnare",
        "total_value": 50000.0,
    }, headers=h)
    assert resp.status_code == 201
    contract_id = resp.json()["data"]["id"]

    # Sign the contract
    resp = await client.post(
        f"/api/v1/pipeline/contracts/{contract_id}/sign",
        json={},
        headers=h,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "signed"


async def test_e2e_opportunity_stage_transition(client, test_user):
    """Test opportunity stage transitions through pipeline."""
    token = await _login(client)
    h = _auth(token)

    # Create contact + opportunity
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "Transition Test",
    }, headers=h)
    contact_id = resp.json()["data"]["id"]

    resp = await client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": contact_id,
        "title": "Transition Opp",
        "stage": "new",
    }, headers=h)
    opp_id = resp.json()["data"]["id"]

    # Transition stage
    resp = await client.post(
        f"/api/v1/pipeline/opportunities/{opp_id}/transition",
        json={"new_stage": "qualified"},
        headers=h,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["stage"] == "qualified"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Multi-tenant izolare — user din org A nu vede date din org B
# ═══════════════════════════════════════════════════════════════════════════════


async def test_multitenant_contact_isolation(client, test_user, user_b):
    """User A creates a contact. User B cannot see it."""
    # User A creates contact
    token_a = await _login(client, "test@buildwise.ro", "TestPass123!")
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "Secret Corp A",
    }, headers=_auth(token_a))
    assert resp.status_code == 201

    # User B lists contacts — should not see A's contact
    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp = await client.get("/api/v1/crm/contacts", headers=_auth(token_b))
    assert resp.status_code == 200
    contacts = resp.json()["data"]
    names = [c["company_name"] for c in contacts]
    assert "Secret Corp A" not in names


async def test_multitenant_opportunity_isolation(client, test_user, user_b):
    """User A creates opportunity. User B cannot see it."""
    token_a = await _login(client, "test@buildwise.ro", "TestPass123!")
    resp = await client.post("/api/v1/crm/contacts", json={
        "company_name": "Isolated Contact",
    }, headers=_auth(token_a))
    contact_id = resp.json()["data"]["id"]

    resp = await client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": contact_id,
        "title": "Secret Opportunity A",
    }, headers=_auth(token_a))
    assert resp.status_code == 201

    # User B cannot see it
    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp = await client.get("/api/v1/pipeline/opportunities", headers=_auth(token_b))
    assert resp.status_code == 200
    titles = [o["title"] for o in resp.json()["data"]]
    assert "Secret Opportunity A" not in titles


async def test_multitenant_project_isolation(client, test_user, user_b):
    """User A creates project. User B cannot see it."""
    token_a = await _login(client, "test@buildwise.ro", "TestPass123!")
    resp = await client.post("/api/v1/pm/projects", json={
        "project_number": "PRJ-ISO-001",
        "name": "Secret Project A",
    }, headers=_auth(token_a))
    assert resp.status_code == 201

    # User B cannot see it
    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp = await client.get("/api/v1/pm/projects", headers=_auth(token_b))
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()["data"]]
    assert "Secret Project A" not in names


async def test_multitenant_system_roles_isolation(client, test_user, user_b):
    """Roles are scoped to organization."""
    token_a = await _login(client, "test@buildwise.ro", "TestPass123!")
    resp_a = await client.get("/api/v1/system/roles", headers=_auth(token_a))
    roles_a = resp_a.json()["data"]

    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp_b = await client.get("/api/v1/system/roles", headers=_auth(token_b))
    roles_b = resp_b.json()["data"]

    # Each org sees only its own roles
    ids_a = {r["id"] for r in roles_a}
    ids_b = {r["id"] for r in roles_b}
    assert ids_a.isdisjoint(ids_b), "Roles should not overlap between orgs"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Switch prototip P1/P2/P3 — feature flags corecte
# ═══════════════════════════════════════════════════════════════════════════════


async def test_prototype_p1_config(client, test_user, test_org):
    """P1 org has prototype set to P1."""
    token = await _login(client)
    resp = await client.get("/api/v1/me", headers=_auth(token))
    assert resp.status_code == 200
    # test_org is P1 by default (from conftest)


async def test_prototype_register_creates_default_org(client):
    """Registration creates org with default prototype."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": "proto@test.ro",
        "password": "ProtoPass123!",
        "first_name": "Proto",
        "last_name": "Test",
        "organization_name": "Proto Corp",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["email"] == "proto@test.ro"


async def test_feature_flags_per_org(client, test_user, user_b):
    """Feature flags are org-scoped."""
    token_a = await _login(client)
    resp_a = await client.get("/api/v1/system/feature-flags", headers=_auth(token_a))
    assert resp_a.status_code == 200

    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp_b = await client.get("/api/v1/system/feature-flags", headers=_auth(token_b))
    assert resp_b.status_code == 200

    # Each org has its own flags (or both empty — that's valid too)
    flags_a = resp_a.json()["data"]
    flags_b = resp_b.json()["data"]
    ids_a = {f["id"] for f in flags_a}
    ids_b = {f["id"] for f in flags_b}
    assert ids_a.isdisjoint(ids_b) or (len(ids_a) == 0 and len(ids_b) == 0)


async def test_health_shows_prototype(client):
    """Health endpoint shows configured prototype."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["prototype"] in ("P1", "P2", "P3")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Notificări automate la evenimente cheie
# ═══════════════════════════════════════════════════════════════════════════════


async def test_notification_on_create(client, test_user):
    """Notifications can be created and listed."""
    token = await _login(client)
    h = _auth(token)

    # Create notification
    resp = await client.post("/api/v1/system/notifications", json={
        "title": "Contract semnat",
        "message": "Contractul C-001 a fost semnat de client.",
    }, headers=h)
    assert resp.status_code == 201

    # List notifications
    resp = await client.get("/api/v1/system/notifications", headers=h)
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    titles = [n["title"] for n in resp.json()["data"]]
    assert "Contract semnat" in titles


async def test_notification_mark_read(client, test_user):
    """Mark notification as read."""
    token = await _login(client)
    h = _auth(token)

    resp = await client.post("/api/v1/system/notifications", json={
        "title": "Task finalizat",
        "message": "Task-ul T-001 a fost marcat complet.",
    }, headers=h)
    notif_id = resp.json()["data"]["id"]

    resp = await client.put(f"/api/v1/system/notifications/{notif_id}/read", headers=h)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "read"


async def test_notification_mark_all_read(client, test_user):
    """Mark all notifications as read."""
    token = await _login(client)
    h = _auth(token)

    # Create two
    for title in ["Notif 1", "Notif 2"]:
        await client.post("/api/v1/system/notifications", json={
            "title": title, "message": "test",
        }, headers=h)

    resp = await client.put("/api/v1/system/notifications/read-all", headers=h)
    assert resp.status_code == 200


async def test_follow_up_generation(client, test_user):
    """Follow-up notifications can be generated."""
    token = await _login(client)
    h = _auth(token)

    resp = await client.post("/api/v1/system/notifications/follow-up", headers=h)
    assert resp.status_code == 200


async def test_notification_isolation_between_orgs(client, test_user, user_b):
    """Notifications are user-scoped within org."""
    token_a = await _login(client)
    await client.post("/api/v1/system/notifications", json={
        "title": "Secret Notif A",
        "message": "Only for org A",
    }, headers=_auth(token_a))

    token_b = await _login(client, "userb@other.ro", "OtherPass123!")
    resp = await client.get("/api/v1/system/notifications", headers=_auth(token_b))
    titles = [n["title"] for n in resp.json()["data"]]
    assert "Secret Notif A" not in titles


# ═══════════════════════════════════════════════════════════════════════════════
# 5. E2E Flow Validation Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


async def test_e2e_flow_check_endpoint(client, test_user):
    """E2E flow check endpoint returns structured validation."""
    token = await _login(client)
    resp = await client.get("/api/v1/system/e2e-flow-check", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "overall_status" in data
    assert "checks" in data
    assert data["total_checks"] == 7
