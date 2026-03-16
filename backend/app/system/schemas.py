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
