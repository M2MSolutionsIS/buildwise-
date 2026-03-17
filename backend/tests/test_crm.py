"""
Tests for CRM module endpoints — F001–F024 P0 coverage.

Tests cover: Contacts CRUD, Interactions, Products, Offers, Contracts, Invoices, KPI.
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
    """Create a sample contact for tests."""
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
        "persons": [
            {
                "first_name": "Ion",
                "last_name": "Popescu",
                "role": "Director",
                "email": "ion@bahn.ro",
                "is_primary": True,
            }
        ],
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
# F001: CONTACTS CRUD
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_contact(auth_client):
    """F001: Create a contact with persons."""
    resp = await auth_client.post("/api/v1/crm/contacts", json={
        "company_name": "Test Company SRL",
        "cui": "RO99999999",
        "stage": "prospect",
        "contact_type": "pj",
        "city": "Cluj-Napoca",
        "gdpr_consent": True,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["company_name"] == "Test Company SRL"
    assert data["cui"] == "RO99999999"
    assert data["stage"] == "prospect"


@pytest.mark.asyncio
async def test_list_contacts(auth_client, sample_contact):
    """F001: List contacts with pagination."""
    resp = await auth_client.get("/api/v1/crm/contacts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["total"] >= 1
    assert len(body["data"]) >= 1


@pytest.mark.asyncio
async def test_list_contacts_search(auth_client, sample_contact):
    """F001: Search contacts by name."""
    resp = await auth_client.get("/api/v1/crm/contacts?search=BAHN")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_list_contacts_filter_stage(auth_client, sample_contact):
    """F003: Filter contacts by stage."""
    resp = await auth_client.get("/api/v1/crm/contacts?stage=prospect")
    assert resp.status_code == 200
    for c in resp.json()["data"]:
        assert c["stage"] == "prospect"


@pytest.mark.asyncio
async def test_get_contact(auth_client, sample_contact):
    """F001: Get contact detail."""
    contact_id = sample_contact["id"]
    resp = await auth_client.get(f"/api/v1/crm/contacts/{contact_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == contact_id
    assert data["company_name"] == "BAHN S.R.L."
    assert len(data["persons"]) == 1
    assert data["persons"][0]["first_name"] == "Ion"


@pytest.mark.asyncio
async def test_update_contact(auth_client, sample_contact):
    """F001/F003: Update contact, change stage."""
    contact_id = sample_contact["id"]
    resp = await auth_client.put(f"/api/v1/crm/contacts/{contact_id}", json={
        "stage": "active",
        "city": "Timișoara",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stage"] == "active"
    assert data["city"] == "Timișoara"


@pytest.mark.asyncio
async def test_delete_contact(auth_client, sample_contact):
    """F001: Soft-delete a contact."""
    contact_id = sample_contact["id"]
    resp = await auth_client.delete(f"/api/v1/crm/contacts/{contact_id}")
    assert resp.status_code == 204

    # Verify it's gone from list
    resp = await auth_client.get(f"/api/v1/crm/contacts/{contact_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_contact_not_found(auth_client):
    """F001: 404 for non-existent contact."""
    fake_id = str(uuid.uuid4())
    resp = await auth_client.get(f"/api/v1/crm/contacts/{fake_id}")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F001: CONTACT PERSONS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_add_contact_person(auth_client, sample_contact):
    """F001: Add a person to contact."""
    contact_id = sample_contact["id"]
    resp = await auth_client.post(f"/api/v1/crm/contacts/{contact_id}/persons", json={
        "first_name": "Maria",
        "last_name": "Ionescu",
        "role": "Manager",
        "email": "maria@bahn.ro",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["first_name"] == "Maria"


@pytest.mark.asyncio
async def test_update_contact_person(auth_client, sample_contact):
    """F001: Update a contact person."""
    contact_id = sample_contact["id"]
    person_id = sample_contact["persons"][0]["id"]
    resp = await auth_client.put(
        f"/api/v1/crm/contacts/{contact_id}/persons/{person_id}",
        json={"role": "CEO"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "CEO"


@pytest.mark.asyncio
async def test_delete_contact_person(auth_client, sample_contact):
    """F001: Delete a contact person."""
    contact_id = sample_contact["id"]
    person_id = sample_contact["persons"][0]["id"]
    resp = await auth_client.delete(
        f"/api/v1/crm/contacts/{contact_id}/persons/{person_id}"
    )
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F002: INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_interaction(auth_client, sample_contact):
    """F002: Create an interaction for a contact."""
    contact_id = sample_contact["id"]
    resp = await auth_client.post(
        f"/api/v1/crm/contacts/{contact_id}/interactions",
        json={
            "interaction_type": "call",
            "subject": "Discuție inițială",
            "description": "Am discutat despre proiect.",
            "interaction_date": "2026-03-15T10:00:00Z",
            "duration_minutes": 30,
        },
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["interaction_type"] == "call"
    assert data["subject"] == "Discuție inițială"


@pytest.mark.asyncio
async def test_list_interactions(auth_client, sample_contact):
    """F002: List interactions (timeline)."""
    contact_id = sample_contact["id"]
    # Create two interactions
    for itype in ["call", "email"]:
        await auth_client.post(
            f"/api/v1/crm/contacts/{contact_id}/interactions",
            json={
                "interaction_type": itype,
                "subject": f"Test {itype}",
                "interaction_date": "2026-03-15T10:00:00Z",
            },
        )

    resp = await auth_client.get(f"/api/v1/crm/contacts/{contact_id}/interactions")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# F005/F006: PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_product(auth_client):
    """F005: Create a product."""
    resp = await auth_client.post("/api/v1/crm/products", json={
        "name": "Fereastră PVC",
        "code": "FPVC-001",
        "product_type": "product",
        "unit_price": 500.0,
        "unit_of_measure": "buc",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Fereastră PVC"
    assert data["unit_price"] == 500.0


@pytest.mark.asyncio
async def test_create_sub_product(auth_client, sample_product):
    """F006: Create a sub-article (hierarchic)."""
    parent_id = sample_product["id"]
    resp = await auth_client.post("/api/v1/crm/products", json={
        "name": "Sticlă tratată 4mm",
        "code": "STT-001-A",
        "product_type": "product",
        "unit_price": 80.0,
        "parent_product_id": parent_id,
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["parent_product_id"] == parent_id


@pytest.mark.asyncio
async def test_list_products(auth_client, sample_product):
    """F005: List products."""
    resp = await auth_client.get("/api/v1/crm/products")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_product(auth_client, sample_product):
    """F005: Update product price (tracks history)."""
    product_id = sample_product["id"]
    resp = await auth_client.put(f"/api/v1/crm/products/{product_id}", json={
        "unit_price": 175.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["unit_price"] == 175.0


@pytest.mark.asyncio
async def test_delete_product(auth_client, sample_product):
    """F005: Soft-delete product."""
    product_id = sample_product["id"]
    resp = await auth_client.delete(f"/api/v1/crm/products/{product_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F007: PRODUCT CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_product_category_crud(auth_client):
    """F007: Product category CRUD."""
    # Create
    resp = await auth_client.post("/api/v1/crm/product-categories", json={
        "name": "Materiale construcții",
        "sort_order": 1,
    })
    assert resp.status_code == 201
    cat_id = resp.json()["data"]["id"]

    # List
    resp = await auth_client.get("/api/v1/crm/product-categories")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await auth_client.put(f"/api/v1/crm/product-categories/{cat_id}", json={
        "name": "Materiale de construcții",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Materiale de construcții"

    # Delete
    resp = await auth_client.delete(f"/api/v1/crm/product-categories/{cat_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F008/F009/F014/F016: OFFERS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_offer(auth_client, sample_contact, sample_product):
    """F008/F009: Create offer with line items."""
    resp = await auth_client.post("/api/v1/crm/offers", json={
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
async def test_list_offers(auth_client, sample_contact, sample_product):
    """F016: List offers with filtering."""
    # Create an offer first
    await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Test Offer",
        "line_items": [
            {"description": "Item 1", "quantity": 1, "unit_price": 100.0}
        ],
    })

    resp = await auth_client.get("/api/v1/crm/offers")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_offer_approval_flow(auth_client, sample_contact):
    """F014: Submit and approve offer."""
    # Create
    resp = await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă aprobare",
        "line_items": [
            {"description": "Serviciu audit", "quantity": 1, "unit_price": 5000.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    # Submit for approval
    resp = await auth_client.post(f"/api/v1/crm/offers/{offer_id}/submit", json={
        "comment": "Vă rog aprobați.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "pending_approval"

    # Approve
    resp = await auth_client.post(f"/api/v1/crm/offers/{offer_id}/approve", json={
        "approved": True,
        "comment": "Aprobat.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_offer_rejection(auth_client, sample_contact):
    """F014: Reject offer."""
    resp = await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă respingere",
        "line_items": [
            {"description": "Test", "quantity": 1, "unit_price": 100.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    await auth_client.post(f"/api/v1/crm/offers/{offer_id}/submit", json={})

    resp = await auth_client.post(f"/api/v1/crm/offers/{offer_id}/approve", json={
        "approved": False,
        "comment": "Prea scump.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "rejected"


@pytest.mark.asyncio
async def test_update_offer_draft_only(auth_client, sample_contact):
    """F008: Only draft offers can be updated."""
    # Create and submit
    resp = await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Locked Offer",
        "line_items": [
            {"description": "Item", "quantity": 1, "unit_price": 100.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]
    await auth_client.post(f"/api/v1/crm/offers/{offer_id}/submit", json={})

    # Try to update — should fail
    resp = await auth_client.put(f"/api/v1/crm/offers/{offer_id}", json={
        "title": "Updated Title",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_offer(auth_client, sample_contact):
    """F008: Delete draft offer."""
    resp = await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "To Delete",
        "line_items": [
            {"description": "Item", "quantity": 1, "unit_price": 50.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/crm/offers/{offer_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F017/F018/F022: CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_contract(auth_client, sample_contact):
    """F017: Create a contract."""
    resp = await auth_client.post("/api/v1/crm/contracts", json={
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
    """F018: Create contract from approved offer."""
    # Create and approve offer
    resp = await auth_client.post("/api/v1/crm/offers", json={
        "contact_id": sample_contact["id"],
        "title": "Ofertă pentru contract",
        "terms_and_conditions": "Termeni standard BAHN.",
        "line_items": [
            {"description": "Lucrare", "quantity": 1, "unit_price": 25000.0}
        ],
    })
    offer_id = resp.json()["data"]["id"]
    await auth_client.post(f"/api/v1/crm/offers/{offer_id}/submit", json={})
    await auth_client.post(f"/api/v1/crm/offers/{offer_id}/approve", json={
        "approved": True,
    })

    # Create contract from offer
    resp = await auth_client.post("/api/v1/crm/contracts/from-offer", json={
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
    """F022: List contracts."""
    await auth_client.post("/api/v1/crm/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract test",
        "total_value": 10000.0,
    })

    resp = await auth_client.get("/api/v1/crm/contracts")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_contract(auth_client, sample_contact):
    """F017: Update contract (draft only)."""
    resp = await auth_client.post("/api/v1/crm/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract update test",
        "total_value": 10000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.put(f"/api/v1/crm/contracts/{contract_id}", json={
        "total_value": 15000.0,
        "notes": "Actualizat valoare.",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["total_value"] == 15000.0


@pytest.mark.asyncio
async def test_delete_contract(auth_client, sample_contact):
    """F017: Soft-delete draft contract."""
    resp = await auth_client.post("/api/v1/crm/contracts", json={
        "contact_id": sample_contact["id"],
        "title": "Contract de șters",
        "total_value": 5000.0,
    })
    contract_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/crm/contracts/{contract_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F023: SALES KPI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sales_kpi(auth_client, sample_contact):
    """F023: Get sales KPI."""
    resp = await auth_client.get("/api/v1/crm/kpi/sales")
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
async def test_contacts_require_auth(client):
    """All CRM endpoints require authentication."""
    resp = await client.get("/api/v1/crm/contacts")
    assert resp.status_code == 403
