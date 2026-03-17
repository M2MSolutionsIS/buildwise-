"""
Sales Pipeline module schemas — F019, F028, F031, F035.

Covers: Offers, OfferLineItems, Contracts, Invoices, Sales KPI.
Moved from CRM module to align with Centralizator_M2M_ERP_Lite.md.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ─── Offer Schemas — F019 (Offer Builder), F028 (Approval) ──────────────────


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


# ─── Contract Schemas — F031 (Contract Builder) ─────────────────────────────


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


# ─── Invoice Schemas — F035 (Billing) ───────────────────────────────────────


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


# ─── Sales KPI ───────────────────────────────────────────────────────────────


class SalesKPIOut(BaseModel):
    """Sales KPI monitoring."""
    total_contacts: int = 0
    active_contacts: int = 0
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
    currency: str = "RON"
