"""
Tests for BI (Business Intelligence) module — F132, F133, F148, F152 P0 endpoints.

Covers: KPI Builder, KPI Dashboard, Dashboards, AI Chatbot,
Executive Summary, Reports.
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
async def sample_kpi(auth_client):
    resp = await auth_client.post("/api/v1/bi/kpis", json={
        "name": "Win Rate",
        "code": "WIN_RATE",
        "module": "pipeline",
        "formula": {"type": "ratio", "numerator": "won_deals", "denominator": "total_deals"},
        "formula_text": "Won Deals / Total Deals * 100",
        "unit": "%",
        "thresholds": [
            {"color": "red", "min": 0, "max": 30},
            {"color": "yellow", "min": 30, "max": 60},
            {"color": "green", "min": 60, "max": 100},
        ],
        "display_type": "gauge",
    })
    assert resp.status_code == 201
    return resp.json()["data"]


# ═══════════════════════════════════════════════════════════════════════════════
# F148 — KPI Builder
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_kpi(auth_client):
    resp = await auth_client.post("/api/v1/bi/kpis", json={
        "name": "Revenue",
        "code": "REVENUE",
        "module": "pipeline",
        "formula": {"type": "sum", "field": "contract_value"},
        "unit": "RON",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Revenue"
    assert data["code"] == "REVENUE"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_kpis(auth_client, sample_kpi):
    resp = await auth_client.get("/api/v1/bi/kpis")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_kpi(auth_client, sample_kpi):
    resp = await auth_client.get(f"/api/v1/bi/kpis/{sample_kpi['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["code"] == "WIN_RATE"


@pytest.mark.asyncio
async def test_update_kpi(auth_client, sample_kpi):
    resp = await auth_client.put(f"/api/v1/bi/kpis/{sample_kpi['id']}", json={
        "name": "Win Rate Updated",
        "thresholds": [
            {"color": "red", "min": 0, "max": 25},
            {"color": "yellow", "min": 25, "max": 50},
            {"color": "green", "min": 50, "max": 100},
        ],
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Win Rate Updated"


@pytest.mark.asyncio
async def test_delete_kpi(auth_client, sample_kpi):
    resp = await auth_client.delete(f"/api/v1/bi/kpis/{sample_kpi['id']}")
    assert resp.status_code == 200
    # Verify deleted
    resp = await auth_client.get(f"/api/v1/bi/kpis/{sample_kpi['id']}")
    assert resp.status_code == 404


# ─── KPI Values ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_kpi_value(auth_client, sample_kpi):
    """F148: Record KPI value with auto threshold color."""
    resp = await auth_client.post(f"/api/v1/bi/kpis/{sample_kpi['id']}/values", json={
        "kpi_definition_id": sample_kpi["id"],
        "value": 75.0,
        "period_start": "2026-03-01T00:00:00Z",
        "period_end": "2026-03-31T00:00:00Z",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["value"] == 75.0
    assert data["threshold_color"] == "green"  # 75 is in green range (60-100)


@pytest.mark.asyncio
async def test_record_kpi_value_yellow(auth_client, sample_kpi):
    """F148: KPI value in yellow range."""
    resp = await auth_client.post(f"/api/v1/bi/kpis/{sample_kpi['id']}/values", json={
        "kpi_definition_id": sample_kpi["id"],
        "value": 45.0,
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["threshold_color"] == "yellow"


@pytest.mark.asyncio
async def test_kpi_value_history(auth_client, sample_kpi):
    """F152: Get KPI value trend."""
    # Record multiple values
    for v in [20.0, 40.0, 65.0]:
        await auth_client.post(f"/api/v1/bi/kpis/{sample_kpi['id']}/values", json={
            "kpi_definition_id": sample_kpi["id"],
            "value": v,
        })

    resp = await auth_client.get(f"/api/v1/bi/kpis/{sample_kpi['id']}/values")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# F152 — KPI Dashboard
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_kpi_dashboard(auth_client, sample_kpi):
    """F152: KPI dashboard grid with current values."""
    # Record a value first
    await auth_client.post(f"/api/v1/bi/kpis/{sample_kpi['id']}/values", json={
        "kpi_definition_id": sample_kpi["id"],
        "value": 80.0,
    })

    resp = await auth_client.get("/api/v1/bi/kpi-dashboard")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["current_value"] == 80.0
    assert data[0]["kpi"]["code"] == "WIN_RATE"
    assert len(data[0]["trend"]) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F133 — Dashboards
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_dashboard_crud(auth_client):
    """F133: Dashboard CRUD with widgets."""
    # Create
    resp = await auth_client.post("/api/v1/bi/dashboards", json={
        "name": "Executive Dashboard",
        "description": "Cross-module overview",
        "dashboard_type": "executive",
        "widgets": [
            {
                "widget_type": "kpi_card",
                "title": "Pipeline Value",
                "config": {"source": "pipeline", "metric": "total_value"},
                "position_x": 0,
                "position_y": 0,
                "width": 4,
                "height": 2,
            },
            {
                "widget_type": "chart",
                "title": "Opportunities by Stage",
                "config": {"source": "pipeline", "chart_type": "bar"},
                "position_x": 4,
                "position_y": 0,
                "width": 8,
                "height": 4,
            },
        ],
    })
    assert resp.status_code == 201
    dash = resp.json()["data"]
    assert dash["name"] == "Executive Dashboard"
    assert len(dash["widgets"]) == 2

    # List
    resp = await auth_client.get("/api/v1/bi/dashboards")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Get with widgets
    resp = await auth_client.get(f"/api/v1/bi/dashboards/{dash['id']}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]["widgets"]) == 2

    # Update
    resp = await auth_client.put(f"/api/v1/bi/dashboards/{dash['id']}", json={
        "name": "Executive Dashboard v2",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Executive Dashboard v2"

    # Delete
    resp = await auth_client.delete(f"/api/v1/bi/dashboards/{dash['id']}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_executive_summary(auth_client):
    """F133: Executive summary — cross-module aggregation."""
    resp = await auth_client.get("/api/v1/bi/executive-summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "total_contacts" in data
    assert "total_opportunities" in data
    assert "pipeline_value" in data
    assert "active_projects" in data


# ═══════════════════════════════════════════════════════════════════════════════
# F132 — AI Chatbot
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_chatbot_conversation(auth_client):
    """F132: Create conversation and send messages."""
    # Create conversation
    resp = await auth_client.post("/api/v1/bi/conversations", json={
        "title": "Test Conversation",
    })
    assert resp.status_code == 201
    conv = resp.json()["data"]
    assert conv["title"] == "Test Conversation"
    assert conv["is_active"] is True

    # Send message
    resp = await auth_client.post(f"/api/v1/bi/conversations/{conv['id']}/messages", json={
        "content": "Ajutor cu CRM-ul",
    })
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["user_message"]["role"] == "user"
    assert data["assistant_message"]["role"] == "assistant"
    assert len(data["assistant_message"]["content"]) > 0

    # Get conversation with messages
    resp = await auth_client.get(f"/api/v1/bi/conversations/{conv['id']}")
    assert resp.status_code == 200
    assert len(resp.json()["data"]["messages"]) == 2

    # List conversations
    resp = await auth_client.get("/api/v1/bi/conversations")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Reports
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_report_definitions(auth_client):
    """Report definition CRUD."""
    # Create
    resp = await auth_client.post("/api/v1/bi/reports", json={
        "name": "Monthly Sales Report",
        "report_type": "financial",
        "module": "pipeline",
        "query_config": {"table": "contracts", "period": "monthly"},
        "columns_config": ["contract_number", "total_value", "status"],
    })
    assert resp.status_code == 201
    report = resp.json()["data"]
    assert report["name"] == "Monthly Sales Report"

    # List
    resp = await auth_client.get("/api/v1/bi/reports")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await auth_client.put(f"/api/v1/bi/reports/{report['id']}", json={
        "name": "Monthly Sales Report v2",
        "is_scheduled": True,
        "schedule_cron": "0 8 1 * *",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["is_scheduled"] is True
