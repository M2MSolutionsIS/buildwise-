"""
Tests for RM (Resource Management) module — F107–F122 P0 endpoints.

Covers: Employees CRUD, HR Planning, Leaves, Equipment,
Materials, Procurement, Resource Allocation, Budget, Consumption, Efficiency.
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _auth_headers(user_id: uuid.UUID, org_id: uuid.UUID) -> dict:
    token = create_access_token({
        "sub": str(user_id),
        "org": str(org_id),
        "roles": ["admin"],
    })
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_client(client, test_user, test_org):
    headers = _auth_headers(test_user.id, test_org.id)
    client.headers.update(headers)
    return client


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def sample_employee(auth_client):
    resp = await auth_client.post("/api/v1/rm/employees", json={
        "first_name": "Andrei",
        "last_name": "Ionescu",
        "email": "andrei@test.ro",
        "phone": "+40700000001",
        "position": "Inginer",
        "department": "Tehnic",
        "cost_center": "CC-01",
        "contract_type": "full_time",
        "hire_date": "2024-01-15T00:00:00Z",
        "gross_salary": 8000.0,
        "hourly_rate": 47.62,
        "skills": ["AutoCAD", "BIM"],
        "qualifications": ["Ing. construcții"],
    })
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest_asyncio.fixture
async def sample_project(auth_client):
    """Create a project for allocation tests."""
    resp = await auth_client.post("/api/v1/pm/projects", json={
        "name": "Proiect Reabilitare",
        "project_number": "PR-001",
        "project_type": "client",
    })
    assert resp.status_code == 201
    return resp.json()["data"]


# ═══════════════════════════════════════════════════════════════════════════════
# F107 — Employee CRUD
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_employee(auth_client):
    resp = await auth_client.post("/api/v1/rm/employees", json={
        "first_name": "Maria",
        "last_name": "Popescu",
        "position": "Manager",
        "department": "Vânzări",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["first_name"] == "Maria"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_employees(auth_client, sample_employee):
    resp = await auth_client.get("/api/v1/rm/employees")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_employee(auth_client, sample_employee):
    emp_id = sample_employee["id"]
    resp = await auth_client.get(f"/api/v1/rm/employees/{emp_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["first_name"] == "Andrei"


@pytest.mark.asyncio
async def test_update_employee(auth_client, sample_employee):
    emp_id = sample_employee["id"]
    resp = await auth_client.put(f"/api/v1/rm/employees/{emp_id}", json={
        "position": "Senior Inginer",
        "gross_salary": 10000.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["position"] == "Senior Inginer"


@pytest.mark.asyncio
async def test_delete_employee(auth_client, sample_employee):
    emp_id = sample_employee["id"]
    resp = await auth_client.delete(f"/api/v1/rm/employees/{emp_id}")
    assert resp.status_code == 200
    # Verify soft-deleted
    resp2 = await auth_client.get(f"/api/v1/rm/employees/{emp_id}")
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_filter_employees_by_department(auth_client, sample_employee):
    resp = await auth_client.get("/api/v1/rm/employees?department=Tehnic")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_search_employees(auth_client, sample_employee):
    resp = await auth_client.get("/api/v1/rm/employees?search=Andrei")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F108 — HR Planning
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_hr_planning_crud(auth_client):
    # Create
    resp = await auth_client.post("/api/v1/rm/hr-planning", json={
        "entry_type": "hire",
        "position": "Dezvoltator",
        "department": "IT",
        "target_date": "2026-06-01T00:00:00Z",
        "description": "Angajare dezvoltator React",
    })
    assert resp.status_code == 201
    entry = resp.json()["data"]
    assert entry["entry_type"] == "hire"
    assert entry["status"] == "open"

    # List
    resp = await auth_client.get("/api/v1/rm/hr-planning")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await auth_client.put(f"/api/v1/rm/hr-planning/{entry['id']}", json={
        "status": "filled",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "filled"


# ═══════════════════════════════════════════════════════════════════════════════
# F109 — Leaves / Availability
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_leaves_crud(auth_client, sample_employee):
    emp_id = sample_employee["id"]

    # Create leave
    resp = await auth_client.post("/api/v1/rm/leaves", json={
        "employee_id": emp_id,
        "leave_type": "annual",
        "start_date": "2026-07-01T00:00:00Z",
        "end_date": "2026-07-15T00:00:00Z",
        "reason": "Concediu de odihnă",
    })
    assert resp.status_code == 201
    leave = resp.json()["data"]
    assert leave["status"] == "pending"

    # List leaves
    resp = await auth_client.get(f"/api/v1/rm/leaves?employee_id={emp_id}")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Approve
    resp = await auth_client.put(f"/api/v1/rm/leaves/{leave['id']}", json={
        "status": "approved",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_check_availability(auth_client, sample_employee):
    emp_id = sample_employee["id"]

    # Create leave first
    await auth_client.post("/api/v1/rm/leaves", json={
        "employee_id": emp_id,
        "leave_type": "annual",
        "start_date": "2026-08-01T00:00:00Z",
        "end_date": "2026-08-10T00:00:00Z",
    })

    # Check availability overlapping
    resp = await auth_client.get(
        f"/api/v1/rm/employees/{emp_id}/availability"
        f"?start_date=2026-08-05T00:00:00Z&end_date=2026-08-12T00:00:00Z"
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["available"] is False
    assert len(data["conflicting_leaves"]) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Equipment
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_equipment_crud(auth_client):
    # Create
    resp = await auth_client.post("/api/v1/rm/equipment", json={
        "name": "Macara Turn",
        "code": "EQ-001",
        "category": "Utilaje grele",
        "manufacturer": "Liebherr",
        "daily_rate": 500.0,
    })
    assert resp.status_code == 201
    eq = resp.json()["data"]
    assert eq["name"] == "Macara Turn"
    assert eq["status"] == "available"

    # Get
    resp = await auth_client.get(f"/api/v1/rm/equipment/{eq['id']}")
    assert resp.status_code == 200

    # Update
    resp = await auth_client.put(f"/api/v1/rm/equipment/{eq['id']}", json={
        "status": "allocated",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "allocated"

    # Delete
    resp = await auth_client.delete(f"/api/v1/rm/equipment/{eq['id']}")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F114 — Material Stock
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_materials_crud(auth_client):
    # Create
    resp = await auth_client.post("/api/v1/rm/materials", json={
        "name": "Ciment Portland",
        "code": "MAT-001",
        "unit_of_measure": "kg",
        "current_quantity": 5000,
        "minimum_quantity": 1000,
        "unit_cost": 0.5,
        "warehouse": "Depozit Central",
    })
    assert resp.status_code == 201
    mat = resp.json()["data"]
    assert mat["is_below_minimum"] is False
    assert mat["total_value"] == 2500.0

    # Update with low stock
    resp = await auth_client.put(f"/api/v1/rm/materials/{mat['id']}", json={
        "current_quantity": 500,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["is_below_minimum"] is True

    # Filter below minimum
    resp = await auth_client.get("/api/v1/rm/materials?below_minimum=true")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F112, F113 — Procurement
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_procurement_crud(auth_client):
    # Create order with line items
    resp = await auth_client.post("/api/v1/rm/procurement", json={
        "currency": "RON",
        "expected_delivery": "2026-05-01T00:00:00Z",
        "line_items": [
            {"description": "Ciment", "quantity": 100, "unit_of_measure": "kg", "unit_price": 0.5},
            {"description": "Cărămidă", "quantity": 500, "unit_of_measure": "buc", "unit_price": 2.0},
        ],
    })
    assert resp.status_code == 201
    order = resp.json()["data"]
    assert order["total_amount"] == 1050.0
    assert order["status"] == "draft"
    assert order["order_number"].startswith("PO-")

    # List
    resp = await auth_client.get("/api/v1/rm/procurement")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Get detail
    resp = await auth_client.get(f"/api/v1/rm/procurement/{order['id']}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]["line_items"]) == 2

    # Update status
    resp = await auth_client.put(f"/api/v1/rm/procurement/{order['id']}", json={
        "status": "approved",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"


@pytest.mark.asyncio
async def test_procurement_documents(auth_client):
    """F113: Add invoice/NIR to procurement order."""
    # Create order first
    order_resp = await auth_client.post("/api/v1/rm/procurement", json={
        "line_items": [
            {"description": "Material X", "quantity": 10, "unit_of_measure": "buc", "unit_price": 100},
        ],
    })
    order_id = order_resp.json()["data"]["id"]

    # Add invoice document
    resp = await auth_client.post(f"/api/v1/rm/procurement/{order_id}/documents", json={
        "order_id": order_id,
        "document_type": "invoice",
        "document_number": "FV-001",
        "document_date": "2026-04-01T00:00:00Z",
        "amount": 1000.0,
    })
    assert resp.status_code == 201
    doc = resp.json()["data"]
    assert doc["document_type"] == "invoice"

    # Add NIR
    resp = await auth_client.post(f"/api/v1/rm/procurement/{order_id}/documents", json={
        "order_id": order_id,
        "document_type": "nir",
        "document_number": "NIR-001",
        "document_date": "2026-04-02T00:00:00Z",
        "amount": 1000.0,
    })
    assert resp.status_code == 201

    # List documents
    resp = await auth_client.get(f"/api/v1/rm/procurement/{order_id}/documents")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# F117 — Resource Allocation
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_allocation_crud(auth_client, sample_employee, sample_project):
    emp_id = sample_employee["id"]
    proj_id = sample_project["id"]

    # Create allocation
    resp = await auth_client.post("/api/v1/rm/allocations", json={
        "resource_type": "employee",
        "employee_id": emp_id,
        "project_id": proj_id,
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-06-30T00:00:00Z",
        "allocated_hours": 500,
        "planned_cost": 25000.0,
        "allocation_percent": 100.0,
    })
    assert resp.status_code == 201
    alloc = resp.json()["data"]
    assert alloc["status"] == "planned"
    assert alloc["has_conflict"] is False

    # Update with actuals
    resp = await auth_client.put(f"/api/v1/rm/allocations/{alloc['id']}", json={
        "actual_hours": 200,
        "actual_cost": 10000.0,
        "status": "active",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["actual_hours"] == 200

    # List
    resp = await auth_client.get(f"/api/v1/rm/allocations?project_id={proj_id}")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Delete
    resp = await auth_client.delete(f"/api/v1/rm/allocations/{alloc['id']}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_allocation_conflict_detection(auth_client, sample_employee, sample_project):
    """F117: Detect conflicts when employee is double-allocated."""
    emp_id = sample_employee["id"]
    proj_id = sample_project["id"]

    # First allocation
    await auth_client.post("/api/v1/rm/allocations", json={
        "resource_type": "employee",
        "employee_id": emp_id,
        "project_id": proj_id,
        "start_date": "2026-05-01T00:00:00Z",
        "end_date": "2026-05-31T00:00:00Z",
        "allocated_hours": 168,
        "allocation_percent": 100.0,
    })

    # Create second project
    p2 = await auth_client.post("/api/v1/pm/projects", json={
        "name": "Proiect 2",
        "project_number": "PR-002",
    })
    proj2_id = p2.json()["data"]["id"]

    # Second allocation — same employee, overlapping dates
    resp = await auth_client.post("/api/v1/rm/allocations", json={
        "resource_type": "employee",
        "employee_id": emp_id,
        "project_id": proj2_id,
        "start_date": "2026-05-15T00:00:00Z",
        "end_date": "2026-06-15T00:00:00Z",
        "allocated_hours": 168,
        "allocation_percent": 100.0,
    })
    assert resp.status_code == 201
    alloc = resp.json()["data"]
    assert alloc["has_conflict"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# F118 — Resource Consumption
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_resource_consumption(auth_client, sample_employee, sample_project):
    """F118: Allocated vs actual consumption for project."""
    emp_id = sample_employee["id"]
    proj_id = sample_project["id"]

    # Create allocation
    alloc_resp = await auth_client.post("/api/v1/rm/allocations", json={
        "resource_type": "employee",
        "employee_id": emp_id,
        "project_id": proj_id,
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-04-30T00:00:00Z",
        "allocated_hours": 168,
        "planned_cost": 8000.0,
    })
    alloc_id = alloc_resp.json()["data"]["id"]
    # Update with actuals
    await auth_client.put(f"/api/v1/rm/allocations/{alloc_id}", json={
        "actual_hours": 150,
        "actual_cost": 7000.0,
    })

    resp = await auth_client.get(f"/api/v1/rm/projects/{proj_id}/consumption")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_allocated_hours"] == 168
    assert data["total_actual_hours"] == 150
    assert data["utilization_percent"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# F115 — Budget / Financial Planning
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_budget_crud(auth_client):
    """F115: Budget CRUD with variance calculation."""
    # Create
    resp = await auth_client.post("/api/v1/rm/budgets", json={
        "cost_center": "CC-01",
        "category": "Salarii",
        "period_month": 4,
        "period_year": 2026,
        "budgeted_amount": 50000.0,
        "actual_amount": 45000.0,
    })
    assert resp.status_code == 201
    entry = resp.json()["data"]
    assert entry["variance"] == 5000.0

    # List
    resp = await auth_client.get("/api/v1/rm/budgets?cost_center=CC-01")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await auth_client.put(f"/api/v1/rm/budgets/{entry['id']}", json={
        "actual_amount": 52000.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["variance"] == -2000.0


@pytest.mark.asyncio
async def test_cost_analysis(auth_client):
    """F116: Cost analysis per cost center."""
    # Create entries
    await auth_client.post("/api/v1/rm/budgets", json={
        "cost_center": "CC-01",
        "category": "Salarii",
        "period_month": 4,
        "period_year": 2026,
        "budgeted_amount": 50000.0,
        "actual_amount": 45000.0,
    })
    await auth_client.post("/api/v1/rm/budgets", json={
        "cost_center": "CC-01",
        "category": "Materiale",
        "period_month": 4,
        "period_year": 2026,
        "budgeted_amount": 20000.0,
        "actual_amount": 22000.0,
    })

    resp = await auth_client.get("/api/v1/rm/cost-analysis?cost_center=CC-01")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["cost_center"] == "CC-01"
    assert data[0]["total_budgeted"] == 70000.0


# ═══════════════════════════════════════════════════════════════════════════════
# F121 — Resource Utilization
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_resource_utilization(auth_client, sample_employee):
    """F121: Resource utilization report."""
    resp = await auth_client.get("/api/v1/rm/utilization")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert "employee_name" in data[0]
    assert "utilization_percent" in data[0]
