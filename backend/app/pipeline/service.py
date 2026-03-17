"""
Sales Pipeline module service layer — F019, F023, F026–F029, F031, F033, F035,
F037, F042–F056, F058, F049.

CRUD operations for Opportunities, Milestones, Activities, Offers, Contracts,
Invoices, Pipeline Board, Sales KPI/Dashboard.
All operations include audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.crm.models import Contact, ContactStage
from app.pipeline.models import (
    Activity,
    ActivityStatus,
    ActivityType,
    ApprovalStatus,
    ApprovalStep,
    ApprovalWorkflow,
    BillingSchedule,
    Contract,
    ContractStatus,
    Invoice,
    InvoiceStatus,
    LossReason,
    Milestone,
    MilestoneDependency,
    MilestoneStatus,
    MilestoneTemplate,
    Offer,
    OfferLineItem,
    OfferStatus,
    Opportunity,
    OpportunityStage,
    PredefinedLossReason,
)


# ─── Win probability by stage (F052) ─────────────────────────────────────────

STAGE_WIN_PROBABILITY = {
    OpportunityStage.NEW.value: 0.10,
    OpportunityStage.QUALIFIED.value: 0.20,
    OpportunityStage.SCOPING.value: 0.35,
    OpportunityStage.OFFERING.value: 0.50,
    OpportunityStage.SENT.value: 0.60,
    OpportunityStage.NEGOTIATION.value: 0.75,
    OpportunityStage.WON.value: 1.00,
    OpportunityStage.LOST.value: 0.00,
}

# ─── Valid stage transitions (F051) ──────────────────────────────────────────

VALID_STAGE_TRANSITIONS = {
    OpportunityStage.NEW.value: {
        OpportunityStage.QUALIFIED.value, OpportunityStage.LOST.value,
    },
    OpportunityStage.QUALIFIED.value: {
        OpportunityStage.SCOPING.value, OpportunityStage.LOST.value,
    },
    OpportunityStage.SCOPING.value: {
        OpportunityStage.OFFERING.value, OpportunityStage.LOST.value,
    },
    OpportunityStage.OFFERING.value: {
        OpportunityStage.SENT.value, OpportunityStage.LOST.value,
    },
    OpportunityStage.SENT.value: {
        OpportunityStage.NEGOTIATION.value, OpportunityStage.WON.value,
        OpportunityStage.LOST.value,
    },
    OpportunityStage.NEGOTIATION.value: {
        OpportunityStage.WON.value, OpportunityStage.LOST.value,
    },
    OpportunityStage.WON.value: set(),
    OpportunityStage.LOST.value: set(),
}


# ═══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITIES — F042, F050, F051, F052, F053
# ═══════════════════════════════════════════════════════════════════════════════


async def list_opportunities(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    stage: str | None = None,
    owner_id: uuid.UUID | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Opportunity], int]:
    query = select(Opportunity).where(
        Opportunity.organization_id == org_id,
        Opportunity.is_deleted.is_(False),
    )
    if stage:
        query = query.where(Opportunity.stage == stage)
    if owner_id:
        query = query.where(Opportunity.owner_id == owner_id)
    if contact_id:
        query = query.where(Opportunity.contact_id == contact_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(Opportunity.title.ilike(pattern))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Opportunity.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_opportunity(
    db: AsyncSession, org_id: uuid.UUID, opp_id: uuid.UUID
) -> Opportunity | None:
    result = await db.execute(
        select(Opportunity)
        .options(
            selectinload(Opportunity.milestones),
            selectinload(Opportunity.activities),
            selectinload(Opportunity.offers),
        )
        .where(
            Opportunity.id == opp_id,
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_opportunity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Opportunity:
    """F042: Create opportunity (CRM → Pipeline handover)."""
    stage = data.get("stage", OpportunityStage.NEW.value)
    win_prob = STAGE_WIN_PROBABILITY.get(stage, 0.10)
    estimated_value = data.get("estimated_value") or 0.0
    weighted_value = round(estimated_value * win_prob, 2)

    opp = Opportunity(
        id=uuid.uuid4(),
        organization_id=org_id,
        owner_id=data.pop("owner_id", None) or user_id,
        created_by=user_id,
        updated_by=user_id,
        win_probability=win_prob,
        weighted_value=weighted_value,
        stage_entered_at=datetime.now(timezone.utc),
        **data,
    )
    db.add(opp)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="opportunities",
        entity_id=opp.id,
        new_values=model_to_dict(opp),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return opp


async def update_opportunity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    opp_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Opportunity | None:
    opp = await get_opportunity(db, org_id, opp_id)
    if opp is None:
        return None

    old_values = model_to_dict(opp)
    for key, val in data.items():
        if val is not None:
            setattr(opp, key, val)
    opp.updated_by = user_id

    # Recalculate weighted value if estimated_value changed
    est = opp.estimated_value or 0.0
    prob = opp.win_probability or STAGE_WIN_PROBABILITY.get(opp.stage, 0.10)
    opp.weighted_value = round(est * prob, 2)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="opportunities",
        entity_id=opp.id,
        old_values=old_values,
        new_values=model_to_dict(opp),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return opp


async def transition_opportunity_stage(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    opp_id: uuid.UUID,
    new_stage: str,
    *,
    loss_reason: str | None = None,
    loss_reason_detail: str | None = None,
    won_reason: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Opportunity | None:
    """F051: Validate stage transition + update probability (F052)."""
    opp = await get_opportunity(db, org_id, opp_id)
    if opp is None:
        return None

    # Validate transition
    allowed = VALID_STAGE_TRANSITIONS.get(opp.stage, set())
    if new_stage not in allowed:
        return None

    old_values = model_to_dict(opp)
    opp.stage = new_stage
    opp.stage_entered_at = datetime.now(timezone.utc)
    opp.updated_by = user_id

    # F052: Auto win probability
    opp.win_probability = STAGE_WIN_PROBABILITY.get(new_stage, 0.0)
    est = opp.estimated_value or 0.0
    opp.weighted_value = round(est * opp.win_probability, 2)

    if new_stage == OpportunityStage.WON.value:
        opp.actual_close_date = datetime.now(timezone.utc)
        opp.won_reason = won_reason
    elif new_stage == OpportunityStage.LOST.value:
        opp.actual_close_date = datetime.now(timezone.utc)
        # F053: Validate loss_reason against predefined reasons
        if loss_reason:
            valid = await validate_loss_reason_code(db, org_id, loss_reason)
            if not valid:
                return None  # Invalid loss reason
        opp.loss_reason = loss_reason
        opp.loss_reason_detail = loss_reason_detail

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="opportunities",
        entity_id=opp.id,
        old_values=old_values,
        new_values=model_to_dict(opp),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return opp


async def qualify_opportunity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    opp_id: uuid.UUID,
    checklist: dict | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Opportunity | None:
    """F042: Mark opportunity as qualified."""
    opp = await get_opportunity(db, org_id, opp_id)
    if opp is None:
        return None

    old_values = model_to_dict(opp)
    opp.is_qualified = True
    if checklist:
        opp.qualification_checklist = checklist
    opp.updated_by = user_id

    # Auto-transition to QUALIFIED if still NEW
    if opp.stage == OpportunityStage.NEW.value:
        opp.stage = OpportunityStage.QUALIFIED.value
        opp.stage_entered_at = datetime.now(timezone.utc)
        opp.win_probability = STAGE_WIN_PROBABILITY[OpportunityStage.QUALIFIED.value]
        est = opp.estimated_value or 0.0
        opp.weighted_value = round(est * opp.win_probability, 2)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="opportunities",
        entity_id=opp.id,
        old_values=old_values,
        new_values=model_to_dict(opp),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return opp


async def delete_opportunity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    opp_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    opp = await get_opportunity(db, org_id, opp_id)
    if opp is None:
        return False

    opp.is_deleted = True
    opp.deleted_at = datetime.now(timezone.utc)
    opp.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="opportunities",
        entity_id=opp.id,
        old_values=model_to_dict(opp),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


async def get_pipeline_board(
    db: AsyncSession, org_id: uuid.UUID
) -> dict:
    """F050: Build Kanban board data grouped by stage."""
    stages_order = [
        OpportunityStage.NEW.value,
        OpportunityStage.QUALIFIED.value,
        OpportunityStage.SCOPING.value,
        OpportunityStage.OFFERING.value,
        OpportunityStage.SENT.value,
        OpportunityStage.NEGOTIATION.value,
        OpportunityStage.WON.value,
        OpportunityStage.LOST.value,
    ]

    result = await db.execute(
        select(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
        ).order_by(Opportunity.stage_entered_at.desc())
    )
    all_opps = result.scalars().all()

    # Group by stage
    by_stage = {s: [] for s in stages_order}
    for opp in all_opps:
        if opp.stage in by_stage:
            by_stage[opp.stage].append(opp)

    stages = []
    total_pipeline = 0.0
    total_weighted = 0.0
    for s in stages_order:
        opps = by_stage[s]
        stage_value = sum((o.estimated_value or 0.0) for o in opps)
        stage_weighted = sum((o.weighted_value or 0.0) for o in opps)
        total_pipeline += stage_value
        total_weighted += stage_weighted
        stages.append({
            "stage": s,
            "count": len(opps),
            "total_value": round(stage_value, 2),
            "weighted_value": round(stage_weighted, 2),
            "opportunities": opps,
        })

    return {
        "stages": stages,
        "total_pipeline_value": round(total_pipeline, 2),
        "total_weighted_value": round(total_weighted, 2),
        "currency": "RON",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONES — F043, F044, F045, F046, F047, F048
# ═══════════════════════════════════════════════════════════════════════════════


async def list_milestones(
    db: AsyncSession,
    org_id: uuid.UUID,
    opportunity_id: uuid.UUID,
) -> list[Milestone]:
    """F043: List milestones for an opportunity."""
    result = await db.execute(
        select(Milestone)
        .options(selectinload(Milestone.dependencies))
        .where(
            Milestone.organization_id == org_id,
            Milestone.opportunity_id == opportunity_id,
        )
        .order_by(Milestone.sort_order)
    )
    return result.scalars().all()


async def get_milestone(
    db: AsyncSession, org_id: uuid.UUID, milestone_id: uuid.UUID
) -> Milestone | None:
    result = await db.execute(
        select(Milestone)
        .options(selectinload(Milestone.dependencies), selectinload(Milestone.children))
        .where(
            Milestone.id == milestone_id,
            Milestone.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_milestone(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Milestone:
    """F043: Create milestone."""
    ms = Milestone(
        id=uuid.uuid4(),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(ms)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="milestones",
        entity_id=ms.id,
        new_values=model_to_dict(ms),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return ms


async def update_milestone(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Milestone | None:
    ms = await get_milestone(db, org_id, milestone_id)
    if ms is None:
        return None

    old_values = model_to_dict(ms)
    for key, val in data.items():
        if val is not None:
            setattr(ms, key, val)
    ms.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="milestones",
        entity_id=ms.id,
        old_values=old_values,
        new_values=model_to_dict(ms),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return ms


async def delete_milestone(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    milestone_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    ms = await get_milestone(db, org_id, milestone_id)
    if ms is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="milestones",
        entity_id=ms.id,
        old_values=model_to_dict(ms),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(ms)
    await db.flush()
    return True


async def add_milestone_dependency(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    milestone_id: uuid.UUID,
    depends_on_id: uuid.UUID,
    dependency_type: str = "finish_to_start",
    lag_days: int = 0,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> MilestoneDependency | None:
    """F047: Add dependency between milestones."""
    ms = await get_milestone(db, org_id, milestone_id)
    dep_ms = await get_milestone(db, org_id, depends_on_id)
    if ms is None or dep_ms is None:
        return None

    dep = MilestoneDependency(
        id=uuid.uuid4(),
        milestone_id=milestone_id,
        depends_on_id=depends_on_id,
        dependency_type=dependency_type,
        lag_days=lag_days,
    )
    db.add(dep)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="milestone_dependencies",
        entity_id=dep.id,
        new_values=model_to_dict(dep),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return dep


async def get_milestone_time_summary(
    db: AsyncSession, org_id: uuid.UUID, opportunity_id: uuid.UUID
) -> dict:
    """F044: Summarize time estimation for all milestones in opportunity."""
    milestones = await list_milestones(db, org_id, opportunity_id)

    total_days = 0
    total_cost = 0.0
    items = []
    for ms in milestones:
        days = ms.estimated_duration_days or 0
        cost = ms.estimated_cost or 0.0
        total_days += days
        total_cost += cost
        items.append({
            "id": str(ms.id),
            "title": ms.title,
            "estimated_duration_days": days,
            "estimated_cost": cost,
            "status": ms.status,
            "rm_validated": ms.rm_validated,
        })

    return {
        "opportunity_id": str(opportunity_id),
        "total_estimated_days": total_days,
        "total_estimated_cost": round(total_cost, 2),
        "milestones": items,
    }


# ─── Milestone Templates — F048 ─────────────────────────────────────────────

async def list_milestone_templates(
    db: AsyncSession, org_id: uuid.UUID
) -> list[MilestoneTemplate]:
    result = await db.execute(
        select(MilestoneTemplate).where(
            MilestoneTemplate.organization_id == org_id,
            MilestoneTemplate.is_active.is_(True),
        ).order_by(MilestoneTemplate.name)
    )
    return result.scalars().all()


async def create_milestone_template(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> MilestoneTemplate:
    tmpl = MilestoneTemplate(
        id=uuid.uuid4(),
        organization_id=org_id,
        **data,
    )
    db.add(tmpl)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="milestone_templates",
        entity_id=tmpl.id,
        new_values=model_to_dict(tmpl),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return tmpl


async def apply_milestone_template(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    template_id: uuid.UUID,
    opportunity_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> list[Milestone]:
    """F048: Apply template to create milestones for an opportunity."""
    result = await db.execute(
        select(MilestoneTemplate).where(
            MilestoneTemplate.id == template_id,
            MilestoneTemplate.organization_id == org_id,
        )
    )
    tmpl = result.scalar_one_or_none()
    if tmpl is None:
        return []

    created = []
    items = tmpl.template_data.get("milestones", [])
    for idx, item in enumerate(items):
        ms = Milestone(
            id=uuid.uuid4(),
            organization_id=org_id,
            opportunity_id=opportunity_id,
            title=item.get("title", f"Milestone {idx + 1}"),
            description=item.get("description"),
            sort_order=idx,
            estimated_duration_days=item.get("estimated_duration_days"),
            estimated_cost=item.get("estimated_cost"),
            template_id=template_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(ms)
        created.append(ms)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="milestones",
        entity_id=opportunity_id,
        new_values={"template_id": str(template_id), "count": len(created)},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return created


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVITIES — F054, F055, F056
# ═══════════════════════════════════════════════════════════════════════════════


async def list_activities(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    activity_type: str | None = None,
    status: str | None = None,
    owner_id: uuid.UUID | None = None,
    contact_id: uuid.UUID | None = None,
    opportunity_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Activity], int]:
    query = select(Activity).where(
        Activity.organization_id == org_id,
    )
    if activity_type:
        query = query.where(Activity.activity_type == activity_type)
    if status:
        query = query.where(Activity.status == status)
    if owner_id:
        query = query.where(Activity.owner_id == owner_id)
    if contact_id:
        query = query.where(Activity.contact_id == contact_id)
    if opportunity_id:
        query = query.where(Activity.opportunity_id == opportunity_id)
    if date_from:
        query = query.where(Activity.scheduled_date >= date_from)
    if date_to:
        query = query.where(Activity.scheduled_date <= date_to)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Activity.scheduled_date.asc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_activity(
    db: AsyncSession, org_id: uuid.UUID, activity_id: uuid.UUID
) -> Activity | None:
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id,
            Activity.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_activity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Activity:
    """F054/F055/F056: Create activity."""
    act = Activity(
        id=uuid.uuid4(),
        organization_id=org_id,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(act)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="activities",
        entity_id=act.id,
        new_values=model_to_dict(act),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return act


async def update_activity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    activity_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Activity | None:
    act = await get_activity(db, org_id, activity_id)
    if act is None:
        return None

    old_values = model_to_dict(act)
    for key, val in data.items():
        if val is not None:
            setattr(act, key, val)
    act.updated_by = user_id

    # Mark completed_at if status changes to completed
    if data.get("status") == ActivityStatus.COMPLETED.value:
        act.completed_at = datetime.now(timezone.utc)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="activities",
        entity_id=act.id,
        old_values=old_values,
        new_values=model_to_dict(act),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return act


async def delete_activity(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    activity_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    act = await get_activity(db, org_id, activity_id)
    if act is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="activities",
        entity_id=act.id,
        old_values=model_to_dict(act),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(act)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# OFFERS — F019, F026, F028
# ═══════════════════════════════════════════════════════════════════════════════


def _compute_offer_totals(line_items_data: list[dict]) -> dict:
    """Calculate subtotal, VAT, total from line items."""
    subtotal = 0.0
    vat_amount = 0.0
    for item in line_items_data:
        qty = item.get("quantity", 1.0)
        price = item.get("unit_price", 0.0)
        discount = item.get("discount_percent", 0.0)
        vat_rate = item.get("vat_rate", 0.19)
        line_total = qty * price * (1 - discount / 100)
        subtotal += line_total
        vat_amount += line_total * vat_rate
    return {
        "subtotal": round(subtotal, 2),
        "vat_amount": round(vat_amount, 2),
        "total_amount": round(subtotal + vat_amount, 2),
    }


async def _generate_offer_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"OF-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Offer)
        .where(
            Offer.organization_id == org_id,
            Offer.offer_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def list_offers(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Offer], int]:
    query = select(Offer).where(
        Offer.organization_id == org_id,
        Offer.is_deleted.is_(False),
    )
    if status:
        query = query.where(Offer.status == status)
    if contact_id:
        query = query.where(Offer.contact_id == contact_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Offer.title.ilike(pattern) | Offer.offer_number.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Offer.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_offer(
    db: AsyncSession, org_id: uuid.UUID, offer_id: uuid.UUID
) -> Offer | None:
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.line_items))
        .where(
            Offer.id == offer_id,
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer:
    """F019: Create an offer with line items."""
    line_items_data = data.pop("line_items", [])
    offer_number = await _generate_offer_number(db, org_id)

    totals = _compute_offer_totals(line_items_data)
    valid_until = datetime.now(timezone.utc) + timedelta(days=data.get("validity_days", 30))

    offer = Offer(
        id=uuid.uuid4(),
        organization_id=org_id,
        offer_number=offer_number,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        valid_until=valid_until,
        **totals,
        **data,
    )
    db.add(offer)
    await db.flush()

    for item_data in line_items_data:
        qty = item_data.get("quantity", 1.0)
        price = item_data.get("unit_price", 0.0)
        discount = item_data.get("discount_percent", 0.0)
        line_total = round(qty * price * (1 - discount / 100), 2)
        line_item = OfferLineItem(
            id=uuid.uuid4(),
            offer_id=offer.id,
            organization_id=org_id,
            total_price=line_total,
            **item_data,
        )
        db.add(line_item)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def update_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    offer = await get_offer(db, org_id, offer_id)
    if offer is None:
        return None
    if offer.status != OfferStatus.DRAFT.value:
        return None

    old_values = model_to_dict(offer)
    for key, val in data.items():
        if val is not None:
            setattr(offer, key, val)
    offer.updated_by = user_id

    if data.get("validity_days"):
        offer.valid_until = datetime.now(timezone.utc) + timedelta(days=data["validity_days"])

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        old_values=old_values,
        new_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def create_offer_version(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """F026: Create a new version of an offer (snapshot old, create new)."""
    original = await get_offer(db, org_id, offer_id)
    if original is None:
        return None

    # Mark original as snapshot
    original.is_snapshot = True
    original.updated_by = user_id

    # New version
    new_number = await _generate_offer_number(db, org_id)
    new_version = original.version + 1

    line_items_data = data.get("line_items") or []
    if not line_items_data:
        # Copy line items from original
        line_items_data = [
            {
                "product_id": li.product_id,
                "description": li.description,
                "quantity": li.quantity,
                "unit_of_measure": li.unit_of_measure,
                "unit_price": li.unit_price,
                "discount_percent": li.discount_percent,
                "vat_rate": li.vat_rate,
                "sort_order": li.sort_order,
            }
            for li in original.line_items
        ]

    totals = _compute_offer_totals(line_items_data)
    valid_until = datetime.now(timezone.utc) + timedelta(days=original.validity_days)

    new_offer = Offer(
        id=uuid.uuid4(),
        organization_id=org_id,
        contact_id=original.contact_id,
        opportunity_id=original.opportunity_id,
        property_id=original.property_id,
        offer_number=new_number,
        title=data.get("title") or original.title,
        description=original.description,
        status=OfferStatus.DRAFT.value,
        version=new_version,
        parent_offer_id=original.id,
        currency=original.currency,
        terms_and_conditions=original.terms_and_conditions,
        validity_days=original.validity_days,
        valid_until=valid_until,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        is_quick_quote=original.is_quick_quote,
        **totals,
    )
    db.add(new_offer)
    await db.flush()

    for item_data in line_items_data:
        qty = item_data.get("quantity", 1.0)
        price = item_data.get("unit_price", 0.0)
        discount = item_data.get("discount_percent", 0.0)
        line_total = round(qty * price * (1 - discount / 100), 2)
        # Remove product_id if it's a UUID object (can't be spread directly)
        pid = item_data.pop("product_id", None)
        li = OfferLineItem(
            id=uuid.uuid4(),
            offer_id=new_offer.id,
            organization_id=org_id,
            product_id=pid,
            total_price=line_total,
            **item_data,
        )
        db.add(li)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="offers",
        entity_id=new_offer.id,
        new_values={"version": new_version, "parent_offer_id": str(offer_id)},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return new_offer


async def submit_offer_for_approval(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    comment: str | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """F028: Submit offer for approval."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.DRAFT.value:
        return None

    offer.status = OfferStatus.PENDING_APPROVAL.value
    offer.updated_by = user_id

    workflow = ApprovalWorkflow(
        id=uuid.uuid4(),
        organization_id=org_id,
        entity_type="offer",
        entity_id=offer.id,
        submitted_by=user_id,
    )
    db.add(workflow)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values={"status": "pending_approval", "comment": comment},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def approve_or_reject_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    approved: bool,
    comment: str | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """F028: Approve or reject an offer."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.PENDING_APPROVAL.value:
        return None

    if approved:
        offer.status = OfferStatus.APPROVED.value
    else:
        offer.status = OfferStatus.REJECTED.value
        offer.rejected_at = datetime.now(timezone.utc)

    offer.updated_by = user_id

    wf_result = await db.execute(
        select(ApprovalWorkflow).where(
            ApprovalWorkflow.entity_type == "offer",
            ApprovalWorkflow.entity_id == offer_id,
            ApprovalWorkflow.organization_id == org_id,
            ApprovalWorkflow.status == ApprovalStatus.PENDING.value,
        )
    )
    workflow = wf_result.scalar_one_or_none()
    if workflow:
        workflow.status = ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value
        step = ApprovalStep(
            id=uuid.uuid4(),
            workflow_id=workflow.id,
            approver_id=user_id,
            step_order=1,
            status=ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value,
            comment=comment,
            decided_at=datetime.now(timezone.utc),
        )
        db.add(step)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values={
            "status": offer.status,
            "approved": approved,
            "comment": comment,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def delete_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.DRAFT.value:
        return False

    offer.is_deleted = True
    offer.deleted_at = datetime.now(timezone.utc)
    offer.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="offers",
        entity_id=offer.id,
        old_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


async def get_offer_analytics(db: AsyncSession, org_id: uuid.UUID) -> dict:
    """F029: Offer analytics."""
    base = select(Offer).where(
        Offer.organization_id == org_id, Offer.is_deleted.is_(False)
    )

    total = (await db.execute(
        select(func.count()).select_from(base.subquery())
    )).scalar()

    # By status
    status_result = await db.execute(
        select(Offer.status, func.count())
        .where(Offer.organization_id == org_id, Offer.is_deleted.is_(False))
        .group_by(Offer.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    accepted = by_status.get(OfferStatus.ACCEPTED.value, 0)
    conversion = (accepted / total * 100) if total > 0 else 0.0

    total_value = (await db.execute(
        select(func.coalesce(func.sum(Offer.total_amount), 0.0)).where(
            Offer.organization_id == org_id, Offer.is_deleted.is_(False)
        )
    )).scalar()

    avg_value = (total_value / total) if total > 0 else 0.0

    return {
        "total_offers": total,
        "offers_by_status": by_status,
        "conversion_rate": round(conversion, 2),
        "avg_offer_value": round(avg_value, 2),
        "total_value": round(total_value, 2),
        "currency": "RON",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTS — F031, F035
# ═══════════════════════════════════════════════════════════════════════════════


async def _generate_contract_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"CT-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Contract)
        .where(
            Contract.organization_id == org_id,
            Contract.contract_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def list_contracts(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Contract], int]:
    query = select(Contract).where(
        Contract.organization_id == org_id,
        Contract.is_deleted.is_(False),
    )
    if status:
        query = query.where(Contract.status == status)
    if contact_id:
        query = query.where(Contract.contact_id == contact_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Contract.title.ilike(pattern) | Contract.contract_number.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Contract.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_contract(
    db: AsyncSession, org_id: uuid.UUID, contract_id: uuid.UUID
) -> Contract | None:
    result = await db.execute(
        select(Contract)
        .options(
            selectinload(Contract.billing_schedule),
            selectinload(Contract.invoices),
        )
        .where(
            Contract.id == contract_id,
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract:
    contract_number = await _generate_contract_number(db, org_id)

    contract = Contract(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_number=contract_number,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(contract)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="contracts",
        entity_id=contract.id,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def create_contract_from_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    *,
    title: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    additional_terms: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    """F031: Auto-populate contract from accepted offer."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None:
        return None
    if offer.status not in (OfferStatus.ACCEPTED.value, OfferStatus.APPROVED.value):
        return None

    contract_number = await _generate_contract_number(db, org_id)

    terms = offer.terms_and_conditions or ""
    if additional_terms:
        terms = f"{terms}\n\n{additional_terms}"

    contract = Contract(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_number=contract_number,
        contact_id=offer.contact_id,
        offer_id=offer.id,
        opportunity_id=offer.opportunity_id,
        title=title or f"Contract - {offer.title}",
        total_value=offer.total_amount,
        currency=offer.currency,
        start_date=start_date,
        end_date=end_date,
        terms_and_conditions=terms,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(contract)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="contracts",
        entity_id=contract.id,
        new_values={"from_offer": str(offer_id), **model_to_dict(contract)},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def update_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status != ContractStatus.DRAFT.value:
        return None

    old_values = model_to_dict(contract)
    for key, val in data.items():
        if val is not None:
            setattr(contract, key, val)
    contract.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=old_values,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def sign_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    signed_date: datetime | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    """F031: Sign contract → triggers Project Setup (F063)."""
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status not in (
        ContractStatus.DRAFT.value,
        ContractStatus.APPROVED.value,
        ContractStatus.SENT.value,
    ):
        return None

    old_values = model_to_dict(contract)
    contract.status = ContractStatus.SIGNED.value
    contract.signed_date = signed_date or datetime.now(timezone.utc)
    contract.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=old_values,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def terminate_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    reason: str,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    """F035: Terminate contract with propagation."""
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status in (
        ContractStatus.TERMINATED.value,
        ContractStatus.COMPLETED.value,
    ):
        return None

    old_values = model_to_dict(contract)
    contract.status = ContractStatus.TERMINATED.value
    contract.terminated_date = datetime.now(timezone.utc)
    contract.termination_reason = reason
    contract.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=old_values,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def delete_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    contract = await get_contract(db, org_id, contract_id)
    if contract is None or contract.status != ContractStatus.DRAFT.value:
        return False

    contract.is_deleted = True
    contract.deleted_at = datetime.now(timezone.utc)
    contract.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


async def add_billing_schedule(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> BillingSchedule | None:
    """F035: Add billing schedule item."""
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None

    bs = BillingSchedule(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_id=contract_id,
        **data,
    )
    db.add(bs)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="billing_schedules",
        entity_id=bs.id,
        new_values=model_to_dict(bs),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return bs


async def get_contract_analytics(db: AsyncSession, org_id: uuid.UUID) -> dict:
    """F037: Contracts analytics."""
    total = (await db.execute(
        select(func.count()).select_from(Contract).where(
            Contract.organization_id == org_id, Contract.is_deleted.is_(False)
        )
    )).scalar()

    status_result = await db.execute(
        select(Contract.status, func.count())
        .where(Contract.organization_id == org_id, Contract.is_deleted.is_(False))
        .group_by(Contract.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    active_value = (await db.execute(
        select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
            Contract.status.in_([
                ContractStatus.ACTIVE.value,
                ContractStatus.SIGNED.value,
            ]),
        )
    )).scalar()

    total_value = (await db.execute(
        select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
            Contract.organization_id == org_id, Contract.is_deleted.is_(False)
        )
    )).scalar()

    avg_value = (total_value / total) if total > 0 else 0.0
    terminated = by_status.get(ContractStatus.TERMINATED.value, 0)
    term_rate = (terminated / total * 100) if total > 0 else 0.0

    return {
        "total_contracts": total,
        "contracts_by_status": by_status,
        "total_active_value": round(active_value, 2),
        "avg_contract_value": round(avg_value, 2),
        "termination_rate": round(term_rate, 2),
        "currency": "RON",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICES — F035
# ═══════════════════════════════════════════════════════════════════════════════


async def _generate_invoice_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"INV-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Invoice)
        .where(
            Invoice.organization_id == org_id,
            Invoice.invoice_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def create_invoice_from_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Invoice | None:
    contract_id = data["contract_id"]
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status not in (
        ContractStatus.ACTIVE.value,
        ContractStatus.SIGNED.value,
    ):
        return None

    invoice_number = await _generate_invoice_number(db, org_id)
    amount = data["amount"]
    vat_amount = data.get("vat_amount", 0.0)

    invoice = Invoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_id=contract_id,
        invoice_number=invoice_number,
        amount=amount,
        vat_amount=vat_amount,
        total_amount=round(amount + vat_amount, 2),
        currency=data.get("currency", contract.currency),
        issue_date=data["issue_date"],
        due_date=data["due_date"],
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(invoice)

    billing_id = data.get("billing_schedule_id")
    if billing_id:
        bs_result = await db.execute(
            select(BillingSchedule).where(
                BillingSchedule.id == billing_id,
                BillingSchedule.contract_id == contract_id,
            )
        )
        bs = bs_result.scalar_one_or_none()
        if bs:
            bs.is_invoiced = True
            bs.invoice_id = invoice.id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="invoices",
        entity_id=invoice.id,
        new_values=model_to_dict(invoice),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return invoice


async def list_invoices(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contract_id: uuid.UUID | None = None,
) -> tuple[list[Invoice], int]:
    query = select(Invoice).where(Invoice.organization_id == org_id)
    if status:
        query = query.where(Invoice.status == status)
    if contract_id:
        query = query.where(Invoice.contract_id == contract_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Invoice.issue_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


# ═══════════════════════════════════════════════════════════════════════════════
# SALES KPI / DASHBOARD — F058
# ═══════════════════════════════════════════════════════════════════════════════


async def get_sales_kpi(db: AsyncSession, org_id: uuid.UUID) -> dict:
    """F058: Sales Dashboard — KPIs, funnel, forecast."""
    # Contacts
    total_contacts = (await db.execute(
        select(func.count()).select_from(Contact).where(
            Contact.organization_id == org_id, Contact.is_deleted.is_(False)
        )
    )).scalar()

    active_contacts = (await db.execute(
        select(func.count()).select_from(Contact).where(
            Contact.organization_id == org_id,
            Contact.is_deleted.is_(False),
            Contact.stage == ContactStage.ACTIVE.value,
        )
    )).scalar()

    # Opportunities
    total_opportunities = (await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
        )
    )).scalar()

    open_opportunities = (await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage.notin_([
                OpportunityStage.WON.value, OpportunityStage.LOST.value,
            ]),
        )
    )).scalar()

    won_opportunities = (await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage == OpportunityStage.WON.value,
        )
    )).scalar()

    lost_opportunities = (await db.execute(
        select(func.count()).select_from(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage == OpportunityStage.LOST.value,
        )
    )).scalar()

    pipeline_value = (await db.execute(
        select(func.coalesce(func.sum(Opportunity.estimated_value), 0.0)).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage.notin_([
                OpportunityStage.WON.value, OpportunityStage.LOST.value,
            ]),
        )
    )).scalar()

    weighted_pipeline = (await db.execute(
        select(func.coalesce(func.sum(Opportunity.weighted_value), 0.0)).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage.notin_([
                OpportunityStage.WON.value, OpportunityStage.LOST.value,
            ]),
        )
    )).scalar()

    # Offers
    total_offers = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id, Offer.is_deleted.is_(False)
        )
    )).scalar()

    offers_sent = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.SENT.value,
        )
    )).scalar()

    offers_accepted = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.ACCEPTED.value,
        )
    )).scalar()

    offers_rejected = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.REJECTED.value,
        )
    )).scalar()

    conversion_rate = (offers_accepted / total_offers * 100) if total_offers > 0 else 0.0

    # Contracts
    total_contracts = (await db.execute(
        select(func.count()).select_from(Contract).where(
            Contract.organization_id == org_id, Contract.is_deleted.is_(False)
        )
    )).scalar()

    active_contracts = (await db.execute(
        select(func.count()).select_from(Contract).where(
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
            Contract.status == ContractStatus.ACTIVE.value,
        )
    )).scalar()

    total_revenue = (await db.execute(
        select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
            Contract.status.in_([
                ContractStatus.ACTIVE.value,
                ContractStatus.SIGNED.value,
                ContractStatus.COMPLETED.value,
            ]),
        )
    )).scalar()

    # Invoices
    total_invoiced = (await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0.0)).where(
            Invoice.organization_id == org_id,
            Invoice.status != InvoiceStatus.CANCELLED.value,
        )
    )).scalar()

    total_paid = (await db.execute(
        select(func.coalesce(func.sum(Invoice.paid_amount), 0.0)).where(
            Invoice.organization_id == org_id,
            Invoice.status == InvoiceStatus.PAID.value,
        )
    )).scalar()

    avg_deal = (total_revenue / won_opportunities) if won_opportunities > 0 else 0.0

    # Funnel data
    funnel_stages = [
        OpportunityStage.NEW.value,
        OpportunityStage.QUALIFIED.value,
        OpportunityStage.SCOPING.value,
        OpportunityStage.OFFERING.value,
        OpportunityStage.SENT.value,
        OpportunityStage.NEGOTIATION.value,
        OpportunityStage.WON.value,
    ]
    funnel = []
    for stage in funnel_stages:
        count = (await db.execute(
            select(func.count()).select_from(Opportunity).where(
                Opportunity.organization_id == org_id,
                Opportunity.is_deleted.is_(False),
                Opportunity.stage == stage,
            )
        )).scalar()
        funnel.append({"stage": stage, "count": count})

    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "total_opportunities": total_opportunities,
        "open_opportunities": open_opportunities,
        "won_opportunities": won_opportunities,
        "lost_opportunities": lost_opportunities,
        "pipeline_value": round(pipeline_value, 2),
        "weighted_pipeline_value": round(weighted_pipeline, 2),
        "total_offers": total_offers,
        "offers_sent": offers_sent,
        "offers_accepted": offers_accepted,
        "offers_rejected": offers_rejected,
        "conversion_rate": round(conversion_rate, 2),
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "total_revenue": round(total_revenue, 2),
        "total_invoiced": round(total_invoiced, 2),
        "total_paid": round(total_paid, 2),
        "avg_deal_value": round(avg_deal, 2),
        "currency": "RON",
        "funnel": funnel,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# F023/F033 — Document Generation (template-based)
# ═══════════════════════════════════════════════════════════════════════════════


async def generate_offer_document(
    db: AsyncSession,
    org_id: uuid.UUID,
    offer_id: uuid.UUID,
    *,
    template_id: uuid.UUID | None = None,
    format: str = "json",
    include_line_items: bool = True,
    include_terms: bool = True,
) -> dict | None:
    """F023: Generate document from offer using template."""
    offer = await get_offer(db, org_id, offer_id)
    if not offer:
        return None

    # Get template if specified
    template_name = None
    if template_id:
        from app.system.models import DocumentTemplate
        tmpl = (await db.execute(
            select(DocumentTemplate).where(
                DocumentTemplate.id == template_id, DocumentTemplate.organization_id == org_id
            )
        )).scalar_one_or_none()
        template_name = tmpl.name if tmpl else None

    # Get contact info
    from app.crm.models import Contact
    contact = (await db.execute(
        select(Contact).where(Contact.id == offer.contact_id)
    )).scalar_one_or_none()

    content = {
        "offer_number": offer.offer_number,
        "title": offer.title,
        "status": offer.status,
        "date": offer.created_at.isoformat() if offer.created_at else None,
        "valid_until": offer.valid_until.isoformat() if offer.valid_until else None,
        "contact": {
            "company_name": contact.company_name if contact else None,
            "cui": contact.cui if contact else None,
            "address": contact.address if contact else None,
            "email": contact.email if contact else None,
        } if contact else {},
        "subtotal": offer.subtotal,
        "vat_amount": offer.vat_amount,
        "total_amount": offer.total_amount,
        "currency": offer.currency,
    }
    if include_line_items:
        # Eagerly load line items
        li_result = await db.execute(
            select(OfferLineItem).where(OfferLineItem.offer_id == offer.id)
        )
        items = li_result.scalars().all()
        content["line_items"] = [
            {
                "description": li.description,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "total_price": li.total_price,
            }
            for li in items
        ]
    if include_terms:
        content["terms_and_conditions"] = offer.terms_and_conditions

    return {
        "entity_type": "offer",
        "entity_id": offer.id,
        "template_name": template_name,
        "format": format,
        "generated_at": datetime.now(timezone.utc),
        "content": content,
    }


async def generate_contract_document(
    db: AsyncSession,
    org_id: uuid.UUID,
    contract_id: uuid.UUID,
    *,
    template_id: uuid.UUID | None = None,
    format: str = "json",
    include_terms: bool = True,
) -> dict | None:
    """F033: Generate document from contract using template."""
    contract = await get_contract(db, org_id, contract_id)
    if not contract:
        return None

    template_name = None
    if template_id:
        from app.system.models import DocumentTemplate
        tmpl = (await db.execute(
            select(DocumentTemplate).where(
                DocumentTemplate.id == template_id, DocumentTemplate.organization_id == org_id
            )
        )).scalar_one_or_none()
        template_name = tmpl.name if tmpl else None

    from app.crm.models import Contact
    contact = (await db.execute(
        select(Contact).where(Contact.id == contract.contact_id)
    )).scalar_one_or_none()

    content = {
        "contract_number": contract.contract_number,
        "title": contract.title,
        "status": contract.status,
        "start_date": contract.start_date.isoformat() if contract.start_date else None,
        "end_date": contract.end_date.isoformat() if contract.end_date else None,
        "signed_date": contract.signed_date.isoformat() if contract.signed_date else None,
        "contact": {
            "company_name": contact.company_name if contact else None,
            "cui": contact.cui if contact else None,
            "address": contact.address if contact else None,
        } if contact else {},
        "total_value": contract.total_value,
        "currency": contract.currency,
    }
    if include_terms:
        content["terms_and_conditions"] = contract.terms_and_conditions

    return {
        "entity_type": "contract",
        "entity_id": contract.id,
        "template_name": template_name,
        "format": format,
        "generated_at": datetime.now(timezone.utc),
        "content": content,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# F049 — Simplified Offer Flow
# ═══════════════════════════════════════════════════════════════════════════════


async def create_simplified_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> "Offer":
    """F049: Quick offer with minimal fields — auto-generates offer number."""
    offer_number = await _generate_offer_number(db, org_id)
    offer = Offer(
        id=uuid.uuid4(),
        organization_id=org_id,
        offer_number=offer_number,
        contact_id=data["contact_id"],
        title=data["title"],
        subtotal=data["total_value"],
        vat_amount=data["total_value"] * 0.19,
        total_amount=data["total_value"] * 1.19,
        currency=data.get("currency", "RON"),
        valid_until=data.get("valid_until"),
        is_quick_quote=True,
        status="draft",
        version=1,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(offer)

    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="offers", entity_id=offer.id,
        new_values=model_to_dict(offer),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return offer


# ═══════════════════════════════════════════════════════════════════════════════
# F053 — PREDEFINED LOSS REASONS
# ═══════════════════════════════════════════════════════════════════════════════


async def list_loss_reasons(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    active_only: bool = False,
) -> list[PredefinedLossReason]:
    """F053: List predefined loss reasons for the org."""
    q = select(PredefinedLossReason).where(
        PredefinedLossReason.organization_id == org_id,
    )
    if active_only:
        q = q.where(PredefinedLossReason.is_active.is_(True))
    q = q.order_by(PredefinedLossReason.sort_order, PredefinedLossReason.label)
    result = await db.execute(q)
    return list(result.scalars().all())


async def create_loss_reason(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PredefinedLossReason:
    """F053: Create a predefined loss reason."""
    reason = PredefinedLossReason(
        id=uuid.uuid4(),
        organization_id=org_id,
        **data,
    )
    db.add(reason)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="predefined_loss_reasons", entity_id=reason.id,
        new_values=model_to_dict(reason),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return reason


async def get_loss_reason(
    db: AsyncSession,
    org_id: uuid.UUID,
    reason_id: uuid.UUID,
) -> PredefinedLossReason | None:
    """F053: Get a single predefined loss reason."""
    result = await db.execute(
        select(PredefinedLossReason).where(
            PredefinedLossReason.id == reason_id,
            PredefinedLossReason.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def update_loss_reason(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    reason_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PredefinedLossReason | None:
    """F053: Update a predefined loss reason."""
    reason = await get_loss_reason(db, org_id, reason_id)
    if reason is None:
        return None
    old_values = model_to_dict(reason)
    for k, v in data.items():
        if v is not None:
            setattr(reason, k, v)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="predefined_loss_reasons", entity_id=reason.id,
        old_values=old_values, new_values=model_to_dict(reason),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return reason


async def delete_loss_reason(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    reason_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """F053: Delete a predefined loss reason."""
    reason = await get_loss_reason(db, org_id, reason_id)
    if reason is None:
        return False
    old_values = model_to_dict(reason)
    await db.delete(reason)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="predefined_loss_reasons", entity_id=reason_id,
        old_values=old_values,
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return True


async def validate_loss_reason_code(
    db: AsyncSession,
    org_id: uuid.UUID,
    loss_reason: str,
) -> bool:
    """F053: Check if loss_reason is a valid predefined code for this org."""
    # Accept both old enum values and predefined codes
    try:
        LossReason(loss_reason)
        return True
    except ValueError:
        pass
    result = await db.execute(
        select(PredefinedLossReason.id).where(
            PredefinedLossReason.organization_id == org_id,
            PredefinedLossReason.code == loss_reason,
            PredefinedLossReason.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none() is not None


# ═══════════════════════════════════════════════════════════════════════════════
# F053 — WEIGHTED PIPELINE VALUE
# ═══════════════════════════════════════════════════════════════════════════════


async def get_weighted_pipeline(
    db: AsyncSession,
    org_id: uuid.UUID,
) -> dict:
    """F053: Aggregated weighted pipeline value by stage (excludes won/lost)."""
    active_stages = [
        OpportunityStage.NEW.value,
        OpportunityStage.QUALIFIED.value,
        OpportunityStage.SCOPING.value,
        OpportunityStage.OFFERING.value,
        OpportunityStage.SENT.value,
        OpportunityStage.NEGOTIATION.value,
    ]

    result = await db.execute(
        select(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.is_deleted.is_(False),
            Opportunity.stage.in_(active_stages),
        ).order_by(Opportunity.stage_entered_at.desc())
    )
    all_opps = result.scalars().all()

    by_stage = {s: [] for s in active_stages}
    for opp in all_opps:
        if opp.stage in by_stage:
            by_stage[opp.stage].append(opp)

    stages = []
    total_pipeline = 0.0
    total_weighted = 0.0
    for s in active_stages:
        opps = by_stage[s]
        stage_value = sum((o.estimated_value or 0.0) for o in opps)
        stage_weighted = sum((o.weighted_value or 0.0) for o in opps)
        win_prob = STAGE_WIN_PROBABILITY.get(s, 0.0)
        total_pipeline += stage_value
        total_weighted += stage_weighted
        stages.append({
            "stage": s,
            "count": len(opps),
            "total_value": round(stage_value, 2),
            "weighted_value": round(stage_weighted, 2),
            "win_probability": win_prob,
        })

    return {
        "stages": stages,
        "total_pipeline_value": round(total_pipeline, 2),
        "total_weighted_value": round(total_weighted, 2),
        "currency": "RON",
    }
