"""
Tests for System module endpoints — F040, F041, F039, F106, F136, F139, F141, F142, F143.

Covers:
  - RBAC Admin (roles CRUD, permissions, user-role assignment)
  - Audit Logs (filtered search)
  - Custom Fields CRUD
  - Document Templates CRUD
  - Pipeline Stage Configs + Feature Flags
  - Currencies + Exchange Rates
  - TrueCast
  - Notifications
  - Report Export
  - Sync Status
"""

import pytest

pytestmark = pytest.mark.asyncio


async def _get_admin_token(client, test_user):
    """Helper: login and return access token."""
    resp = await client.post("/api/auth/login", json={
        "email": "test@buildwise.ro",
        "password": "TestPass123!",
    })
    return resp.json()["access_token"]


# ═══════════════════════════════════════════════════════════════════════════════
# F040 — RBAC Admin
# ═══════════════════════════════════════════════════════════════════════════════


async def test_list_roles(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "data" in resp.json()


async def test_create_role(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.post(
        "/api/v1/system/roles",
        json={"name": "Custom Role", "code": "custom_role", "description": "Test role"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Custom Role"
    assert data["code"] == "custom_role"
    assert data["is_system"] is False


async def test_update_role(client, test_user, test_role):
    token = await _get_admin_token(client, test_user)
    resp = await client.put(
        f"/api/v1/system/roles/{test_role.id}",
        json={"name": "Updated Admin", "description": "Updated desc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Admin"


async def test_delete_system_role_fails(client, test_user, test_role):
    """System roles cannot be deleted."""
    token = await _get_admin_token(client, test_user)
    resp = await client.delete(
        f"/api/v1/system/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404  # is_system=True, so not found by delete query


async def test_list_permissions(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/permissions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_assign_user_roles(client, test_user, test_role):
    token = await _get_admin_token(client, test_user)
    resp = await client.put(
        f"/api/v1/system/users/{test_user.id}/roles",
        json={"role_ids": [str(test_role.id)]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F041 — Audit Logs (filtered)
# ═══════════════════════════════════════════════════════════════════════════════


async def test_audit_logs(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "meta" in resp.json()


async def test_audit_logs_search(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/audit-logs/search?entity_type=users&action=LOGIN",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F039 — Custom Fields
# ═══════════════════════════════════════════════════════════════════════════════


async def test_custom_fields_crud(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/custom-fields",
        json={
            "entity_type": "contact",
            "field_name": "custom_score",
            "field_label": "Custom Score",
            "field_type": "number",
            "is_required": False,
            "sort_order": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    field_id = resp.json()["data"]["id"]

    # List
    resp = await client.get(
        "/api/v1/system/custom-fields?entity_type=contact",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await client.put(
        f"/api/v1/system/custom-fields/{field_id}",
        json={"field_label": "Updated Score"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["field_label"] == "Updated Score"


# ═══════════════════════════════════════════════════════════════════════════════
# F106 — Document Templates
# ═══════════════════════════════════════════════════════════════════════════════


async def test_document_templates_crud(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/document-templates",
        json={
            "name": "Offer Template v1",
            "template_type": "offer",
            "content": "<h1>{{company_name}}</h1>",
            "placeholders": ["company_name", "total_value"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    tmpl_id = resp.json()["data"]["id"]

    # List
    resp = await client.get(
        "/api/v1/system/document-templates?template_type=offer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await client.put(
        f"/api/v1/system/document-templates/{tmpl_id}",
        json={"name": "Offer Template v2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Offer Template v2"


# ═══════════════════════════════════════════════════════════════════════════════
# F136 — Pipeline Stages + Feature Flags
# ═══════════════════════════════════════════════════════════════════════════════


async def test_pipeline_stages_crud(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/pipeline-stages",
        json={
            "name": "Negociere",
            "code": "negotiation",
            "sort_order": 4,
            "color": "#FF9800",
            "win_probability": 0.6,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    stage_id = resp.json()["data"]["id"]

    # List
    resp = await client.get(
        "/api/v1/system/pipeline-stages",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await client.put(
        f"/api/v1/system/pipeline-stages/{stage_id}",
        json={"name": "Negociere Avansată"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_feature_flags_list(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/feature-flags",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F139 — Currencies
# ═══════════════════════════════════════════════════════════════════════════════


async def test_currencies_crud(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/currencies",
        json={"code": "EUR", "name": "Euro", "symbol": "€", "is_default": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    cur_id = resp.json()["data"]["id"]

    # List
    resp = await client.get(
        "/api/v1/system/currencies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await client.put(
        f"/api/v1/system/currencies/{cur_id}",
        json={"name": "Euro (EU)"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Euro (EU)"


async def test_exchange_rates(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/exchange-rates",
        json={
            "from_currency": "RON",
            "to_currency": "EUR",
            "rate": 0.2,
            "effective_date": "2026-01-01T00:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201

    # List
    resp = await client.get(
        "/api/v1/system/exchange-rates?from_currency=RON",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# F140 — TrueCast
# ═══════════════════════════════════════════════════════════════════════════════


async def test_truecast(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/truecast",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F141 — Notifications
# ═══════════════════════════════════════════════════════════════════════════════


async def test_notifications_crud(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/notifications",
        json={"title": "Test Notif", "message": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    notif_id = resp.json()["data"]["id"]

    # List
    resp = await client.get(
        "/api/v1/system/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Mark read
    resp = await client.put(
        f"/api/v1/system/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "read"


async def test_notification_templates(client, test_user):
    token = await _get_admin_token(client, test_user)

    # Create
    resp = await client.post(
        "/api/v1/system/notification-templates",
        json={
            "name": "New Opportunity",
            "event_type": "opportunity_created",
            "channel": "in_app",
            "subject_template": "New opportunity: {{title}}",
            "body_template": "A new opportunity was created.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201

    # List
    resp = await client.get(
        "/api/v1/system/notification-templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# F142 — Report Export
# ═══════════════════════════════════════════════════════════════════════════════


async def test_report_export(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.post(
        "/api/v1/system/reports/export",
        json={"report_type": "contacts", "format": "json"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["report_type"] == "contacts"
    assert "record_count" in data


# ═══════════════════════════════════════════════════════════════════════════════
# F143 — Sync Status
# ═══════════════════════════════════════════════════════════════════════════════


async def test_sync_status(client, test_user):
    token = await _get_admin_token(client, test_user)
    resp = await client.get(
        "/api/v1/system/sync-status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 3  # crm, pipeline, pm
    assert all(d["status"] == "ok" for d in data)
