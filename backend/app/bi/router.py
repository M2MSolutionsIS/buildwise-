"""
BI (Business Intelligence) module router — F132, F133, F135, F148, F152.

Endpoints:
  # KPI — F148
  GET    /api/v1/bi/kpis                     — List KPI definitions
  POST   /api/v1/bi/kpis                     — Create KPI definition
  GET    /api/v1/bi/kpis/{id}                — Get KPI definition
  PUT    /api/v1/bi/kpis/{id}                — Update KPI definition
  DELETE /api/v1/bi/kpis/{id}                — Delete KPI definition
  POST   /api/v1/bi/kpis/{id}/values         — Record KPI value
  GET    /api/v1/bi/kpis/{id}/values          — Get KPI value history

  # KPI Dashboard — F152
  GET    /api/v1/bi/kpi-dashboard            — KPI dashboard grid

  # Dashboards — F133
  GET    /api/v1/bi/dashboards               — List dashboards
  POST   /api/v1/bi/dashboards               — Create dashboard
  GET    /api/v1/bi/dashboards/{id}           — Get dashboard with widgets
  PUT    /api/v1/bi/dashboards/{id}           — Update dashboard
  DELETE /api/v1/bi/dashboards/{id}           — Delete dashboard
  GET    /api/v1/bi/executive-summary         — F133: Executive summary

  # AI Chatbot — F132
  GET    /api/v1/bi/conversations             — List conversations
  POST   /api/v1/bi/conversations             — Create conversation
  GET    /api/v1/bi/conversations/{id}         — Get conversation with messages
  POST   /api/v1/bi/conversations/{id}/messages — Send message

  # Reports
  GET    /api/v1/bi/reports                   — List report definitions
  POST   /api/v1/bi/reports                   — Create report definition
  PUT    /api/v1/bi/reports/{id}              — Update report definition
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.bi import service
from app.bi.schemas import (
    AIConversationCreate,
    AIConversationListOut,
    AIConversationOut,
    AIMessageCreate,
    AIMessageOut,
    DashboardCreate,
    DashboardOut,
    DashboardUpdate,
    DashboardWidgetOut,
    ExecutiveSummaryOut,
    KPIDashboardItem,
    KPIDefinitionCreate,
    KPIDefinitionOut,
    KPIDefinitionUpdate,
    KPIValueCreate,
    KPIValueOut,
    ReportDefinitionCreate,
    ReportDefinitionOut,
    ReportDefinitionUpdate,
)
from app.system.schemas import ApiResponse, Meta

bi_router = APIRouter(prefix="/api/v1/bi", tags=["Business Intelligence"])


# ═══════════════════════════════════════════════════════════════════════════════
# KPI DEFINITIONS — F148
# ═══════════════════════════════════════════════════════════════════════════════


@bi_router.get("/kpis", response_model=ApiResponse)
async def list_kpis(
    page: int = 1,
    per_page: int = 20,
    module: str | None = None,
    is_active: bool | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: List KPI definitions."""
    rows, total = await service.list_kpi_definitions(
        db, current_user.organization_id,
        page=page, per_page=per_page, module=module, is_active=is_active,
    )
    return ApiResponse(
        data=[KPIDefinitionOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@bi_router.post("/kpis", response_model=ApiResponse, status_code=201)
async def create_kpi(
    body: KPIDefinitionCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: Create KPI definition."""
    req_info = await get_request_info(request)
    kpi = await service.create_kpi_definition(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=KPIDefinitionOut.model_validate(kpi))


@bi_router.get("/kpis/{kpi_id}", response_model=ApiResponse)
async def get_kpi(
    kpi_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: Get KPI definition."""
    kpi = await service.get_kpi_definition(db, current_user.organization_id, kpi_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI definition not found")
    return ApiResponse(data=KPIDefinitionOut.model_validate(kpi))


@bi_router.put("/kpis/{kpi_id}", response_model=ApiResponse)
async def update_kpi(
    kpi_id: uuid.UUID,
    body: KPIDefinitionUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: Update KPI definition."""
    req_info = await get_request_info(request)
    kpi = await service.update_kpi_definition(
        db, current_user.organization_id, current_user.id, kpi_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI definition not found")
    await db.commit()
    return ApiResponse(data=KPIDefinitionOut.model_validate(kpi))


@bi_router.delete("/kpis/{kpi_id}", response_model=ApiResponse)
async def delete_kpi(
    kpi_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: Delete KPI definition."""
    req_info = await get_request_info(request)
    ok = await service.delete_kpi_definition(
        db, current_user.organization_id, current_user.id, kpi_id,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="KPI definition not found")
    await db.commit()
    return ApiResponse(data={"deleted": True})


# ─── KPI Values ────────────────────────────────────────────────────────────


@bi_router.post("/kpis/{kpi_id}/values", response_model=ApiResponse, status_code=201)
async def record_kpi_value(
    kpi_id: uuid.UUID,
    body: KPIValueCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F148: Record a KPI value measurement."""
    req_info = await get_request_info(request)
    data = body.model_dump()
    data["kpi_definition_id"] = kpi_id
    val = await service.record_kpi_value(
        db, current_user.organization_id, current_user.id, data,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=KPIValueOut.model_validate(val))


@bi_router.get("/kpis/{kpi_id}/values", response_model=ApiResponse)
async def list_kpi_values(
    kpi_id: uuid.UUID,
    limit: int = 50,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F152: Get KPI value history for drill-down."""
    values = await service.list_kpi_values(
        db, current_user.organization_id, kpi_id, limit=limit,
    )
    return ApiResponse(data=[KPIValueOut.model_validate(v) for v in values])


# ─── F152: KPI Dashboard ──────────────────────────────────────────────────


@bi_router.get("/kpi-dashboard", response_model=ApiResponse)
async def kpi_dashboard(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F152: KPI Dashboard — grid of cards with current values and trends."""
    items = await service.get_kpi_dashboard(db, current_user.organization_id)
    result = []
    for item in items:
        result.append({
            "kpi": KPIDefinitionOut.model_validate(item["kpi"]),
            "current_value": item["current_value"],
            "threshold_color": item["threshold_color"],
            "trend": [KPIValueOut.model_validate(v) for v in item["trend"]],
        })
    return ApiResponse(data=result)


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARDS — F133
# ═══════════════════════════════════════════════════════════════════════════════


@bi_router.get("/dashboards", response_model=ApiResponse)
async def list_dashboards(
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: List dashboards."""
    rows, total = await service.list_dashboards(
        db, current_user.organization_id, page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[DashboardOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@bi_router.post("/dashboards", response_model=ApiResponse, status_code=201)
async def create_dashboard(
    body: DashboardCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: Create dashboard with widgets."""
    req_info = await get_request_info(request)
    dash = await service.create_dashboard(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=DashboardOut.model_validate(dash))


@bi_router.get("/dashboards/{dashboard_id}", response_model=ApiResponse)
async def get_dashboard(
    dashboard_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: Get dashboard with widgets."""
    dash = await service.get_dashboard(db, current_user.organization_id, dashboard_id)
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return ApiResponse(data=DashboardOut.model_validate(dash))


@bi_router.put("/dashboards/{dashboard_id}", response_model=ApiResponse)
async def update_dashboard(
    dashboard_id: uuid.UUID,
    body: DashboardUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: Update dashboard."""
    req_info = await get_request_info(request)
    dash = await service.update_dashboard(
        db, current_user.organization_id, current_user.id, dashboard_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    await db.commit()
    return ApiResponse(data=DashboardOut.model_validate(dash))


@bi_router.delete("/dashboards/{dashboard_id}", response_model=ApiResponse)
async def delete_dashboard(
    dashboard_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: Delete dashboard."""
    req_info = await get_request_info(request)
    ok = await service.delete_dashboard(
        db, current_user.organization_id, current_user.id, dashboard_id,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    await db.commit()
    return ApiResponse(data={"deleted": True})


@bi_router.get("/executive-summary", response_model=ApiResponse)
async def executive_summary(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F133: Executive summary — cross-module aggregated data."""
    data = await service.get_executive_summary(db, current_user.organization_id)
    # Serialize KPI items
    kpi_items = []
    for item in data.get("kpi_summary", []):
        kpi_items.append({
            "kpi": KPIDefinitionOut.model_validate(item["kpi"]),
            "current_value": item["current_value"],
            "threshold_color": item["threshold_color"],
            "trend": [KPIValueOut.model_validate(v) for v in item["trend"]],
        })
    data["kpi_summary"] = kpi_items
    return ApiResponse(data=data)


# ═══════════════════════════════════════════════════════════════════════════════
# AI CHATBOT — F132
# ═══════════════════════════════════════════════════════════════════════════════


@bi_router.get("/conversations", response_model=ApiResponse)
async def list_conversations(
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F132: List AI conversations for current user."""
    rows, total = await service.list_conversations(
        db, current_user.organization_id, current_user.id,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[AIConversationListOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@bi_router.post("/conversations", response_model=ApiResponse, status_code=201)
async def create_conversation(
    body: AIConversationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F132: Create new AI conversation."""
    conv = await service.create_conversation(
        db, current_user.organization_id, current_user.id,
        title=body.title,
    )
    await db.commit()
    return ApiResponse(data=AIConversationListOut.model_validate(conv))


@bi_router.get("/conversations/{conversation_id}", response_model=ApiResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F132: Get conversation with messages."""
    conv = await service.get_conversation(
        db, current_user.organization_id, current_user.id, conversation_id,
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ApiResponse(data=AIConversationOut.model_validate(conv))


@bi_router.post("/conversations/{conversation_id}/messages", response_model=ApiResponse, status_code=201)
async def send_message(
    conversation_id: uuid.UUID,
    body: AIMessageCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F132: Send message to AI chatbot."""
    result = await service.add_message(
        db, current_user.organization_id, current_user.id,
        conversation_id, body.content,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.commit()
    return ApiResponse(data={
        "user_message": AIMessageOut.model_validate(result["user_message"]),
        "assistant_message": AIMessageOut.model_validate(result["assistant_message"]),
    })


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════════════


@bi_router.get("/reports", response_model=ApiResponse)
async def list_reports(
    page: int = 1,
    per_page: int = 20,
    report_type: str | None = None,
    module: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List report definitions."""
    rows, total = await service.list_report_definitions(
        db, current_user.organization_id,
        page=page, per_page=per_page, report_type=report_type, module=module,
    )
    return ApiResponse(
        data=[ReportDefinitionOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@bi_router.post("/reports", response_model=ApiResponse, status_code=201)
async def create_report(
    body: ReportDefinitionCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create report definition."""
    req_info = await get_request_info(request)
    report = await service.create_report_definition(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=ReportDefinitionOut.model_validate(report))


@bi_router.put("/reports/{report_id}", response_model=ApiResponse)
async def update_report(
    report_id: uuid.UUID,
    body: ReportDefinitionUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update report definition."""
    req_info = await get_request_info(request)
    report = await service.update_report_definition(
        db, current_user.organization_id, current_user.id, report_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    await db.commit()
    return ApiResponse(data=ReportDefinitionOut.model_validate(report))
