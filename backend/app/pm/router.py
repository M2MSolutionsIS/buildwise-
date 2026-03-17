"""
PM module router — F063, F066, F069–F080, F083, F084, F086, F088,
F090, F091–F095, F100, F101, F103, F105, F123, F125, F130, F144, F161.

All endpoints require JWT authentication and enforce multi-tenant isolation
via organization_id from the authenticated user.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.pm import service
from app.pm.schemas import (
    CashFlowCreate,
    CashFlowOut,
    DailyReportCreate,
    DailyReportOut,
    DevizItemCreate,
    DevizItemOut,
    DevizItemUpdate,
    EnergyImpactCreate,
    EnergyImpactOut,
    EnergyPortfolioOut,
    ImportJobCreate,
    ImportJobOut,
    MaterialConsumptionCreate,
    MaterialConsumptionOut,
    ProjectCancelRequest,
    ProjectCloseRequest,
    ProjectCreate,
    ProjectFinanceCreate,
    ProjectFinanceOut,
    ProjectListOut,
    ProjectOut,
    ProjectReportOut,
    ProjectUpdate,
    PunchItemCreate,
    PunchItemOut,
    PunchItemUpdate,
    RiskCreate,
    RiskOut,
    RiskUpdate,
    SubcontractorCreate,
    SubcontractorOut,
    SubcontractorUpdate,
    TaskCreate,
    TaskDependencyCreate,
    TaskDependencyOut,
    TaskOut,
    TaskUpdate,
    TimesheetCreate,
    TimesheetOut,
    TimesheetUpdate,
    WBSNodeCreate,
    WBSNodeOut,
    WBSNodeUpdate,
    WikiCommentCreate,
    WikiCommentOut,
    WikiPostCreate,
    WikiPostOut,
    WikiPostUpdate,
    WorkSituationCreate,
    WorkSituationOut,
    WorkSituationUpdate,
)
from app.system.schemas import ApiResponse, Meta

pm_router = APIRouter(prefix="/api/v1/pm", tags=["Project Management"])


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECTS — F063, F101, F103
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects", response_model=ApiResponse)
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    search: str | None = None,
    project_type: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F101: List projects — portfolio view."""
    projects, total = await service.list_projects(
        db, current_user.organization_id,
        page=page, per_page=per_page,
        status=status, search=search, project_type=project_type,
    )
    return ApiResponse(
        data=[ProjectListOut.model_validate(p) for p in projects],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects", response_model=ApiResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F063: Create a new project."""
    req_info = await get_request_info(request)
    project = await service.create_project(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ProjectOut.model_validate(project))


@pm_router.get("/projects/{project_id}", response_model=ApiResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F063: Get project detail."""
    project = await service.get_project(db, current_user.organization_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectOut.model_validate(project))


@pm_router.put("/projects/{project_id}", response_model=ApiResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F063/F078: Update project (including progress monitoring)."""
    req_info = await get_request_info(request)
    project = await service.update_project(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectOut.model_validate(project))


@pm_router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a project."""
    req_info = await get_request_info(request)
    deleted = await service.delete_project(
        db, current_user.organization_id, current_user.id, project_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")


@pm_router.post("/projects/{project_id}/close", response_model=ApiResponse)
async def close_project(
    project_id: uuid.UUID,
    body: ProjectCloseRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F103: Close project with grace period."""
    req_info = await get_request_info(request)
    project = await service.close_project(
        db, current_user.organization_id, current_user.id, project_id,
        grace_period_days=body.grace_period_days,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectOut.model_validate(project))


@pm_router.post("/projects/{project_id}/cancel", response_model=ApiResponse)
async def cancel_project(
    project_id: uuid.UUID,
    body: ProjectCancelRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F103: Cancel project with reason."""
    req_info = await get_request_info(request)
    project = await service.cancel_project(
        db, current_user.organization_id, current_user.id, project_id,
        reason=body.cancellation_reason,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectOut.model_validate(project))


@pm_router.get("/completed-projects", response_model=ApiResponse)
async def list_completed_projects(
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F090: Completed projects database."""
    projects, total = await service.list_completed_projects(
        db, current_user.organization_id, page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[ProjectListOut.model_validate(p) for p in projects],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WBS — F069
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/wbs", response_model=ApiResponse)
async def list_wbs(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F069: List WBS nodes (hierarchical structure)."""
    nodes = await service.list_wbs_nodes(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[WBSNodeOut.model_validate(n) for n in nodes],
        meta=Meta(total=len(nodes)),
    )


@pm_router.post("/projects/{project_id}/wbs", response_model=ApiResponse, status_code=201)
async def create_wbs(
    project_id: uuid.UUID,
    body: WBSNodeCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F069: Create a WBS node."""
    req_info = await get_request_info(request)
    node = await service.create_wbs_node(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=WBSNodeOut.model_validate(node))


@pm_router.put("/wbs/{node_id}", response_model=ApiResponse)
async def update_wbs(
    node_id: uuid.UUID,
    body: WBSNodeUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F069: Update a WBS node."""
    req_info = await get_request_info(request)
    node = await service.update_wbs_node(
        db, current_user.organization_id, current_user.id, node_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if node is None:
        raise HTTPException(status_code=404, detail="WBS node not found")
    return ApiResponse(data=WBSNodeOut.model_validate(node))


@pm_router.delete("/wbs/{node_id}", status_code=204)
async def delete_wbs(
    node_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F069: Delete a WBS node."""
    req_info = await get_request_info(request)
    deleted = await service.delete_wbs_node(
        db, current_user.organization_id, current_user.id, node_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="WBS node not found")


# ═══════════════════════════════════════════════════════════════════════════════
# TASKS / GANTT — F070, F073
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/tasks", response_model=ApiResponse)
async def list_tasks(
    project_id: uuid.UUID,
    page: int = 1,
    per_page: int = 100,
    status: str | None = None,
    assigned_to: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F070: List tasks (Gantt data)."""
    tasks, total = await service.list_tasks(
        db, current_user.organization_id, project_id,
        status=status, assigned_to=assigned_to,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[TaskOut.model_validate(t) for t in tasks],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects/{project_id}/tasks", response_model=ApiResponse, status_code=201)
async def create_task(
    project_id: uuid.UUID,
    body: TaskCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F070/F073: Create a task."""
    req_info = await get_request_info(request)
    task = await service.create_task(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=TaskOut.model_validate(task))


@pm_router.get("/tasks/{task_id}", response_model=ApiResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F073: Get task detail with dependencies."""
    task = await service.get_task(db, current_user.organization_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return ApiResponse(data=TaskOut.model_validate(task))


@pm_router.put("/tasks/{task_id}", response_model=ApiResponse)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F073: Update task (including status transitions)."""
    req_info = await get_request_info(request)
    try:
        task = await service.update_task(
            db, current_user.organization_id, current_user.id, task_id,
            body.model_dump(exclude_unset=True),
            ip_address=req_info["ip_address"],
            user_agent=req_info["user_agent"],
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return ApiResponse(data=TaskOut.model_validate(task))


@pm_router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    req_info = await get_request_info(request)
    deleted = await service.delete_task(
        db, current_user.organization_id, current_user.id, task_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@pm_router.post("/tasks/{task_id}/dependencies", response_model=ApiResponse, status_code=201)
async def add_dependency(
    task_id: uuid.UUID,
    body: TaskDependencyCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F070: Add task dependency."""
    dep = await service.add_task_dependency(
        db, current_user.organization_id, task_id,
        body.model_dump(exclude_unset=True),
    )
    return ApiResponse(data=TaskDependencyOut.model_validate(dep))


@pm_router.delete("/tasks/{task_id}/dependencies/{dep_id}", status_code=204)
async def remove_dependency(
    task_id: uuid.UUID,
    dep_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F070: Remove task dependency."""
    deleted = await service.remove_task_dependency(db, dep_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dependency not found")


# ═══════════════════════════════════════════════════════════════════════════════
# DEVIZ — F071, F125
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/deviz", response_model=ApiResponse)
async def list_deviz(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F071: List deviz items."""
    items = await service.list_deviz_items(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[DevizItemOut.model_validate(i) for i in items],
        meta=Meta(total=len(items)),
    )


@pm_router.post("/projects/{project_id}/deviz", response_model=ApiResponse, status_code=201)
async def create_deviz(
    project_id: uuid.UUID,
    body: DevizItemCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F071: Create a deviz item."""
    req_info = await get_request_info(request)
    item = await service.create_deviz_item(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=DevizItemOut.model_validate(item))


@pm_router.put("/deviz/{item_id}", response_model=ApiResponse)
async def update_deviz(
    item_id: uuid.UUID,
    body: DevizItemUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F071/F125: Update deviz item (Work Tracker)."""
    req_info = await get_request_info(request)
    item = await service.update_deviz_item(
        db, current_user.organization_id, current_user.id, item_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Deviz item not found")
    return ApiResponse(data=DevizItemOut.model_validate(item))


@pm_router.delete("/deviz/{item_id}", status_code=204)
async def delete_deviz(
    item_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F071: Delete deviz item."""
    req_info = await get_request_info(request)
    deleted = await service.delete_deviz_item(
        db, current_user.organization_id, current_user.id, item_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Deviz item not found")


# ═══════════════════════════════════════════════════════════════════════════════
# TIMESHEETS — F072
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/timesheets", response_model=ApiResponse)
async def list_timesheets(
    project_id: uuid.UUID,
    page: int = 1,
    per_page: int = 50,
    user_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F072: List timesheet entries."""
    entries, total = await service.list_timesheets(
        db, current_user.organization_id, project_id,
        page=page, per_page=per_page, user_id_filter=user_id,
    )
    return ApiResponse(
        data=[TimesheetOut.model_validate(e) for e in entries],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects/{project_id}/timesheets", response_model=ApiResponse, status_code=201)
async def create_timesheet(
    project_id: uuid.UUID,
    body: TimesheetCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F072: Log hours on a task."""
    req_info = await get_request_info(request)
    entry = await service.create_timesheet(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=TimesheetOut.model_validate(entry))


@pm_router.put("/timesheets/{entry_id}", response_model=ApiResponse)
async def update_timesheet(
    entry_id: uuid.UUID,
    body: TimesheetUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F072: Update timesheet entry."""
    req_info = await get_request_info(request)
    entry = await service.update_timesheet(
        db, current_user.organization_id, current_user.id, entry_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Timesheet entry not found")
    return ApiResponse(data=TimesheetOut.model_validate(entry))


@pm_router.post("/timesheets/{entry_id}/approve", response_model=ApiResponse)
async def approve_timesheet(
    entry_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F072: Approve timesheet entry (PM action)."""
    req_info = await get_request_info(request)
    entry = await service.approve_timesheet(
        db, current_user.organization_id, current_user.id, entry_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Timesheet entry not found")
    return ApiResponse(data=TimesheetOut.model_validate(entry))


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIALS — F074
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/materials", response_model=ApiResponse)
async def list_materials(
    project_id: uuid.UUID,
    page: int = 1,
    per_page: int = 50,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F074: List material consumption records."""
    entries, total = await service.list_material_consumptions(
        db, current_user.organization_id, project_id,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[MaterialConsumptionOut.model_validate(e) for e in entries],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects/{project_id}/materials", response_model=ApiResponse, status_code=201)
async def create_material(
    project_id: uuid.UUID,
    body: MaterialConsumptionCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F074: Record material consumption."""
    req_info = await get_request_info(request)
    entry = await service.create_material_consumption(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=MaterialConsumptionOut.model_validate(entry))


# ═══════════════════════════════════════════════════════════════════════════════
# SUBCONTRACTORS — F075
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/subcontractors", response_model=ApiResponse)
async def list_subcontractors(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F075: List subcontractors."""
    subs = await service.list_subcontractors(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[SubcontractorOut.model_validate(s) for s in subs],
        meta=Meta(total=len(subs)),
    )


@pm_router.post("/projects/{project_id}/subcontractors", response_model=ApiResponse, status_code=201)
async def create_subcontractor(
    project_id: uuid.UUID,
    body: SubcontractorCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F075: Add subcontractor."""
    req_info = await get_request_info(request)
    sub = await service.create_subcontractor(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=SubcontractorOut.model_validate(sub))


@pm_router.put("/subcontractors/{sub_id}", response_model=ApiResponse)
async def update_subcontractor(
    sub_id: uuid.UUID,
    body: SubcontractorUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F075: Update subcontractor."""
    req_info = await get_request_info(request)
    sub = await service.update_subcontractor(
        db, current_user.organization_id, current_user.id, sub_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if sub is None:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    return ApiResponse(data=SubcontractorOut.model_validate(sub))


# ═══════════════════════════════════════════════════════════════════════════════
# DAILY REPORTS — F077
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/daily-reports", response_model=ApiResponse)
async def list_daily_reports(
    project_id: uuid.UUID,
    page: int = 1,
    per_page: int = 30,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F077: List daily site reports."""
    reports, total = await service.list_daily_reports(
        db, current_user.organization_id, project_id,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[DailyReportOut.model_validate(r) for r in reports],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects/{project_id}/daily-reports", response_model=ApiResponse, status_code=201)
async def create_daily_report(
    project_id: uuid.UUID,
    body: DailyReportCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F077: Create daily site report."""
    req_info = await get_request_info(request)
    report = await service.create_daily_report(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=DailyReportOut.model_validate(report))


# ═══════════════════════════════════════════════════════════════════════════════
# WORK SITUATIONS — F079
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/work-situations", response_model=ApiResponse)
async def list_work_situations(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F079: List work situations (SdL)."""
    sdls = await service.list_work_situations(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[WorkSituationOut.model_validate(s) for s in sdls],
        meta=Meta(total=len(sdls)),
    )


@pm_router.post("/projects/{project_id}/work-situations", response_model=ApiResponse, status_code=201)
async def create_work_situation(
    project_id: uuid.UUID,
    body: WorkSituationCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F079: Create work situation."""
    req_info = await get_request_info(request)
    sdl = await service.create_work_situation(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=WorkSituationOut.model_validate(sdl))


@pm_router.put("/work-situations/{sdl_id}", response_model=ApiResponse)
async def update_work_situation(
    sdl_id: uuid.UUID,
    body: WorkSituationUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F079: Update work situation."""
    req_info = await get_request_info(request)
    sdl = await service.update_work_situation(
        db, current_user.organization_id, current_user.id, sdl_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if sdl is None:
        raise HTTPException(status_code=404, detail="Work situation not found")
    return ApiResponse(data=WorkSituationOut.model_validate(sdl))


@pm_router.post("/work-situations/{sdl_id}/approve", response_model=ApiResponse)
async def approve_work_situation(
    sdl_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F079: Approve work situation."""
    req_info = await get_request_info(request)
    sdl = await service.approve_work_situation(
        db, current_user.organization_id, current_user.id, sdl_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if sdl is None:
        raise HTTPException(status_code=404, detail="Work situation not found")
    return ApiResponse(data=WorkSituationOut.model_validate(sdl))


# ═══════════════════════════════════════════════════════════════════════════════
# RISK REGISTER — F084
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/risks", response_model=ApiResponse)
async def list_risks(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F084: List project risks."""
    risks = await service.list_risks(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[RiskOut.model_validate(r) for r in risks],
        meta=Meta(total=len(risks)),
    )


@pm_router.post("/projects/{project_id}/risks", response_model=ApiResponse, status_code=201)
async def create_risk(
    project_id: uuid.UUID,
    body: RiskCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F084: Create a risk."""
    req_info = await get_request_info(request)
    risk = await service.create_risk(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=RiskOut.model_validate(risk))


@pm_router.put("/risks/{risk_id}", response_model=ApiResponse)
async def update_risk(
    risk_id: uuid.UUID,
    body: RiskUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F084: Update a risk."""
    req_info = await get_request_info(request)
    risk = await service.update_risk(
        db, current_user.organization_id, current_user.id, risk_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return ApiResponse(data=RiskOut.model_validate(risk))


@pm_router.delete("/risks/{risk_id}", status_code=204)
async def delete_risk(
    risk_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F084: Delete a risk."""
    req_info = await get_request_info(request)
    deleted = await service.delete_risk(
        db, current_user.organization_id, current_user.id, risk_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Risk not found")


# ═══════════════════════════════════════════════════════════════════════════════
# PUNCH ITEMS — F086
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/punch-items", response_model=ApiResponse)
async def list_punch_items(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F086: List punch items."""
    items = await service.list_punch_items(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[PunchItemOut.model_validate(i) for i in items],
        meta=Meta(total=len(items)),
    )


@pm_router.post("/projects/{project_id}/punch-items", response_model=ApiResponse, status_code=201)
async def create_punch_item(
    project_id: uuid.UUID,
    body: PunchItemCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F086: Create punch item."""
    req_info = await get_request_info(request)
    item = await service.create_punch_item(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=PunchItemOut.model_validate(item))


@pm_router.put("/punch-items/{item_id}", response_model=ApiResponse)
async def update_punch_item(
    item_id: uuid.UUID,
    body: PunchItemUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F086: Update punch item."""
    req_info = await get_request_info(request)
    item = await service.update_punch_item(
        db, current_user.organization_id, current_user.id, item_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Punch item not found")
    return ApiResponse(data=PunchItemOut.model_validate(item))


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY IMPACT — F088, F090, F105, F161
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/energy-impact", response_model=ApiResponse)
async def get_energy_impact(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F088: Get energy impact for a project."""
    impact = await service.get_energy_impact(db, current_user.organization_id, project_id)
    if impact is None:
        return ApiResponse(data=None)
    return ApiResponse(data=EnergyImpactOut.model_validate(impact))


@pm_router.put("/projects/{project_id}/energy-impact", response_model=ApiResponse)
async def upsert_energy_impact(
    project_id: uuid.UUID,
    body: EnergyImpactCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F088/F105: Create or update energy impact measurements."""
    req_info = await get_request_info(request)
    impact = await service.upsert_energy_impact(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=EnergyImpactOut.model_validate(impact))


@pm_router.get("/energy-portfolio", response_model=ApiResponse)
async def get_energy_portfolio(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F161: Aggregated energy portfolio across all projects."""
    data = await service.get_energy_portfolio(db, current_user.organization_id)
    return ApiResponse(data=EnergyPortfolioOut(**data))


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT FINANCE — F091, F092, F093, F094
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/finance", response_model=ApiResponse)
async def list_finance(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F091: Get project P&L entries."""
    entries = await service.list_finance_entries(
        db, current_user.organization_id, project_id
    )
    return ApiResponse(
        data=[ProjectFinanceOut.model_validate(e) for e in entries],
        meta=Meta(total=len(entries)),
    )


@pm_router.post("/projects/{project_id}/finance", response_model=ApiResponse, status_code=201)
async def create_finance(
    project_id: uuid.UUID,
    body: ProjectFinanceCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F091: Create P&L entry."""
    entry = await service.create_finance_entry(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
    )
    return ApiResponse(data=ProjectFinanceOut.model_validate(entry))


@pm_router.get("/projects/{project_id}/cash-flow", response_model=ApiResponse)
async def list_cash_flow(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F092: Get project cash flow entries."""
    entries = await service.list_cash_flow_entries(
        db, current_user.organization_id, project_id
    )
    return ApiResponse(
        data=[CashFlowOut.model_validate(e) for e in entries],
        meta=Meta(total=len(entries)),
    )


@pm_router.post("/projects/{project_id}/cash-flow", response_model=ApiResponse, status_code=201)
async def create_cash_flow(
    project_id: uuid.UUID,
    body: CashFlowCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F092: Create cash flow entry."""
    entry = await service.create_cash_flow_entry(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
    )
    return ApiResponse(data=CashFlowOut.model_validate(entry))


@pm_router.get("/global-pl", response_model=ApiResponse)
async def get_global_pl(
    year: int | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F093: Global P&L aggregated across all projects."""
    entries = await service.get_global_pl(
        db, current_user.organization_id, year=year
    )
    return ApiResponse(
        data=[ProjectFinanceOut.model_validate(e) for e in entries],
        meta=Meta(total=len(entries)),
    )


@pm_router.get("/global-cash-flow", response_model=ApiResponse)
async def get_global_cash_flow(
    year: int | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F094: Global Cash Flow aggregated."""
    entries = await service.get_global_cash_flow(
        db, current_user.organization_id, year=year
    )
    return ApiResponse(
        data=[CashFlowOut.model_validate(e) for e in entries],
        meta=Meta(total=len(entries)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT ENGINE — F123
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.post("/projects/{project_id}/import", response_model=ApiResponse, status_code=201)
async def create_import_job(
    project_id: uuid.UUID,
    body: ImportJobCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F123: Create an import job."""
    req_info = await get_request_info(request)
    job = await service.create_import_job(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ImportJobOut.model_validate(job))


@pm_router.get("/import-jobs/{job_id}", response_model=ApiResponse)
async def get_import_job(
    job_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F123: Get import job status."""
    job = await service.get_import_job(db, current_user.organization_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Import job not found")
    return ApiResponse(data=ImportJobOut.model_validate(job))


# ═══════════════════════════════════════════════════════════════════════════════
# WIKI — F144
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/wiki", response_model=ApiResponse)
async def list_wiki_posts(
    project_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F144: List wiki posts (timeline)."""
    posts, total = await service.list_wiki_posts(
        db, current_user.organization_id, project_id,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[WikiPostOut.model_validate(p) for p in posts],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pm_router.post("/projects/{project_id}/wiki", response_model=ApiResponse, status_code=201)
async def create_wiki_post(
    project_id: uuid.UUID,
    body: WikiPostCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F144: Create wiki post."""
    req_info = await get_request_info(request)
    post = await service.create_wiki_post(
        db, current_user.organization_id, current_user.id, project_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=WikiPostOut.model_validate(post))


@pm_router.put("/wiki/{post_id}", response_model=ApiResponse)
async def update_wiki_post(
    post_id: uuid.UUID,
    body: WikiPostUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F144: Update wiki post."""
    req_info = await get_request_info(request)
    post = await service.update_wiki_post(
        db, current_user.organization_id, current_user.id, post_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if post is None:
        raise HTTPException(status_code=404, detail="Wiki post not found")
    return ApiResponse(data=WikiPostOut.model_validate(post))


@pm_router.get("/wiki/{post_id}/comments", response_model=ApiResponse)
async def list_wiki_comments(
    post_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F144: List comments for a wiki post."""
    comments = await service.list_wiki_comments(
        db, current_user.organization_id, post_id
    )
    return ApiResponse(
        data=[WikiCommentOut.model_validate(c) for c in comments],
        meta=Meta(total=len(comments)),
    )


@pm_router.post("/wiki/{post_id}/comments", response_model=ApiResponse, status_code=201)
async def create_wiki_comment(
    post_id: uuid.UUID,
    body: WikiCommentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F144: Add comment to wiki post (supports threading via parent_comment_id)."""
    comment = await service.create_wiki_comment(
        db, current_user.organization_id, current_user.id, post_id,
        body.model_dump(exclude_unset=True),
    )
    return ApiResponse(data=WikiCommentOut.model_validate(comment))


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT REPORTS — F095
# ═══════════════════════════════════════════════════════════════════════════════


@pm_router.get("/projects/{project_id}/reports", response_model=ApiResponse)
async def get_project_reports(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F095: Get aggregated project report (schedule + financial + KPIs)."""
    report = await service.get_project_report(
        db, current_user.organization_id, project_id
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectReportOut(**report))
