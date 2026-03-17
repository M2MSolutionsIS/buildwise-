"""
Pydantic schemas for System module — auth, users, roles, organizations.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ─── Auth Schemas ─────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    organization_name: str | None = Field(None, max_length=255)


# ─── User Schemas ─────────────────────────────────────────────────────────────


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_superuser: bool
    organization_id: uuid.UUID
    language: str
    last_login: datetime | None = None
    created_at: datetime
    roles: list[str] = []

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    language: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# ─── Role Schemas ─────────────────────────────────────────────────────────────


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    is_system: bool

    model_config = {"from_attributes": True}


# ─── Organization Schemas ─────────────────────────────────────────────────────


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    active_prototype: str
    default_language: str
    default_currency: str
    setup_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Audit Log Schemas ───────────────────────────────────────────────────────


class AuditLogOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: uuid.UUID
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ─── Generic API Response Wrapper ─────────────────────────────────────────────


class Meta(BaseModel):
    total: int = 0
    page: int = 1
    per_page: int = 20


class ApiResponse(BaseModel):
    """Standard response wrapper: { data: ..., meta: ... }"""
    data: object
    meta: Meta | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    prototype: str


# ═══════════════════════════════════════════════════════════════════════════════
# RBAC Admin — F040 (CRUD roles/permissions/user-role assignment)
# ═══════════════════════════════════════════════════════════════════════════════


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class PermissionOut(BaseModel):
    id: uuid.UUID
    module: str
    action: str
    description: str | None = None

    model_config = {"from_attributes": True}


class RolePermissionAssign(BaseModel):
    permission_ids: list[uuid.UUID]


class UserRoleAssign(BaseModel):
    role_ids: list[uuid.UUID]


# ═══════════════════════════════════════════════════════════════════════════════
# Audit Log — F041 (filtering)
# ═══════════════════════════════════════════════════════════════════════════════


class AuditLogFilter(BaseModel):
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    action: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# Configurators — F039, F106, F136
# ═══════════════════════════════════════════════════════════════════════════════


class CustomFieldCreate(BaseModel):
    """F039/F106: Create custom field definition."""
    entity_type: str = Field(..., min_length=1)
    field_name: str = Field(..., min_length=1)
    field_label: str = Field(..., min_length=1)
    field_type: str  # text, number, date, select, etc.
    is_required: bool = False
    default_value: str | None = None
    options: list | None = None
    sort_order: int = 0


class CustomFieldUpdate(BaseModel):
    field_label: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    default_value: str | None = None
    options: list | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CustomFieldOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    entity_type: str
    field_name: str
    field_label: str
    field_type: str
    is_required: bool
    default_value: str | None = None
    options: list | None = None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentTemplateCreate(BaseModel):
    """F106: Create document template."""
    name: str = Field(..., min_length=1)
    template_type: str  # offer, contract, report, invoice
    content: str | None = None
    placeholders: list | None = None
    layout_config: dict | None = None
    is_default: bool = False


class DocumentTemplateUpdate(BaseModel):
    name: str | None = None
    content: str | None = None
    placeholders: list | None = None
    layout_config: dict | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class DocumentTemplateOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    template_type: str
    content: str | None = None
    placeholders: list | None = None
    layout_config: dict | None = None
    is_default: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineStageConfigCreate(BaseModel):
    """F039/F136: Pipeline stage config."""
    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    sort_order: int
    color: str | None = None
    win_probability: float | None = None
    stagnation_days: int | None = None
    required_fields: list | None = None
    auto_advance_rules: dict | None = None
    is_closed_won: bool = False
    is_closed_lost: bool = False


class PipelineStageConfigUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    color: str | None = None
    win_probability: float | None = None
    stagnation_days: int | None = None
    required_fields: list | None = None
    auto_advance_rules: dict | None = None
    is_active: bool | None = None


class PipelineStageConfigOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    sort_order: int
    color: str | None = None
    win_probability: float | None = None
    stagnation_days: int | None = None
    required_fields: list | None = None
    auto_advance_rules: dict | None = None
    is_active: bool
    is_closed_won: bool
    is_closed_lost: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagOut(BaseModel):
    id: uuid.UUID
    f_code: str
    name: str
    module: str
    is_p1: bool
    is_p2: bool
    is_p3: bool
    is_enabled: bool
    config: dict | None = None

    model_config = {"from_attributes": True}


class FeatureFlagUpdate(BaseModel):
    is_enabled: bool | None = None
    config: dict | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# Currency — F139
# ═══════════════════════════════════════════════════════════════════════════════


class CurrencyCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    is_default: bool = False


class CurrencyUpdate(BaseModel):
    name: str | None = None
    symbol: str | None = None
    is_default: bool | None = None


class CurrencyOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    symbol: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ExchangeRateCreate(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate: float
    effective_date: datetime


class ExchangeRateOut(BaseModel):
    id: uuid.UUID
    from_currency: str
    to_currency: str
    rate: float
    effective_date: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# TrueCast — F140
# ═══════════════════════════════════════════════════════════════════════════════


class TrueCastOut(BaseModel):
    """F140: Actual vs Forecast comparison across modules."""
    project_id: uuid.UUID
    project_name: str
    # Schedule
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    schedule_variance_days: int | None = None
    # Budget
    budget_forecast: float | None = None
    budget_actual: float | None = None
    budget_variance: float | None = None
    # Hours
    hours_estimated: float = 0.0
    hours_actual: float = 0.0
    hours_variance: float = 0.0
    # Deviz
    deviz_estimated: float = 0.0
    deviz_actual: float = 0.0
    deviz_variance: float = 0.0
    # EVM
    cpi: float | None = None
    spi: float | None = None
    # Invoices
    invoiced_forecast: float = 0.0
    invoiced_actual: float = 0.0
    invoiced_variance: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Notifications — F141
# ═══════════════════════════════════════════════════════════════════════════════


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    link: str | None = None
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None


class NotificationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    status: str
    link: str | None = None
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    read_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    channel: str = "in_app"
    subject_template: str | None = None
    body_template: str | None = None
    target_roles: list | None = None


class NotificationTemplateOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    event_type: str
    channel: str
    subject_template: str | None = None
    body_template: str | None = None
    is_active: bool
    target_roles: list | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Report Export — F142
# ═══════════════════════════════════════════════════════════════════════════════


class ReportExportRequest(BaseModel):
    """F142: Request report export."""
    report_type: str  # project_report, budget, pipeline, contacts, etc.
    format: str = "json"  # json, csv (actual PDF/Excel requires engine)
    filters: dict | None = None
    project_id: uuid.UUID | None = None


class ReportExportOut(BaseModel):
    report_type: str
    format: str
    generated_at: datetime
    record_count: int = 0
    data: list | object = []


# ═══════════════════════════════════════════════════════════════════════════════
# Sync Journal — F143
# ═══════════════════════════════════════════════════════════════════════════════


class SyncStatusOut(BaseModel):
    """F143: Cross-module sync status."""
    module: str
    entity_type: str
    total_records: int = 0
    last_sync: datetime | None = None
    errors: list = []
    status: str = "ok"
