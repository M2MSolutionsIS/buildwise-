"""
Sales Pipeline module models — F019, F023, F026–F029, F031, F033, F035, F037,
F042–F056, F058, F049.

Covers: Opportunities, Milestones, Activities, Offers, Offer Lines, Offer Versions,
Contracts, Billing Schedules, Approval Workflows.
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
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import (
    AuditFieldsMixin,
    BasePKMixin,
    NoteMixin,
    OrgMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.database import Base

import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class OpportunityStage(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    SCOPING = "scoping"
    OFFERING = "offering"
    SENT = "sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class MilestoneStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DependencyType(str, enum.Enum):
    FS = "finish_to_start"
    SS = "start_to_start"
    FF = "finish_to_finish"
    SF = "start_to_finish"


class ActivityType(str, enum.Enum):
    CALL = "call"
    MEETING = "meeting"
    FOLLOW_UP = "follow_up"
    TECHNICAL_VISIT = "technical_visit"
    EMAIL = "email"
    TASK = "task"


class ActivityStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class OfferStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    NEGOTIATION = "negotiation"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    SIGNED = "signed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    COMPLETED = "completed"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LossReason(str, enum.Enum):
    PRICE = "price"
    COMPETITION = "competition"
    TIMING = "timing"
    NO_BUDGET = "no_budget"
    NO_NEED = "no_need"
    NO_RESPONSE = "no_response"
    OTHER = "other"


# ─── Predefined Loss Reasons — F053 ──────────────────────────────────────────

class PredefinedLossReason(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    F053: Predefined loss reasons managed per organization.
    Admins can CRUD these; agents pick from dropdown on Lost transition.
    """
    __tablename__ = "predefined_loss_reasons"

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_predefined_loss_reasons_org", "organization_id"),
    )


# ─── Opportunity — F042, F050, F051, F052, F053 ──────────────────────────────

class Opportunity(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Sales opportunity in the pipeline.
    F042: CRM → Pipeline handover.
    F050: Kanban board.
    F051: Drag & drop + validation + stagnation alert.
    F052: Auto win probability.
    F053: Weighted pipeline value + loss reasons.
    """
    __tablename__ = "opportunities"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pipeline — F050, F051
    stage: Mapped[str] = mapped_column(
        Enum(OpportunityStage), default=OpportunityStage.NEW, nullable=False
    )
    stage_entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Value — F053
    estimated_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    win_probability: Mapped[float | None] = mapped_column(Float, nullable=True)  # F052
    weighted_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Dates
    expected_close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Owner
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Won/Lost — F053 (String to support both enum + predefined custom reasons)
    loss_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    loss_reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    won_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Qualification checklist — F042
    qualification_checklist: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # RM validation — F045
    rm_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Source
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    milestones = relationship("Milestone", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="opportunity")
    offers = relationship("Offer", back_populates="opportunity")

    __table_args__ = (
        Index("ix_opportunity_org_stage", "organization_id", "stage"),
        Index("ix_opportunity_owner", "owner_id"),
        Index("ix_opportunity_contact", "contact_id"),
    )


# ─── Milestone — F043, F044, F045, F046, F047, F048 ──────────────────────────

class Milestone(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Hierarchical milestones per opportunity.
    F043: Create/edit milestones.
    F044: Time estimation.
    F045: Pre-dimensioning (resources + costs).
    F046: Task allocation.
    F047: Dependencies (FS/SS/FF/SF).
    F048: Template library.
    """
    __tablename__ = "milestones"

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("milestones.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED, nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Time estimation — F044
    estimated_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Pre-dimensioning — F045
    estimated_resources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    rm_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Assignment — F046
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Template reference — F048
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    opportunity = relationship("Opportunity", back_populates="milestones")
    children = relationship("Milestone", back_populates="parent")
    parent = relationship("Milestone", back_populates="children", remote_side="Milestone.id")
    dependencies = relationship(
        "MilestoneDependency",
        foreign_keys="MilestoneDependency.milestone_id",
        back_populates="milestone",
    )


class MilestoneDependency(Base, BasePKMixin):
    """
    Dependency links between milestones.
    F047: FS/SS/FF/SF dependencies.
    """
    __tablename__ = "milestone_dependencies"

    milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("milestones.id"), nullable=False
    )
    depends_on_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("milestones.id"), nullable=False
    )
    dependency_type: Mapped[str] = mapped_column(
        Enum(DependencyType), default=DependencyType.FS, nullable=False
    )
    lag_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    milestone = relationship("Milestone", foreign_keys=[milestone_id], back_populates="dependencies")
    depends_on = relationship("Milestone", foreign_keys=[depends_on_id])


class MilestoneTemplate(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Reusable milestone templates per product/service category.
    F048: Bibliotecă template-uri milestone.
    """
    __tablename__ = "milestone_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )
    template_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ─── Activity — F054, F055, F056, F058 ───────────────────────────────────────

class Activity(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Sales activities: calls, meetings, visits, follow-ups.
    F054: Daily planner.
    F055: Technical visits with photos + measurements.
    F056: Call log + email tracking.
    """
    __tablename__ = "activities"

    activity_type: Mapped[str] = mapped_column(Enum(ActivityType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ActivityStatus), default=ActivityStatus.PLANNED, nullable=False
    )

    # Scheduling
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Links
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Technical visit data — F055
    visit_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    measurements: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Call/email tracking — F056
    call_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    call_outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email_subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email_tracked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Template reference
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    opportunity = relationship("Opportunity", back_populates="activities")

    __table_args__ = (
        Index("ix_activity_owner_date", "owner_id", "scheduled_date"),
        Index("ix_activity_org_date", "organization_id", "scheduled_date"),
    )


# ─── Offer — F019, F023, F026, F027, F028, F029, F049 ────────────────────────

class Offer(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Sales offer/quote.
    F019: Offer Builder wizard.
    F023: Output — preview + export PDF/DOC.
    F026: Versioning (v1, v2...).
    F027: Status tracking (Draft→Sent→Accepted).
    F028: Approval workflow.
    F029: Offers Analytics.
    F049: Simplified flow for simple products.
    """
    __tablename__ = "offers"

    # Links
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True
    )
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True
    )

    # Offer data
    offer_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status — F027
    status: Mapped[str] = mapped_column(
        Enum(OfferStatus), default=OfferStatus.DRAFT, nullable=False
    )

    # Versioning — F026
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offers.id"), nullable=True
    )
    is_snapshot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Financial
    subtotal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    vat_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Terms & Conditions
    terms_and_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    validity_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Dates
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Follow-up — F027
    next_follow_up: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Owner
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Template
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=True
    )

    # Is quick quote — F049
    is_quick_quote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # PDF path
    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="offers")
    line_items = relationship("OfferLineItem", back_populates="offer", cascade="all, delete-orphan")
    versions = relationship("Offer", back_populates="parent_offer")
    parent_offer = relationship("Offer", back_populates="versions", remote_side="Offer.id")

    __table_args__ = (
        Index("ix_offer_org_status", "organization_id", "status"),
        Index("ix_offer_contact", "contact_id"),
    )


class OfferLineItem(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Individual line items in an offer.
    F019: Product selection in Offer Builder.
    """
    __tablename__ = "offer_line_items"

    offer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offers.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="buc", nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    vat_rate: Mapped[float] = mapped_column(Float, default=0.19, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    offer = relationship("Offer", back_populates="line_items")


# ─── Contract — F031, F033, F035, F037 ────────────────────────────────────────

class Contract(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Contract entity.
    F031: Contract Builder — from offer or direct.
    F033: Contract Output — preview + export.
    F035: Billing schedule + invoicing.
    F037: Contracts Analytics.
    """
    __tablename__ = "contracts"

    # Links
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offers.id"), nullable=True
    )
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True
    )

    # Contract data
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False
    )

    # Financial
    total_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Dates
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    terminated_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    termination_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Terms
    terms_and_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    standard_clauses: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Owner
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Template
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=True
    )

    # Project auto-creation trigger
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    billing_schedule = relationship("BillingSchedule", back_populates="contract", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="contract")

    __table_args__ = (
        Index("ix_contract_org_status", "organization_id", "status"),
        Index("ix_contract_contact", "contact_id"),
    )


# ─── Billing Schedule — F035 ─────────────────────────────────────────────────

class BillingSchedule(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Auto-generated payment schedule per contract.
    F035: Billing — grafic facturare.
    """
    __tablename__ = "billing_schedules"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_invoiced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Link to SdL (Situație de Lucrări) — F079
    work_situation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    contract = relationship("Contract", back_populates="billing_schedule")


class Invoice(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Invoice issued from billing schedule.
    """
    __tablename__ = "invoices"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    vat_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    contract = relationship("Contract", back_populates="invoices")

    __table_args__ = (
        Index("ix_invoice_org_status", "organization_id", "status"),
    )


# ─── Approval Workflow — F028 ────────────────────────────────────────────────

class ApprovalWorkflow(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Approval flow for offers and contracts.
    F028: Flux aprobare — thresholds + workflow.
    """
    __tablename__ = "approval_workflows"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # offer, contract
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False
    )

    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Threshold rule that triggered
    threshold_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_approval_entity", "entity_type", "entity_id"),
    )


class ApprovalStep(Base, BasePKMixin, TimestampMixin):
    """
    Individual approval step (approver action).
    """
    __tablename__ = "approval_steps"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False
    )
    approver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
