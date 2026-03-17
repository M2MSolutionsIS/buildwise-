"""
RM (Resource Management) module router — F107–F122.

Endpoints:
  # Employees — F107
  GET    /api/v1/rm/employees               — List employees
  POST   /api/v1/rm/employees               — Create employee
  GET    /api/v1/rm/employees/{id}           — Get employee detail
  PUT    /api/v1/rm/employees/{id}           — Update employee
  DELETE /api/v1/rm/employees/{id}           — Soft-delete employee

  # HR Planning — F108
  GET    /api/v1/rm/hr-planning              — List HR planning entries
  POST   /api/v1/rm/hr-planning              — Create HR planning entry
  PUT    /api/v1/rm/hr-planning/{id}         — Update HR planning entry

  # Leaves — F109
  GET    /api/v1/rm/leaves                   — List leaves
  POST   /api/v1/rm/leaves                   — Create leave request
  PUT    /api/v1/rm/leaves/{id}              — Update (approve/reject)
  GET    /api/v1/rm/employees/{id}/availability — Check availability

  # Equipment
  GET    /api/v1/rm/equipment                — List equipment
  POST   /api/v1/rm/equipment                — Create equipment
  GET    /api/v1/rm/equipment/{id}           — Get equipment detail
  PUT    /api/v1/rm/equipment/{id}           — Update equipment
  DELETE /api/v1/rm/equipment/{id}           — Delete equipment

  # Materials — F114
  GET    /api/v1/rm/materials                — List materials
  POST   /api/v1/rm/materials                — Create material stock
  PUT    /api/v1/rm/materials/{id}           — Update material stock

  # Procurement — F112, F113
  GET    /api/v1/rm/procurement              — List procurement orders
  POST   /api/v1/rm/procurement              — Create procurement order
  GET    /api/v1/rm/procurement/{id}         — Get procurement order
  PUT    /api/v1/rm/procurement/{id}         — Update procurement order
  GET    /api/v1/rm/procurement/{id}/documents — List documents
  POST   /api/v1/rm/procurement/{id}/documents — Add document (invoice/NIR)

  # Resource Allocation — F117, F118, F119, F120
  GET    /api/v1/rm/allocations              — List allocations
  POST   /api/v1/rm/allocations              — Create allocation
  PUT    /api/v1/rm/allocations/{id}         — Update allocation
  DELETE /api/v1/rm/allocations/{id}         — Delete allocation
  GET    /api/v1/rm/projects/{id}/consumption — F118: Resource consumption
  GET    /api/v1/rm/projects/{id}/efficiency  — F119: Project efficiency

  # Budget — F115, F116
  GET    /api/v1/rm/budgets                  — List budget entries
  POST   /api/v1/rm/budgets                  — Create budget entry
  PUT    /api/v1/rm/budgets/{id}             — Update budget entry
  GET    /api/v1/rm/cost-analysis            — F116: Cost analysis

  # Reports — F121
  GET    /api/v1/rm/utilization              — F121: Resource utilization
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.rm import service
from app.rm.schemas import (
    BudgetEntryCreate,
    BudgetEntryOut,
    BudgetEntryUpdate,
    CostAnalysisOut,
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    EquipmentCreate,
    EquipmentOut,
    EquipmentUpdate,
    HRPlanningCreate,
    HRPlanningOut,
    HRPlanningUpdate,
    LeaveCreate,
    LeaveOut,
    LeaveUpdate,
    MaterialStockCreate,
    MaterialStockOut,
    MaterialStockUpdate,
    ProcurementDocumentCreate,
    ProcurementDocumentOut,
    ProcurementOrderCreate,
    ProcurementOrderOut,
    ProcurementOrderUpdate,
    ResourceAllocationCreate,
    ResourceAllocationOut,
    ResourceAllocationUpdate,
    ResourceConsumptionOut,
    ProjectEfficiencyOut,
    ResourceUtilizationOut,
)
from app.system.schemas import ApiResponse, Meta

rm_router = APIRouter(prefix="/api/v1/rm", tags=["Resource Management"])


# ═══════════════════════════════════════════════════════════════════════════════
# EMPLOYEES — F107
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/employees", response_model=ApiResponse)
async def list_employees(
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    department: str | None = None,
    status: str | None = None,
    is_external: bool | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F107: List employees with filters."""
    rows, total = await service.list_employees(
        db, current_user.organization_id,
        page=page, per_page=per_page, search=search,
        department=department, status=status, is_external=is_external,
    )
    return ApiResponse(
        data=[EmployeeOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/employees", response_model=ApiResponse, status_code=201)
async def create_employee(
    body: EmployeeCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F107: Create employee."""
    req_info = await get_request_info(request)
    emp = await service.create_employee(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=EmployeeOut.model_validate(emp))


@rm_router.get("/employees/{employee_id}", response_model=ApiResponse)
async def get_employee(
    employee_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F107: Get employee detail."""
    emp = await service.get_employee(db, current_user.organization_id, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return ApiResponse(data=EmployeeOut.model_validate(emp))


@rm_router.put("/employees/{employee_id}", response_model=ApiResponse)
async def update_employee(
    employee_id: uuid.UUID,
    body: EmployeeUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F107: Update employee."""
    req_info = await get_request_info(request)
    emp = await service.update_employee(
        db, current_user.organization_id, current_user.id, employee_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    await db.commit()
    return ApiResponse(data=EmployeeOut.model_validate(emp))


@rm_router.delete("/employees/{employee_id}", response_model=ApiResponse)
async def delete_employee(
    employee_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F107: Soft-delete employee."""
    req_info = await get_request_info(request)
    ok = await service.delete_employee(
        db, current_user.organization_id, current_user.id, employee_id,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    await db.commit()
    return ApiResponse(data={"deleted": True})


# ═══════════════════════════════════════════════════════════════════════════════
# HR PLANNING — F108
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/hr-planning", response_model=ApiResponse)
async def list_hr_planning(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    entry_type: str | None = None,
    department: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F108: List HR planning entries."""
    rows, total = await service.list_hr_planning(
        db, current_user.organization_id,
        page=page, per_page=per_page, status=status,
        entry_type=entry_type, department=department,
    )
    return ApiResponse(
        data=[HRPlanningOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/hr-planning", response_model=ApiResponse, status_code=201)
async def create_hr_planning(
    body: HRPlanningCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F108: Create HR planning entry."""
    req_info = await get_request_info(request)
    entry = await service.create_hr_planning(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=HRPlanningOut.model_validate(entry))


@rm_router.put("/hr-planning/{entry_id}", response_model=ApiResponse)
async def update_hr_planning(
    entry_id: uuid.UUID,
    body: HRPlanningUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F108: Update HR planning entry."""
    req_info = await get_request_info(request)
    entry = await service.update_hr_planning(
        db, current_user.organization_id, current_user.id, entry_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not entry:
        raise HTTPException(status_code=404, detail="HR planning entry not found")
    await db.commit()
    return ApiResponse(data=HRPlanningOut.model_validate(entry))


# ═══════════════════════════════════════════════════════════════════════════════
# LEAVES — F109
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/leaves", response_model=ApiResponse)
async def list_leaves(
    page: int = 1,
    per_page: int = 20,
    employee_id: uuid.UUID | None = None,
    status: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F109: List leave requests."""
    rows, total = await service.list_leaves(
        db, current_user.organization_id,
        employee_id=employee_id, status=status,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[LeaveOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/leaves", response_model=ApiResponse, status_code=201)
async def create_leave(
    body: LeaveCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F109: Create leave request."""
    req_info = await get_request_info(request)
    leave = await service.create_leave(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=LeaveOut.model_validate(leave))


@rm_router.put("/leaves/{leave_id}", response_model=ApiResponse)
async def update_leave(
    leave_id: uuid.UUID,
    body: LeaveUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F109: Update leave (approve/reject)."""
    req_info = await get_request_info(request)
    leave = await service.update_leave(
        db, current_user.organization_id, current_user.id, leave_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await db.commit()
    return ApiResponse(data=LeaveOut.model_validate(leave))


@rm_router.get("/employees/{employee_id}/availability", response_model=ApiResponse)
async def check_availability(
    employee_id: uuid.UUID,
    start_date: str,
    end_date: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F109: Check employee availability for a date range."""
    from datetime import datetime
    sd = datetime.fromisoformat(start_date)
    ed = datetime.fromisoformat(end_date)
    conflicts = await service.check_availability(
        db, current_user.organization_id, employee_id, sd, ed,
    )
    return ApiResponse(data={
        "employee_id": str(employee_id),
        "available": len(conflicts) == 0,
        "conflicting_leaves": [LeaveOut.model_validate(c) for c in conflicts],
    })


# ═══════════════════════════════════════════════════════════════════════════════
# EQUIPMENT
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/equipment", response_model=ApiResponse)
async def list_equipment(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    category: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await service.list_equipment(
        db, current_user.organization_id,
        page=page, per_page=per_page, status=status, category=category,
    )
    return ApiResponse(
        data=[EquipmentOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/equipment", response_model=ApiResponse, status_code=201)
async def create_equipment(
    body: EquipmentCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    req_info = await get_request_info(request)
    eq = await service.create_equipment(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=EquipmentOut.model_validate(eq))


@rm_router.get("/equipment/{equipment_id}", response_model=ApiResponse)
async def get_equipment(
    equipment_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    eq = await service.get_equipment(db, current_user.organization_id, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return ApiResponse(data=EquipmentOut.model_validate(eq))


@rm_router.put("/equipment/{equipment_id}", response_model=ApiResponse)
async def update_equipment(
    equipment_id: uuid.UUID,
    body: EquipmentUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    req_info = await get_request_info(request)
    eq = await service.update_equipment(
        db, current_user.organization_id, current_user.id, equipment_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    await db.commit()
    return ApiResponse(data=EquipmentOut.model_validate(eq))


@rm_router.delete("/equipment/{equipment_id}", response_model=ApiResponse)
async def delete_equipment(
    equipment_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    req_info = await get_request_info(request)
    ok = await service.delete_equipment(
        db, current_user.organization_id, current_user.id, equipment_id,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Equipment not found")
    await db.commit()
    return ApiResponse(data={"deleted": True})


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL STOCK — F114
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/materials", response_model=ApiResponse)
async def list_materials(
    page: int = 1,
    per_page: int = 20,
    below_minimum: bool | None = None,
    warehouse: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F114: List materials with stock alerts."""
    rows, total = await service.list_materials(
        db, current_user.organization_id,
        page=page, per_page=per_page, below_minimum=below_minimum, warehouse=warehouse,
    )
    return ApiResponse(
        data=[MaterialStockOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/materials", response_model=ApiResponse, status_code=201)
async def create_material(
    body: MaterialStockCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F114: Create material stock entry."""
    req_info = await get_request_info(request)
    mat = await service.create_material(
        db, current_user.organization_id, current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=MaterialStockOut.model_validate(mat))


@rm_router.put("/materials/{material_id}", response_model=ApiResponse)
async def update_material(
    material_id: uuid.UUID,
    body: MaterialStockUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F114: Update material stock."""
    req_info = await get_request_info(request)
    mat = await service.update_material(
        db, current_user.organization_id, current_user.id, material_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not mat:
        raise HTTPException(status_code=404, detail="Material stock not found")
    await db.commit()
    return ApiResponse(data=MaterialStockOut.model_validate(mat))


# ═══════════════════════════════════════════════════════════════════════════════
# PROCUREMENT — F112, F113
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/procurement", response_model=ApiResponse)
async def list_procurement(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F112: List procurement orders."""
    rows, total = await service.list_procurement_orders(
        db, current_user.organization_id,
        page=page, per_page=per_page, status=status,
    )
    return ApiResponse(
        data=[ProcurementOrderOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/procurement", response_model=ApiResponse, status_code=201)
async def create_procurement(
    body: ProcurementOrderCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F112: Create procurement order."""
    req_info = await get_request_info(request)
    order = await service.create_procurement_order(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=ProcurementOrderOut.model_validate(order))


@rm_router.get("/procurement/{order_id}", response_model=ApiResponse)
async def get_procurement(
    order_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F112: Get procurement order detail."""
    order = await service.get_procurement_order(db, current_user.organization_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Procurement order not found")
    return ApiResponse(data=ProcurementOrderOut.model_validate(order))


@rm_router.put("/procurement/{order_id}", response_model=ApiResponse)
async def update_procurement(
    order_id: uuid.UUID,
    body: ProcurementOrderUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F112: Update procurement order."""
    req_info = await get_request_info(request)
    order = await service.update_procurement_order(
        db, current_user.organization_id, current_user.id, order_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not order:
        raise HTTPException(status_code=404, detail="Procurement order not found")
    await db.commit()
    return ApiResponse(data=ProcurementOrderOut.model_validate(order))


@rm_router.get("/procurement/{order_id}/documents", response_model=ApiResponse)
async def list_procurement_documents(
    order_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F113: List documents for a procurement order."""
    docs = await service.list_procurement_documents(
        db, current_user.organization_id, order_id,
    )
    return ApiResponse(data=[ProcurementDocumentOut.model_validate(d) for d in docs])


@rm_router.post("/procurement/{order_id}/documents", response_model=ApiResponse, status_code=201)
async def create_procurement_document(
    order_id: uuid.UUID,
    body: ProcurementDocumentCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F113: Add document (invoice, NIR, consumption voucher) to procurement order."""
    req_info = await get_request_info(request)
    doc_data = body.model_dump()
    doc_data["order_id"] = order_id
    doc = await service.create_procurement_document(
        db, current_user.organization_id, current_user.id, doc_data,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=ProcurementDocumentOut.model_validate(doc))


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE ALLOCATION — F117, F118, F119, F120
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/allocations", response_model=ApiResponse)
async def list_allocations(
    page: int = 1,
    per_page: int = 20,
    project_id: uuid.UUID | None = None,
    employee_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    status: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F117: List resource allocations."""
    rows, total = await service.list_allocations(
        db, current_user.organization_id,
        project_id=project_id, employee_id=employee_id,
        resource_type=resource_type, status=status,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[ResourceAllocationOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/allocations", response_model=ApiResponse, status_code=201)
async def create_allocation(
    body: ResourceAllocationCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F117: Create resource allocation with conflict detection."""
    req_info = await get_request_info(request)
    alloc = await service.create_allocation(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=ResourceAllocationOut.model_validate(alloc))


@rm_router.put("/allocations/{allocation_id}", response_model=ApiResponse)
async def update_allocation(
    allocation_id: uuid.UUID,
    body: ResourceAllocationUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F117: Update resource allocation."""
    req_info = await get_request_info(request)
    alloc = await service.update_allocation(
        db, current_user.organization_id, current_user.id, allocation_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")
    await db.commit()
    return ApiResponse(data=ResourceAllocationOut.model_validate(alloc))


@rm_router.delete("/allocations/{allocation_id}", response_model=ApiResponse)
async def delete_allocation(
    allocation_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F117: Delete resource allocation."""
    req_info = await get_request_info(request)
    ok = await service.delete_allocation(
        db, current_user.organization_id, current_user.id, allocation_id,
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Allocation not found")
    await db.commit()
    return ApiResponse(data={"deleted": True})


@rm_router.get("/projects/{project_id}/consumption", response_model=ApiResponse)
async def get_resource_consumption(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F118: Resource consumption — allocated vs actual for a project."""
    data = await service.get_resource_consumption(
        db, current_user.organization_id, project_id,
    )
    data["allocations"] = [ResourceAllocationOut.model_validate(a) for a in data["allocations"]]
    return ApiResponse(data=data)


@rm_router.get("/projects/{project_id}/efficiency", response_model=ApiResponse)
async def get_project_efficiency(
    project_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F119: Project efficiency evaluation."""
    data = await service.get_project_efficiency(
        db, current_user.organization_id, project_id,
    )
    return ApiResponse(data=data)


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET / FINANCIAL PLANNING — F115, F116
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/budgets", response_model=ApiResponse)
async def list_budgets(
    page: int = 1,
    per_page: int = 20,
    cost_center: str | None = None,
    period_year: int | None = None,
    period_month: int | None = None,
    project_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F115: List budget entries."""
    rows, total = await service.list_budget_entries(
        db, current_user.organization_id,
        page=page, per_page=per_page, cost_center=cost_center,
        period_year=period_year, period_month=period_month, project_id=project_id,
    )
    return ApiResponse(
        data=[BudgetEntryOut.model_validate(r) for r in rows],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@rm_router.post("/budgets", response_model=ApiResponse, status_code=201)
async def create_budget(
    body: BudgetEntryCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F115: Create budget entry."""
    req_info = await get_request_info(request)
    entry = await service.create_budget_entry(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    await db.commit()
    return ApiResponse(data=BudgetEntryOut.model_validate(entry))


@rm_router.put("/budgets/{budget_id}", response_model=ApiResponse)
async def update_budget(
    budget_id: uuid.UUID,
    body: BudgetEntryUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F115: Update budget entry."""
    req_info = await get_request_info(request)
    entry = await service.update_budget_entry(
        db, current_user.organization_id, current_user.id, budget_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Budget entry not found")
    await db.commit()
    return ApiResponse(data=BudgetEntryOut.model_validate(entry))


@rm_router.get("/cost-analysis", response_model=ApiResponse)
async def get_cost_analysis(
    cost_center: str | None = None,
    period_year: int | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F116: Cost analysis — budgeted vs actual per cost center."""
    data = await service.get_cost_analysis(
        db, current_user.organization_id,
        cost_center=cost_center, period_year=period_year,
    )
    for item in data:
        item["entries"] = [BudgetEntryOut.model_validate(e) for e in item["entries"]]
    return ApiResponse(data=data)


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE UTILIZATION — F121
# ═══════════════════════════════════════════════════════════════════════════════


@rm_router.get("/utilization", response_model=ApiResponse)
async def get_utilization(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F121: Resource utilization report per employee."""
    data = await service.get_resource_utilization(db, current_user.organization_id)
    return ApiResponse(data=data)
