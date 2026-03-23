"""
PM module service layer — F063, F066, F069–F080, F083, F084, F086, F088,
F090, F091–F095, F100, F101, F103, F105, F123, F125, F130, F144, F161.

CRUD operations with audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.pm.models import (
    DailyReport,
    DevizItem,
    EnergyImpact,
    ImportJob,
    MaterialConsumption,
    Project,
    ProjectCashFlowEntry,
    ProjectFinanceEntry,
    ProjectStatus,
    PunchItem,
    PunchItemStatus,
    Risk,
    RiskStatus,
    Subcontractor,
    Task,
    TaskDependency,
    TaskStatus,
    TimesheetEntry,
    TimesheetStatus,
    Warranty,
    WBSNode,
    WikiComment,
    WikiPost,
    WorkSituation,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECTS — F063, F101, F103
# ═══════════════════════════════════════════════════════════════════════════════


RISK_SCORE_MAP = {
    "very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5,
    "negligible": 1, "minor": 2, "moderate": 3, "major": 4, "critical": 5,
}


async def list_projects(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    search: str | None = None,
    project_type: str | None = None,
) -> tuple[list[Project], int]:
    """F101: List projects (portfolio view)."""
    query = select(Project).where(
        Project.organization_id == org_id,
        Project.is_deleted.is_(False),
    )
    if status:
        query = query.where(Project.status == status)
    if project_type:
        query = query.where(Project.project_type == project_type)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Project.name.ilike(pattern)
            | Project.project_number.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Project.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_project(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> Project | None:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == org_id,
            Project.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Project:
    """F063: Create a project."""
    project = Project(
        id=uuid.uuid4(),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(project)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="projects",
        entity_id=project.id,
        new_values=model_to_dict(project),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return project


async def create_project_from_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    *,
    name: str | None = None,
    project_type: str = "client",
    planned_start_date: datetime | None = None,
    planned_end_date: datetime | None = None,
    import_milestones: bool = True,
    kickoff_checklist: dict | None = None,
    notes: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Project:
    """F063: Auto-create project from signed contract with milestone import to WBS."""
    from app.pipeline.models import Contract, Milestone, Opportunity

    # Fetch contract
    contract = (await db.execute(
        select(Contract).where(
            Contract.id == contract_id,
            Contract.organization_id == org_id,
        )
    )).scalar_one_or_none()
    if contract is None:
        raise ValueError("Contract not found")

    # Generate project number
    count = (await db.execute(
        select(func.count()).select_from(Project).where(
            Project.organization_id == org_id,
        )
    )).scalar() or 0
    project_number = f"PRJ-{count + 1:04d}"

    project_name = name or f"Proiect — {contract.title}"

    # Create project
    project = Project(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_id=contract.id,
        contact_id=contract.contact_id,
        project_number=project_number,
        name=project_name,
        project_type=project_type,
        status="kickoff",
        planned_start_date=planned_start_date or datetime.now(timezone.utc),
        planned_end_date=planned_end_date,
        budget_allocated=float(contract.total_value) if contract.total_value else None,
        currency=getattr(contract, "currency", "RON") or "RON",
        kickoff_checklist=kickoff_checklist or {
            "contract_signed": True,
            "team_assigned": False,
            "wbs_created": False,
            "budget_approved": False,
            "kickoff_meeting": False,
        },
        notes=notes,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(project)
    await db.flush()

    # Link contract back to project
    contract.project_id = project.id
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="projects",
        entity_id=project.id,
        new_values=model_to_dict(project),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Import milestones from pipeline opportunity as WBS nodes
    if import_milestones and contract.opportunity_id:
        milestones = (await db.execute(
            select(Milestone).where(
                Milestone.opportunity_id == contract.opportunity_id,
                Milestone.organization_id == org_id,
            ).order_by(Milestone.sort_order)
        )).scalars().all()

        for idx, ms in enumerate(milestones):
            wbs_node = WBSNode(
                id=uuid.uuid4(),
                organization_id=org_id,
                project_id=project.id,
                code=f"WBS-{idx + 1:03d}",
                name=ms.title,
                description=ms.description,
                node_type="chapter",
                sort_order=ms.sort_order or idx,
                level=1,
                budget_allocated=ms.estimated_cost,
                responsible_id=ms.assigned_to,
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(wbs_node)

            # Also create a task from the milestone for Gantt
            task = Task(
                id=uuid.uuid4(),
                organization_id=org_id,
                project_id=project.id,
                wbs_node_id=wbs_node.id,
                title=ms.title,
                description=ms.description,
                status="todo",
                planned_start_date=ms.start_date,
                planned_end_date=ms.end_date,
                planned_duration_days=ms.estimated_duration_days,
                estimated_hours=float(ms.estimated_duration_days * 8) if ms.estimated_duration_days else None,
                estimated_cost=ms.estimated_cost,
                assigned_to=ms.assigned_to,
                sort_order=ms.sort_order or idx,
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(task)

        await db.flush()

        # Update kickoff checklist
        if project.kickoff_checklist:
            project.kickoff_checklist = {
                **project.kickoff_checklist,
                "wbs_created": len(milestones) > 0,
            }

        await log_audit(
            db,
            user_id=user_id,
            organization_id=org_id,
            action="CREATE",
            entity_type="wbs_import",
            entity_id=project.id,
            new_values={"milestones_imported": len(milestones), "source": "pipeline_deal"},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    await db.flush()
    return project


async def update_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Project | None:
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    old_values = model_to_dict(project)
    for key, val in data.items():
        if val is not None:
            setattr(project, key, val)
    project.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="projects",
        entity_id=project.id,
        old_values=old_values,
        new_values=model_to_dict(project),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    await db.refresh(project)
    return project


async def delete_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    project = await get_project(db, org_id, project_id)
    if project is None:
        return False

    old_values = model_to_dict(project)
    project.is_deleted = True
    project.deleted_at = datetime.now(timezone.utc)
    project.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="projects",
        entity_id=project.id,
        old_values=old_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


async def close_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    grace_period_days: int = 30,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Project | None:
    """F103: Close project with grace period."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    old_values = model_to_dict(project)
    now = datetime.now(timezone.utc)
    project.status = ProjectStatus.CLOSING
    project.close_date = now
    project.grace_period_end = now + timedelta(days=grace_period_days)
    project.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="projects",
        entity_id=project.id,
        old_values=old_values,
        new_values=model_to_dict(project),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    await db.refresh(project)
    return project


async def cancel_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    reason: str,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Project | None:
    """F103: Cancel project with reason."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    old_values = model_to_dict(project)
    project.status = ProjectStatus.CANCELLED
    project.cancellation_reason = reason
    project.actual_end_date = datetime.now(timezone.utc)
    project.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="projects",
        entity_id=project.id,
        old_values=old_values,
        new_values=model_to_dict(project),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    await db.refresh(project)
    return project


# ═══════════════════════════════════════════════════════════════════════════════
# WBS — F069
# ═══════════════════════════════════════════════════════════════════════════════


async def list_wbs_nodes(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[WBSNode]:
    result = await db.execute(
        select(WBSNode).where(
            WBSNode.project_id == project_id,
            WBSNode.organization_id == org_id,
        ).order_by(WBSNode.sort_order, WBSNode.code)
    )
    return result.scalars().all()


async def create_wbs_node(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WBSNode:
    node = WBSNode(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(node)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="wbs_nodes",
        entity_id=node.id,
        new_values=model_to_dict(node),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return node


async def update_wbs_node(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    node_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WBSNode | None:
    result = await db.execute(
        select(WBSNode).where(
            WBSNode.id == node_id,
            WBSNode.organization_id == org_id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        return None

    old_values = model_to_dict(node)
    for key, val in data.items():
        if val is not None:
            setattr(node, key, val)
    node.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="wbs_nodes",
        entity_id=node.id,
        old_values=old_values,
        new_values=model_to_dict(node),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return node


async def delete_wbs_node(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    node_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(WBSNode).where(
            WBSNode.id == node_id,
            WBSNode.organization_id == org_id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="wbs_nodes",
        entity_id=node.id,
        old_values=model_to_dict(node),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(node)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# TASKS / GANTT — F070, F073
# ═══════════════════════════════════════════════════════════════════════════════


async def list_tasks(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    status: str | None = None,
    assigned_to: uuid.UUID | None = None,
    page: int = 1,
    per_page: int = 100,
) -> tuple[list[Task], int]:
    query = select(Task).where(
        Task.project_id == project_id,
        Task.organization_id == org_id,
    )
    if status:
        query = query.where(Task.status == status)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Task.sort_order, Task.planned_start)
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_task(
    db: AsyncSession, org_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.dependencies))
        .where(
            Task.id == task_id,
            Task.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Task:
    task = Task(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(task)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="tasks",
        entity_id=task.id,
        new_values=model_to_dict(task),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return task


async def update_task(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Task | None:
    """F073: Update task including status transitions with blocked_reason validation."""
    task = await get_task(db, org_id, task_id)
    if task is None:
        return None

    old_values = model_to_dict(task)

    # F073: If transitioning to BLOCKED, blocked_reason is mandatory
    new_status = data.get("status")
    if new_status == TaskStatus.BLOCKED.value or new_status == TaskStatus.BLOCKED:
        if not data.get("blocked_reason") and not task.blocked_reason:
            raise ValueError("blocked_reason is required when status is BLOCKED")
        task.escalated = True

    for key, val in data.items():
        if val is not None:
            setattr(task, key, val)
    task.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="tasks",
        entity_id=task.id,
        old_values=old_values,
        new_values=model_to_dict(task),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    task = await get_task(db, org_id, task_id)
    if task is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="tasks",
        entity_id=task.id,
        old_values=model_to_dict(task),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(task)
    await db.flush()
    return True


async def add_task_dependency(
    db: AsyncSession,
    org_id: uuid.UUID,
    task_id: uuid.UUID,
    data: dict,
) -> TaskDependency:
    dep = TaskDependency(
        id=uuid.uuid4(),
        task_id=task_id,
        **data,
    )
    db.add(dep)
    await db.flush()
    return dep


async def remove_task_dependency(
    db: AsyncSession,
    dep_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(TaskDependency).where(TaskDependency.id == dep_id)
    )
    dep = result.scalar_one_or_none()
    if dep is None:
        return False
    await db.delete(dep)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# DEVIZ — F071, F125
# ═══════════════════════════════════════════════════════════════════════════════


async def list_deviz_items(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
) -> list[DevizItem]:
    result = await db.execute(
        select(DevizItem).where(
            DevizItem.project_id == project_id,
            DevizItem.organization_id == org_id,
        ).order_by(DevizItem.sort_order, DevizItem.code)
    )
    return result.scalars().all()


async def create_deviz_item(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> DevizItem:
    # Auto-calculate estimated_total
    est_qty = data.get("estimated_quantity", 0.0)
    est_mat = data.get("estimated_unit_price_material", 0.0)
    est_lab = data.get("estimated_unit_price_labor", 0.0)
    data["estimated_total"] = est_qty * (est_mat + est_lab)

    item = DevizItem(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(item)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="deviz_items",
        entity_id=item.id,
        new_values=model_to_dict(item),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return item


async def update_deviz_item(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> DevizItem | None:
    result = await db.execute(
        select(DevizItem).where(
            DevizItem.id == item_id,
            DevizItem.organization_id == org_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return None

    old_values = model_to_dict(item)
    for key, val in data.items():
        if val is not None:
            setattr(item, key, val)

    # Recalculate totals
    item.estimated_total = item.estimated_quantity * (
        item.estimated_unit_price_material + item.estimated_unit_price_labor
    )
    item.actual_total = item.actual_quantity * (
        item.actual_unit_price_material + item.actual_unit_price_labor
    )
    # F125: Over budget alert
    item.over_budget_alert = item.actual_total > item.estimated_total if item.estimated_total > 0 else False
    item.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="deviz_items",
        entity_id=item.id,
        old_values=old_values,
        new_values=model_to_dict(item),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return item


async def delete_deviz_item(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(DevizItem).where(
            DevizItem.id == item_id,
            DevizItem.organization_id == org_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="deviz_items",
        entity_id=item.id,
        old_values=model_to_dict(item),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(item)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# TIMESHEETS — F072
# ═══════════════════════════════════════════════════════════════════════════════


async def list_timesheets(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 50,
    user_id_filter: uuid.UUID | None = None,
) -> tuple[list[TimesheetEntry], int]:
    query = select(TimesheetEntry).where(
        TimesheetEntry.project_id == project_id,
        TimesheetEntry.organization_id == org_id,
    )
    if user_id_filter:
        query = query.where(TimesheetEntry.user_id == user_id_filter)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(TimesheetEntry.work_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_timesheet(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TimesheetEntry:
    # F072: cost = hours × hourly_rate
    hours = data.get("hours", 0)
    rate = data.get("hourly_rate")
    cost = hours * rate if rate else None

    entry = TimesheetEntry(
        id=uuid.uuid4(),
        project_id=project_id,
        user_id=user_id,
        organization_id=org_id,
        cost=cost,
        **data,
    )
    db.add(entry)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="timesheet_entries",
        entity_id=entry.id,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


async def update_timesheet(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TimesheetEntry | None:
    result = await db.execute(
        select(TimesheetEntry).where(
            TimesheetEntry.id == entry_id,
            TimesheetEntry.organization_id == org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return None

    old_values = model_to_dict(entry)
    for key, val in data.items():
        if val is not None:
            setattr(entry, key, val)

    # Recalculate cost
    if entry.hourly_rate:
        entry.cost = entry.hours * entry.hourly_rate

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="timesheet_entries",
        entity_id=entry.id,
        old_values=old_values,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


async def approve_timesheet(
    db: AsyncSession,
    org_id: uuid.UUID,
    approver_id: uuid.UUID,
    entry_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TimesheetEntry | None:
    result = await db.execute(
        select(TimesheetEntry).where(
            TimesheetEntry.id == entry_id,
            TimesheetEntry.organization_id == org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return None

    old_values = model_to_dict(entry)
    entry.status = TimesheetStatus.APPROVED
    entry.approved_by = approver_id
    entry.approved_at = datetime.now(timezone.utc)

    await log_audit(
        db,
        user_id=approver_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="timesheet_entries",
        entity_id=entry.id,
        old_values=old_values,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIALS — F074
# ═══════════════════════════════════════════════════════════════════════════════


async def list_material_consumptions(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[MaterialConsumption], int]:
    query = select(MaterialConsumption).where(
        MaterialConsumption.project_id == project_id,
        MaterialConsumption.organization_id == org_id,
    )
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(MaterialConsumption.consumption_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_material_consumption(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> MaterialConsumption:
    # Auto-calc total_cost
    qty = data.get("consumed_quantity", 0)
    price = data.get("unit_price")
    total_cost = qty * price if price else None

    entry = MaterialConsumption(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        registered_by=user_id,
        created_by=user_id,
        updated_by=user_id,
        total_cost=total_cost,
        **data,
    )
    db.add(entry)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="material_consumptions",
        entity_id=entry.id,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# SUBCONTRACTORS — F075
# ═══════════════════════════════════════════════════════════════════════════════


async def list_subcontractors(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[Subcontractor]:
    result = await db.execute(
        select(Subcontractor).where(
            Subcontractor.project_id == project_id,
            Subcontractor.organization_id == org_id,
        ).order_by(Subcontractor.company_name)
    )
    return result.scalars().all()


async def create_subcontractor(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Subcontractor:
    sub = Subcontractor(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(sub)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="subcontractors",
        entity_id=sub.id,
        new_values=model_to_dict(sub),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return sub


async def update_subcontractor(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    sub_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Subcontractor | None:
    result = await db.execute(
        select(Subcontractor).where(
            Subcontractor.id == sub_id,
            Subcontractor.organization_id == org_id,
        )
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        return None

    old_values = model_to_dict(sub)
    for key, val in data.items():
        if val is not None:
            setattr(sub, key, val)
    sub.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="subcontractors",
        entity_id=sub.id,
        old_values=old_values,
        new_values=model_to_dict(sub),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return sub


# ═══════════════════════════════════════════════════════════════════════════════
# DAILY REPORTS — F077
# ═══════════════════════════════════════════════════════════════════════════════


async def list_daily_reports(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 30,
) -> tuple[list[DailyReport], int]:
    query = select(DailyReport).where(
        DailyReport.project_id == project_id,
        DailyReport.organization_id == org_id,
    )
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(DailyReport.report_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_daily_report(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> DailyReport:
    report = DailyReport(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        reported_by=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(report)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="daily_reports",
        entity_id=report.id,
        new_values=model_to_dict(report),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# WORK SITUATIONS — F079
# ═══════════════════════════════════════════════════════════════════════════════


async def list_work_situations(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[WorkSituation]:
    result = await db.execute(
        select(WorkSituation).where(
            WorkSituation.project_id == project_id,
            WorkSituation.organization_id == org_id,
        ).order_by(WorkSituation.period_year.desc(), WorkSituation.period_month.desc())
    )
    return result.scalars().all()


async def create_work_situation(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WorkSituation:
    sdl = WorkSituation(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(sdl)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="work_situations",
        entity_id=sdl.id,
        new_values=model_to_dict(sdl),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return sdl


async def update_work_situation(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    sdl_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WorkSituation | None:
    result = await db.execute(
        select(WorkSituation).where(
            WorkSituation.id == sdl_id,
            WorkSituation.organization_id == org_id,
        )
    )
    sdl = result.scalar_one_or_none()
    if sdl is None:
        return None

    old_values = model_to_dict(sdl)
    for key, val in data.items():
        if val is not None:
            setattr(sdl, key, val)
    sdl.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="work_situations",
        entity_id=sdl.id,
        old_values=old_values,
        new_values=model_to_dict(sdl),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return sdl


async def approve_work_situation(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    sdl_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WorkSituation | None:
    result = await db.execute(
        select(WorkSituation).where(
            WorkSituation.id == sdl_id,
            WorkSituation.organization_id == org_id,
        )
    )
    sdl = result.scalar_one_or_none()
    if sdl is None:
        return None

    old_values = model_to_dict(sdl)
    sdl.is_approved = True
    sdl.approved_by = user_id
    sdl.approved_at = datetime.now(timezone.utc)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="work_situations",
        entity_id=sdl.id,
        old_values=old_values,
        new_values=model_to_dict(sdl),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return sdl


# ═══════════════════════════════════════════════════════════════════════════════
# RISK REGISTER — F084
# ═══════════════════════════════════════════════════════════════════════════════


async def list_risks(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[Risk]:
    result = await db.execute(
        select(Risk).where(
            Risk.project_id == project_id,
            Risk.organization_id == org_id,
        ).order_by(Risk.risk_score.desc().nulls_last())
    )
    return result.scalars().all()


async def create_risk(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Risk:
    # Auto-calculate risk_score = P × I
    prob = RISK_SCORE_MAP.get(data.get("probability", ""), 1)
    impact = RISK_SCORE_MAP.get(data.get("impact", ""), 1)
    data["risk_score"] = prob * impact

    if "identified_date" not in data or data["identified_date"] is None:
        data["identified_date"] = datetime.now(timezone.utc)

    risk = Risk(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(risk)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="risks",
        entity_id=risk.id,
        new_values=model_to_dict(risk),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return risk


async def update_risk(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    risk_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Risk | None:
    result = await db.execute(
        select(Risk).where(
            Risk.id == risk_id,
            Risk.organization_id == org_id,
        )
    )
    risk = result.scalar_one_or_none()
    if risk is None:
        return None

    old_values = model_to_dict(risk)
    for key, val in data.items():
        if val is not None:
            setattr(risk, key, val)

    # Recalculate risk_score
    prob = RISK_SCORE_MAP.get(str(risk.probability).split(".")[-1], 1)
    impact = RISK_SCORE_MAP.get(str(risk.impact).split(".")[-1], 1)
    risk.risk_score = prob * impact
    risk.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="risks",
        entity_id=risk.id,
        old_values=old_values,
        new_values=model_to_dict(risk),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return risk


async def delete_risk(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    risk_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(Risk).where(
            Risk.id == risk_id,
            Risk.organization_id == org_id,
        )
    )
    risk = result.scalar_one_or_none()
    if risk is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="risks",
        entity_id=risk.id,
        old_values=model_to_dict(risk),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(risk)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# PUNCH ITEMS — F086
# ═══════════════════════════════════════════════════════════════════════════════


async def list_punch_items(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[PunchItem]:
    result = await db.execute(
        select(PunchItem).where(
            PunchItem.project_id == project_id,
            PunchItem.organization_id == org_id,
        ).order_by(PunchItem.created_at.desc())
    )
    return result.scalars().all()


async def create_punch_item(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PunchItem:
    item = PunchItem(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(item)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="punch_items",
        entity_id=item.id,
        new_values=model_to_dict(item),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return item


async def update_punch_item(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PunchItem | None:
    result = await db.execute(
        select(PunchItem).where(
            PunchItem.id == item_id,
            PunchItem.organization_id == org_id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return None

    old_values = model_to_dict(item)

    # Auto set resolved_at when status changes to resolved/verified
    new_status = data.get("status")
    if new_status in ("resolved", "verified") and item.resolved_at is None:
        item.resolved_at = datetime.now(timezone.utc)

    for key, val in data.items():
        if val is not None:
            setattr(item, key, val)
    item.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="punch_items",
        entity_id=item.id,
        old_values=old_values,
        new_values=model_to_dict(item),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return item


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY IMPACT — F088, F090, F105, F161
# ═══════════════════════════════════════════════════════════════════════════════


async def get_energy_impact(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> EnergyImpact | None:
    result = await db.execute(
        select(EnergyImpact).where(
            EnergyImpact.project_id == project_id,
            EnergyImpact.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def upsert_energy_impact(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> EnergyImpact:
    existing = await get_energy_impact(db, org_id, project_id)

    if existing:
        old_values = model_to_dict(existing)
        for key, val in data.items():
            if val is not None:
                setattr(existing, key, val)
        existing.updated_by = user_id

        await log_audit(
            db,
            user_id=user_id,
            organization_id=org_id,
            action="UPDATE",
            entity_type="energy_impacts",
            entity_id=existing.id,
            old_values=old_values,
            new_values=model_to_dict(existing),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.flush()
        return existing

    impact = EnergyImpact(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(impact)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="energy_impacts",
        entity_id=impact.id,
        new_values=model_to_dict(impact),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return impact


async def get_energy_portfolio(
    db: AsyncSession, org_id: uuid.UUID
) -> dict:
    """F161: Aggregated energy portfolio across completed projects."""
    result = await db.execute(
        select(
            func.coalesce(func.sum(EnergyImpact.actual_kwh_savings), 0).label("total_kwh"),
            func.coalesce(func.sum(EnergyImpact.actual_co2_reduction), 0).label("total_co2"),
            func.count(EnergyImpact.id).label("total_projects"),
            func.coalesce(func.sum(EnergyImpact.treated_area_sqm), 0).label("total_area"),
            func.avg(EnergyImpact.pre_u_value_avg).label("avg_u_pre"),
            func.avg(EnergyImpact.post_u_value_avg).label("avg_u_post"),
        ).where(EnergyImpact.organization_id == org_id)
    )
    row = result.one()
    return {
        "total_kwh_saved": float(row.total_kwh),
        "total_co2_reduced": float(row.total_co2),
        "total_projects": int(row.total_projects),
        "total_area_treated_sqm": float(row.total_area),
        "avg_u_value_pre": float(row.avg_u_pre) if row.avg_u_pre else None,
        "avg_u_value_post": float(row.avg_u_post) if row.avg_u_post else None,
    }


async def list_completed_projects(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Project], int]:
    """F090: List completed projects database."""
    query = select(Project).where(
        Project.organization_id == org_id,
        Project.status == ProjectStatus.COMPLETED,
        Project.is_deleted.is_(False),
    )
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Project.actual_end_date.desc().nulls_last())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT FINANCE — F091, F092, F093, F094
# ═══════════════════════════════════════════════════════════════════════════════


async def list_finance_entries(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[ProjectFinanceEntry]:
    result = await db.execute(
        select(ProjectFinanceEntry).where(
            ProjectFinanceEntry.project_id == project_id,
            ProjectFinanceEntry.organization_id == org_id,
        ).order_by(
            ProjectFinanceEntry.period_year,
            ProjectFinanceEntry.period_month,
        )
    )
    return result.scalars().all()


async def create_finance_entry(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
) -> ProjectFinanceEntry:
    # Auto-calculate variance
    data["variance"] = data.get("actual_amount", 0) - data.get("forecast_amount", 0)

    entry = ProjectFinanceEntry(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        **data,
    )
    db.add(entry)
    await db.flush()
    return entry


async def list_cash_flow_entries(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[ProjectCashFlowEntry]:
    result = await db.execute(
        select(ProjectCashFlowEntry).where(
            ProjectCashFlowEntry.project_id == project_id,
            ProjectCashFlowEntry.organization_id == org_id,
        ).order_by(ProjectCashFlowEntry.transaction_date)
    )
    return result.scalars().all()


async def create_cash_flow_entry(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
) -> ProjectCashFlowEntry:
    entry = ProjectCashFlowEntry(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        **data,
    )
    db.add(entry)
    await db.flush()
    return entry


async def get_global_pl(
    db: AsyncSession, org_id: uuid.UUID, year: int | None = None
) -> list[ProjectFinanceEntry]:
    """F093: Global P&L aggregated across all projects."""
    query = select(ProjectFinanceEntry).where(
        ProjectFinanceEntry.organization_id == org_id,
    )
    if year:
        query = query.where(ProjectFinanceEntry.period_year == year)
    query = query.order_by(
        ProjectFinanceEntry.period_year,
        ProjectFinanceEntry.period_month,
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_global_cash_flow(
    db: AsyncSession, org_id: uuid.UUID, year: int | None = None
) -> list[ProjectCashFlowEntry]:
    """F094: Global Cash Flow aggregated."""
    query = select(ProjectCashFlowEntry).where(
        ProjectCashFlowEntry.organization_id == org_id,
    )
    if year:
        from sqlalchemy import extract
        query = query.where(
            extract("year", ProjectCashFlowEntry.transaction_date) == year
        )
    query = query.order_by(ProjectCashFlowEntry.transaction_date)
    result = await db.execute(query)
    return result.scalars().all()


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT JOB — F123
# ═══════════════════════════════════════════════════════════════════════════════


async def create_import_job(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> ImportJob:
    job = ImportJob(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(job)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="import_jobs",
        entity_id=job.id,
        new_values=model_to_dict(job),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return job


async def get_import_job(
    db: AsyncSession, org_id: uuid.UUID, job_id: uuid.UUID
) -> ImportJob | None:
    result = await db.execute(
        select(ImportJob).where(
            ImportJob.id == job_id,
            ImportJob.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


# ═══════════════════════════════════════════════════════════════════════════════
# WIKI — F144
# ═══════════════════════════════════════════════════════════════════════════════


async def list_wiki_posts(
    db: AsyncSession,
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[WikiPost], int]:
    query = select(WikiPost).where(
        WikiPost.project_id == project_id,
        WikiPost.organization_id == org_id,
    )
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(WikiPost.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_wiki_post(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WikiPost:
    post = WikiPost(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        author_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(post)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="wiki_posts",
        entity_id=post.id,
        new_values=model_to_dict(post),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return post


async def update_wiki_post(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    post_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WikiPost | None:
    result = await db.execute(
        select(WikiPost).where(
            WikiPost.id == post_id,
            WikiPost.organization_id == org_id,
        )
    )
    post = result.scalar_one_or_none()
    if post is None:
        return None

    old_values = model_to_dict(post)
    for key, val in data.items():
        if val is not None:
            setattr(post, key, val)
    post.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="wiki_posts",
        entity_id=post.id,
        old_values=old_values,
        new_values=model_to_dict(post),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return post


async def create_wiki_comment(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    post_id: uuid.UUID,
    data: dict,
) -> WikiComment:
    comment = WikiComment(
        id=uuid.uuid4(),
        post_id=post_id,
        organization_id=org_id,
        author_id=user_id,
        **data,
    )
    db.add(comment)
    await db.flush()
    return comment


async def list_wiki_comments(
    db: AsyncSession, org_id: uuid.UUID, post_id: uuid.UUID
) -> list[WikiComment]:
    result = await db.execute(
        select(WikiComment).where(
            WikiComment.post_id == post_id,
            WikiComment.organization_id == org_id,
        ).order_by(WikiComment.created_at)
    )
    return result.scalars().all()


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT REPORTS — F095
# ═══════════════════════════════════════════════════════════════════════════════


async def get_project_report(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict | None:
    """F095: Aggregated project report (schedule + financial + KPIs)."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    # Count tasks
    total_tasks_q = select(func.count()).select_from(Task).where(
        Task.project_id == project_id, Task.organization_id == org_id
    )
    total_tasks = (await db.execute(total_tasks_q)).scalar()

    completed_tasks_q = select(func.count()).select_from(Task).where(
        Task.project_id == project_id,
        Task.organization_id == org_id,
        Task.status == TaskStatus.DONE,
    )
    completed_tasks = (await db.execute(completed_tasks_q)).scalar()

    # Count open risks
    open_risks_q = select(func.count()).select_from(Risk).where(
        Risk.project_id == project_id,
        Risk.organization_id == org_id,
        Risk.status.in_([RiskStatus.IDENTIFIED, RiskStatus.ASSESSED, RiskStatus.MITIGATING]),
    )
    open_risks = (await db.execute(open_risks_q)).scalar()

    # Count open punch items
    open_punch_q = select(func.count()).select_from(PunchItem).where(
        PunchItem.project_id == project_id,
        PunchItem.organization_id == org_id,
        PunchItem.status.in_([PunchItemStatus.OPEN, PunchItemStatus.IN_PROGRESS]),
    )
    open_punch = (await db.execute(open_punch_q)).scalar()

    budget_variance = None
    if project.budget_allocated and project.budget_actual:
        budget_variance = project.budget_actual - project.budget_allocated

    return {
        "project_id": project.id,
        "project_name": project.name,
        "status": str(project.status).split(".")[-1] if "." in str(project.status) else str(project.status),
        "percent_complete": project.percent_complete,
        "planned_start": project.planned_start_date,
        "planned_end": project.planned_end_date,
        "actual_start": project.actual_start_date,
        "actual_end": project.actual_end_date,
        "budget_allocated": project.budget_allocated,
        "budget_actual": project.budget_actual,
        "budget_variance": budget_variance,
        "cpi": project.cpi,
        "spi": project.spi,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "open_risks": open_risks,
        "open_punch_items": open_punch,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENT PORTAL — F066
# ═══════════════════════════════════════════════════════════════════════════════


async def get_client_portal(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict | None:
    """F066: Aggregate CRM contact + project + invoices for client portal."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    # Fetch contact info from CRM
    contact_data = {"contact_name": None, "contact_email": None, "contact_phone": None}
    if project.contact_id:
        from app.crm.models import Contact
        result = await db.execute(
            select(Contact).where(
                Contact.id == project.contact_id,
                Contact.organization_id == org_id,
            )
        )
        contact = result.scalar_one_or_none()
        if contact:
            contact_data = {
                "contact_name": contact.company_name,
                "contact_email": contact.email,
                "contact_phone": contact.phone,
            }

    # Fetch contract data
    contract_data = {"contract_number": None, "contract_value": None}
    if project.contract_id:
        from app.pipeline.models import Contract
        result = await db.execute(
            select(Contract).where(
                Contract.id == project.contract_id,
                Contract.organization_id == org_id,
            )
        )
        contract = result.scalar_one_or_none()
        if contract:
            contract_data = {
                "contract_number": contract.contract_number,
                "contract_value": contract.total_value,
            }

    # Fetch invoices linked to the contract
    invoices_list = []
    total_invoiced = 0.0
    total_paid = 0.0
    if project.contract_id:
        from app.pipeline.models import Invoice
        result = await db.execute(
            select(Invoice).where(
                Invoice.contract_id == project.contract_id,
                Invoice.organization_id == org_id,
            ).order_by(Invoice.issue_date.desc())
        )
        for inv in result.scalars().all():
            inv_status = str(inv.status).split(".")[-1] if "." in str(inv.status) else str(inv.status)
            amount = float(inv.amount or 0)
            paid = float(inv.paid_amount or 0)
            invoices_list.append({
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "amount": amount,
                "paid_amount": paid,
                "status": inv_status,
                "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
            })
            total_invoiced += amount
            total_paid += paid

    proj_status = str(project.status).split(".")[-1] if "." in str(project.status) else str(project.status)

    return {
        "project_id": project.id,
        "project_name": project.name,
        "project_status": proj_status,
        "contact_id": project.contact_id,
        **contact_data,
        "contract_id": project.contract_id,
        **contract_data,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_outstanding": total_invoiced - total_paid,
        "percent_complete": project.percent_complete,
        "planned_end_date": project.planned_end_date,
        "invoices": invoices_list,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE ALLOCATION — F083
# ═══════════════════════════════════════════════════════════════════════════════


async def list_resource_allocations(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list:
    """F083: List resource allocations for a project."""
    from app.rm.models import ResourceAllocation
    result = await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.project_id == project_id,
            ResourceAllocation.organization_id == org_id,
        ).order_by(ResourceAllocation.start_date)
    )
    return result.scalars().all()


async def create_resource_allocation(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
):
    """F083: Allocate resource to project (sync with RM module)."""
    from app.rm.models import ResourceAllocation

    alloc = ResourceAllocation(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(alloc)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="resource_allocations",
        entity_id=alloc.id,
        new_values=model_to_dict(alloc),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return alloc


async def update_resource_allocation(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    alloc_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
):
    """F083: Update resource allocation."""
    from app.rm.models import ResourceAllocation
    result = await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.id == alloc_id,
            ResourceAllocation.organization_id == org_id,
        )
    )
    alloc = result.scalar_one_or_none()
    if alloc is None:
        return None

    old_values = model_to_dict(alloc)
    for key, val in data.items():
        if val is not None:
            setattr(alloc, key, val)
    alloc.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="resource_allocations",
        entity_id=alloc.id,
        old_values=old_values,
        new_values=model_to_dict(alloc),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return alloc


# ═══════════════════════════════════════════════════════════════════════════════
# INVESTOR DASHBOARD — F100
# ═══════════════════════════════════════════════════════════════════════════════


async def get_investor_dashboard(
    db: AsyncSession, org_id: uuid.UUID
) -> dict:
    """F100: Investor dashboard — aggregated project data + notifications."""
    # Count projects by status
    all_projects_q = select(Project).where(
        Project.organization_id == org_id,
        Project.is_deleted.is_(False),
    )
    result = await db.execute(all_projects_q)
    projects = result.scalars().all()

    total = len(projects)
    active = sum(1 for p in projects if str(p.status).split(".")[-1] in ("in_progress", "planning", "kickoff"))
    completed = sum(1 for p in projects if str(p.status).split(".")[-1] == "completed")

    budget_allocated = sum(p.budget_allocated or 0 for p in projects)
    budget_actual = sum(p.budget_actual or 0 for p in projects)

    cpi_values = [p.cpi for p in projects if p.cpi is not None]
    spi_values = [p.spi for p in projects if p.spi is not None]

    on_track = sum(1 for p in projects if p.health_indicator == "green")
    at_risk = sum(1 for p in projects if p.health_indicator == "yellow")
    delayed = sum(1 for p in projects if p.health_indicator == "red")

    pct_values = [p.percent_complete for p in projects if p.percent_complete is not None]

    # Notifications: projects that are delayed or over budget
    notifications = []
    for p in projects:
        status_str = str(p.status).split(".")[-1] if "." in str(p.status) else str(p.status)
        if p.health_indicator == "red":
            notifications.append({
                "type": "warning",
                "project_id": str(p.id),
                "project_name": p.name,
                "message": f"Project '{p.name}' is flagged RED.",
            })
        if p.budget_allocated and p.budget_actual and p.budget_actual > p.budget_allocated:
            notifications.append({
                "type": "budget_alert",
                "project_id": str(p.id),
                "project_name": p.name,
                "message": f"Project '{p.name}' is over budget.",
            })

    return {
        "total_projects": total,
        "active_projects": active,
        "completed_projects": completed,
        "total_budget_allocated": budget_allocated,
        "total_budget_actual": budget_actual,
        "total_budget_variance": budget_actual - budget_allocated,
        "avg_percent_complete": sum(pct_values) / len(pct_values) if pct_values else 0.0,
        "avg_cpi": sum(cpi_values) / len(cpi_values) if cpi_values else None,
        "avg_spi": sum(spi_values) / len(spi_values) if spi_values else None,
        "projects_on_track": on_track,
        "projects_at_risk": at_risk,
        "projects_delayed": delayed,
        "notifications": notifications,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY CAPACITY DASHBOARD — F130
# ═══════════════════════════════════════════════════════════════════════════════


async def get_company_capacity(
    db: AsyncSession, org_id: uuid.UUID
) -> dict:
    """F130: Company capacity — resources available vs allocated."""
    from app.rm.models import Employee, Equipment, ResourceAllocation, EmployeeStatus, EquipmentStatus, AllocationStatus

    # Employees
    emp_result = await db.execute(
        select(func.count()).select_from(Employee).where(
            Employee.organization_id == org_id,
            Employee.status == EmployeeStatus.ACTIVE,
            Employee.is_deleted.is_(False),
        )
    )
    total_employees = emp_result.scalar() or 0

    # Allocated employees (active allocations)
    alloc_emp_q = select(func.count(func.distinct(ResourceAllocation.employee_id))).where(
        ResourceAllocation.organization_id == org_id,
        ResourceAllocation.status.in_([AllocationStatus.PLANNED, AllocationStatus.CONFIRMED, AllocationStatus.ACTIVE]),
        ResourceAllocation.employee_id.isnot(None),
    )
    allocated_employees = (await db.execute(alloc_emp_q)).scalar() or 0

    # Equipment
    equip_result = await db.execute(
        select(func.count()).select_from(Equipment).where(
            Equipment.organization_id == org_id,
            Equipment.is_deleted.is_(False),
        )
    )
    total_equipment = equip_result.scalar() or 0

    alloc_equip_q = select(func.count(func.distinct(ResourceAllocation.equipment_id))).where(
        ResourceAllocation.organization_id == org_id,
        ResourceAllocation.status.in_([AllocationStatus.PLANNED, AllocationStatus.CONFIRMED, AllocationStatus.ACTIVE]),
        ResourceAllocation.equipment_id.isnot(None),
    )
    allocated_equipment = (await db.execute(alloc_equip_q)).scalar() or 0

    # Total allocated hours and cost
    alloc_totals = await db.execute(
        select(
            func.coalesce(func.sum(ResourceAllocation.allocated_hours), 0),
            func.coalesce(func.sum(ResourceAllocation.planned_cost), 0),
            func.count(ResourceAllocation.id),
        ).where(
            ResourceAllocation.organization_id == org_id,
            ResourceAllocation.status.in_([AllocationStatus.PLANNED, AllocationStatus.CONFIRMED, AllocationStatus.ACTIVE]),
        )
    )
    row = alloc_totals.one()
    total_hours = float(row[0])
    total_cost = float(row[1])

    # Conflicts
    conflicts_q = select(func.count()).select_from(ResourceAllocation).where(
        ResourceAllocation.organization_id == org_id,
        ResourceAllocation.has_conflict.is_(True),
    )
    conflicts = (await db.execute(conflicts_q)).scalar() or 0

    # Active projects
    active_q = select(func.count()).select_from(Project).where(
        Project.organization_id == org_id,
        Project.status.in_([ProjectStatus.IN_PROGRESS, ProjectStatus.PLANNING, ProjectStatus.KICKOFF]),
        Project.is_deleted.is_(False),
    )
    active_projects = (await db.execute(active_q)).scalar() or 0

    utilization = (allocated_employees / total_employees * 100) if total_employees > 0 else 0.0

    return {
        "total_employees": total_employees,
        "allocated_employees": allocated_employees,
        "available_employees": total_employees - allocated_employees,
        "total_equipment": total_equipment,
        "allocated_equipment": allocated_equipment,
        "available_equipment": total_equipment - allocated_equipment,
        "total_allocated_hours": total_hours,
        "total_planned_cost": total_cost,
        "utilization_rate": round(utilization, 1),
        "active_projects_count": active_projects,
        "allocations_with_conflicts": conflicts,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS MONITORING — F078
# ═══════════════════════════════════════════════════════════════════════════════


async def get_progress_monitoring(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict | None:
    """F078: Detailed progress monitoring with task breakdown and delay alerts."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    # Task counts by status
    for status_val in [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.DONE]:
        pass  # query below

    task_counts = {}
    for status_val in [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.DONE]:
        q = select(func.count()).select_from(Task).where(
            Task.project_id == project_id,
            Task.organization_id == org_id,
            Task.status == status_val,
        )
        task_counts[status_val.value] = (await db.execute(q)).scalar() or 0

    total_tasks = sum(task_counts.values())

    # Milestones
    milestone_total_q = select(func.count()).select_from(Task).where(
        Task.project_id == project_id,
        Task.organization_id == org_id,
        Task.is_milestone.is_(True),
    )
    total_milestones = (await db.execute(milestone_total_q)).scalar() or 0

    milestone_done_q = select(func.count()).select_from(Task).where(
        Task.project_id == project_id,
        Task.organization_id == org_id,
        Task.is_milestone.is_(True),
        Task.status == TaskStatus.DONE,
    )
    completed_milestones = (await db.execute(milestone_done_q)).scalar() or 0

    # Overdue tasks (planned_end < now and not done)
    now = datetime.now(timezone.utc)
    overdue_q = select(func.count()).select_from(Task).where(
        Task.project_id == project_id,
        Task.organization_id == org_id,
        Task.planned_end < now,
        Task.status != TaskStatus.DONE,
    )
    overdue_tasks = (await db.execute(overdue_q)).scalar() or 0

    # Schedule variance
    is_behind = False
    variance_days = None
    if project.planned_end_date:
        # Normalize timezone awareness for comparison (SQLite stores naive datetimes)
        planned_end = project.planned_end_date
        if planned_end.tzinfo is None:
            planned_end = planned_end.replace(tzinfo=timezone.utc)
        if project.actual_end_date:
            actual_end = project.actual_end_date
            if actual_end.tzinfo is None:
                actual_end = actual_end.replace(tzinfo=timezone.utc)
            delta = actual_end - planned_end
            variance_days = delta.days
            is_behind = variance_days > 0
        elif now > planned_end and str(project.status).split(".")[-1] not in ("completed", "cancelled"):
            delta = now - planned_end
            variance_days = delta.days
            is_behind = True

    proj_status = str(project.status).split(".")[-1] if "." in str(project.status) else str(project.status)

    return {
        "project_id": project.id,
        "project_name": project.name,
        "percent_complete": project.percent_complete,
        "planned_start": project.planned_start_date,
        "planned_end": project.planned_end_date,
        "actual_start": project.actual_start_date,
        "actual_end": project.actual_end_date,
        "cpi": project.cpi,
        "spi": project.spi,
        "total_tasks": total_tasks,
        "tasks_todo": task_counts.get("todo", 0),
        "tasks_in_progress": task_counts.get("in_progress", 0),
        "tasks_blocked": task_counts.get("blocked", 0),
        "tasks_done": task_counts.get("done", 0),
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "overdue_tasks": overdue_tasks,
        "is_behind_schedule": is_behind,
        "schedule_variance_days": variance_days,
        "trend_data": [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET CONTROL — F080
# ═══════════════════════════════════════════════════════════════════════════════


async def get_budget_control(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict | None:
    """F080: Detailed budget control with variance analysis and alerts."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    # Deviz aggregation
    deviz_q = select(
        func.coalesce(func.sum(DevizItem.estimated_total), 0).label("est_total"),
        func.coalesce(func.sum(DevizItem.actual_total), 0).label("act_total"),
        func.coalesce(func.sum(DevizItem.estimated_quantity * DevizItem.estimated_unit_price_labor), 0).label("labor_est"),
        func.coalesce(func.sum(DevizItem.actual_quantity * DevizItem.actual_unit_price_labor), 0).label("labor_act"),
        func.coalesce(func.sum(DevizItem.estimated_quantity * DevizItem.estimated_unit_price_material), 0).label("mat_est"),
        func.coalesce(func.sum(DevizItem.actual_quantity * DevizItem.actual_unit_price_material), 0).label("mat_act"),
        func.count(DevizItem.id).label("total_items"),
    ).where(
        DevizItem.project_id == project_id,
        DevizItem.organization_id == org_id,
    )
    row = (await db.execute(deviz_q)).one()

    # Over-budget items count
    over_q = select(func.count()).select_from(DevizItem).where(
        DevizItem.project_id == project_id,
        DevizItem.organization_id == org_id,
        DevizItem.over_budget_alert.is_(True),
    )
    items_over = (await db.execute(over_q)).scalar() or 0

    budget_alloc = project.budget_allocated or 0
    budget_actual = project.budget_actual or 0
    budget_remaining = budget_alloc - budget_actual if budget_alloc else None
    budget_variance = budget_actual - budget_alloc if budget_alloc else None
    budget_variance_pct = (budget_actual / budget_alloc * 100) if budget_alloc else None
    is_over = budget_actual > budget_alloc if budget_alloc else False

    # Simple burn rate: budget_actual / months elapsed
    burn_rate = None
    if project.actual_start_date and budget_actual > 0:
        months = max(1, (datetime.now(timezone.utc) - project.actual_start_date).days / 30)
        burn_rate = round(budget_actual / months, 2)

    return {
        "project_id": project.id,
        "project_name": project.name,
        "currency": project.currency,
        "budget_allocated": project.budget_allocated,
        "budget_committed": project.budget_committed,
        "budget_actual": project.budget_actual,
        "budget_remaining": budget_remaining,
        "budget_variance": budget_variance,
        "budget_variance_percent": round(budget_variance_pct, 1) if budget_variance_pct else None,
        "cpi": project.cpi,
        "spi": project.spi,
        "total_estimated": float(row.est_total),
        "total_actual": float(row.act_total),
        "deviz_variance": float(row.act_total) - float(row.est_total),
        "items_over_budget": items_over,
        "total_deviz_items": int(row.total_items),
        "labor_cost_estimated": float(row.labor_est),
        "labor_cost_actual": float(row.labor_act),
        "material_cost_estimated": float(row.mat_est),
        "material_cost_actual": float(row.mat_act),
        "is_over_budget": is_over,
        "budget_alert_threshold": 0.9,
        "burn_rate_monthly": burn_rate,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ML DATA EXPORT — F105
# ═══════════════════════════════════════════════════════════════════════════════


async def get_ml_export_status(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict:
    """F105: Get ML data export status for a project."""
    impact = await get_energy_impact(db, org_id, project_id)

    validation_errors = []
    if impact is None:
        return {
            "project_id": project_id,
            "has_energy_impact": False,
            "ml_data_mapping": None,
            "ml_dataset_exported": False,
            "ml_export_date": None,
            "is_verified": False,
            "validation_errors": ["No energy impact data found for this project."],
        }

    # Validate required fields for ML export
    if impact.pre_kwh_annual is None:
        validation_errors.append("pre_kwh_annual is required")
    if impact.post_kwh_annual is None:
        validation_errors.append("post_kwh_annual is required")
    if impact.total_area_sqm is None:
        validation_errors.append("total_area_sqm is required")

    return {
        "project_id": project_id,
        "has_energy_impact": True,
        "ml_data_mapping": impact.ml_data_mapping,
        "ml_dataset_exported": impact.ml_dataset_exported,
        "ml_export_date": impact.ml_export_date,
        "is_verified": impact.is_verified,
        "validation_errors": validation_errors,
    }


async def trigger_ml_export(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    mapping_config: dict | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    """F105: Trigger ML data export — validate mapping and mark as exported."""
    impact = await get_energy_impact(db, org_id, project_id)
    if impact is None:
        return {"success": False, "error": "No energy impact data found."}

    old_values = model_to_dict(impact)

    if mapping_config:
        impact.ml_data_mapping = mapping_config
    impact.ml_dataset_exported = True
    impact.ml_export_date = datetime.now(timezone.utc)
    impact.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="energy_impacts",
        entity_id=impact.id,
        old_values=old_values,
        new_values=model_to_dict(impact),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    await db.refresh(impact)

    return {
        "success": True,
        "project_id": project_id,
        "has_energy_impact": True,
        "ml_data_mapping": impact.ml_data_mapping,
        "ml_dataset_exported": True,
        "ml_export_date": impact.ml_export_date,
        "is_verified": impact.is_verified,
        "validation_errors": [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# WORK TRACKER — F125
# ═══════════════════════════════════════════════════════════════════════════════


async def get_work_tracker(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> dict | None:
    """F125: Work tracker — quantities/costs estimated vs actual per deviz item."""
    project = await get_project(db, org_id, project_id)
    if project is None:
        return None

    result = await db.execute(
        select(DevizItem).where(
            DevizItem.project_id == project_id,
            DevizItem.organization_id == org_id,
        ).order_by(DevizItem.sort_order)
    )
    items = result.scalars().all()

    tracker_items = []
    total_est_qty = 0.0
    total_act_qty = 0.0
    total_est_cost = 0.0
    total_act_cost = 0.0
    over_count = 0
    under_count = 0

    for item in items:
        qty_var = item.actual_quantity - item.estimated_quantity
        cost_var = item.actual_total - item.estimated_total
        is_over = item.over_budget_alert

        total_est_qty += item.estimated_quantity
        total_act_qty += item.actual_quantity
        total_est_cost += item.estimated_total
        total_act_cost += item.actual_total

        if is_over:
            over_count += 1
        elif item.actual_total > 0 and item.actual_total <= item.estimated_total:
            under_count += 1

        tracker_items.append({
            "id": item.id,
            "code": item.code,
            "description": item.description,
            "unit_of_measure": item.unit_of_measure,
            "estimated_quantity": item.estimated_quantity,
            "actual_quantity": item.actual_quantity,
            "quantity_variance": qty_var,
            "estimated_total": item.estimated_total,
            "actual_total": item.actual_total,
            "cost_variance": cost_var,
            "over_budget": is_over,
        })

    return {
        "project_id": project.id,
        "project_name": project.name,
        "currency": project.currency,
        "total_estimated_quantity": total_est_qty,
        "total_actual_quantity": total_act_qty,
        "quantity_variance": total_act_qty - total_est_qty,
        "total_estimated_cost": total_est_cost,
        "total_actual_cost": total_act_cost,
        "cost_variance": total_act_cost - total_est_cost,
        "items": tracker_items,
        "items_over_budget": over_count,
        "items_under_budget": under_count,
        "total_items": len(tracker_items),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# WARRANTY — F086 (completion)
# ═══════════════════════════════════════════════════════════════════════════════


async def list_warranties(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID
) -> list[Warranty]:
    result = await db.execute(
        select(Warranty).where(
            Warranty.project_id == project_id,
            Warranty.organization_id == org_id,
        ).order_by(Warranty.end_date)
    )
    return result.scalars().all()


async def create_warranty(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Warranty:
    warranty = Warranty(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        **data,
    )
    db.add(warranty)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="warranties",
        entity_id=warranty.id,
        new_values=model_to_dict(warranty),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return warranty


async def update_warranty(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    warranty_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Warranty | None:
    result = await db.execute(
        select(Warranty).where(
            Warranty.id == warranty_id,
            Warranty.organization_id == org_id,
        )
    )
    warranty = result.scalar_one_or_none()
    if warranty is None:
        return None

    old_values = model_to_dict(warranty)
    for key, val in data.items():
        if val is not None:
            setattr(warranty, key, val)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="warranties",
        entity_id=warranty.id,
        old_values=old_values,
        new_values=model_to_dict(warranty),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return warranty


async def create_reception(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> WikiPost:
    """F086: Create formal reception (PV recepție) stored as wiki document."""
    reception_data = {
        "reception_type": data.get("reception_type", "partial"),
        "reception_date": data.get("reception_date"),
        "committee_members": data.get("committee_members"),
        "observations": data.get("observations"),
        "is_accepted": data.get("is_accepted", True),
        "conditions": data.get("conditions"),
        "documents": data.get("documents"),
    }

    post = WikiPost(
        id=uuid.uuid4(),
        project_id=project_id,
        organization_id=org_id,
        author_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        post_type="document",
        is_official=True,
        title=f"PV Recepție {data.get('reception_type', 'partial').capitalize()} — {data.get('reception_date', '')}",
        content=str(reception_data),
        document_type_badge="PV Recepție",
    )
    db.add(post)
    await db.flush()

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="wiki_posts",
        entity_id=post.id,
        new_values=model_to_dict(post),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return post


# ═══════════════════════════════════════════════════════════════════════════════
# WIKI — F145, F146 (department files & official documents)
# ═══════════════════════════════════════════════════════════════════════════════


async def list_department_files(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    department: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[WikiPost], int]:
    """F145: List files per department."""
    query = select(WikiPost).where(
        WikiPost.organization_id == org_id,
        WikiPost.post_type == "file",
    )
    if department:
        query = query.where(WikiPost.department == department)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(WikiPost.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def list_official_documents(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    department: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[WikiPost], int]:
    """F146: List official documents per department."""
    query = select(WikiPost).where(
        WikiPost.organization_id == org_id,
        WikiPost.is_official.is_(True),
    )
    if department:
        query = query.where(WikiPost.department == department)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(WikiPost.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total
