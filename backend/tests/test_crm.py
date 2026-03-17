"""
Tests for CRM module endpoints — F001–F005, F007, F010, F012, F016, F018.

Tests cover: Contacts CRUD, Interactions, Products, ProductCategories,
Properties, EnergyProfiles, WorkHistory, DuplicateCheck, Segmentation.
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


@pytest_asyncio.fixture
async def sample_property(auth_client, sample_contact):
    """Create a sample property for a contact."""
    resp = await auth_client.post(
        f"/api/v1/crm/contacts/{sample_contact['id']}/properties",
        json={
            "contact_id": sample_contact["id"],
            "name": "Bloc A1 — Sector 3",
            "property_type": "bloc_panou_prefabricat",
            "address": "Str. Energiei 42",
            "city": "București",
            "county": "București",
            "total_area_sqm": 2500.0,
            "heated_area_sqm": 2200.0,
            "floors_count": 10,
            "year_built": 1975,
            "structure_material": "panou prefabricat",
            "energy_class": "E",
        },
    )
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
# F005: DUPLICATE CHECK
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_duplicate_check_by_cui(auth_client, sample_contact):
    """F005: Detect duplicate by CUI."""
    resp = await auth_client.post("/api/v1/crm/contacts/check-duplicates", json={
        "company_name": "Another Company",
        "cui": "RO12345678",  # Same CUI as sample_contact
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["has_duplicates"] is True
    assert len(data["matches"]) >= 1
    assert data["matches"][0]["match_field"] == "cui"


@pytest.mark.asyncio
async def test_duplicate_check_no_match(auth_client, sample_contact):
    """F005: No duplicates found."""
    resp = await auth_client.post("/api/v1/crm/contacts/check-duplicates", json={
        "company_name": "Unique Company",
        "cui": "RO00000000",
        "email": "unique@company.ro",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["has_duplicates"] is False


@pytest.mark.asyncio
async def test_duplicate_check_by_email(auth_client, sample_contact):
    """F005: Detect duplicate by email."""
    resp = await auth_client.post("/api/v1/crm/contacts/check-duplicates", json={
        "company_name": "Email Dup",
        "email": "contact@bahn.ro",  # Same email as sample_contact
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["has_duplicates"] is True


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
# F007: PRODUCTS & CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_product(auth_client):
    """F007: Create a product."""
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
    """F007: Create a sub-article (hierarchic)."""
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
    """F007: List products."""
    resp = await auth_client.get("/api/v1/crm/products")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_product(auth_client, sample_product):
    """F007: Update product price (tracks history)."""
    product_id = sample_product["id"]
    resp = await auth_client.put(f"/api/v1/crm/products/{product_id}", json={
        "unit_price": 175.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["unit_price"] == 175.0


@pytest.mark.asyncio
async def test_delete_product(auth_client, sample_product):
    """F007: Soft-delete product."""
    product_id = sample_product["id"]
    resp = await auth_client.delete(f"/api/v1/crm/products/{product_id}")
    assert resp.status_code == 204


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
# F010: PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_property(auth_client, sample_contact):
    """F010: Create a property for a contact."""
    contact_id = sample_contact["id"]
    resp = await auth_client.post(f"/api/v1/crm/contacts/{contact_id}/properties", json={
        "contact_id": contact_id,
        "name": "Bloc B2 — Sector 6",
        "property_type": "bloc_caramida",
        "city": "București",
        "total_area_sqm": 1800.0,
        "year_built": 1985,
        "energy_class": "D",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Bloc B2 — Sector 6"
    assert data["property_type"] == "bloc_caramida"
    assert data["total_area_sqm"] == 1800.0


@pytest.mark.asyncio
async def test_list_properties(auth_client, sample_contact, sample_property):
    """F010: List properties for a contact."""
    contact_id = sample_contact["id"]
    resp = await auth_client.get(f"/api/v1/crm/contacts/{contact_id}/properties")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_property(auth_client, sample_property):
    """F010: Get property detail."""
    prop_id = sample_property["id"]
    resp = await auth_client.get(f"/api/v1/crm/properties/{prop_id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "Bloc A1 — Sector 3"
    assert data["year_built"] == 1975


@pytest.mark.asyncio
async def test_update_property(auth_client, sample_property):
    """F010: Update a property."""
    prop_id = sample_property["id"]
    resp = await auth_client.put(f"/api/v1/crm/properties/{prop_id}", json={
        "year_renovated": 2020,
        "energy_class": "C",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["year_renovated"] == 2020
    assert data["energy_class"] == "C"


@pytest.mark.asyncio
async def test_delete_property(auth_client, sample_property):
    """F010: Soft-delete a property."""
    prop_id = sample_property["id"]
    resp = await auth_client.delete(f"/api/v1/crm/properties/{prop_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F012: ENERGY PROFILE
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_energy_profile(auth_client, sample_property):
    """F012: Create energy profile for a property."""
    prop_id = sample_property["id"]
    resp = await auth_client.put(f"/api/v1/crm/properties/{prop_id}/energy-profile", json={
        "u_value_walls": 1.2,
        "u_value_windows": 2.5,
        "u_value_treated_glass": 0.3,
        "hvac_type": "centrală termică gaz",
        "hvac_capacity_kw": 150.0,
        "annual_consumption_kwh": 250000.0,
        "climate_zone": "III",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["u_value_walls"] == 1.2
    assert data["u_value_treated_glass"] == 0.3
    assert data["property_id"] == prop_id


@pytest.mark.asyncio
async def test_get_energy_profile(auth_client, sample_property):
    """F012: Get energy profile (create first, then get)."""
    prop_id = sample_property["id"]
    # Create
    await auth_client.put(f"/api/v1/crm/properties/{prop_id}/energy-profile", json={
        "u_value_walls": 1.5,
    })
    # Get
    resp = await auth_client.get(f"/api/v1/crm/properties/{prop_id}/energy-profile")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["u_value_walls"] == 1.5


@pytest.mark.asyncio
async def test_energy_calculator(auth_client):
    """F012: Energy savings calculator."""
    resp = await auth_client.post("/api/v1/crm/energy/calculator", json={
        "total_area_sqm": 100.0,
        "u_value_current": 1.5,
        "u_value_proposed": 0.3,
        "heating_degree_days": 3000.0,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["savings_kwh"] > 0
    assert data["savings_percent"] > 0
    assert data["estimated_co2_reduction_kg"] > 0
    # Check math: Q = U * A * HDD * 24 / 1000
    # current: 1.5 * 100 * 3000 * 24 / 1000 = 10800
    # proposed: 0.3 * 100 * 3000 * 24 / 1000 = 2160
    # savings: 8640
    assert data["current_loss_kwh"] == 10800.0
    assert data["proposed_loss_kwh"] == 2160.0
    assert data["savings_kwh"] == 8640.0


# ═══════════════════════════════════════════════════════════════════════════════
# F016: WORK HISTORY
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_work_history(auth_client, sample_property):
    """F016: Add work history entry."""
    prop_id = sample_property["id"]
    resp = await auth_client.post(f"/api/v1/crm/properties/{prop_id}/work-history", json={
        "title": "Reabilitare termică fațadă",
        "work_type": "termoizolație",
        "performed_by": "BAHN S.R.L.",
        "start_date": "2024-06-01T00:00:00Z",
        "end_date": "2024-09-30T00:00:00Z",
        "cost": 150000.0,
        "currency": "RON",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Reabilitare termică fațadă"
    assert data["cost"] == 150000.0


@pytest.mark.asyncio
async def test_list_work_history(auth_client, sample_property):
    """F016: List work history."""
    prop_id = sample_property["id"]
    # Create entry
    await auth_client.post(f"/api/v1/crm/properties/{prop_id}/work-history", json={
        "title": "Înlocuire ferestre",
        "work_type": "tâmplărie",
    })

    resp = await auth_client.get(f"/api/v1/crm/properties/{prop_id}/work-history")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_work_history(auth_client, sample_property):
    """F016: Update work history entry."""
    prop_id = sample_property["id"]
    resp = await auth_client.post(f"/api/v1/crm/properties/{prop_id}/work-history", json={
        "title": "Lucrare inițială",
    })
    entry_id = resp.json()["data"]["id"]

    resp = await auth_client.put(f"/api/v1/crm/work-history/{entry_id}", json={
        "title": "Lucrare actualizată",
        "cost": 50000.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Lucrare actualizată"
    assert resp.json()["data"]["cost"] == 50000.0


@pytest.mark.asyncio
async def test_delete_work_history(auth_client, sample_property):
    """F016: Delete work history entry."""
    prop_id = sample_property["id"]
    resp = await auth_client.post(f"/api/v1/crm/properties/{prop_id}/work-history", json={
        "title": "De șters",
    })
    entry_id = resp.json()["data"]["id"]

    resp = await auth_client.delete(f"/api/v1/crm/work-history/{entry_id}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F018: SEGMENTATION FILTERING
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_filter_contacts_by_city(auth_client, sample_contact):
    """F018: Filter contacts by city."""
    resp = await auth_client.get("/api/v1/crm/contacts?city=București")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_filter_contacts_by_county(auth_client, sample_contact):
    """F018: Filter contacts by county."""
    resp = await auth_client.get("/api/v1/crm/contacts?county=București")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH REQUIRED
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_contacts_require_auth(client):
    """All CRM endpoints require authentication."""
    resp = await client.get("/api/v1/crm/contacts")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# F004 — Import / Export / Merge
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_import_contacts(auth_client):
    """F004: Bulk import contacts."""
    resp = await auth_client.post("/api/v1/crm/contacts/import", json={
        "rows": [
            {"company_name": "Import Co 1", "cui": "RO11111111", "city": "Cluj"},
            {"company_name": "Import Co 2", "email": "import2@test.ro"},
        ],
        "skip_duplicates": True,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total_rows"] == 2
    assert data["imported"] == 2
    assert data["skipped_duplicates"] == 0


@pytest.mark.asyncio
async def test_import_contacts_skip_duplicates(auth_client, sample_contact):
    """F004: Import skips duplicates by CUI."""
    resp = await auth_client.post("/api/v1/crm/contacts/import", json={
        "rows": [
            {"company_name": "Dup Company", "cui": "RO12345678"},  # same CUI as sample_contact
        ],
        "skip_duplicates": True,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["skipped_duplicates"] == 1
    assert data["imported"] == 0


@pytest.mark.asyncio
async def test_export_contacts(auth_client, sample_contact):
    """F004: Export contacts with filters."""
    resp = await auth_client.post("/api/v1/crm/contacts/export", json={
        "format": "json",
        "stage": "prospect",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_merge_contacts(auth_client):
    """F004: Merge two contacts."""
    # Create two contacts
    resp1 = await auth_client.post("/api/v1/crm/contacts", json={
        "company_name": "Source Corp", "cui": "RO99999991", "city": "Sibiu",
    })
    source_id = resp1.json()["data"]["id"]

    resp2 = await auth_client.post("/api/v1/crm/contacts", json={
        "company_name": "Target Corp", "cui": "RO99999992",
    })
    target_id = resp2.json()["data"]["id"]

    # Merge source into target, taking city from source
    resp = await auth_client.post("/api/v1/crm/contacts/merge", json={
        "source_id": source_id,
        "target_id": target_id,
        "fields_from_source": ["city"],
    })
    assert resp.status_code == 200
    merged = resp.json()["data"]
    assert merged["id"] == target_id
    assert merged["city"] == "Sibiu"

    # Source should be soft-deleted
    resp = await auth_client.get(f"/api/v1/crm/contacts/{source_id}")
    assert resp.status_code == 404
