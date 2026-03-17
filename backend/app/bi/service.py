"""
BI (Business Intelligence) module service layer — F132, F133, F135, F148, F152.

All operations include audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.bi.models import (
    AIConversation,
    AIMessage,
    Dashboard,
    DashboardWidget,
    KPIDefinition,
    KPIValue,
    ReportDefinition,
    ReportExecution,
)


# ═══════════════════════════════════════════════════════════════════════════════
# KPI DEFINITIONS — F148
# ═══════════════════════════════════════════════════════════════════════════════


async def list_kpi_definitions(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
    module: str | None = None, is_active: bool | None = None,
) -> tuple[list[KPIDefinition], int]:
    query = select(KPIDefinition).where(KPIDefinition.organization_id == org_id)
    if module:
        query = query.where(KPIDefinition.module == module)
    if is_active is not None:
        query = query.where(KPIDefinition.is_active == is_active)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(KPIDefinition.sort_order).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def get_kpi_definition(db: AsyncSession, org_id: uuid.UUID, kpi_id: uuid.UUID) -> KPIDefinition | None:
    return (await db.execute(
        select(KPIDefinition).where(KPIDefinition.id == kpi_id, KPIDefinition.organization_id == org_id)
    )).scalar_one_or_none()


async def create_kpi_definition(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> KPIDefinition:
    kpi = KPIDefinition(
        id=uuid.uuid4(), organization_id=org_id,
        created_by=user_id, updated_by=user_id, **data,
    )
    db.add(kpi)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="kpi_definitions", entity_id=kpi.id,
        new_values=model_to_dict(kpi), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return kpi


async def update_kpi_definition(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, kpi_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> KPIDefinition | None:
    kpi = await get_kpi_definition(db, org_id, kpi_id)
    if not kpi:
        return None
    old = model_to_dict(kpi)
    for k, v in data.items():
        if v is not None:
            setattr(kpi, k, v)
    kpi.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="kpi_definitions", entity_id=kpi.id,
        old_values=old, new_values=model_to_dict(kpi),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return kpi


async def delete_kpi_definition(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, kpi_id: uuid.UUID,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> bool:
    kpi = await get_kpi_definition(db, org_id, kpi_id)
    if not kpi:
        return False
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="kpi_definitions", entity_id=kpi.id,
        old_values=model_to_dict(kpi), ip_address=ip_address, user_agent=user_agent,
    )
    await db.delete(kpi)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# KPI VALUES — F148, F152
# ═══════════════════════════════════════════════════════════════════════════════


async def record_kpi_value(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> KPIValue:
    """Record a KPI measurement, auto-compute threshold color."""
    kpi_def = await get_kpi_definition(db, org_id, data["kpi_definition_id"])
    value = data["value"]

    # Auto-determine threshold color from definition
    color = data.get("threshold_color")
    if not color and kpi_def and kpi_def.thresholds:
        for t in kpi_def.thresholds:
            if t.get("min", float("-inf")) <= value <= t.get("max", float("inf")):
                color = t.get("color")
                break

    kpi_val = KPIValue(
        id=uuid.uuid4(), organization_id=org_id,
        kpi_definition_id=data["kpi_definition_id"],
        value=value, threshold_color=color,
        period_start=data.get("period_start"),
        period_end=data.get("period_end"),
        project_id=data.get("project_id"),
        user_id=data.get("user_id"),
        raw_data=data.get("raw_data"),
    )
    db.add(kpi_val)
    await db.flush()
    return kpi_val


async def list_kpi_values(
    db: AsyncSession, org_id: uuid.UUID,
    kpi_definition_id: uuid.UUID,
    *, limit: int = 50,
) -> list[KPIValue]:
    result = await db.execute(
        select(KPIValue).where(
            KPIValue.organization_id == org_id,
            KPIValue.kpi_definition_id == kpi_definition_id,
        ).order_by(KPIValue.computed_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


# ─── F152: KPI Dashboard ──────────────────────────────────────────────────


async def get_kpi_dashboard(
    db: AsyncSession, org_id: uuid.UUID,
) -> list[dict]:
    """F152: Build KPI dashboard with current values and trends."""
    kpis = (await db.execute(
        select(KPIDefinition).where(
            KPIDefinition.organization_id == org_id,
            KPIDefinition.is_active.is_(True),
        ).order_by(KPIDefinition.sort_order)
    )).scalars().all()

    result = []
    for kpi in kpis:
        # Get latest value
        latest = (await db.execute(
            select(KPIValue).where(
                KPIValue.kpi_definition_id == kpi.id,
                KPIValue.organization_id == org_id,
            ).order_by(KPIValue.computed_at.desc()).limit(1)
        )).scalar_one_or_none()

        # Get trend (last 10 values)
        trend = (await db.execute(
            select(KPIValue).where(
                KPIValue.kpi_definition_id == kpi.id,
                KPIValue.organization_id == org_id,
            ).order_by(KPIValue.computed_at.desc()).limit(10)
        )).scalars().all()

        result.append({
            "kpi": kpi,
            "current_value": latest.value if latest else None,
            "threshold_color": latest.threshold_color if latest else None,
            "trend": list(trend),
        })
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARDS — F133
# ═══════════════════════════════════════════════════════════════════════════════


async def list_dashboards(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
) -> tuple[list[Dashboard], int]:
    query = select(Dashboard).where(Dashboard.organization_id == org_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.options(selectinload(Dashboard.widgets))
        .order_by(Dashboard.name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def get_dashboard(db: AsyncSession, org_id: uuid.UUID, dash_id: uuid.UUID) -> Dashboard | None:
    return (await db.execute(
        select(Dashboard).options(selectinload(Dashboard.widgets))
        .where(Dashboard.id == dash_id, Dashboard.organization_id == org_id)
    )).scalar_one_or_none()


async def create_dashboard(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Dashboard:
    widgets_data = data.pop("widgets", [])
    dash = Dashboard(
        id=uuid.uuid4(), organization_id=org_id,
        owner_id=user_id, created_by=user_id, updated_by=user_id, **data,
    )
    for w in widgets_data:
        widget = DashboardWidget(
            id=uuid.uuid4(), organization_id=org_id,
            dashboard_id=dash.id, **w,
        )
        dash.widgets.append(widget)
    db.add(dash)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="dashboards", entity_id=dash.id,
        new_values=model_to_dict(dash), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return dash


async def update_dashboard(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, dash_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Dashboard | None:
    dash = await get_dashboard(db, org_id, dash_id)
    if not dash:
        return None
    old = model_to_dict(dash)
    for k, v in data.items():
        if v is not None:
            setattr(dash, k, v)
    dash.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="dashboards", entity_id=dash.id,
        old_values=old, new_values=model_to_dict(dash),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return dash


async def delete_dashboard(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, dash_id: uuid.UUID,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> bool:
    dash = await get_dashboard(db, org_id, dash_id)
    if not dash:
        return False
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="dashboards", entity_id=dash.id,
        old_values=model_to_dict(dash), ip_address=ip_address, user_agent=user_agent,
    )
    await db.delete(dash)
    await db.flush()
    return True


# ─── F133: Executive Summary ──────────────────────────────────────────────


async def get_executive_summary(db: AsyncSession, org_id: uuid.UUID) -> dict:
    """F133: Cross-module aggregated data for executive dashboard."""
    from app.crm.models import Contact
    from app.pipeline.models import Opportunity
    from app.pm.models import Project

    total_contacts = (await db.execute(
        select(func.count()).where(Contact.organization_id == org_id, Contact.is_deleted.is_(False))
    )).scalar() or 0

    total_opps = (await db.execute(
        select(func.count()).where(Opportunity.organization_id == org_id, Opportunity.is_deleted.is_(False))
    )).scalar() or 0

    pipeline_value = (await db.execute(
        select(func.coalesce(func.sum(Opportunity.estimated_value), 0.0)).where(
            Opportunity.organization_id == org_id, Opportunity.is_deleted.is_(False),
        )
    )).scalar() or 0.0

    active_projects = (await db.execute(
        select(func.count()).where(
            Project.organization_id == org_id, Project.is_deleted.is_(False),
            Project.status.in_(["planning", "in_progress"]),
        )
    )).scalar() or 0

    # RM counts (optional — may not have data)
    total_employees = 0
    total_allocations = 0
    try:
        from app.rm.models import Employee, ResourceAllocation
        total_employees = (await db.execute(
            select(func.count()).where(Employee.organization_id == org_id, Employee.is_deleted.is_(False))
        )).scalar() or 0
        total_allocations = (await db.execute(
            select(func.count()).where(ResourceAllocation.organization_id == org_id)
        )).scalar() or 0
    except Exception:
        pass

    # KPI summary
    kpi_items = await get_kpi_dashboard(db, org_id)

    return {
        "total_contacts": total_contacts,
        "total_opportunities": total_opps,
        "pipeline_value": pipeline_value,
        "active_projects": active_projects,
        "total_employees": total_employees,
        "total_allocations": total_allocations,
        "kpi_summary": kpi_items,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AI CHATBOT — F132
# ═══════════════════════════════════════════════════════════════════════════════


async def list_conversations(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
) -> tuple[list[AIConversation], int]:
    query = select(AIConversation).where(
        AIConversation.organization_id == org_id,
        AIConversation.user_id == user_id,
    )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(AIConversation.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_conversation(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID,
    title: str | None = None,
) -> AIConversation:
    conv = AIConversation(
        id=uuid.uuid4(), organization_id=org_id,
        user_id=user_id, title=title,
    )
    db.add(conv)
    await db.flush()
    return conv


async def get_conversation(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, conv_id: uuid.UUID,
) -> AIConversation | None:
    return (await db.execute(
        select(AIConversation).options(selectinload(AIConversation.messages))
        .where(
            AIConversation.id == conv_id,
            AIConversation.organization_id == org_id,
            AIConversation.user_id == user_id,
        )
    )).scalar_one_or_none()


async def add_message(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID,
    conv_id: uuid.UUID, content: str,
) -> dict | None:
    """F132: Add user message and generate assistant response."""
    conv = await get_conversation(db, org_id, user_id, conv_id)
    if not conv:
        return None

    # Save user message
    user_msg = AIMessage(
        id=uuid.uuid4(), conversation_id=conv_id,
        role="user", content=content,
    )
    db.add(user_msg)
    await db.flush()

    # Generate assistant response (simple rule-based for now)
    response = _generate_assistant_response(content)
    assistant_msg = AIMessage(
        id=uuid.uuid4(), conversation_id=conv_id,
        role="assistant", content=response,
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg,
    }


def _generate_assistant_response(content: str) -> str:
    """Simple rule-based response generator. Will be replaced with AI/ML."""
    lower = content.lower()
    if any(w in lower for w in ["ajutor", "help"]):
        return "Cum te pot ajuta? Poți naviga la CRM, Pipeline, Proiecte, sau Resurse din meniul principal."
    if any(w in lower for w in ["contact", "crm"]):
        return "Pentru gestionarea contactelor, accesează modulul CRM din meniul principal. Poți adăuga, edita și importa contacte."
    if any(w in lower for w in ["proiect", "project"]):
        return "Modulul PM (Project Management) îți permite să gestionezi proiecte, WBS, task-uri și devize."
    if any(w in lower for w in ["raport", "report", "dashboard"]):
        return "Poți accesa rapoartele din modulul BI. Dashboard-ul executiv oferă o vedere de ansamblu cross-module."
    return "Înțeleg. Cum te pot ajuta mai departe? Poți întreba despre module, funcționalități, sau navigare."


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS — F142 (extended from System)
# ═══════════════════════════════════════════════════════════════════════════════


async def list_report_definitions(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
    report_type: str | None = None, module: str | None = None,
) -> tuple[list[ReportDefinition], int]:
    query = select(ReportDefinition).where(ReportDefinition.organization_id == org_id)
    if report_type:
        query = query.where(ReportDefinition.report_type == report_type)
    if module:
        query = query.where(ReportDefinition.module == module)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(ReportDefinition.name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_report_definition(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ReportDefinition:
    report = ReportDefinition(
        id=uuid.uuid4(), organization_id=org_id,
        owner_id=user_id, created_by=user_id, updated_by=user_id, **data,
    )
    db.add(report)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="report_definitions", entity_id=report.id,
        new_values=model_to_dict(report), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return report


async def update_report_definition(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, report_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ReportDefinition | None:
    report = (await db.execute(
        select(ReportDefinition).where(
            ReportDefinition.id == report_id, ReportDefinition.organization_id == org_id,
        )
    )).scalar_one_or_none()
    if not report:
        return None
    old = model_to_dict(report)
    for k, v in data.items():
        if v is not None:
            setattr(report, k, v)
    report.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="report_definitions", entity_id=report.id,
        old_values=old, new_values=model_to_dict(report),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return report
