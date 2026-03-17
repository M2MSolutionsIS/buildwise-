"""
RM (Resource Management) module schemas — F107–F122.

Covers: Employees (HR), HR Planning, Leaves, Equipment,
MaterialStock, Procurement, Resource Allocation, Budget/Financial Planning.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ─── Employee — F107, F110, F111 ────────────────────────────────────────────


class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str | None = None
    phone: str | None = None
    employee_number: str | None = None
    position: str | None = None
    department: str | None = None
    cost_center: str | None = None
    contract_type: str = "full_time"
    hire_date: datetime | None = None
    # F111
    gross_salary: float | None = None
    net_salary: float | None = None
    hourly_rate: float | None = None
    standard_hours_month: float = 168.0
    currency: str = "RON"
    # F110
    skills: list | None = None
    qualifications: list | None = None
    certifications: list | None = None
    # F120
    is_external: bool = False
    external_company: str | None = None
    external_contract_ref: str | None = None
    external_daily_rate: float | None = None
    # Link
    user_id: uuid.UUID | None = None


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    employee_number: str | None = None
    position: str | None = None
    department: str | None = None
    cost_center: str | None = None
    status: str | None = None
    contract_type: str | None = None
    hire_date: datetime | None = None
    termination_date: datetime | None = None
    gross_salary: float | None = None
    net_salary: float | None = None
    hourly_rate: float | None = None
    standard_hours_month: float | None = None
    currency: str | None = None
    skills: list | None = None
    qualifications: list | None = None
    certifications: list | None = None
    is_external: bool | None = None
    external_company: str | None = None
    external_contract_ref: str | None = None
    external_daily_rate: float | None = None


class EmployeeOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    employee_number: str | None = None
    position: str | None = None
    department: str | None = None
    cost_center: str | None = None
    status: str
    contract_type: str
    hire_date: datetime | None = None
    termination_date: datetime | None = None
    gross_salary: float | None = None
    net_salary: float | None = None
    hourly_rate: float | None = None
    standard_hours_month: float
    currency: str
    skills: list | None = None
    qualifications: list | None = None
    certifications: list | None = None
    is_external: bool
    external_company: str | None = None
    external_contract_ref: str | None = None
    external_daily_rate: float | None = None
    user_id: uuid.UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── HR Planning — F108 ────────────────────────────────────────────────────


class HRPlanningCreate(BaseModel):
    entry_type: str = Field(..., pattern="^(hire|terminate)$")
    position: str = Field(..., min_length=1, max_length=100)
    department: str | None = None
    target_date: datetime
    description: str | None = None
    employee_id: uuid.UUID | None = None


class HRPlanningUpdate(BaseModel):
    entry_type: str | None = None
    position: str | None = None
    department: str | None = None
    target_date: datetime | None = None
    status: str | None = None
    description: str | None = None
    employee_id: uuid.UUID | None = None


class HRPlanningOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    entry_type: str
    position: str
    department: str | None = None
    target_date: datetime
    status: str
    description: str | None = None
    employee_id: uuid.UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Leave — F109 ──────────────────────────────────────────────────────────


class LeaveCreate(BaseModel):
    employee_id: uuid.UUID
    leave_type: str
    start_date: datetime
    end_date: datetime
    reason: str | None = None


class LeaveUpdate(BaseModel):
    status: str | None = None
    reason: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class LeaveOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    leave_type: str
    start_date: datetime
    end_date: datetime
    status: str
    approved_by: uuid.UUID | None = None
    reason: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Equipment ──────────────────────────────────────────────────────────────


class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str | None = None
    category: str | None = None
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    purchase_date: datetime | None = None
    purchase_cost: float | None = None
    daily_rate: float | None = None
    currency: str = "RON"
    location: str | None = None


class EquipmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    category: str | None = None
    description: str | None = None
    status: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    purchase_date: datetime | None = None
    purchase_cost: float | None = None
    daily_rate: float | None = None
    currency: str | None = None
    location: str | None = None
    next_maintenance_date: datetime | None = None


class EquipmentOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str | None = None
    category: str | None = None
    description: str | None = None
    status: str
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    purchase_date: datetime | None = None
    purchase_cost: float | None = None
    daily_rate: float | None = None
    currency: str
    location: str | None = None
    next_maintenance_date: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── MaterialStock — F114 ──────────────────────────────────────────────────


class MaterialStockCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str | None = None
    unit_of_measure: str = "buc"
    current_quantity: float = 0.0
    minimum_quantity: float = 0.0
    location: str | None = None
    warehouse: str | None = None
    unit_cost: float | None = None
    currency: str = "RON"
    product_id: uuid.UUID | None = None


class MaterialStockUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    unit_of_measure: str | None = None
    current_quantity: float | None = None
    minimum_quantity: float | None = None
    reserved_quantity: float | None = None
    location: str | None = None
    warehouse: str | None = None
    unit_cost: float | None = None
    currency: str | None = None


class MaterialStockOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str | None = None
    unit_of_measure: str
    current_quantity: float
    minimum_quantity: float
    reserved_quantity: float
    location: str | None = None
    warehouse: str | None = None
    unit_cost: float | None = None
    total_value: float | None = None
    currency: str
    is_below_minimum: bool
    product_id: uuid.UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Procurement — F112, F113 ──────────────────────────────────────────────


class ProcurementLineItemCreate(BaseModel):
    description: str
    quantity: float
    unit_of_measure: str = "buc"
    unit_price: float
    material_stock_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None


class ProcurementLineItemOut(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    description: str
    quantity: float
    unit_of_measure: str
    unit_price: float
    total_price: float
    received_quantity: float
    material_stock_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class ProcurementOrderCreate(BaseModel):
    supplier_contact_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    wbs_node_id: uuid.UUID | None = None
    currency: str = "RON"
    expected_delivery: datetime | None = None
    line_items: list[ProcurementLineItemCreate] = []


class ProcurementOrderUpdate(BaseModel):
    status: str | None = None
    supplier_contact_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    expected_delivery: datetime | None = None
    actual_delivery: datetime | None = None


class ProcurementOrderOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_number: str
    supplier_contact_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    wbs_node_id: uuid.UUID | None = None
    status: str
    total_amount: float
    currency: str
    order_date: datetime | None = None
    expected_delivery: datetime | None = None
    actual_delivery: datetime | None = None
    line_items: list[ProcurementLineItemOut] = []
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProcurementDocumentCreate(BaseModel):
    order_id: uuid.UUID
    document_type: str  # invoice, nir, consumption_voucher, delivery_note
    document_number: str
    document_date: datetime
    amount: float
    currency: str = "RON"
    file_path: str | None = None


class ProcurementDocumentOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_id: uuid.UUID
    document_type: str
    document_number: str
    document_date: datetime
    amount: float
    currency: str
    file_path: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Resource Allocation — F117, F118, F119, F120 ──────────────────────────


class ResourceAllocationCreate(BaseModel):
    resource_type: str  # employee, equipment, material, external
    employee_id: uuid.UUID | None = None
    equipment_id: uuid.UUID | None = None
    project_id: uuid.UUID
    wbs_node_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    start_date: datetime
    end_date: datetime
    allocated_hours: float | None = None
    planned_cost: float | None = None
    currency: str = "RON"
    allocation_percent: float = 100.0


class ResourceAllocationUpdate(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    allocated_hours: float | None = None
    actual_hours: float | None = None
    planned_cost: float | None = None
    actual_cost: float | None = None
    status: str | None = None
    allocation_percent: float | None = None


class ResourceAllocationOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    resource_type: str
    employee_id: uuid.UUID | None = None
    equipment_id: uuid.UUID | None = None
    project_id: uuid.UUID
    wbs_node_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    start_date: datetime
    end_date: datetime
    allocated_hours: float | None = None
    actual_hours: float | None = None
    planned_cost: float | None = None
    actual_cost: float | None = None
    currency: str
    status: str
    has_conflict: bool
    conflict_details: dict | None = None
    allocation_percent: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResourceConsumptionOut(BaseModel):
    """F118: Allocated vs actual consumption summary."""
    project_id: uuid.UUID
    total_allocated_hours: float
    total_actual_hours: float
    total_planned_cost: float
    total_actual_cost: float
    utilization_percent: float
    allocations: list[ResourceAllocationOut] = []


class ProjectEfficiencyOut(BaseModel):
    """F119: Project efficiency evaluation."""
    project_id: uuid.UUID
    planned_hours: float
    actual_hours: float
    hours_variance: float
    planned_cost: float
    actual_cost: float
    cost_variance: float
    efficiency_score: float  # actual/planned ratio


# ─── Budget / Financial Planning — F115, F116 ──────────────────────────────


class BudgetEntryCreate(BaseModel):
    cost_center: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2000, le=2100)
    budgeted_amount: float = 0.0
    actual_amount: float = 0.0
    currency: str = "RON"
    project_id: uuid.UUID | None = None


class BudgetEntryUpdate(BaseModel):
    cost_center: str | None = None
    category: str | None = None
    description: str | None = None
    budgeted_amount: float | None = None
    actual_amount: float | None = None


class BudgetEntryOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    cost_center: str
    category: str
    description: str | None = None
    period_month: int
    period_year: int
    budgeted_amount: float
    actual_amount: float
    variance: float
    currency: str
    project_id: uuid.UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CostAnalysisOut(BaseModel):
    """F116: Cost analysis — budgeted vs actual per cost center."""
    cost_center: str
    total_budgeted: float
    total_actual: float
    total_variance: float
    entries: list[BudgetEntryOut] = []


# ─── Resource Utilization Report — F121 ────────────────────────────────────


class ResourceUtilizationOut(BaseModel):
    """F121: Resource utilization report per employee."""
    employee_id: uuid.UUID
    employee_name: str
    total_allocated_hours: float
    total_actual_hours: float
    utilization_percent: float
    project_count: int
