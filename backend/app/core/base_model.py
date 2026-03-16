"""Base model mixin with common fields for all entities."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    """Adds soft delete capability."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class OrgMixin:
    """Adds organization_id for multi-tenant isolation (P3)."""

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )


class PrototypeFlagMixin:
    """Feature flag mixin to control visibility per prototype."""

    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BasePKMixin:
    """UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class AuditFieldsMixin:
    """Tracks who created/updated a record."""

    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class NoteMixin:
    """Adds a notes text field."""

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
