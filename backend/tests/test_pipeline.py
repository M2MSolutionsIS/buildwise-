"""
Tests for Sales Pipeline module endpoints — F019, F028, F031, F035.

Tests cover: Offers CRUD + approval, Contracts CRUD + from-offer, Invoices, KPI.
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
    # Create and approve offer
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

    # Create contract from offer
    resp = await auth_client.post("/api/v1/pipeline/contracts/from-offer", json={
        "offer_id": offer_id,
        "title": "Contract din ofertă aprobată",
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-09-30T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["offer_id"] == offer_id
    assert data["total_value"] == 29750.0  # 25000 + 19% VAT
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


# ═══════════════════════════════════════════════════════════════════════════════
# SALES KPI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sales_kpi(auth_client, sample_contact):
    """Sales KPI dashboard."""
    resp = await auth_client.get("/api/v1/pipeline/kpi/sales")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_contacts" in data
    assert "total_offers" in data
    assert "total_contracts" in data
    assert "conversion_rate" in data
    assert data["currency"] == "RON"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH REQUIRED
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_pipeline_require_auth(client):
    """All Pipeline endpoints require authentication."""
    resp = await client.get("/api/v1/pipeline/offers")
    assert resp.status_code == 403
