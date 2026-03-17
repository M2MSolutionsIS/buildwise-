"""
Sales Pipeline module schemas — F019, F023, F026–F029, F031, F033, F035, F037,
F042–F056, F058, F049.

Covers: Opportunities, Milestones, Activities, Offers, Contracts, Invoices,
Pipeline Board, Sales Dashboard, Analytics.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITY — F042, F050, F051, F052, F053
# ═══════════════════════════════════════════════════════════════════════════════


class OpportunityCreate(BaseModel):
    """F042: Qualify & Handover — create opportunity from CRM."""
    contact_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    stage: str = "new"
    estimated_value: float | None = None
    currency: str = "RON"
    expected_close_date: datetime | None = None
    owner_id: uuid.UUID | None = None
    source: str | None = None
    tags: list[str] | None = None
    qualification_checklist: dict | None = None
    is_qualified: bool = False
    notes: str | None = None


class OpportunityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    estimated_value: float | None = None
    currency: str | None = None
    expected_close_date: datetime | None = None
    owner_id: uuid.UUID | None = None
    source: str | None = None
    tags: list[str] | None = None
    qualification_checklist: dict | None = None
    notes: str | None = None


class OpportunityStageTransition(BaseModel):
    """F051: Drag & drop stage transition with validation."""
    new_stage: str
    loss_reason: str | None = None
    loss_reason_detail: str | None = None
    won_reason: str | None = None


class OpportunityQualify(BaseModel):
    """F042: Qualify opportunity (CRM → Pipeline handover)."""
    qualification_checklist: dict | None = None


class OpportunityOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    title: str
    description: str | None = None
    stage: str
    stage_entered_at: datetime | None = None
    estimated_value: float | None = None
    currency: str
    win_probability: float | None = None
    weighted_value: float | None = None
    expected_close_date: datetime | None = None
    actual_close_date: datetime | None = None
    owner_id: uuid.UUID | None = None
    loss_reason: str | None = None
    loss_reason_detail: str | None = None
    won_reason: str | None = None
    qualification_checklist: dict | None = None
    is_qualified: bool
    rm_validated: bool
    source: str | None = None
    tags: list | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class OpportunityListOut(BaseModel):
    id: uuid.UUID
    title: str
    stage: str
    estimated_value: float | None = None
    currency: str
    win_probability: float | None = None
    weighted_value: float | None = None
    contact_id: uuid.UUID
    owner_id: uuid.UUID | None = None
    expected_close_date: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONE — F043, F044, F045, F046, F047, F048
# ═══════════════════════════════════════════════════════════════════════════════


class MilestoneCreate(BaseModel):
    """F043: Create milestone for an opportunity."""
    opportunity_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    sort_order: int = 0
    estimated_duration_days: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    estimated_resources: dict | None = None
    estimated_cost: float | None = None
    currency: str = "RON"
    assigned_to: uuid.UUID | None = None
    deadline: datetime | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = None
    sort_order: int | None = None
    estimated_duration_days: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    estimated_resources: dict | None = None
    estimated_cost: float | None = None
    currency: str | None = None
    rm_validated: bool | None = None
    assigned_to: uuid.UUID | None = None
    deadline: datetime | None = None


class MilestoneOut(BaseModel):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    status: str
    sort_order: int
    estimated_duration_days: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    estimated_resources: dict | None = None
    estimated_cost: float | None = None
    currency: str
    rm_validated: bool
    assigned_to: uuid.UUID | None = None
    deadline: datetime | None = None
    template_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class MilestoneDependencyCreate(BaseModel):
    """F047: Create dependency between milestones."""
    depends_on_id: uuid.UUID
    dependency_type: str = "finish_to_start"
    lag_days: int = 0


class MilestoneDependencyOut(BaseModel):
    id: uuid.UUID
    milestone_id: uuid.UUID
    depends_on_id: uuid.UUID
    dependency_type: str
    lag_days: int

    model_config = {"from_attributes": True}


class MilestoneTemplateCreate(BaseModel):
    """F048: Create milestone template."""
    name: str = Field(..., min_length=1, max_length=255)
    product_category_id: uuid.UUID | None = None
    template_data: dict
    is_active: bool = True


class MilestoneTemplateOut(BaseModel):
    id: uuid.UUID
    name: str
    product_category_id: uuid.UUID | None = None
    template_data: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MilestoneTemplateApply(BaseModel):
    """F048: Apply template to an opportunity."""
    template_id: uuid.UUID
    opportunity_id: uuid.UUID


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVITY — F054, F055, F056
# ═══════════════════════════════════════════════════════════════════════════════


class ActivityCreate(BaseModel):
    """F054: Create activity (call, meeting, visit, follow-up)."""
    activity_type: str
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    scheduled_date: datetime
    scheduled_end_date: datetime | None = None
    duration_minutes: int | None = None
    contact_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    # Technical visit — F055
    visit_data: dict | None = None
    measurements: dict | None = None
    # Call/email — F056
    call_duration_seconds: int | None = None
    call_outcome: str | None = None
    email_subject: str | None = None
    email_tracked: bool = False
    is_recurring: bool = False
    recurrence_rule: dict | None = None
    notes: str | None = None


class ActivityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = None
    scheduled_date: datetime | None = None
    scheduled_end_date: datetime | None = None
    duration_minutes: int | None = None
    contact_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    visit_data: dict | None = None
    measurements: dict | None = None
    call_duration_seconds: int | None = None
    call_outcome: str | None = None
    email_subject: str | None = None
    email_tracked: bool | None = None
    notes: str | None = None


class ActivityOut(BaseModel):
    id: uuid.UUID
    activity_type: str
    title: str
    description: str | None = None
    status: str
    scheduled_date: datetime
    scheduled_end_date: datetime | None = None
    duration_minutes: int | None = None
    completed_at: datetime | None = None
    contact_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    visit_data: dict | None = None
    measurements: dict | None = None
    call_duration_seconds: int | None = None
    call_outcome: str | None = None
    email_subject: str | None = None
    email_tracked: bool
    is_recurring: bool
    recurrence_rule: dict | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ActivityListOut(BaseModel):
    id: uuid.UUID
    activity_type: str
    title: str
    status: str
    scheduled_date: datetime
    contact_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# OFFER — F019, F023, F026, F027, F028, F029, F049
# ═══════════════════════════════════════════════════════════════════════════════


class OfferLineItemCreate(BaseModel):
    product_id: uuid.UUID | None = None
    description: str
    quantity: float = 1.0
    unit_of_measure: str = "buc"
    unit_price: float
    discount_percent: float = 0.0
    vat_rate: float = 0.19
    sort_order: int = 0


class OfferLineItemOut(BaseModel):
    id: uuid.UUID
    offer_id: uuid.UUID
    product_id: uuid.UUID | None = None
    description: str
    quantity: float
    unit_of_measure: str
    unit_price: float
    discount_percent: float
    vat_rate: float
    total_price: float
    sort_order: int

    model_config = {"from_attributes": True}


class OfferCreate(BaseModel):
    contact_id: uuid.UUID
    opportunity_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    currency: str = "RON"
    terms_and_conditions: str | None = None
    validity_days: int = 30
    template_id: uuid.UUID | None = None
    is_quick_quote: bool = False
    line_items: list[OfferLineItemCreate] = []


class OfferUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    currency: str | None = None
    terms_and_conditions: str | None = None
    validity_days: int | None = None
    template_id: uuid.UUID | None = None
    notes: str | None = None


class OfferOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    opportunity_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    offer_number: str
    title: str
    description: str | None = None
    status: str
    version: int
    parent_offer_id: uuid.UUID | None = None
    subtotal: float
    discount_percent: float
    discount_amount: float
    vat_amount: float
    total_amount: float
    currency: str
    terms_and_conditions: str | None = None
    validity_days: int
    valid_until: datetime | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    rejected_at: datetime | None = None
    owner_id: uuid.UUID | None = None
    is_quick_quote: bool
    pdf_path: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    line_items: list[OfferLineItemOut] = []

    model_config = {"from_attributes": True}


class OfferListOut(BaseModel):
    id: uuid.UUID
    offer_number: str
    title: str
    status: str
    total_amount: float
    currency: str
    contact_id: uuid.UUID
    created_at: datetime
    valid_until: datetime | None = None

    model_config = {"from_attributes": True}


class OfferApprovalRequest(BaseModel):
    """F028: Submit offer for approval."""
    comment: str | None = None


class OfferApprovalDecision(BaseModel):
    """F028: Approve or reject offer."""
    approved: bool
    comment: str | None = None


class OfferVersionCreate(BaseModel):
    """F026: Create new version of an offer."""
    title: str | None = None
    line_items: list[OfferLineItemCreate] | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT — F031, F033, F035, F037
# ═══════════════════════════════════════════════════════════════════════════════


class ContractCreate(BaseModel):
    contact_id: uuid.UUID
    offer_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    total_value: float = 0.0
    currency: str = "RON"
    start_date: datetime | None = None
    end_date: datetime | None = None
    terms_and_conditions: str | None = None
    standard_clauses: list[str] | None = None
    template_id: uuid.UUID | None = None


class ContractFromOffer(BaseModel):
    """F031: Auto-populate contract from accepted offer."""
    offer_id: uuid.UUID
    title: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    additional_terms: str | None = None


class ContractUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    total_value: float | None = None
    currency: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    terms_and_conditions: str | None = None
    standard_clauses: list[str] | None = None
    notes: str | None = None


class ContractSignRequest(BaseModel):
    """F031: Sign a contract — triggers Project Setup (F063)."""
    signed_date: datetime | None = None


class ContractTerminateRequest(BaseModel):
    """F035: Terminate a contract."""
    termination_reason: str


class ContractOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    offer_id: uuid.UUID | None = None
    opportunity_id: uuid.UUID | None = None
    contract_number: str
    title: str
    description: str | None = None
    status: str
    total_value: float
    currency: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    signed_date: datetime | None = None
    terms_and_conditions: str | None = None
    owner_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    pdf_path: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContractListOut(BaseModel):
    id: uuid.UUID
    contract_number: str
    title: str
    status: str
    total_value: float
    currency: str
    contact_id: uuid.UUID
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICE — F035
# ═══════════════════════════════════════════════════════════════════════════════


class BillingScheduleCreate(BaseModel):
    """F035: Add billing schedule item to contract."""
    installment_number: int
    description: str | None = None
    amount: float
    currency: str = "RON"
    due_date: datetime


class BillingScheduleOut(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    installment_number: int
    description: str | None = None
    amount: float
    currency: str
    due_date: datetime
    is_invoiced: bool
    invoice_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    """F035: Create invoice from contract billing schedule."""
    contract_id: uuid.UUID
    amount: float
    vat_amount: float = 0.0
    currency: str = "RON"
    issue_date: datetime
    due_date: datetime
    billing_schedule_id: uuid.UUID | None = None


class InvoiceOut(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    invoice_number: str
    status: str
    amount: float
    vat_amount: float
    total_amount: float
    currency: str
    issue_date: datetime
    due_date: datetime
    paid_date: datetime | None = None
    paid_amount: float | None = None
    pdf_path: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE BOARD — F050, F053
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineBoardStage(BaseModel):
    """One column on the Kanban board."""
    stage: str
    count: int
    total_value: float
    weighted_value: float
    opportunities: list[OpportunityListOut]


class PipelineBoardOut(BaseModel):
    """F050: Full Kanban board view."""
    stages: list[PipelineBoardStage]
    total_pipeline_value: float
    total_weighted_value: float
    currency: str = "RON"


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS — F029, F037, F058
# ═══════════════════════════════════════════════════════════════════════════════


class OfferAnalyticsOut(BaseModel):
    """F029: Offers Analytics."""
    total_offers: int = 0
    offers_by_status: dict = {}
    conversion_rate: float = 0.0
    avg_offer_value: float = 0.0
    total_value: float = 0.0
    currency: str = "RON"


class ContractAnalyticsOut(BaseModel):
    """F037: Contracts Analytics."""
    total_contracts: int = 0
    contracts_by_status: dict = {}
    total_active_value: float = 0.0
    avg_contract_value: float = 0.0
    termination_rate: float = 0.0
    currency: str = "RON"


class SalesKPIOut(BaseModel):
    """F058: Sales Dashboard — KPIs, funnel, forecast."""
    total_contacts: int = 0
    active_contacts: int = 0
    total_opportunities: int = 0
    open_opportunities: int = 0
    won_opportunities: int = 0
    lost_opportunities: int = 0
    pipeline_value: float = 0.0
    weighted_pipeline_value: float = 0.0
    total_offers: int = 0
    offers_sent: int = 0
    offers_accepted: int = 0
    offers_rejected: int = 0
    conversion_rate: float = 0.0
    total_contracts: int = 0
    active_contracts: int = 0
    total_revenue: float = 0.0
    total_invoiced: float = 0.0
    total_paid: float = 0.0
    avg_deal_value: float = 0.0
    currency: str = "RON"
    funnel: list[dict] = []
