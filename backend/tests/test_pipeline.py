"""
Tests for Sales Pipeline module endpoints — F019, F026, F028, F029, F031,
F035, F037, F042–F056, F058.

Tests cover:
  - Opportunities CRUD + qualify + stage transitions + pipeline board
  - Milestones CRUD + dependencies + templates
  - Activities CRUD
  - Offers CRUD + approval + versioning + analytics
  - Contracts CRUD + from-offer + sign + terminate + billing + analytics
  - Invoices
  - Sales KPI Dashboard
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password
from app.database import Base


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _auth_headers(user_id: uuid.UUID, org_id: uuid.UUID) -> dict:
    """Generate JWT auth headers for testing."""
    token = create_access_token({
        "sub": str(user_id),
        "org": str(org_id),
        "roles": ["admin"],
    })
    return {"Authorization": f"Bearer {token}"}


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def auth_client(client, test_user, test_org):
    """Client with auth headers set."""
    headers = _auth_headers(test_user.id, test_org.id)
    client.headers.update(headers)
    return client


@pytest_asyncio.fixture
async def sample_contact(auth_client):
    """Create a sample contact for pipeline tests."""
    resp = await auth_client.post("/api/v1/crm/contacts", json={
        "company_name": "BAHN S.R.L.",
        "cui": "RO12345678",
        "stage": "prospect",
        "contact_type": "pj",
        "email": "contact@bahn.ro",
        "phone": "+40700000001",
        "city": "București",
        "county": "București",
        "gdpr_consent": True,
    })
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest_asyncio.fixture
async def sample_product(auth_client):
    """Create a sample product."""
    resp = await auth_client.post("/api/v1/crm/products", json={
        "name": "Sticlă tratată termic",
        "code": "STT-001",
        "product_type": "product",
        "unit_price": 150.0,
        "currency": "RON",
        "vat_rate": 0.19,
        "unit_of_measure": "mp",
    })
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest_asyncio.fixture
async def sample_opportunity(auth_client, sample_contact):
    """Create a sample opportunity."""
    resp = await auth_client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": sample_contact["id"],
        "title": "Renovare bloc A1",
        "estimated_value": 100000.0,
        "currency": "RON",
    })
    assert resp.status_code == 201
    return resp.json()["data"]


# ═══════════════════════════════════════════════════════════════════════════════
# F042: OPPORTUNITIES — QUALIFY & HANDOVER
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_opportunity(auth_client, sample_contact):
    """F042: Create opportunity with auto win probability (F052)."""
    resp = await auth_client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": sample_contact["id"],
        "title": "Renovare termoizolație bloc",
        "estimated_value": 50000.0,
        "currency": "RON",
        "source": "referral",
        "tags": ["termoizolatie", "bloc"],
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["stage"] == "new"
    assert data["win_probability"] == 0.10
    assert data["weighted_value"] == 5000.0
    assert data["is_qualified"] is False


@pytest.mark.asyncio
async def test_list_opportunities(auth_client, sample_opportunity):
    """F050: List opportunities."""
    resp = await auth_client.get("/api/v1/pipeline/opportunities")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_opportunity(auth_client, sample_opportunity):
    """F050: Get opportunity detail."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.get(f"/api/v1/pipeline/opportunities/{opp_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Renovare bloc A1"


@pytest.mark.asyncio
async def test_update_opportunity(auth_client, sample_opportunity):
    """Update opportunity."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.put(f"/api/v1/pipeline/opportunities/{opp_id}", json={
        "estimated_value": 120000.0,
        "notes": "Actualizat valoare.",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["estimated_value"] == 120000.0
    # Weighted value should recalculate
    assert data["weighted_value"] == 12000.0  # 120000 * 0.10


@pytest.mark.asyncio
async def test_delete_opportunity(auth_client, sample_opportunity):
    """Delete opportunity."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.delete(f"/api/v1/pipeline/opportunities/{opp_id}")
    assert resp.status_code == 204

    # Verify it's gone
    resp = await auth_client.get(f"/api/v1/pipeline/opportunities/{opp_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_qualify_opportunity(auth_client, sample_opportunity):
    """F042: Qualify opportunity — auto-transition to QUALIFIED."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.post(f"/api/v1/pipeline/opportunities/{opp_id}/qualify", json={
        "qualification_checklist": {
            "has_budget": True,
            "has_decision_maker": True,
            "has_timeline": True,
        },
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["is_qualified"] is True
    assert data["stage"] == "qualified"
    assert data["win_probability"] == 0.20


# ═══════════════════════════════════════════════════════════════════════════════
# F051: STAGE TRANSITIONS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_stage_transition_valid(auth_client, sample_opportunity):
    """F051: Valid stage transition new → qualified."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.post(f"/api/v1/pipeline/opportunities/{opp_id}/transition", json={
        "new_stage": "qualified",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stage"] == "qualified"
    assert data["win_probability"] == 0.20


@pytest.mark.asyncio
async def test_stage_transition_invalid(auth_client, sample_opportunity):
    """F051: Invalid transition new → won should fail."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.post(f"/api/v1/pipeline/opportunities/{opp_id}/transition", json={
        "new_stage": "won",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_stage_transition_to_lost(auth_client, sample_opportunity):
    """F053: Transition to lost with reason."""
    opp_id = sample_opportunity["id"]
    resp = await auth_client.post(f"/api/v1/pipeline/opportunities/{opp_id}/transition", json={
        "new_stage": "lost",
        "loss_reason": "price",
        "loss_reason_detail": "Competitorul a oferit un preț mai mic cu 20%.",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stage"] == "lost"
    assert data["loss_reason"] == "price"
    assert data["win_probability"] == 0.0


@pytest.mark.asyncio
async def test_full_pipeline_journey(auth_client, sample_contact):
    """F051/F052: Full pipeline journey new → qualified → scoping → offering → sent → negotiation → won."""
    # Create
    resp = await auth_client.post("/api/v1/pipeline/opportunities", json={
        "contact_id": sample_contact["id"],
        "title": "Deal complet",
        "estimated_value": 200000.0,
    })
    opp_id = resp.json()["data"]["id"]

    stages = [
        ("qualified", 0.20),
        ("scoping", 0.35),
        ("offering", 0.50),
        ("sent", 0.60),
        ("negotiation", 0.75),
    ]

    for stage, expected_prob in stages:
        resp = await auth_client.post(
            f"/api/v1/pipeline/opportunities/{opp_id}/transition",
            json={"new_stage": stage},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["win_probability"] == expected_prob

    # Win
    resp = await auth_client.post(
        f"/api/v1/pipeline/opportunities/{opp_id}/transition",
        json={"new_stage": "won", "won_reason": "Cel mai bun preț și calitate."},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stage"] == "won"
    assert data["win_probability"] == 1.0
    assert data["actual_close_date"] is not None


# ═══════════════════════════════════════════════════════════════════════════════
# F050: PIPELINE BOARD
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_pipeline_board(auth_client, sample_opportunity):
    """F050: Pipeline Kanban board."""
    resp = await auth_client.get("/api/v1/pipeline/board")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "stages" in data
    assert len(data["stages"]) == 8  # All stages
    assert data["total_pipeline_value"] >= 0
    assert data["currency"] == "RON"


# ═══════════════════════════════════════════════════════════════════════════════
# F043-F048: MILESTONES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_milestone(auth_client, sample_opportunity):
    """F043: Create milestone."""
    resp = await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": sample_opportunity["id"],
        "title": "Evaluare tehnică",
        "description": "Evaluare structurală și energetică",
        "estimated_duration_days": 5,
        "estimated_cost": 2500.0,
        "sort_order": 0,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Evaluare tehnică"
    assert data["status"] == "not_started"
    assert data["estimated_duration_days"] == 5


@pytest.mark.asyncio
async def test_list_milestones(auth_client, sample_opportunity):
    """F043: List milestones for opportunity."""
    opp_id = sample_opportunity["id"]
    # Create 2 milestones
    await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "MS1",
        "sort_order": 0,
    })
    await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "MS2",
        "sort_order": 1,
    })

    resp = await auth_client.get(f"/api/v1/pipeline/opportunities/{opp_id}/milestones")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_update_milestone(auth_client, sample_opportunity):
    """F043-F046: Update milestone."""
    resp = await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": sample_opportunity["id"],
        "title": "Milestone de actualizat",
    })
    ms_id = resp.json()["data"]["id"]

    resp = await auth_client.put(f"/api/v1/pipeline/milestones/{ms_id}", json={
        "status": "in_progress",
        "estimated_cost": 5000.0,
        "rm_validated": True,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "in_progress"
    assert data["estimated_cost"] == 5000.0
    assert data["rm_validated"] is True


@pytest.mark.asyncio
async def test_delete_milestone(auth_client, sample_opportunity):
    """Delete milestone."""
    resp = await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": sample_opportunity["id"],
        "title": "De șters",
    })
    ms_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/pipeline/milestones/{ms_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_milestone_dependency(auth_client, sample_opportunity):
    """F047: Add dependency between milestones."""
    opp_id = sample_opportunity["id"]

    resp1 = await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "Evaluare",
        "sort_order": 0,
    })
    ms1_id = resp1.json()["data"]["id"]

    resp2 = await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "Proiectare",
        "sort_order": 1,
    })
    ms2_id = resp2.json()["data"]["id"]

    resp = await auth_client.post(f"/api/v1/pipeline/milestones/{ms2_id}/dependencies", json={
        "depends_on_id": ms1_id,
        "dependency_type": "finish_to_start",
        "lag_days": 2,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["depends_on_id"] == ms1_id
    assert data["dependency_type"] == "finish_to_start"
    assert data["lag_days"] == 2


@pytest.mark.asyncio
async def test_time_summary(auth_client, sample_opportunity):
    """F044: Time estimation summary."""
    opp_id = sample_opportunity["id"]

    await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "Faza 1",
        "estimated_duration_days": 10,
        "estimated_cost": 5000.0,
    })
    await auth_client.post("/api/v1/pipeline/milestones", json={
        "opportunity_id": opp_id,
        "title": "Faza 2",
        "estimated_duration_days": 15,
        "estimated_cost": 8000.0,
    })

    resp = await auth_client.get(f"/api/v1/pipeline/opportunities/{opp_id}/time-summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_estimated_days"] == 25
    assert data["total_estimated_cost"] == 13000.0
    assert len(data["milestones"]) == 2


@pytest.mark.asyncio
async def test_milestone_template_crud_and_apply(auth_client, sample_opportunity):
    """F048: Create template, list, and apply to opportunity."""
    # Create template
    resp = await auth_client.post("/api/v1/pipeline/milestone-templates", json={
        "name": "Template renovare standard",
        "template_data": {
            "milestones": [
                {"title": "Evaluare inițială", "estimated_duration_days": 3, "estimated_cost": 1000.0},
                {"title": "Proiectare", "estimated_duration_days": 10, "estimated_cost": 5000.0},
                {"title": "Execuție", "estimated_duration_days": 30, "estimated_cost": 20000.0},
            ]
        },
    })
    assert resp.status_code == 201
    template_id = resp.json()["data"]["id"]

    # List templates
    resp = await auth_client.get("/api/v1/pipeline/milestone-templates")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1

    # Apply template
    resp = await auth_client.post("/api/v1/pipeline/milestone-templates/apply", json={
        "template_id": template_id,
        "opportunity_id": sample_opportunity["id"],
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 3
    assert data[0]["title"] == "Evaluare inițială"


# ═══════════════════════════════════════════════════════════════════════════════
# F054-F056: ACTIVITIES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_activity(auth_client, sample_contact, sample_opportunity):
    """F054: Create activity (meeting)."""
    resp = await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "meeting",
        "title": "Întâlnire evaluare tehnică",
        "scheduled_date": "2026-04-01T10:00:00Z",
        "scheduled_end_date": "2026-04-01T11:00:00Z",
        "duration_minutes": 60,
        "contact_id": sample_contact["id"],
        "opportunity_id": sample_opportunity["id"],
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["activity_type"] == "meeting"
    assert data["status"] == "planned"


@pytest.mark.asyncio
async def test_create_technical_visit(auth_client, sample_contact):
    """F055: Create technical visit with measurements."""
    resp = await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "technical_visit",
        "title": "Vizită tehnică bloc A1",
        "scheduled_date": "2026-04-02T09:00:00Z",
        "contact_id": sample_contact["id"],
        "visit_data": {
            "location": "Str. Exemplu 123, București",
            "persons_present": ["Ion Popescu", "Maria Ionescu"],
            "observations": "Fațada degradată, termoizolație inexistentă",
        },
        "measurements": {
            "wall_area_m2": 450,
            "window_area_m2": 80,
            "u_value_wall": 1.8,
            "u_value_window": 2.5,
        },
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["activity_type"] == "technical_visit"
    assert data["measurements"]["wall_area_m2"] == 450


@pytest.mark.asyncio
async def test_create_call_log(auth_client, sample_contact):
    """F056: Log a call."""
    resp = await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "call",
        "title": "Apel follow-up",
        "scheduled_date": "2026-04-03T14:00:00Z",
        "contact_id": sample_contact["id"],
        "call_duration_seconds": 300,
        "call_outcome": "interested",
        "notes": "Clientul e interesat de ofertă.",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["activity_type"] == "call"
    assert data["call_duration_seconds"] == 300


@pytest.mark.asyncio
async def test_list_activities(auth_client, sample_contact):
    """F054: List activities with filtering."""
    await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "follow_up",
        "title": "Follow-up 1",
        "scheduled_date": "2026-04-04T10:00:00Z",
        "contact_id": sample_contact["id"],
    })

    resp = await auth_client.get("/api/v1/pipeline/activities")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Filter by type
    resp = await auth_client.get("/api/v1/pipeline/activities?activity_type=follow_up")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_activity(auth_client, sample_contact):
    """Update activity status to completed."""
    resp = await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "task",
        "title": "Pregătire documentație",
        "scheduled_date": "2026-04-05T10:00:00Z",
    })
    act_id = resp.json()["data"]["id"]

    resp = await auth_client.put(f"/api/v1/pipeline/activities/{act_id}", json={
        "status": "completed",
        "notes": "Finalizat.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_delete_activity(auth_client, sample_contact):
    """Delete activity."""
    resp = await auth_client.post("/api/v1/pipeline/activities", json={
        "activity_type": "email",
        "title": "Email de șters",
        "scheduled_date": "2026-04-06T10:00:00Z",
    })
    act_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/pipeline/activities/{act_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F019: OFFERS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_offer(auth_client, sample_contact, sample_product):
    """F019: Create offer with line items."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă renovare termoizolație",
        "currency": "RON",
        "validity_days": 30,
        "line_items": [
            {
                "product_id": sample_product["id"],
                "description": "Sticlă tratată termic 100mp",
                "quantity": 100,
                "unit_price": 150.0,
                "unit_of_measure": "mp",
                "vat_rate": 0.19,
            }
        ],
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["status"] == "draft"
    assert data["subtotal"] == 15000.0
    assert data["vat_amount"] == 2850.0
    assert data["total_amount"] == 17850.0
    assert len(data["line_items"]) == 1
    assert data["offer_number"].startswith("OF-")


@pytest.mark.asyncio
async def test_list_offers(auth_client, sample_contact):
    """F019: List offers with filtering."""
    await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Test Offer",
        "line_items": [
            {"description": "Item 1", "quantity": 1, "unit_price": 100.0}
        ],
    })

    resp = await auth_client.get("/api/v1/pipeline/offers")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_offer_approval_flow(auth_client, sample_contact):
    """F028: Submit and approve offer."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă aprobare",
        "line_items": [
            {"description": "Serviciu audit", "quantity": 1, "unit_price": 5000.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    # Submit for approval
    resp = await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/submit", json={
        "comment": "Vă rog aprobați.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "pending_approval"

    # Approve
    resp = await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/approve", json={
        "approved": True,
        "comment": "Aprobat.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_offer_rejection(auth_client, sample_contact):
    """F028: Reject offer."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă respingere",
        "line_items": [
            {"description": "Test", "quantity": 1, "unit_price": 100.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/submit", json={})

    resp = await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/approve", json={
        "approved": False,
        "comment": "Prea scump.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "rejected"


@pytest.mark.asyncio
async def test_update_offer_draft_only(auth_client, sample_contact):
    """F019: Only draft offers can be updated."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Locked Offer",
        "line_items": [
            {"description": "Item", "quantity": 1, "unit_price": 100.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]
    await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/submit", json={})

    resp = await auth_client.put(f"/api/v1/pipeline/offers/{offer_id}", json={
        "title": "Updated Title",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_offer(auth_client, sample_contact):
    """F019: Delete draft offer."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "To Delete",
        "line_items": [
            {"description": "Item", "quantity": 1, "unit_price": 50.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/pipeline/offers/{offer_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_offer_versioning(auth_client, sample_contact):
    """F026: Create new version of an offer."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă v1",
        "line_items": [
            {"description": "Serviciu", "quantity": 1, "unit_price": 10000.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]
    assert resp.json()["data"]["version"] == 1

    # Create v2
    resp = await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/version", json={
        "title": "Ofertă v2 — preț redus",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["version"] == 2
    assert data["parent_offer_id"] == offer_id
    assert data["title"] == "Ofertă v2 — preț redus"
    assert len(data["line_items"]) == 1  # Copied from v1


# ═══════════════════════════════════════════════════════════════════════════════
# F031: CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_contract(auth_client, sample_contact):
    """F031: Create a contract."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract lucrări renovare",
        "total_value": 50000.0,
        "currency": "RON",
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-12-31T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["status"] == "draft"
    assert data["total_value"] == 50000.0
    assert data["contract_number"].startswith("CT-")


@pytest.mark.asyncio
async def test_create_contract_from_offer(auth_client, sample_contact):
    """F031: Create contract from approved offer."""
    resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă pentru contract",
        "terms_and_conditions": "Termeni standard BAHN.",
        "line_items": [
            {"description": "Lucrare", "quantity": 1, "unit_price": 25000.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]
    await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/submit", json={})
    await auth_client.post(f"/api/v1/pipeline/offers/{offer_id}/approve", json={
        "approved": True,
    })

    resp = await auth_client.post("/api/v1/pipeline/contracts/from-offer", json={
        "offer_id": offer_id,
        "title": "Contract din ofertă aprobată",
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-09-30T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["offer_id"] == offer_id
    assert data["total_value"] == 29750.0
    assert "Termeni standard BAHN." in data["terms_and_conditions"]


@pytest.mark.asyncio
async def test_list_contracts(auth_client, sample_contact):
    """F031: List contracts."""
    await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract test",
        "total_value": 10000.0,
    })

    resp = await auth_client.get("/api/v1/pipeline/contracts")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_contract(auth_client, sample_contact):
    """F031: Update contract (draft only)."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract update test",
        "total_value": 10000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.put(f"/api/v1/pipeline/contracts/{contract_id}", json={
        "total_value": 15000.0,
        "notes": "Actualizat valoare.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["total_value"] == 15000.0


@pytest.mark.asyncio
async def test_delete_contract(auth_client, sample_contact):
    """F031: Soft-delete draft contract."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract de șters",
        "total_value": 5000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/pipeline/contracts/{contract_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_sign_contract(auth_client, sample_contact):
    """F031: Sign contract."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract de semnat",
        "total_value": 75000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.post(f"/api/v1/pipeline/contracts/{contract_id}/sign", json={
        "signed_date": "2026-04-01T10:00:00Z",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "signed"
    assert data["signed_date"] is not None


@pytest.mark.asyncio
async def test_terminate_contract(auth_client, sample_contact):
    """F035: Terminate contract."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract de reziliat",
        "total_value": 50000.0,
    })
    contract_id = resp.json()["data"]["id"]

    # Sign first
    await auth_client.post(f"/api/v1/pipeline/contracts/{contract_id}/sign", json={})

    # Terminate
    resp = await auth_client.post(f"/api/v1/pipeline/contracts/{contract_id}/terminate", json={
        "termination_reason": "Client a renunțat la proiect.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "terminated"


@pytest.mark.asyncio
async def test_billing_schedule(auth_client, sample_contact):
    """F035: Add billing schedule to contract."""
    resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract cu grafic facturare",
        "total_value": 90000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.post(f"/api/v1/pipeline/contracts/{contract_id}/billing", json={
        "installment_number": 1,
        "description": "Avans 30%",
        "amount": 27000.0,
        "due_date": "2026-04-15T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["installment_number"] == 1
    assert data["amount"] == 27000.0
    assert data["is_invoiced"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# SALES KPI & ANALYTICS — F029, F037, F058
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sales_kpi(auth_client, sample_contact):
    """F058: Sales KPI dashboard."""
    resp = await auth_client.get("/api/v1/pipeline/kpi/sales")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_contacts" in data
    assert "total_opportunities" in data
    assert "pipeline_value" in data
    assert "total_offers" in data
    assert "total_contracts" in data
    assert "conversion_rate" in data
    assert "funnel" in data
    assert data["currency"] == "RON"


@pytest.mark.asyncio
async def test_offer_analytics(auth_client, sample_contact):
    """F029: Offers analytics."""
    # Create some offers
    await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă analytics 1",
        "line_items": [{"description": "Item", "quantity": 1, "unit_price": 1000.0}],
    })

    resp = await auth_client.get("/api/v1/pipeline/analytics/offers")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_offers" in data
    assert "offers_by_status" in data
    assert "conversion_rate" in data
    assert "avg_offer_value" in data


@pytest.mark.asyncio
async def test_contract_analytics(auth_client, sample_contact):
    """F037: Contracts analytics."""
    await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract analytics",
        "total_value": 30000.0,
    })

    resp = await auth_client.get("/api/v1/pipeline/analytics/contracts")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_contracts" in data
    assert "contracts_by_status" in data
    assert "termination_rate" in data


# ═══════════════════════════════════════════════════════════════════════════════
# F023/F033 — Document Generation
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_generate_offer_document(auth_client, sample_contact):
    """F023: Generate document from offer."""
    offer_resp = await auth_client.post("/api/v1/pipeline/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Doc Gen Test Offer",
        "validity_days": 30,
        "line_items": [
            {"description": "Service A", "quantity": 1, "unit_price": 1000, "vat_rate": 0.19}
        ],
    })
    assert offer_resp.status_code == 201
    offer_id = offer_resp.json()["data"]["id"]

    resp = await auth_client.post(
        f"/api/v1/pipeline/offers/{offer_id}/generate-document",
        json={"format": "json", "include_line_items": True, "include_terms": True},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["entity_type"] == "offer"
    assert "content" in data
    assert data["content"]["title"] == "Doc Gen Test Offer"


@pytest.mark.asyncio
async def test_generate_contract_document(auth_client, sample_contact):
    """F033: Generate document from contract."""
    contract_resp = await auth_client.post("/api/v1/pipeline/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Doc Gen Test Contract",
        "total_value": 50000.0,
    })
    assert contract_resp.status_code == 201
    contract_id = contract_resp.json()["data"]["id"]

    resp = await auth_client.post(
        f"/api/v1/pipeline/contracts/{contract_id}/generate-document",
        json={"format": "json"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["entity_type"] == "contract"
    assert data["content"]["title"] == "Doc Gen Test Contract"


@pytest.mark.asyncio
async def test_generate_document_not_found(auth_client):
    """F023: Generate document for non-existent offer returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await auth_client.post(
        f"/api/v1/pipeline/offers/{fake_id}/generate-document",
        json={"format": "json"},
    )
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F049 — Simplified Offer Flow
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_simplified_offer(auth_client, sample_contact):
    """F049: Quick offer creation with minimal fields."""
    resp = await auth_client.post("/api/v1/pipeline/offers/quick", json={
        "contact_id": sample_contact["id"],
        "title": "Quick Offer",
        "total_value": 15000.0,
        "currency": "RON",
        "notes": "Quick test",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Quick Offer"
    assert data["status"] == "draft"
    assert data["subtotal"] == 15000.0


@pytest.mark.asyncio
async def test_simplified_offer_bad_contact(auth_client):
    """F049: Quick offer with invalid contact returns 400."""
    resp = await auth_client.post("/api/v1/pipeline/offers/quick", json={
        "contact_id": str(uuid.uuid4()),
        "title": "Bad Contact Offer",
        "total_value": 1000.0,
    })
    assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH REQUIRED
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_pipeline_require_auth(client):
    """All Pipeline endpoints require authentication."""
    resp = await client.get("/api/v1/pipeline/offers")
    assert resp.status_code == 403

    resp = await client.get("/api/v1/pipeline/opportunities")
    assert resp.status_code == 403

    resp = await client.get("/api/v1/pipeline/activities")
    assert resp.status_code == 403

    resp = await client.get("/api/v1/pipeline/board")
    assert resp.status_code == 403
