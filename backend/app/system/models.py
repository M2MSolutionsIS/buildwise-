"""
System module models — F040, F041, F039, F061, F106, F131, F136, F137, F138, F139, F140, F141, F142, F143, F157, F158, F160.

Covers: Organizations, Users, Roles, Permissions, Audit Trail, Notifications,
Feature Flags, Currencies, Templates, Custom Fields, and Tenant configuration.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import (
    AuditFieldsMixin,
    BasePKMixin,
    OrgMixin,
    PrototypeFlagMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.database import Base

import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class PrototypeEnum(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER_VANZARI = "manager_vanzari"
    AGENT_COMERCIAL = "agent_comercial"
    TEHNICIAN = "tehnician"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    BOTH = "both"


class NotificationStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class CustomFieldType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    BOOLEAN = "boolean"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"


# ─── Organization (Multi-tenant P3) — F160 ───────────────────────────────────

class Organization(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, PrototypeFlagMixin):
    """
    Multi-tenant organization. Each tenant is isolated.
    F160: Tenant Setup Wizard.
    """
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    cui: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Prototype config — which prototype is active for this org
    active_prototype: Mapped[str] = mapped_column(
        Enum(PrototypeEnum), default=PrototypeEnum.P1, nullable=False
    )

    # Branding — F137
    primary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    custom_branding: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Localization — F138
    default_language: Mapped[str] = mapped_column(String(5), default="ro", nullable=False)
    supported_languages: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Currency — F139
    default_currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    reference_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    # Module activation flags
    modules_enabled: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Onboarding status
    setup_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization")
    roles = relationship("Role", back_populates="organization")


# ─── User — F040, F131 ───────────────────────────────────────────────────────

class User(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin):
    """
    Platform user. F040: Roles and permissions.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # GDPR consent
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gdpr_consent_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auth
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Notification preferences — F141
    notification_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Language preference — F138
    language: Mapped[str] = mapped_column(String(5), default="ro", nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user")

    __table_args__ = (
        UniqueConstraint("email", "organization_id", name="uq_user_email_org"),
    )


# ─── Role & Permission — F040 ────────────────────────────────────────────────

class Role(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    RBAC role. Default roles: Admin, Manager Vânzări, Agent Comercial, Tehnician.
    """
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    organization = relationship("Organization", back_populates="roles")
    permissions = relationship("RolePermission", back_populates="role")
    user_roles = relationship("UserRole", back_populates="role")

    __table_args__ = (
        UniqueConstraint("code", "organization_id", name="uq_role_code_org"),
    )


class Permission(Base, BasePKMixin):
    """
    System-level permission definition.
    """
    __tablename__ = "permissions"

    module: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("module", "action", name="uq_permission_module_action"),
    )


class RolePermission(Base, BasePKMixin):
    """
    Many-to-many: Role × Permission.
    """
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False
    )

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


class UserRole(Base, BasePKMixin):
    """
    Many-to-many: User × Role.
    """
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )


# ─── Audit Trail — F041 ──────────────────────────────────────────────────────

class AuditLog(Base, BasePKMixin, OrgMixin):
    """
    Automatic audit trail: who, what, when, old/new values.
    F041: Audit log acțiuni utilizatori.
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_timestamp", "timestamp"),
    )


# ─── Notification — F141 ─────────────────────────────────────────────────────

class NotificationTemplate(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Email/in-app notification templates with triggers.
    """
    __tablename__ = "notification_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[str] = mapped_column(Enum(NotificationChannel), nullable=False)
    subject_template: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    target_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)


class Notification(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Individual notification instance sent to a user.
    """
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_templates.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False
    )
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_notification_user_status", "user_id", "status"),
    )


# ─── Custom Fields — F039, F061 ──────────────────────────────────────────────

class CustomFieldDefinition(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    User-defined custom fields per entity type.
    F039: Configurator CRM custom fields.
    F061: Configurator Pipeline.
    """
    __tablename__ = "custom_field_definitions"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # contact, opportunity, project...
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(Enum(CustomFieldType), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)  # For select/multiselect
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "entity_type", "field_name", name="uq_custom_field"),
    )


class CustomFieldValue(Base, BasePKMixin, OrgMixin):
    """
    Stores values of custom fields per entity instance.
    """
    __tablename__ = "custom_field_values"

    field_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("custom_field_definitions.id"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("field_definition_id", "entity_id", name="uq_custom_field_value"),
        Index("ix_custom_field_entity", "entity_type", "entity_id"),
    )


# ─── Currency — F139 ─────────────────────────────────────────────────────────

class Currency(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Multi-currency support with exchange rates.
    """
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(5), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "organization_id", name="uq_currency_code_org"),
    )


class ExchangeRate(Base, BasePKMixin, OrgMixin):
    """
    Exchange rate entries for currency conversion.
    """
    __tablename__ = "exchange_rates"

    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    effective_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_exchange_rate_date", "from_currency", "to_currency", "effective_date"),
    )


# ─── Document Templates — F106, F039 ─────────────────────────────────────────

class DocumentTemplate(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Templates for offers, contracts, reports.
    F039/F106: Configurator templates with placeholders.
    """
    __tablename__ = "document_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)  # offer, contract, report, invoice
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    placeholders: Mapped[list | None] = mapped_column(JSON, nullable=True)
    layout_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ─── Feature Flags ────────────────────────────────────────────────────────────

class FeatureFlag(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Controls feature availability per organization and prototype.
    Maps to F-codes from the Centralizator.
    """
    __tablename__ = "feature_flags"

    f_code: Mapped[str] = mapped_column(String(10), nullable=False)  # F001, F002, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint("f_code", "organization_id", name="uq_feature_flag_org"),
    )


# ─── Pipeline Stage Config — F040, F061 ──────────────────────────────────────

class PipelineStageConfig(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Configurable pipeline stages.
    F061: Configurator Pipeline — stadii, reguli avansare.
    """
    __tablename__ = "pipeline_stage_configs"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    win_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    stagnation_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_fields: Mapped[list | None] = mapped_column(JSON, nullable=True)
    auto_advance_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_closed_won: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_closed_lost: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "organization_id", name="uq_pipeline_stage_code_org"),
    )
