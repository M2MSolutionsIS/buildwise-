"""
Pydantic schemas for CRM module — F001–F024.

Covers: Contacts, ContactPersons, Interactions, Products, ProductCategories,
Offers, OfferLineItems, Contracts, Invoices, Sales KPI.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ─── Contact Schemas — F001, F003 ────────────────────────────────────────────


class ContactPersonCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    is_primary: bool = False


class ContactPersonUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    role: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    is_primary: bool | None = None


class ContactPersonOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    first_name: str
    last_name: str
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    cui: str | None = Field(None, max_length=20)
    registration_number: str | None = Field(None, max_length=50)
    stage: str = "prospect"  # prospect|potential_client|active|inactive|partner
    contact_type: str = "pj"  # pf|imm|pj|corporation
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str = "Romania"
    phone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    website: str | None = Field(None, max_length=255)
    vat_payer: bool = False
    bank_account: str | None = Field(None, max_length=50)
    bank_name: str | None = Field(None, max_length=100)
    gdpr_consent: bool = False
    tags: list[str] | None = None
    source: str | None = Field(None, max_length=100)
    notes: str | None = None
    persons: list[ContactPersonCreate] | None = None


class ContactUpdate(BaseModel):
    company_name: str | None = Field(None, min_length=1, max_length=255)
    cui: str | None = Field(None, max_length=20)
    registration_number: str | None = Field(None, max_length=50)
    stage: str | None = None
    contact_type: str | None = None
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = None
    phone: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    website: str | None = Field(None, max_length=255)
    vat_payer: bool | None = None
    bank_account: str | None = Field(None, max_length=50)
    bank_name: str | None = Field(None, max_length=100)
    gdpr_consent: bool | None = None
    tags: list[str] | None = None
    source: str | None = Field(None, max_length=100)
    notes: str | None = None


class ContactOut(BaseModel):
    id: uuid.UUID
    company_name: str
    cui: str | None = None
    registration_number: str | None = None
    stage: str
    contact_type: str
    address: str | None = None
    city: str | None = None
    county: str | None = None
    postal_code: str | None = None
    country: str
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    vat_payer: bool
    bank_account: str | None = None
    bank_name: str | None = None
    gdpr_consent: bool
    gdpr_consent_date: datetime | None = None
    tags: list | None = None
    source: str | None = None
    notes: str | None = None
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None
    persons: list[ContactPersonOut] = []

    model_config = {"from_attributes": True}


class ContactListOut(BaseModel):
    """Lightweight contact for list views."""
    id: uuid.UUID
    company_name: str
    cui: str | None = None
    stage: str
    contact_type: str
    city: str | None = None
    county: str | None = None
    phone: str | None = None
    email: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Interaction Schemas — F002 ──────────────────────────────────────────────


class InteractionCreate(BaseModel):
    interaction_type: str  # call|email|meeting|offer|contract|note|visit
    subject: str | None = Field(None, max_length=500)
    description: str | None = None
    interaction_date: datetime
    duration_minutes: int | None = None
    opportunity_id: uuid.UUID | None = None
    offer_id: uuid.UUID | None = None
    contract_id: uuid.UUID | None = None
    metadata_json: dict | None = None


class InteractionOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    interaction_type: str
    subject: str | None = None
    description: str | None = None
    interaction_date: datetime
    duration_minutes: int | None = None
    opportunity_id: uuid.UUID | None = None
    offer_id: uuid.UUID | None = None
    contract_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    metadata_json: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Product Category Schemas — F007 ────────────────────────────────────────


class ProductCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: uuid.UUID | None = None
    sort_order: int = 0
    is_active: bool = True


class ProductCategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    parent_id: uuid.UUID | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class ProductCategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None = None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Product Schemas — F005, F006 ───────────────────────────────────────────


class ProductCreate(BaseModel):
    category_id: uuid.UUID | None = None
    code: str | None = Field(None, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    product_type: str = "product"  # product|service|revenue|expense
    unit_of_measure: str = "buc"
    unit_price: float | None = None
    currency: str = "RON"
    vat_rate: float = 0.19
    is_active: bool = True
    parent_product_id: uuid.UUID | None = None


class ProductUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    code: str | None = Field(None, max_length=50)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    product_type: str | None = None
    unit_of_measure: str | None = None
    unit_price: float | None = None
    currency: str | None = None
    vat_rate: float | None = None
    is_active: bool | None = None
    parent_product_id: uuid.UUID | None = None


class ProductOut(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID | None = None
    code: str | None = None
    name: str
    description: str | None = None
    product_type: str
    unit_of_measure: str
    unit_price: float | None = None
    currency: str
    vat_rate: float
    is_active: bool
    parent_product_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Offer Schemas — F008, F009, F010, F012, F014, F015, F016 ───────────────


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
    """F014: Submit offer for approval."""
    comment: str | None = None


class OfferApprovalDecision(BaseModel):
    """F014: Approve or reject offer."""
    approved: bool
    comment: str | None = None


# ─── Contract Schemas — F017, F018, F019, F021, F022 ────────────────────────


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
    """F018: Auto-populate contract from accepted offer."""
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


# ─── Invoice Schemas — F021 ─────────────────────────────────────────────────


class InvoiceCreate(BaseModel):
    """F021: Create invoice from contract billing schedule."""
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


# ─── Sales KPI — F023 ───────────────────────────────────────────────────────


class SalesKPIOut(BaseModel):
    """F023: Sales KPI monitoring."""
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


# ─── Sales Report — F024 ────────────────────────────────────────────────────


class SalesReportRequest(BaseModel):
    """F024: Sales report filters."""
    date_from: datetime | None = None
    date_to: datetime | None = None
    stage: str | None = None
    contact_type: str | None = None
    owner_id: uuid.UUID | None = None
    currency: str = "RON"
