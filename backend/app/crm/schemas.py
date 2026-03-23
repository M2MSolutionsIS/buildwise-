"""
CRM module schemas — F001–F005, F007, F010, F012, F016, F018.

Covers: Contacts, ContactPersons, Interactions, Products, ProductCategories,
Properties, EnergyProfiles, PropertyWorkHistory, Segmentation.
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


# ─── F005: Duplicate Check Response ─────────────────────────────────────────


class DuplicateMatch(BaseModel):
    """A potential duplicate contact."""
    id: uuid.UUID
    company_name: str
    cui: str | None = None
    email: str | None = None
    phone: str | None = None
    match_field: str  # "cui" | "email" | "phone"
    match_value: str


class DuplicateCheckResponse(BaseModel):
    """F005: Duplicate validation result."""
    has_duplicates: bool = False
    matches: list[DuplicateMatch] = []


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


# ─── Product Schemas — F007 ─────────────────────────────────────────────────


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


# ─── Property Schemas — F010 ────────────────────────────────────────────────


class PropertyCreate(BaseModel):
    contact_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    property_type: str = "other"
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    country: str = "Romania"
    total_area_sqm: float | None = None
    heated_area_sqm: float | None = None
    floors_count: int | None = None
    year_built: int | None = None
    year_renovated: int | None = None
    structure_material: str | None = Field(None, max_length=100)
    facade_material: str | None = Field(None, max_length=100)
    roof_type: str | None = Field(None, max_length=100)
    energy_certificate: str | None = Field(None, max_length=50)
    energy_class: str | None = Field(None, max_length=10)
    custom_data: dict | None = None
    notes: str | None = None


class PropertyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    property_type: str | None = None
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    country: str | None = None
    total_area_sqm: float | None = None
    heated_area_sqm: float | None = None
    floors_count: int | None = None
    year_built: int | None = None
    year_renovated: int | None = None
    structure_material: str | None = Field(None, max_length=100)
    facade_material: str | None = Field(None, max_length=100)
    roof_type: str | None = Field(None, max_length=100)
    energy_certificate: str | None = Field(None, max_length=50)
    energy_class: str | None = Field(None, max_length=10)
    custom_data: dict | None = None
    notes: str | None = None


class PropertyOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    name: str
    property_type: str
    address: str | None = None
    city: str | None = None
    county: str | None = None
    country: str
    total_area_sqm: float | None = None
    heated_area_sqm: float | None = None
    floors_count: int | None = None
    year_built: int | None = None
    year_renovated: int | None = None
    structure_material: str | None = None
    facade_material: str | None = None
    roof_type: str | None = None
    energy_certificate: str | None = None
    energy_class: str | None = None
    custom_data: dict | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PropertyListOut(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    name: str
    property_type: str
    city: str | None = None
    county: str | None = None
    total_area_sqm: float | None = None
    energy_class: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Energy Profile Schemas — F012 ──────────────────────────────────────────


class EnergyProfileCreate(BaseModel):
    u_value_walls: float | None = None
    u_value_roof: float | None = None
    u_value_floor: float | None = None
    u_value_windows: float | None = None
    u_value_doors: float | None = None
    u_value_treated_glass: float | None = None
    hvac_type: str | None = Field(None, max_length=100)
    hvac_capacity_kw: float | None = None
    hvac_efficiency: float | None = None
    hvac_year_installed: int | None = None
    heating_source: str | None = Field(None, max_length=100)
    cooling_source: str | None = Field(None, max_length=100)
    annual_consumption_kwh: float | None = None
    annual_consumption_gas_mc: float | None = None
    estimated_savings_kwh: float | None = None
    estimated_co2_reduction_kg: float | None = None
    climate_zone: str | None = Field(None, max_length=50)
    extended_data: dict | None = None


class EnergyProfileUpdate(BaseModel):
    u_value_walls: float | None = None
    u_value_roof: float | None = None
    u_value_floor: float | None = None
    u_value_windows: float | None = None
    u_value_doors: float | None = None
    u_value_treated_glass: float | None = None
    hvac_type: str | None = Field(None, max_length=100)
    hvac_capacity_kw: float | None = None
    hvac_efficiency: float | None = None
    hvac_year_installed: int | None = None
    heating_source: str | None = Field(None, max_length=100)
    cooling_source: str | None = Field(None, max_length=100)
    annual_consumption_kwh: float | None = None
    annual_consumption_gas_mc: float | None = None
    estimated_savings_kwh: float | None = None
    estimated_co2_reduction_kg: float | None = None
    climate_zone: str | None = Field(None, max_length=50)
    extended_data: dict | None = None


class EnergyProfileOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    u_value_walls: float | None = None
    u_value_roof: float | None = None
    u_value_floor: float | None = None
    u_value_windows: float | None = None
    u_value_doors: float | None = None
    u_value_treated_glass: float | None = None
    hvac_type: str | None = None
    hvac_capacity_kw: float | None = None
    hvac_efficiency: float | None = None
    hvac_year_installed: int | None = None
    heating_source: str | None = None
    cooling_source: str | None = None
    annual_consumption_kwh: float | None = None
    annual_consumption_gas_mc: float | None = None
    estimated_savings_kwh: float | None = None
    estimated_co2_reduction_kg: float | None = None
    climate_zone: str | None = None
    extended_data: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class EnergyCalculatorRequest(BaseModel):
    """F012: Simple energy savings calculator input."""
    total_area_sqm: float
    u_value_current: float
    u_value_proposed: float
    heating_degree_days: float = 3000.0  # Default for Romania average


class EnergyCalculatorResponse(BaseModel):
    """F012: Energy savings calculator output."""
    current_loss_kwh: float
    proposed_loss_kwh: float
    savings_kwh: float
    savings_percent: float
    estimated_co2_reduction_kg: float


# ─── Property Work History Schemas — F016 ────────────────────────────────────


class WorkHistoryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    work_type: str | None = Field(None, max_length=100)
    performed_by: str | None = Field(None, max_length=255)
    start_date: datetime | None = None
    end_date: datetime | None = None
    cost: float | None = None
    currency: str = "RON"
    project_id: uuid.UUID | None = None


class WorkHistoryUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    work_type: str | None = Field(None, max_length=100)
    performed_by: str | None = Field(None, max_length=255)
    start_date: datetime | None = None
    end_date: datetime | None = None
    cost: float | None = None
    currency: str | None = None
    project_id: uuid.UUID | None = None


class WorkHistoryOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    title: str
    description: str | None = None
    work_type: str | None = None
    performed_by: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    cost: float | None = None
    currency: str
    project_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# F004 — Import / Export / Merge
# ═══════════════════════════════════════════════════════════════════════════════


class ContactImportRow(BaseModel):
    """A single row from CSV/Excel import."""
    company_name: str
    cui: str | None = None
    email: str | None = None
    phone: str | None = None
    contact_type: str = "pj"
    stage: str = "prospect"
    city: str | None = None
    county: str | None = None
    address: str | None = None
    source: str | None = None


class ContactImportRequest(BaseModel):
    """F004: Bulk import contacts from structured data."""
    rows: list[ContactImportRow]
    skip_duplicates: bool = True


class ContactImportResult(BaseModel):
    """F004: Import result summary."""
    total_rows: int
    imported: int
    skipped_duplicates: int
    errors: list[str] = []


class ContactExportRequest(BaseModel):
    """F004: Export contacts with optional filters."""
    format: str = "json"  # json, csv
    stage: str | None = None
    contact_type: str | None = None
    city: str | None = None
    county: str | None = None


class ContactMergeRequest(BaseModel):
    """F004: Merge two contacts into one."""
    source_id: uuid.UUID
    target_id: uuid.UUID
    fields_from_source: list[str] = []


# ═══════════════════════════════════════════════════════════════════════════════
# F005/F016 — Documents
# ═══════════════════════════════════════════════════════════════════════════════


class DocumentCreate(BaseModel):
    """Create document metadata (file uploaded separately)."""
    entity_type: str = "contact"  # contact | property | project
    entity_id: uuid.UUID
    file_name: str = Field(..., min_length=1, max_length=500)
    file_path: str = Field(..., min_length=1, max_length=1000)
    file_size: int | None = None
    mime_type: str | None = None
    category: str = "other"  # certificate|photo|technical|contract|offer|invoice|other
    description: str | None = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    contact_id: uuid.UUID | None = None
    property_id: uuid.UUID | None = None
    file_name: str
    file_path: str
    file_size: int | None = None
    mime_type: str | None = None
    category: str
    description: str | None = None
    version: int
    created_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListOut(BaseModel):
    id: uuid.UUID
    file_name: str
    file_size: int | None = None
    mime_type: str | None = None
    category: str
    description: str | None = None
    version: int
    created_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
