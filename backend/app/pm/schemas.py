"""
PM module schemas — F063, F066, F069–F080, F083, F084, F086, F088,
F090, F091–F095, F100, F101, F103, F105, F123, F125, F130, F144, F161.

Covers: Projects, WBS, Tasks/Gantt, Deviz, Timesheets, Materials,
Subcontractors, DailyReports, WorkSituations, Risks, PunchItems,
EnergyImpact, ProjectFinance, Wiki, ImportJobs.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT — F063, F101, F103
# ═══════════════════════════════════════════════════════════════════════════════


class ProjectCreate(BaseModel):
    """F063: Project Setup — create from contract or manually."""
    contract_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    project_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    project_type: str = "client"  # client|internal
    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None
    budget_allocated: float | None = None
    currency: str = "RON"
    project_manager_id: uuid.UUID | None = None
    kickoff_checklist: dict | None = None
    tags: list[str] | None = None
    notes: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    project_type: str | None = None
    status: str | None = None
    health_score: float | None = None
    health_indicator: str | None = None
    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None
    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None
    budget_allocated: float | None = None
    budget_committed: float | None = None
    budget_actual: float | None = None
    currency: str | None = None
    cpi: float | None = None
    spi: float | None = None
    percent_complete: float | None = None
    project_manager_id: uuid.UUID | None = None
    kickoff_checklist: dict | None = None
    kickoff_completed: bool | None = None
    tags: list[str] | None = None
    notes: str | None = None


class ProjectOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    contract_id: uuid.UUID | None = None
    contact_id: uuid.UUID | None = None
    project_number: str
    name: str
    description: str | None = None
    project_type: str
    status: str
    health_score: float | None = None
    health_indicator: str | None = None
    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None
    actual_start_date: datetime | None = None
    actual_end_date: datetime | None = None
    budget_allocated: float | None = None
    budget_committed: float | None = None
    budget_actual: float | None = None
    currency: str
    cpi: float | None = None
    spi: float | None = None
    percent_complete: float
    project_manager_id: uuid.UUID | None = None
    kickoff_checklist: dict | None = None
    kickoff_completed: bool
    close_date: datetime | None = None
    grace_period_end: datetime | None = None
    cancellation_reason: str | None = None
    tags: list | None = None
    notes: str | None = None
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProjectListOut(BaseModel):
    """Lightweight project for list/portfolio views (F101)."""
    id: uuid.UUID
    project_number: str
    name: str
    project_type: str
    status: str
    health_indicator: str | None = None
    percent_complete: float
    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None
    budget_allocated: float | None = None
    budget_actual: float | None = None
    currency: str
    project_manager_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectCloseRequest(BaseModel):
    """F103: Close project with grace period."""
    grace_period_days: int = 30


class ProjectCancelRequest(BaseModel):
    """F103: Cancel project with reason."""
    cancellation_reason: str = Field(..., min_length=1)


# ═══════════════════════════════════════════════════════════════════════════════
# WBS — F069
# ═══════════════════════════════════════════════════════════════════════════════


class WBSNodeCreate(BaseModel):
    parent_id: uuid.UUID | None = None
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    node_type: str = "chapter"  # chapter|subchapter|article
    sort_order: int = 0
    level: int = 0
    budget_allocated: float | None = None
    responsible_id: uuid.UUID | None = None


class WBSNodeUpdate(BaseModel):
    parent_id: uuid.UUID | None = None
    code: str | None = Field(None, min_length=1, max_length=50)
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    node_type: str | None = None
    sort_order: int | None = None
    level: int | None = None
    budget_allocated: float | None = None
    budget_actual: float | None = None
    responsible_id: uuid.UUID | None = None


class WBSNodeOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    code: str
    name: str
    description: str | None = None
    node_type: str
    sort_order: int
    level: int
    budget_allocated: float | None = None
    budget_actual: float | None = None
    responsible_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# TASKS / GANTT — F070, F073
# ═══════════════════════════════════════════════════════════════════════════════


class TaskCreate(BaseModel):
    wbs_node_id: uuid.UUID | None = None
    parent_task_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    planned_duration_days: int | None = None
    estimated_hours: float | None = None
    estimated_cost: float | None = None
    assigned_to: uuid.UUID | None = None
    is_milestone: bool = False
    sort_order: int = 0
    notes: str | None = None


class TaskUpdate(BaseModel):
    wbs_node_id: uuid.UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = None
    blocked_reason: str | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    planned_duration_days: int | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    percent_complete: float | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    estimated_cost: float | None = None
    actual_cost: float | None = None
    assigned_to: uuid.UUID | None = None
    is_critical_path: bool | None = None
    is_milestone: bool | None = None
    sort_order: int | None = None
    notes: str | None = None


class TaskOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    wbs_node_id: uuid.UUID | None = None
    parent_task_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    status: str
    blocked_reason: str | None = None
    escalated: bool
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    planned_duration_days: int | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    percent_complete: float
    estimated_hours: float | None = None
    actual_hours: float | None = None
    estimated_cost: float | None = None
    actual_cost: float | None = None
    assigned_to: uuid.UUID | None = None
    is_critical_path: bool
    is_milestone: bool
    sort_order: int
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskDependencyCreate(BaseModel):
    """F070: Task dependency (FS/SS/FF/SF)."""
    depends_on_id: uuid.UUID
    dependency_type: str = "finish_to_start"
    lag_days: int = 0


class TaskDependencyOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    depends_on_id: uuid.UUID
    dependency_type: str
    lag_days: int

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# DEVIZ — F071, F125
# ═══════════════════════════════════════════════════════════════════════════════


class DevizItemCreate(BaseModel):
    wbs_node_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    code: str | None = Field(None, max_length=50)
    description: str = Field(..., min_length=1)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    estimated_quantity: float = 0.0
    estimated_unit_price_material: float = 0.0
    estimated_unit_price_labor: float = 0.0
    currency: str = "RON"
    sort_order: int = 0


class DevizItemUpdate(BaseModel):
    wbs_node_id: uuid.UUID | None = None
    code: str | None = Field(None, max_length=50)
    description: str | None = None
    unit_of_measure: str | None = None
    estimated_quantity: float | None = None
    estimated_unit_price_material: float | None = None
    estimated_unit_price_labor: float | None = None
    actual_quantity: float | None = None
    actual_unit_price_material: float | None = None
    actual_unit_price_labor: float | None = None
    currency: str | None = None
    sort_order: int | None = None


class DevizItemOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    wbs_node_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    code: str | None = None
    description: str
    unit_of_measure: str
    estimated_quantity: float
    estimated_unit_price_material: float
    estimated_unit_price_labor: float
    estimated_total: float
    actual_quantity: float
    actual_unit_price_material: float
    actual_unit_price_labor: float
    actual_total: float
    currency: str
    sort_order: int
    over_budget_alert: bool
    import_source: str | None = None
    import_reference: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# TIMESHEET — F072
# ═══════════════════════════════════════════════════════════════════════════════


class TimesheetCreate(BaseModel):
    task_id: uuid.UUID | None = None
    work_date: datetime
    hours: float = Field(..., gt=0)
    hourly_rate: float | None = None
    description: str | None = None


class TimesheetUpdate(BaseModel):
    task_id: uuid.UUID | None = None
    work_date: datetime | None = None
    hours: float | None = Field(None, gt=0)
    hourly_rate: float | None = None
    description: str | None = None
    status: str | None = None


class TimesheetOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    task_id: uuid.UUID | None = None
    user_id: uuid.UUID
    work_date: datetime
    hours: float
    hourly_rate: float | None = None
    cost: float | None = None
    description: str | None = None
    status: str
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIALS — F074
# ═══════════════════════════════════════════════════════════════════════════════


class MaterialConsumptionCreate(BaseModel):
    wbs_node_id: uuid.UUID | None = None
    deviz_item_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    material_name: str = Field(..., min_length=1, max_length=255)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    planned_quantity: float = 0.0
    consumed_quantity: float = 0.0
    unit_price: float | None = None
    consumption_date: datetime


class MaterialConsumptionOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    wbs_node_id: uuid.UUID | None = None
    deviz_item_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    material_name: str
    unit_of_measure: str
    planned_quantity: float
    consumed_quantity: float
    unit_price: float | None = None
    total_cost: float | None = None
    consumption_date: datetime
    registered_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# SUBCONTRACTORS — F075
# ═══════════════════════════════════════════════════════════════════════════════


class SubcontractorCreate(BaseModel):
    contact_id: uuid.UUID | None = None
    company_name: str = Field(..., min_length=1, max_length=255)
    contract_number: str | None = Field(None, max_length=50)
    contract_value: float | None = None
    currency: str = "RON"
    scope_description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    notes: str | None = None


class SubcontractorUpdate(BaseModel):
    company_name: str | None = Field(None, min_length=1, max_length=255)
    contract_number: str | None = Field(None, max_length=50)
    contract_value: float | None = None
    scope_description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    percent_complete: float | None = None
    invoiced_amount: float | None = None
    paid_amount: float | None = None
    notes: str | None = None


class SubcontractorOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    company_name: str
    contract_number: str | None = None
    contract_value: float | None = None
    currency: str
    scope_description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    percent_complete: float
    invoiced_amount: float
    paid_amount: float
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# DAILY REPORT (RZS) — F077
# ═══════════════════════════════════════════════════════════════════════════════


class DailyReportCreate(BaseModel):
    report_date: datetime
    weather: str | None = Field(None, max_length=100)
    temperature_min: float | None = None
    temperature_max: float | None = None
    activities_summary: str | None = None
    personnel_present: dict | None = None
    equipment_used: dict | None = None
    materials_received: dict | None = None
    observations: str | None = None
    issues: str | None = None
    photos: list | None = None


class DailyReportOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    report_date: datetime
    weather: str | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    activities_summary: str | None = None
    personnel_present: dict | None = None
    equipment_used: dict | None = None
    materials_received: dict | None = None
    observations: str | None = None
    issues: str | None = None
    photos: list | None = None
    reported_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# WORK SITUATION (SdL) — F079
# ═══════════════════════════════════════════════════════════════════════════════


class WorkSituationCreate(BaseModel):
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2000)
    sdl_number: str = Field(..., min_length=1, max_length=50)
    contracted_total: float = 0.0
    executed_current: float = 0.0
    executed_cumulated: float = 0.0
    remaining: float = 0.0
    currency: str = "RON"
    line_items: list | None = None


class WorkSituationUpdate(BaseModel):
    executed_current: float | None = None
    executed_cumulated: float | None = None
    remaining: float | None = None
    line_items: list | None = None


class WorkSituationOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    period_month: int
    period_year: int
    sdl_number: str
    contracted_total: float
    executed_current: float
    executed_cumulated: float
    remaining: float
    currency: str
    is_approved: bool
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    is_invoiced: bool
    line_items: list | None = None
    pdf_path: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# RISK REGISTER — F084
# ═══════════════════════════════════════════════════════════════════════════════


class RiskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    probability: str  # very_low|low|medium|high|very_high
    impact: str  # negligible|minor|moderate|major|critical
    mitigation_plan: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None
    identified_date: datetime | None = None
    review_date: datetime | None = None
    notes: str | None = None


class RiskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    category: str | None = None
    probability: str | None = None
    impact: str | None = None
    status: str | None = None
    risk_score: float | None = None
    mitigation_plan: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None
    review_date: datetime | None = None
    notes: str | None = None


class RiskOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None = None
    category: str | None = None
    probability: str
    impact: str
    risk_score: float | None = None
    status: str
    mitigation_plan: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None
    identified_date: datetime | None = None
    review_date: datetime | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# PUNCH ITEMS — F086
# ═══════════════════════════════════════════════════════════════════════════════


class PunchItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    severity: str = "medium"  # low|medium|high|critical
    responsible_id: uuid.UUID | None = None
    due_date: datetime | None = None
    location: str | None = Field(None, max_length=255)
    photos: list | None = None


class PunchItemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    responsible_id: uuid.UUID | None = None
    due_date: datetime | None = None
    location: str | None = None
    photos: list | None = None


class PunchItemOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None = None
    severity: str
    status: str
    responsible_id: uuid.UUID | None = None
    due_date: datetime | None = None
    resolved_at: datetime | None = None
    photos: list | None = None
    location: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY IMPACT — F088, F090, F105, F161
# ═══════════════════════════════════════════════════════════════════════════════


class EnergyImpactCreate(BaseModel):
    property_id: uuid.UUID | None = None
    pre_kwh_annual: float | None = None
    pre_gas_mc_annual: float | None = None
    pre_co2_kg_annual: float | None = None
    pre_u_value_avg: float | None = None
    post_kwh_annual: float | None = None
    post_gas_mc_annual: float | None = None
    post_co2_kg_annual: float | None = None
    post_u_value_avg: float | None = None
    estimated_kwh_savings: float | None = None
    estimated_co2_reduction: float | None = None
    actual_kwh_savings: float | None = None
    actual_co2_reduction: float | None = None
    total_area_sqm: float | None = None
    treated_area_sqm: float | None = None
    materials_summary: dict | None = None
    total_project_cost: float | None = None
    duration_days: int | None = None
    ml_data_mapping: dict | None = None


class EnergyImpactOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    property_id: uuid.UUID | None = None
    pre_kwh_annual: float | None = None
    pre_gas_mc_annual: float | None = None
    pre_co2_kg_annual: float | None = None
    pre_u_value_avg: float | None = None
    post_kwh_annual: float | None = None
    post_gas_mc_annual: float | None = None
    post_co2_kg_annual: float | None = None
    post_u_value_avg: float | None = None
    estimated_kwh_savings: float | None = None
    estimated_co2_reduction: float | None = None
    actual_kwh_savings: float | None = None
    actual_co2_reduction: float | None = None
    total_area_sqm: float | None = None
    treated_area_sqm: float | None = None
    materials_summary: dict | None = None
    total_project_cost: float | None = None
    duration_days: int | None = None
    ml_data_mapping: dict | None = None
    ml_dataset_exported: bool
    ml_export_date: datetime | None = None
    is_verified: bool
    verified_by: uuid.UUID | None = None
    verified_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EnergyPortfolioOut(BaseModel):
    """F161: Aggregated energy portfolio across all completed projects."""
    total_kwh_saved: float
    total_co2_reduced: float
    total_projects: int
    total_area_treated_sqm: float
    avg_u_value_pre: float | None = None
    avg_u_value_post: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT FINANCE — F091, F092, F093, F094
# ═══════════════════════════════════════════════════════════════════════════════


class ProjectFinanceCreate(BaseModel):
    entry_type: str  # revenue|cost
    category: str = Field(..., min_length=1, max_length=50)
    subcategory: str | None = Field(None, max_length=100)
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2000)
    forecast_amount: float = 0.0
    actual_amount: float = 0.0
    currency: str = "RON"


class ProjectFinanceOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    entry_type: str
    category: str
    subcategory: str | None = None
    period_month: int
    period_year: int
    forecast_amount: float
    actual_amount: float
    variance: float
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CashFlowCreate(BaseModel):
    entry_type: str  # inflow|outflow
    description: str | None = None
    amount: float
    currency: str = "RON"
    transaction_date: datetime
    invoice_id: uuid.UUID | None = None


class CashFlowOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    entry_type: str
    description: str | None = None
    amount: float
    currency: str
    transaction_date: datetime
    invoice_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT JOB — F123
# ═══════════════════════════════════════════════════════════════════════════════


class ImportJobCreate(BaseModel):
    source_type: str  # intersoft|edevize|csv|excel|api
    file_name: str = Field(..., min_length=1, max_length=500)
    file_path: str = Field(..., min_length=1, max_length=1000)
    mapping_config: dict | None = None


class ImportJobOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None = None
    source_type: str
    file_name: str
    file_path: str
    status: str
    mapping_config: dict | None = None
    preview_data: dict | None = None
    error_log: list | None = None
    records_imported: int
    records_total: int
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# WIKI — F144
# ═══════════════════════════════════════════════════════════════════════════════


class WikiPostCreate(BaseModel):
    department: str | None = Field(None, max_length=100)
    post_type: str = "post"  # post|file|document
    title: str = Field(..., min_length=1, max_length=500)
    content: str | None = None
    is_official: bool = False
    document_type_badge: str | None = Field(None, max_length=50)
    file_path: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    mime_type: str | None = None


class WikiPostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    is_official: bool | None = None
    document_type_badge: str | None = None


class WikiPostOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None = None
    department: str | None = None
    post_type: str
    title: str
    content: str | None = None
    is_official: bool
    document_type_badge: str | None = None
    version: int
    file_path: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    author_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WikiCommentCreate(BaseModel):
    parent_comment_id: uuid.UUID | None = None
    content: str = Field(..., min_length=1)


class WikiCommentOut(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    parent_comment_id: uuid.UUID | None = None
    author_id: uuid.UUID | None = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT REPORTS — F095
# ═══════════════════════════════════════════════════════════════════════════════


class ProjectReportOut(BaseModel):
    """F095: Aggregated project report (schedule + financial + KPIs)."""
    project_id: uuid.UUID
    project_name: str
    status: str
    percent_complete: float
    # Schedule
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    # Financial
    budget_allocated: float | None = None
    budget_actual: float | None = None
    budget_variance: float | None = None
    # KPIs
    cpi: float | None = None
    spi: float | None = None
    # Counts
    total_tasks: int = 0
    completed_tasks: int = 0
    open_risks: int = 0
    open_punch_items: int = 0
