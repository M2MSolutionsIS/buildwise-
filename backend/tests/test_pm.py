"""
Tests for PM module endpoints — all P0 F-codes.

F063 (Project Setup), F069 (WBS), F070 (Gantt/Tasks), F071 (Deviz),
F072 (Timesheets), F073 (Task Status), F074 (Materials), F078 (Progress),
F079 (Work Situations), F080 (Budget), F084 (Risks), F088 (Energy Impact),
F090 (Completed Projects), F091 (P&L), F092 (Cash Flow), F095 (Reports),
F101 (Portfolio), F103 (Close/Cancel), F105 (ML Mapping), F123 (Import),
F125 (Work Tracker), F144 (Wiki), F161 (Energy Portfolio).
"""

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
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


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def auth_client(client, test_user, test_org):
    headers = _auth_headers(test_user.id, test_org.id)
    client.headers.update(headers)
    return client


@pytest_asyncio.fixture
async def sample_project(auth_client):
    """Create a sample project for PM tests."""
    resp = await auth_client.post("/api/v1/pm/projects", json={
        "project_number": "PRJ-2026-001",
        "name": "Reabilitare termică Bloc A1",
        "description": "Proiect pilot eficiență energetică",
        "project_type": "client",
        "budget_allocated": 500000.0,
        "currency": "RON",
        "planned_start_date": "2026-04-01T00:00:00Z",
        "planned_end_date": "2026-12-31T00:00:00Z",
        "tags": ["energie", "pilot"],
    })
    assert resp.status_code == 201
    return resp.json()["data"]


# ═══════════════════════════════════════════════════════════════════════════════
# F063: PROJECT SETUP + F101: PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_project(auth_client):
    """F063: Create project with checklist."""
    resp = await auth_client.post("/api/v1/pm/projects", json={
        "project_number": "PRJ-TEST-001",
        "name": "Test Project",
        "project_type": "internal",
        "kickoff_checklist": {"contract_signed": True, "team_assigned": False},
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["project_number"] == "PRJ-TEST-001"
    assert data["status"] == "draft"
    assert data["kickoff_checklist"]["contract_signed"] is True


@pytest.mark.asyncio
async def test_list_projects_portfolio(auth_client, sample_project):
    """F101: Portfolio view — list projects."""
    resp = await auth_client.get("/api/v1/pm/projects")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_project_detail(auth_client, sample_project):
    """F063: Get project detail."""
    resp = await auth_client.get(f"/api/v1/pm/projects/{sample_project['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Reabilitare termică Bloc A1"


@pytest.mark.asyncio
async def test_update_project(auth_client, sample_project):
    """F078: Update project progress."""
    resp = await auth_client.put(f"/api/v1/pm/projects/{sample_project['id']}", json={
        "percent_complete": 25.0,
        "health_indicator": "green",
        "status": "in_progress",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["percent_complete"] == 25.0
    assert data["health_indicator"] == "green"


@pytest.mark.asyncio
async def test_delete_project(auth_client, sample_project):
    """Soft-delete project."""
    resp = await auth_client.delete(f"/api/v1/pm/projects/{sample_project['id']}")
    assert resp.status_code == 204

    resp = await auth_client.get(f"/api/v1/pm/projects/{sample_project['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_project_not_found(auth_client):
    resp = await auth_client.get(f"/api/v1/pm/projects/{uuid.uuid4()}")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F103: CLOSE / CANCEL PROJECT
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_close_project(auth_client, sample_project):
    """F103: Close project with grace period."""
    resp = await auth_client.post(
        f"/api/v1/pm/projects/{sample_project['id']}/close",
        json={"grace_period_days": 30},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "closing"
    assert data["close_date"] is not None
    assert data["grace_period_end"] is not None


@pytest.mark.asyncio
async def test_cancel_project(auth_client, sample_project):
    """F103: Cancel project with reason."""
    resp = await auth_client.post(
        f"/api/v1/pm/projects/{sample_project['id']}/cancel",
        json={"cancellation_reason": "Client a renunțat la contract"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "cancelled"
    assert data["cancellation_reason"] == "Client a renunțat la contract"


# ═══════════════════════════════════════════════════════════════════════════════
# F069: WBS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_wbs_crud(auth_client, sample_project):
    """F069: Create, list, update, delete WBS nodes."""
    pid = sample_project["id"]

    # Create chapter
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/wbs", json={
        "code": "C01",
        "name": "Lucrări de izolare",
        "node_type": "chapter",
        "level": 0,
    })
    assert resp.status_code == 201
    chapter = resp.json()["data"]

    # Create subchapter
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/wbs", json={
        "code": "C01.1",
        "name": "Izolare fațadă",
        "node_type": "subchapter",
        "parent_id": chapter["id"],
        "level": 1,
    })
    assert resp.status_code == 201

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/wbs")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 2

    # Update
    resp = await auth_client.put(f"/api/v1/pm/wbs/{chapter['id']}", json={
        "name": "Lucrări de termoizolare",
        "budget_allocated": 200000.0,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Lucrări de termoizolare"

    # Delete
    resp = await auth_client.delete(f"/api/v1/pm/wbs/{chapter['id']}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F070, F073: TASKS / GANTT
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_task_crud(auth_client, sample_project):
    """F070/F073: CRUD tasks with status transitions."""
    pid = sample_project["id"]

    # Create
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={
        "title": "Montare schele",
        "planned_start": "2026-04-01T08:00:00Z",
        "planned_end": "2026-04-05T17:00:00Z",
        "estimated_hours": 40,
    })
    assert resp.status_code == 201
    task = resp.json()["data"]
    assert task["status"] == "todo"

    # Update status to in_progress
    resp = await auth_client.put(f"/api/v1/pm/tasks/{task['id']}", json={
        "status": "in_progress",
        "actual_start": "2026-04-01T08:00:00Z",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "in_progress"

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/tasks")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Get detail
    resp = await auth_client.get(f"/api/v1/pm/tasks/{task['id']}")
    assert resp.status_code == 200

    # Delete
    resp = await auth_client.delete(f"/api/v1/pm/tasks/{task['id']}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_task_blocked_requires_reason(auth_client, sample_project):
    """F073: Blocked status requires mandatory reason."""
    pid = sample_project["id"]
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={
        "title": "Task to block",
    })
    task = resp.json()["data"]

    # Try blocking without reason — should fail (422)
    resp = await auth_client.put(f"/api/v1/pm/tasks/{task['id']}", json={
        "status": "blocked",
    })
    assert resp.status_code == 422

    # Block with reason — should succeed
    resp = await auth_client.put(f"/api/v1/pm/tasks/{task['id']}", json={
        "status": "blocked",
        "blocked_reason": "Lipsă materiale",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "blocked"
    assert data["escalated"] is True


@pytest.mark.asyncio
async def test_task_dependencies(auth_client, sample_project):
    """F070: Task dependencies (FS/SS/FF/SF)."""
    pid = sample_project["id"]

    r1 = await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={"title": "Task A"})
    r2 = await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={"title": "Task B"})
    task_a = r1.json()["data"]
    task_b = r2.json()["data"]

    # Add dependency
    resp = await auth_client.post(f"/api/v1/pm/tasks/{task_b['id']}/dependencies", json={
        "depends_on_id": task_a["id"],
        "dependency_type": "finish_to_start",
        "lag_days": 2,
    })
    assert resp.status_code == 201
    dep = resp.json()["data"]

    # Remove dependency
    resp = await auth_client.delete(
        f"/api/v1/pm/tasks/{task_b['id']}/dependencies/{dep['id']}"
    )
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F071, F125: DEVIZ / WORK TRACKER
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_deviz_crud(auth_client, sample_project):
    """F071/F125: Deviz CRUD with auto-total calculation."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/deviz", json={
        "description": "Polistiren expandat 10cm",
        "unit_of_measure": "mp",
        "estimated_quantity": 500,
        "estimated_unit_price_material": 45.0,
        "estimated_unit_price_labor": 25.0,
    })
    assert resp.status_code == 201
    item = resp.json()["data"]
    assert item["estimated_total"] == 500 * (45.0 + 25.0)  # 35000.0

    # Update with actual quantities
    resp = await auth_client.put(f"/api/v1/pm/deviz/{item['id']}", json={
        "actual_quantity": 520.0,
        "actual_unit_price_material": 47.0,
        "actual_unit_price_labor": 27.0,
    })
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["actual_total"] == 520.0 * (47.0 + 27.0)
    assert updated["over_budget_alert"] is True  # Actual > Estimated

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/deviz")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1

    # Delete
    resp = await auth_client.delete(f"/api/v1/pm/deviz/{item['id']}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F072: TIMESHEETS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_timesheet_crud(auth_client, sample_project):
    """F072: Create + approve timesheet."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/timesheets", json={
        "work_date": "2026-04-01T00:00:00Z",
        "hours": 8.0,
        "hourly_rate": 50.0,
        "description": "Montaj schele etaj 1",
    })
    assert resp.status_code == 201
    entry = resp.json()["data"]
    assert entry["hours"] == 8.0
    assert entry["cost"] == 400.0  # 8 * 50
    assert entry["status"] == "draft"

    # Approve
    resp = await auth_client.post(f"/api/v1/pm/timesheets/{entry['id']}/approve")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "approved"

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/timesheets")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# F074: MATERIALS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_materials(auth_client, sample_project):
    """F074: Record material consumption."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/materials", json={
        "material_name": "Polistiren expandat 10cm",
        "unit_of_measure": "mp",
        "planned_quantity": 500,
        "consumed_quantity": 120,
        "unit_price": 45.0,
        "consumption_date": "2026-04-10T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["total_cost"] == 120 * 45.0

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/materials")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# F079: WORK SITUATIONS (SdL)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_work_situations(auth_client, sample_project):
    """F079: CRUD + approve work situations."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/work-situations", json={
        "period_month": 4,
        "period_year": 2026,
        "sdl_number": "SDL-001",
        "contracted_total": 500000.0,
        "executed_current": 50000.0,
        "executed_cumulated": 50000.0,
        "remaining": 450000.0,
    })
    assert resp.status_code == 201
    sdl = resp.json()["data"]
    assert sdl["is_approved"] is False

    # Approve
    resp = await auth_client.post(f"/api/v1/pm/work-situations/{sdl['id']}/approve")
    assert resp.status_code == 200
    assert resp.json()["data"]["is_approved"] is True

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/work-situations")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F084: RISK REGISTER
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_risk_crud(auth_client, sample_project):
    """F084: CRUD risks with auto P×I score."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/risks", json={
        "title": "Întârziere livrare materiale",
        "description": "Furnizorul nu poate livra la termen",
        "probability": "high",
        "impact": "major",
        "mitigation_plan": "Identificare furnizor alternativ",
    })
    assert resp.status_code == 201
    risk = resp.json()["data"]
    assert risk["risk_score"] == 4 * 4  # high(4) × major(4) = 16

    # Update
    resp = await auth_client.put(f"/api/v1/pm/risks/{risk['id']}", json={
        "status": "mitigating",
    })
    assert resp.status_code == 200

    # List
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/risks")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1

    # Delete
    resp = await auth_client.delete(f"/api/v1/pm/risks/{risk['id']}")
    assert resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════════
# F088, F105, F161: ENERGY IMPACT + PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_energy_impact(auth_client, sample_project):
    """F088/F105: Create/update energy impact."""
    pid = sample_project["id"]

    resp = await auth_client.put(f"/api/v1/pm/projects/{pid}/energy-impact", json={
        "pre_kwh_annual": 150000,
        "post_kwh_annual": 90000,
        "actual_kwh_savings": 60000,
        "actual_co2_reduction": 13980,
        "total_area_sqm": 2500,
        "treated_area_sqm": 2200,
        "pre_u_value_avg": 1.8,
        "post_u_value_avg": 0.3,
        "ml_data_mapping": {"model": "energy_predictor", "features": ["u_value", "area"]},
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["actual_kwh_savings"] == 60000

    # Get
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/energy-impact")
    assert resp.status_code == 200
    assert resp.json()["data"]["pre_u_value_avg"] == 1.8


@pytest.mark.asyncio
async def test_energy_portfolio(auth_client, sample_project):
    """F161: Energy portfolio aggregated dashboard."""
    pid = sample_project["id"]

    # Create energy impact first
    await auth_client.put(f"/api/v1/pm/projects/{pid}/energy-impact", json={
        "actual_kwh_savings": 60000,
        "actual_co2_reduction": 13980,
        "treated_area_sqm": 2200,
    })

    resp = await auth_client.get("/api/v1/pm/energy-portfolio")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_kwh_saved"] >= 60000
    assert data["total_projects"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F091, F092: PROJECT FINANCE
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_project_finance_pl(auth_client, sample_project):
    """F091: Project P&L."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/finance", json={
        "entry_type": "cost",
        "category": "materials",
        "period_month": 4,
        "period_year": 2026,
        "forecast_amount": 100000,
        "actual_amount": 95000,
    })
    assert resp.status_code == 201
    entry = resp.json()["data"]
    assert entry["variance"] == -5000  # actual - forecast

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/finance")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_project_cash_flow(auth_client, sample_project):
    """F092: Project Cash Flow."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/cash-flow", json={
        "entry_type": "inflow",
        "description": "Tranșa 1 contract",
        "amount": 150000.0,
        "transaction_date": "2026-04-15T00:00:00Z",
    })
    assert resp.status_code == 201

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/cash-flow")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# F123: IMPORT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_import_job(auth_client, sample_project):
    """F123: Create import job."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/import", json={
        "source_type": "excel",
        "file_name": "deviz_import.xlsx",
        "file_path": "/uploads/deviz_import.xlsx",
    })
    assert resp.status_code == 201
    job = resp.json()["data"]
    assert job["status"] == "pending"
    assert job["source_type"] == "excel"

    # Get job status
    resp = await auth_client.get(f"/api/v1/pm/import-jobs/{job['id']}")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F144: WIKI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_wiki_crud(auth_client, sample_project):
    """F144: Wiki posts + nested comments."""
    pid = sample_project["id"]

    # Create post
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/wiki", json={
        "title": "Decizie fundație",
        "content": "S-a decis utilizarea fundației pe piloți.",
    })
    assert resp.status_code == 201
    post = resp.json()["data"]

    # Add comment
    resp = await auth_client.post(f"/api/v1/pm/wiki/{post['id']}/comments", json={
        "content": "Aprobat de PM.",
    })
    assert resp.status_code == 201
    comment = resp.json()["data"]

    # Add nested reply
    resp = await auth_client.post(f"/api/v1/pm/wiki/{post['id']}/comments", json={
        "parent_comment_id": comment["id"],
        "content": "Confirmat și de inginerul structural.",
    })
    assert resp.status_code == 201

    # List comments
    resp = await auth_client.get(f"/api/v1/pm/wiki/{post['id']}/comments")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 2

    # List posts
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/wiki")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1

    # Update post
    resp = await auth_client.put(f"/api/v1/pm/wiki/{post['id']}", json={
        "title": "Decizie fundație — ACTUALIZAT",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Decizie fundație — ACTUALIZAT"


# ═══════════════════════════════════════════════════════════════════════════════
# F095: PROJECT REPORTS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_project_reports(auth_client, sample_project):
    """F095: Get aggregated project report."""
    pid = sample_project["id"]

    # Create a task first
    await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={
        "title": "Test task for report",
    })

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/reports")
    assert resp.status_code == 200
    report = resp.json()["data"]
    assert report["project_name"] == "Reabilitare termică Bloc A1"
    assert report["total_tasks"] == 1
    assert report["completed_tasks"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# F090: COMPLETED PROJECTS DATABASE
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_completed_projects(auth_client):
    """F090: List completed projects."""
    resp = await auth_client.get("/api/v1/pm/completed-projects")
    assert resp.status_code == 200
    # Initially empty
    assert resp.json()["meta"]["total"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# F080: BUDGET CONTROL (via project update)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_budget_control(auth_client, sample_project):
    """F080: Budget control — alocat vs angajat vs realizat."""
    pid = sample_project["id"]

    resp = await auth_client.put(f"/api/v1/pm/projects/{pid}", json={
        "budget_allocated": 500000.0,
        "budget_committed": 350000.0,
        "budget_actual": 200000.0,
        "cpi": 1.05,
        "spi": 0.95,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["budget_committed"] == 350000.0
    assert data["cpi"] == 1.05
    assert data["spi"] == 0.95


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-TENANT ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_no_auth_returns_401(client):
    """Verify JWT is required on all PM endpoints."""
    resp = await client.get("/api/v1/pm/projects")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_search_projects(auth_client, sample_project):
    """F101: Search projects by name."""
    resp = await auth_client.get("/api/v1/pm/projects?search=Reabilitare")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_filter_by_status(auth_client, sample_project):
    """F101: Filter projects by status."""
    resp = await auth_client.get("/api/v1/pm/projects?status=draft")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F066: CLIENT PORTAL
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_client_portal(auth_client, sample_project):
    """F066: Client portal — aggregated CRM + project + invoice data."""
    pid = sample_project["id"]

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/client-portal")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["project_id"] == pid
    assert data["project_name"] == "Reabilitare termică Bloc A1"
    assert data["total_invoiced"] == 0.0
    assert data["total_outstanding"] == 0.0
    assert isinstance(data["invoices"], list)


@pytest.mark.asyncio
async def test_client_portal_not_found(auth_client):
    """F066: Client portal 404 for unknown project."""
    fake_id = str(uuid.uuid4())
    resp = await auth_client.get(f"/api/v1/pm/projects/{fake_id}/client-portal")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F083: RESOURCE ALLOCATION
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_resource_allocation_crud(auth_client, sample_project):
    """F083: Create and list resource allocations for a project."""
    pid = sample_project["id"]

    # Create allocation
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/resource-allocations", json={
        "resource_type": "employee",
        "start_date": "2026-04-01T00:00:00Z",
        "end_date": "2026-06-30T00:00:00Z",
        "allocated_hours": 480.0,
        "planned_cost": 25000.0,
        "allocation_percent": 80.0,
    })
    assert resp.status_code == 201
    alloc = resp.json()["data"]
    assert alloc["resource_type"] == "employee"
    assert alloc["allocated_hours"] == 480.0
    assert alloc["allocation_percent"] == 80.0

    # List allocations
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/resource-allocations")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1

    # Update allocation
    resp = await auth_client.put(f"/api/v1/pm/resource-allocations/{alloc['id']}", json={
        "actual_hours": 200.0,
        "status": "active",
    })
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["actual_hours"] == 200.0


# ═══════════════════════════════════════════════════════════════════════════════
# F100: INVESTOR DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_investor_dashboard(auth_client, sample_project):
    """F100: Investor dashboard — aggregated data + notifications."""
    resp = await auth_client.get("/api/v1/pm/investor-dashboard")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_projects"] >= 1
    assert "active_projects" in data
    assert "completed_projects" in data
    assert "total_budget_allocated" in data
    assert "notifications" in data
    assert isinstance(data["notifications"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# F130: COMPANY CAPACITY DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_company_capacity(auth_client):
    """F130: Company capacity dashboard — resources vs allocations."""
    resp = await auth_client.get("/api/v1/pm/company-capacity")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_employees" in data
    assert "allocated_employees" in data
    assert "available_employees" in data
    assert "total_equipment" in data
    assert "utilization_rate" in data
    assert "active_projects_count" in data


# ═══════════════════════════════════════════════════════════════════════════════
# F078: PROGRESS MONITORING
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_progress_monitoring(auth_client, sample_project):
    """F078: Progress monitoring with task breakdown and delay alerts."""
    pid = sample_project["id"]

    # Create some tasks
    await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={
        "title": "Task A — in progress",
    })
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/tasks", json={
        "title": "Task B — milestone",
        "is_milestone": True,
    })
    task_b = resp.json()["data"]
    await auth_client.put(f"/api/v1/pm/tasks/{task_b['id']}", json={
        "status": "done",
        "percent_complete": 100.0,
    })

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/progress")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_tasks"] == 2
    assert data["tasks_done"] == 1
    assert data["total_milestones"] == 1
    assert data["completed_milestones"] == 1
    assert "overdue_tasks" in data
    assert "is_behind_schedule" in data


@pytest.mark.asyncio
async def test_progress_monitoring_not_found(auth_client):
    """F078: Progress monitoring 404 for unknown project."""
    fake_id = str(uuid.uuid4())
    resp = await auth_client.get(f"/api/v1/pm/projects/{fake_id}/progress")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F080: BUDGET CONTROL (dedicated endpoint)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_budget_control_endpoint(auth_client, sample_project):
    """F080: Budget control with variance analysis and deviz aggregation."""
    pid = sample_project["id"]

    # Set budget
    await auth_client.put(f"/api/v1/pm/projects/{pid}", json={
        "budget_allocated": 500000.0,
        "budget_actual": 200000.0,
    })

    # Create deviz item
    await auth_client.post(f"/api/v1/pm/projects/{pid}/deviz", json={
        "description": "Izolație termică",
        "unit_of_measure": "mp",
        "estimated_quantity": 100,
        "estimated_unit_price_material": 50.0,
        "estimated_unit_price_labor": 30.0,
    })

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/budget-control")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["budget_allocated"] == 500000.0
    assert data["budget_actual"] == 200000.0
    assert data["budget_remaining"] == 300000.0
    assert data["total_estimated"] == 100 * (50.0 + 30.0)  # 8000.0
    assert data["total_deviz_items"] == 1
    assert data["is_over_budget"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# F105: ML DATA EXPORT
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ml_export_status(auth_client, sample_project):
    """F105: Get ML export status — no energy impact yet."""
    pid = sample_project["id"]

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/ml-export")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["has_energy_impact"] is False
    assert len(data["validation_errors"]) > 0


@pytest.mark.asyncio
async def test_ml_export_trigger(auth_client, sample_project):
    """F105: Trigger ML data export after creating energy impact."""
    pid = sample_project["id"]

    # Create energy impact first
    await auth_client.put(f"/api/v1/pm/projects/{pid}/energy-impact", json={
        "pre_kwh_annual": 150000,
        "post_kwh_annual": 90000,
        "total_area_sqm": 2500,
        "actual_kwh_savings": 60000,
    })

    # Trigger export
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/ml-export", json={
        "mapping_config": {"model": "energy_v2", "version": "1.0"},
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["ml_dataset_exported"] is True
    assert data["ml_data_mapping"]["model"] == "energy_v2"
    assert data["ml_export_date"] is not None


@pytest.mark.asyncio
async def test_ml_export_trigger_no_impact(auth_client, sample_project):
    """F105: Trigger ML export fails without energy impact."""
    # Create a project without energy impact
    resp = await auth_client.post("/api/v1/pm/projects", json={
        "project_number": "PRJ-ML-001",
        "name": "ML Test Project",
    })
    pid = resp.json()["data"]["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/ml-export", json={})
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# F125: WORK TRACKER
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_work_tracker(auth_client, sample_project):
    """F125: Work tracker — quantities/costs estimated vs actual."""
    pid = sample_project["id"]

    # Create deviz items
    await auth_client.post(f"/api/v1/pm/projects/{pid}/deviz", json={
        "description": "Tencuiala decorativă",
        "unit_of_measure": "mp",
        "estimated_quantity": 200,
        "estimated_unit_price_material": 30.0,
        "estimated_unit_price_labor": 20.0,
    })
    resp2 = await auth_client.post(f"/api/v1/pm/projects/{pid}/deviz", json={
        "description": "Vopsea lavabilă",
        "unit_of_measure": "mp",
        "estimated_quantity": 300,
        "estimated_unit_price_material": 15.0,
        "estimated_unit_price_labor": 10.0,
    })
    item2 = resp2.json()["data"]

    # Update second with actuals that exceed estimate
    await auth_client.put(f"/api/v1/pm/deviz/{item2['id']}", json={
        "actual_quantity": 350.0,
        "actual_unit_price_material": 18.0,
        "actual_unit_price_labor": 12.0,
    })

    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/work-tracker")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_items"] == 2
    assert data["total_estimated_cost"] > 0
    assert data["items_over_budget"] >= 1
    assert len(data["items"]) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# F086: WARRANTY + RECEPTION (completion)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_warranty_crud(auth_client, sample_project):
    """F086: Warranty tracking CRUD."""
    pid = sample_project["id"]

    # Create warranty
    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/warranties", json={
        "description": "Garanție izolație termică",
        "start_date": "2026-06-01T00:00:00Z",
        "end_date": "2031-06-01T00:00:00Z",
        "alert_before_days": 60,
    })
    assert resp.status_code == 201
    warranty = resp.json()["data"]
    assert warranty["description"] == "Garanție izolație termică"
    assert warranty["alert_before_days"] == 60
    assert warranty["is_active"] is True

    # Update warranty
    resp = await auth_client.put(f"/api/v1/pm/warranties/{warranty['id']}", json={
        "interventions": [{"date": "2027-01-15", "description": "Reparație fisuri"}],
    })
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert len(updated["interventions"]) == 1

    # List warranties
    resp = await auth_client.get(f"/api/v1/pm/projects/{pid}/warranties")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_reception(auth_client, sample_project):
    """F086: Create formal reception (PV recepție)."""
    pid = sample_project["id"]

    resp = await auth_client.post(f"/api/v1/pm/projects/{pid}/receptions", json={
        "reception_type": "final",
        "reception_date": "2026-12-15T00:00:00Z",
        "committee_members": ["Ing. Popescu", "Arh. Ionescu"],
        "observations": "Lucrare conformă cu proiectul",
        "is_accepted": True,
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["is_official"] is True
    assert data["document_type_badge"] == "PV Recepție"
    assert "Final" in data["title"]


# ═══════════════════════════════════════════════════════════════════════════════
# F145: DEPARTMENT FILES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_department_files(auth_client, sample_project):
    """F145: List files per department."""
    pid = sample_project["id"]

    # Create a file-type wiki post
    await auth_client.post(f"/api/v1/pm/projects/{pid}/wiki", json={
        "title": "Plan execuție v2",
        "post_type": "file",
        "department": "engineering",
        "file_name": "plan_v2.pdf",
        "file_path": "/files/plan_v2.pdf",
        "file_size": 2048000,
    })

    # List all department files
    resp = await auth_client.get("/api/v1/pm/department-files")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Filter by department
    resp = await auth_client.get("/api/v1/pm/department-files?department=engineering")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Non-existing department
    resp = await auth_client.get("/api/v1/pm/department-files?department=marketing")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# F146: OFFICIAL DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_official_documents(auth_client, sample_project):
    """F146: List official documents per department."""
    pid = sample_project["id"]

    # Create an official document
    await auth_client.post(f"/api/v1/pm/projects/{pid}/wiki", json={
        "title": "Autorizație de construcție",
        "post_type": "document",
        "is_official": True,
        "department": "legal",
        "document_type_badge": "Autorizație",
    })

    # List official documents
    resp = await auth_client.get("/api/v1/pm/official-documents")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Filter by department
    resp = await auth_client.get("/api/v1/pm/official-documents?department=legal")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1
