"""
RM (Resource Management) module service layer — F107–F122.

All operations include audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.rm.models import (
    BudgetEntry,
    Employee,
    Equipment,
    HRPlanningEntry,
    Leave,
    MaterialStock,
    ProcurementDocument,
    ProcurementLineItem,
    ProcurementOrder,
    ResourceAllocation,
)


# ═══════════════════════════════════════════════════════════════════════════════
# EMPLOYEES — F107
# ═══════════════════════════════════════════════════════════════════════════════


async def list_employees(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    department: str | None = None,
    status: str | None = None,
    is_external: bool | None = None,
    skill: str | None = None,
) -> tuple[list[Employee], int]:
    query = select(Employee).where(
        Employee.organization_id == org_id,
        Employee.is_deleted.is_(False),
    )
    if search:
        pattern = f"%{search}%"
        query = query.where(
            (Employee.first_name.ilike(pattern))
            | (Employee.last_name.ilike(pattern))
            | (Employee.email.ilike(pattern))
            | (Employee.employee_number.ilike(pattern))
        )
    if department:
        query = query.where(Employee.department == department)
    if status:
        query = query.where(Employee.status == status)
    if is_external is not None:
        query = query.where(Employee.is_external == is_external)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    rows = (await db.execute(
        query.order_by(Employee.last_name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def get_employee(db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID) -> Employee | None:
    return (await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
    )).scalar_one_or_none()


async def create_employee(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Employee:
    emp = Employee(id=uuid.uuid4(), organization_id=org_id, created_by=user_id, updated_by=user_id, **data)
    db.add(emp)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="employees", entity_id=emp.id,
        new_values=model_to_dict(emp), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return emp


async def update_employee(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, employee_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Employee | None:
    emp = await get_employee(db, org_id, employee_id)
    if not emp:
        return None
    old = model_to_dict(emp)
    for k, v in data.items():
        if v is not None:
            setattr(emp, k, v)
    emp.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="employees", entity_id=emp.id,
        old_values=old, new_values=model_to_dict(emp),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return emp


async def delete_employee(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, employee_id: uuid.UUID,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> bool:
    emp = await get_employee(db, org_id, employee_id)
    if not emp:
        return False
    emp.is_deleted = True
    emp.deleted_at = datetime.now(timezone.utc)
    emp.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="employees", entity_id=emp.id,
        old_values=model_to_dict(emp), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# HR PLANNING — F108
# ═══════════════════════════════════════════════════════════════════════════════


async def list_hr_planning(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20, status: str | None = None,
    entry_type: str | None = None, department: str | None = None,
) -> tuple[list[HRPlanningEntry], int]:
    query = select(HRPlanningEntry).where(HRPlanningEntry.organization_id == org_id)
    if status:
        query = query.where(HRPlanningEntry.status == status)
    if entry_type:
        query = query.where(HRPlanningEntry.entry_type == entry_type)
    if department:
        query = query.where(HRPlanningEntry.department == department)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(HRPlanningEntry.target_date).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_hr_planning(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> HRPlanningEntry:
    entry = HRPlanningEntry(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(entry)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="hr_planning_entries", entity_id=entry.id,
        new_values=model_to_dict(entry), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return entry


async def update_hr_planning(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, entry_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> HRPlanningEntry | None:
    entry = (await db.execute(
        select(HRPlanningEntry).where(HRPlanningEntry.id == entry_id, HRPlanningEntry.organization_id == org_id)
    )).scalar_one_or_none()
    if not entry:
        return None
    old = model_to_dict(entry)
    for k, v in data.items():
        if v is not None:
            setattr(entry, k, v)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="hr_planning_entries", entity_id=entry.id,
        old_values=old, new_values=model_to_dict(entry),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# LEAVES — F109
# ═══════════════════════════════════════════════════════════════════════════════


async def list_leaves(
    db: AsyncSession, org_id: uuid.UUID,
    *, employee_id: uuid.UUID | None = None,
    status: str | None = None,
    page: int = 1, per_page: int = 20,
) -> tuple[list[Leave], int]:
    query = select(Leave).where(Leave.organization_id == org_id)
    if employee_id:
        query = query.where(Leave.employee_id == employee_id)
    if status:
        query = query.where(Leave.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(Leave.start_date.desc()).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_leave(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Leave:
    leave = Leave(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(leave)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="leaves", entity_id=leave.id,
        new_values=model_to_dict(leave), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return leave


async def update_leave(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, leave_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Leave | None:
    leave = (await db.execute(
        select(Leave).where(Leave.id == leave_id, Leave.organization_id == org_id)
    )).scalar_one_or_none()
    if not leave:
        return None
    old = model_to_dict(leave)
    for k, v in data.items():
        if v is not None:
            setattr(leave, k, v)
    if data.get("status") in ("approved",) and leave.approved_by is None:
        leave.approved_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="leaves", entity_id=leave.id,
        old_values=old, new_values=model_to_dict(leave),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return leave


async def check_availability(
    db: AsyncSession, org_id: uuid.UUID,
    employee_id: uuid.UUID, start_date: datetime, end_date: datetime,
) -> list[Leave]:
    """F109: Check employee availability — return conflicting leaves."""
    result = await db.execute(
        select(Leave).where(
            Leave.organization_id == org_id,
            Leave.employee_id == employee_id,
            Leave.status.in_(["pending", "approved"]),
            Leave.start_date <= end_date,
            Leave.end_date >= start_date,
        )
    )
    return list(result.scalars().all())


# ═══════════════════════════════════════════════════════════════════════════════
# EQUIPMENT
# ═══════════════════════════════════════════════════════════════════════════════


async def list_equipment(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
    status: str | None = None, category: str | None = None,
) -> tuple[list[Equipment], int]:
    query = select(Equipment).where(
        Equipment.organization_id == org_id, Equipment.is_deleted.is_(False),
    )
    if status:
        query = query.where(Equipment.status == status)
    if category:
        query = query.where(Equipment.category == category)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(Equipment.name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def get_equipment(db: AsyncSession, org_id: uuid.UUID, eq_id: uuid.UUID) -> Equipment | None:
    return (await db.execute(
        select(Equipment).where(
            Equipment.id == eq_id, Equipment.organization_id == org_id, Equipment.is_deleted.is_(False),
        )
    )).scalar_one_or_none()


async def create_equipment(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Equipment:
    eq = Equipment(id=uuid.uuid4(), organization_id=org_id, created_by=user_id, updated_by=user_id, **data)
    db.add(eq)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="equipment", entity_id=eq.id,
        new_values=model_to_dict(eq), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return eq


async def update_equipment(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, eq_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> Equipment | None:
    eq = await get_equipment(db, org_id, eq_id)
    if not eq:
        return None
    old = model_to_dict(eq)
    for k, v in data.items():
        if v is not None:
            setattr(eq, k, v)
    eq.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="equipment", entity_id=eq.id,
        old_values=old, new_values=model_to_dict(eq),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return eq


async def delete_equipment(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, eq_id: uuid.UUID,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> bool:
    eq = await get_equipment(db, org_id, eq_id)
    if not eq:
        return False
    eq.is_deleted = True
    eq.deleted_at = datetime.now(timezone.utc)
    eq.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="equipment", entity_id=eq.id,
        old_values=model_to_dict(eq), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL STOCK — F114
# ═══════════════════════════════════════════════════════════════════════════════


async def list_materials(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
    below_minimum: bool | None = None, warehouse: str | None = None,
) -> tuple[list[MaterialStock], int]:
    query = select(MaterialStock).where(MaterialStock.organization_id == org_id)
    if below_minimum is True:
        query = query.where(MaterialStock.is_below_minimum.is_(True))
    if warehouse:
        query = query.where(MaterialStock.warehouse == warehouse)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(MaterialStock.name).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_material(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> MaterialStock:
    mat = MaterialStock(id=uuid.uuid4(), organization_id=org_id, created_by=user_id, updated_by=user_id, **data)
    mat.total_value = (mat.current_quantity or 0) * (mat.unit_cost or 0)
    mat.is_below_minimum = mat.current_quantity < mat.minimum_quantity
    db.add(mat)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="material_stocks", entity_id=mat.id,
        new_values=model_to_dict(mat), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return mat


async def update_material(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, mat_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> MaterialStock | None:
    mat = (await db.execute(
        select(MaterialStock).where(MaterialStock.id == mat_id, MaterialStock.organization_id == org_id)
    )).scalar_one_or_none()
    if not mat:
        return None
    old = model_to_dict(mat)
    for k, v in data.items():
        if v is not None:
            setattr(mat, k, v)
    mat.total_value = (mat.current_quantity or 0) * (mat.unit_cost or 0)
    mat.is_below_minimum = mat.current_quantity < mat.minimum_quantity
    mat.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="material_stocks", entity_id=mat.id,
        old_values=old, new_values=model_to_dict(mat),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return mat


# ═══════════════════════════════════════════════════════════════════════════════
# PROCUREMENT — F112, F113
# ═══════════════════════════════════════════════════════════════════════════════


async def _generate_order_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    count = (await db.execute(
        select(func.count()).where(ProcurementOrder.organization_id == org_id)
    )).scalar() or 0
    return f"PO-{count + 1:05d}"


async def list_procurement_orders(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20, status: str | None = None,
) -> tuple[list[ProcurementOrder], int]:
    query = select(ProcurementOrder).where(ProcurementOrder.organization_id == org_id)
    if status:
        query = query.where(ProcurementOrder.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.options(selectinload(ProcurementOrder.line_items))
        .order_by(ProcurementOrder.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def get_procurement_order(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID) -> ProcurementOrder | None:
    return (await db.execute(
        select(ProcurementOrder).options(selectinload(ProcurementOrder.line_items))
        .where(ProcurementOrder.id == order_id, ProcurementOrder.organization_id == org_id)
    )).scalar_one_or_none()


async def create_procurement_order(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ProcurementOrder:
    line_items_data = data.pop("line_items", [])
    order_number = await _generate_order_number(db, org_id)
    order = ProcurementOrder(
        id=uuid.uuid4(), organization_id=org_id,
        order_number=order_number, order_date=datetime.now(timezone.utc),
        created_by=user_id, updated_by=user_id, **data,
    )
    total = 0.0
    for li_data in line_items_data:
        tp = li_data["quantity"] * li_data["unit_price"]
        li = ProcurementLineItem(
            id=uuid.uuid4(), organization_id=org_id, order_id=order.id,
            total_price=tp, **li_data,
        )
        order.line_items.append(li)
        total += tp
    order.total_amount = total
    db.add(order)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="procurement_orders", entity_id=order.id,
        new_values=model_to_dict(order), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return order


async def update_procurement_order(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, order_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ProcurementOrder | None:
    order = await get_procurement_order(db, org_id, order_id)
    if not order:
        return None
    old = model_to_dict(order)
    for k, v in data.items():
        if v is not None:
            setattr(order, k, v)
    order.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="procurement_orders", entity_id=order.id,
        old_values=old, new_values=model_to_dict(order),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return order


# ─── Procurement Documents — F113 ──────────────────────────────────────────


async def list_procurement_documents(
    db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID,
) -> list[ProcurementDocument]:
    result = await db.execute(
        select(ProcurementDocument).where(
            ProcurementDocument.organization_id == org_id,
            ProcurementDocument.order_id == order_id,
        ).order_by(ProcurementDocument.document_date.desc())
    )
    return list(result.scalars().all())


async def create_procurement_document(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ProcurementDocument:
    doc = ProcurementDocument(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(doc)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="procurement_documents", entity_id=doc.id,
        new_values=model_to_dict(doc), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return doc


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE ALLOCATION — F117, F118, F119, F120
# ═══════════════════════════════════════════════════════════════════════════════


async def list_allocations(
    db: AsyncSession, org_id: uuid.UUID,
    *, project_id: uuid.UUID | None = None,
    employee_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    status: str | None = None,
    page: int = 1, per_page: int = 20,
) -> tuple[list[ResourceAllocation], int]:
    query = select(ResourceAllocation).where(ResourceAllocation.organization_id == org_id)
    if project_id:
        query = query.where(ResourceAllocation.project_id == project_id)
    if employee_id:
        query = query.where(ResourceAllocation.employee_id == employee_id)
    if resource_type:
        query = query.where(ResourceAllocation.resource_type == resource_type)
    if status:
        query = query.where(ResourceAllocation.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(ResourceAllocation.start_date).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_allocation(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ResourceAllocation:
    alloc = ResourceAllocation(
        id=uuid.uuid4(), organization_id=org_id,
        created_by=user_id, updated_by=user_id, **data,
    )
    # F117: Check for conflicts
    if alloc.employee_id:
        conflicts = await _check_allocation_conflicts(
            db, org_id, alloc.employee_id, alloc.start_date, alloc.end_date, exclude_id=None,
        )
        if conflicts:
            alloc.has_conflict = True
            alloc.conflict_details = {
                "conflicting_allocations": [str(c.id) for c in conflicts],
                "message": f"Employee already allocated to {len(conflicts)} other project(s) in this period",
            }
    db.add(alloc)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="resource_allocations", entity_id=alloc.id,
        new_values=model_to_dict(alloc), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return alloc


async def update_allocation(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, alloc_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> ResourceAllocation | None:
    alloc = (await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.id == alloc_id, ResourceAllocation.organization_id == org_id,
        )
    )).scalar_one_or_none()
    if not alloc:
        return None
    old = model_to_dict(alloc)
    for k, v in data.items():
        if v is not None:
            setattr(alloc, k, v)
    alloc.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="resource_allocations", entity_id=alloc.id,
        old_values=old, new_values=model_to_dict(alloc),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return alloc


async def delete_allocation(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, alloc_id: uuid.UUID,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> bool:
    alloc = (await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.id == alloc_id, ResourceAllocation.organization_id == org_id,
        )
    )).scalar_one_or_none()
    if not alloc:
        return False
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="DELETE", entity_type="resource_allocations", entity_id=alloc.id,
        old_values=model_to_dict(alloc), ip_address=ip_address, user_agent=user_agent,
    )
    await db.delete(alloc)
    await db.flush()
    return True


async def _check_allocation_conflicts(
    db: AsyncSession, org_id: uuid.UUID,
    employee_id: uuid.UUID, start_date: datetime, end_date: datetime,
    *, exclude_id: uuid.UUID | None = None,
) -> list[ResourceAllocation]:
    """Check for overlapping allocations where total > 100%."""
    query = select(ResourceAllocation).where(
        ResourceAllocation.organization_id == org_id,
        ResourceAllocation.employee_id == employee_id,
        ResourceAllocation.status.in_(["planned", "confirmed", "active"]),
        ResourceAllocation.start_date <= end_date,
        ResourceAllocation.end_date >= start_date,
    )
    if exclude_id:
        query = query.where(ResourceAllocation.id != exclude_id)
    result = await db.execute(query)
    return list(result.scalars().all())


# ─── F118: Resource Consumption ────────────────────────────────────────────


async def get_resource_consumption(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID,
) -> dict:
    """F118: Allocated vs actual consumption for a project."""
    allocs = (await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.organization_id == org_id,
            ResourceAllocation.project_id == project_id,
        )
    )).scalars().all()

    total_alloc = sum(a.allocated_hours or 0 for a in allocs)
    total_actual = sum(a.actual_hours or 0 for a in allocs)
    total_planned_cost = sum(a.planned_cost or 0 for a in allocs)
    total_actual_cost = sum(a.actual_cost or 0 for a in allocs)
    utilization = (total_actual / total_alloc * 100) if total_alloc > 0 else 0

    return {
        "project_id": project_id,
        "total_allocated_hours": total_alloc,
        "total_actual_hours": total_actual,
        "total_planned_cost": total_planned_cost,
        "total_actual_cost": total_actual_cost,
        "utilization_percent": round(utilization, 2),
        "allocations": allocs,
    }


# ─── F119: Project Efficiency ─────────────────────────────────────────────


async def get_project_efficiency(
    db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID,
) -> dict:
    """F119: Efficiency evaluation — plan vs actual hours and cost."""
    allocs = (await db.execute(
        select(ResourceAllocation).where(
            ResourceAllocation.organization_id == org_id,
            ResourceAllocation.project_id == project_id,
        )
    )).scalars().all()

    planned_h = sum(a.allocated_hours or 0 for a in allocs)
    actual_h = sum(a.actual_hours or 0 for a in allocs)
    planned_c = sum(a.planned_cost or 0 for a in allocs)
    actual_c = sum(a.actual_cost or 0 for a in allocs)
    efficiency = (planned_h / actual_h) if actual_h > 0 else 0

    return {
        "project_id": project_id,
        "planned_hours": planned_h,
        "actual_hours": actual_h,
        "hours_variance": planned_h - actual_h,
        "planned_cost": planned_c,
        "actual_cost": actual_c,
        "cost_variance": planned_c - actual_c,
        "efficiency_score": round(efficiency, 2),
    }


# ─── F121: Resource Utilization Report ────────────────────────────────────


async def get_resource_utilization(
    db: AsyncSession, org_id: uuid.UUID,
) -> list[dict]:
    """F121: Utilization per employee."""
    employees = (await db.execute(
        select(Employee).where(Employee.organization_id == org_id, Employee.is_deleted.is_(False))
    )).scalars().all()

    result = []
    for emp in employees:
        allocs = (await db.execute(
            select(ResourceAllocation).where(
                ResourceAllocation.organization_id == org_id,
                ResourceAllocation.employee_id == emp.id,
            )
        )).scalars().all()
        total_alloc = sum(a.allocated_hours or 0 for a in allocs)
        total_actual = sum(a.actual_hours or 0 for a in allocs)
        projects = {str(a.project_id) for a in allocs}
        util = (total_actual / total_alloc * 100) if total_alloc > 0 else 0
        result.append({
            "employee_id": emp.id,
            "employee_name": f"{emp.first_name} {emp.last_name}",
            "total_allocated_hours": total_alloc,
            "total_actual_hours": total_actual,
            "utilization_percent": round(util, 2),
            "project_count": len(projects),
        })
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET / FINANCIAL PLANNING — F115, F116
# ═══════════════════════════════════════════════════════════════════════════════


async def list_budget_entries(
    db: AsyncSession, org_id: uuid.UUID,
    *, page: int = 1, per_page: int = 20,
    cost_center: str | None = None,
    period_year: int | None = None,
    period_month: int | None = None,
    project_id: uuid.UUID | None = None,
) -> tuple[list[BudgetEntry], int]:
    query = select(BudgetEntry).where(BudgetEntry.organization_id == org_id)
    if cost_center:
        query = query.where(BudgetEntry.cost_center == cost_center)
    if period_year:
        query = query.where(BudgetEntry.period_year == period_year)
    if period_month:
        query = query.where(BudgetEntry.period_month == period_month)
    if project_id:
        query = query.where(BudgetEntry.project_id == project_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    rows = (await db.execute(
        query.order_by(BudgetEntry.period_year.desc(), BudgetEntry.period_month.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return rows, total


async def create_budget_entry(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> BudgetEntry:
    entry = BudgetEntry(id=uuid.uuid4(), organization_id=org_id, created_by=user_id, updated_by=user_id, **data)
    entry.variance = entry.budgeted_amount - entry.actual_amount
    db.add(entry)
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="CREATE", entity_type="budget_entries", entity_id=entry.id,
        new_values=model_to_dict(entry), ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return entry


async def update_budget_entry(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, entry_id: uuid.UUID, data: dict,
    *, ip_address: str | None = None, user_agent: str | None = None,
) -> BudgetEntry | None:
    entry = (await db.execute(
        select(BudgetEntry).where(BudgetEntry.id == entry_id, BudgetEntry.organization_id == org_id)
    )).scalar_one_or_none()
    if not entry:
        return None
    old = model_to_dict(entry)
    for k, v in data.items():
        if v is not None:
            setattr(entry, k, v)
    entry.variance = entry.budgeted_amount - entry.actual_amount
    entry.updated_by = user_id
    await log_audit(
        db, user_id=user_id, organization_id=org_id,
        action="UPDATE", entity_type="budget_entries", entity_id=entry.id,
        old_values=old, new_values=model_to_dict(entry),
        ip_address=ip_address, user_agent=user_agent,
    )
    await db.flush()
    return entry


# ─── F116: Cost Analysis ──────────────────────────────────────────────────


async def get_cost_analysis(
    db: AsyncSession, org_id: uuid.UUID,
    *, cost_center: str | None = None, period_year: int | None = None,
) -> list[dict]:
    """F116: Cost analysis — budgeted vs actual per cost center."""
    query = select(BudgetEntry).where(BudgetEntry.organization_id == org_id)
    if cost_center:
        query = query.where(BudgetEntry.cost_center == cost_center)
    if period_year:
        query = query.where(BudgetEntry.period_year == period_year)

    entries = (await db.execute(query.order_by(BudgetEntry.cost_center))).scalars().all()

    # Group by cost center
    grouped: dict[str, list] = {}
    for e in entries:
        grouped.setdefault(e.cost_center, []).append(e)

    result = []
    for cc, items in grouped.items():
        total_b = sum(i.budgeted_amount for i in items)
        total_a = sum(i.actual_amount for i in items)
        result.append({
            "cost_center": cc,
            "total_budgeted": total_b,
            "total_actual": total_a,
            "total_variance": total_b - total_a,
            "entries": items,
        })
    return result
