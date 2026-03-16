"""
Project Management module models — F063, F066, F069–F080, F083, F084, F086, F088,
F090, F091–F095, F100, F101, F103, F105, F123, F125, F130, F140, F144–F146, F161.

Covers: Projects, WBS, Gantt (tasks + dependencies), Deviz (estimates),
Timesheets, Material consumption, SdL (work situations), Risk register,
Project Finance (P&L, Cash Flow), Reception/Punch list, Energy Impact,
Wiki/Documentation, Daily reports.
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

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    KICKOFF = "kickoff"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    POST_EXECUTION = "post_execution"
    CLOSING = "closing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, enum.Enum):
    CLIENT = "client"
    INTERNAL = "internal"


class WBSNodeType(str, enum.Enum):
    CHAPTER = "chapter"
    SUBCHAPTER = "subchapter"
    ARTICLE = "article"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class TaskDependencyType(str, enum.Enum):
    FS = "finish_to_start"
    SS = "start_to_start"
    FF = "finish_to_finish"
    SF = "start_to_finish"


class RiskProbability(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskImpact(str, enum.Enum):
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class PunchItemStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"


class PunchItemSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimesheetStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class WikiPostType(str, enum.Enum):
    POST = "post"
    FILE = "file"
    DOCUMENT = "document"


class ImportSourceType(str, enum.Enum):
    INTERSOFT = "intersoft"
    EDEVIZE = "edevize"
    CSV = "csv"
    EXCEL = "excel"
    API = "api"


# ─── Project — F063, F101, F130 ──────────────────────────────────────────────

class Project(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Core project entity.
    F063: Project Setup — auto-create from signed contract, checklist, import milestones.
    F101: Portfolio dashboard — status, health indicator.
    """
    __tablename__ = "projects"

    # Links
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )

    # Core
    project_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_type: Mapped[str] = mapped_column(
        Enum(ProjectType), default=ProjectType.CLIENT, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False
    )

    # Health — F101
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    health_indicator: Mapped[str | None] = mapped_column(String(20), nullable=True)  # green, yellow, red

    # Dates
    planned_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Budget — F080
    budget_allocated: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_committed: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # EVM indicators — F078
    cpi: Mapped[float | None] = mapped_column(Float, nullable=True)  # Cost Performance Index
    spi: Mapped[float | None] = mapped_column(Float, nullable=True)  # Schedule Performance Index
    percent_complete: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Team
    project_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Kickoff checklist — F063
    kickoff_checklist: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    kickoff_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Close/Cancel — F103
    close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    grace_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tags
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    wbs_nodes = relationship("WBSNode", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    deviz_items = relationship("DevizItem", back_populates="project", cascade="all, delete-orphan")
    timesheets = relationship("TimesheetEntry", back_populates="project")
    material_consumptions = relationship("MaterialConsumption", back_populates="project")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    daily_reports = relationship("DailyReport", back_populates="project")
    work_situations = relationship("WorkSituation", back_populates="project")
    punch_items = relationship("PunchItem", back_populates="project")
    wiki_posts = relationship("WikiPost", back_populates="project")
    subcontractors = relationship("Subcontractor", back_populates="project")
    energy_impact = relationship("EnergyImpact", back_populates="project", uselist=False)

    __table_args__ = (
        Index("ix_project_org_status", "organization_id", "status"),
        Index("ix_project_pm", "project_manager_id"),
    )


# ─── WBS — F069 ──────────────────────────────────────────────────────────────

class WBSNode(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Work Breakdown Structure — hierarchical (chapters, subchapters, articles).
    F069: 3-level tree structure.
    """
    __tablename__ = "wbs_nodes"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    node_type: Mapped[str] = mapped_column(Enum(WBSNodeType), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Budget per node — F080
    budget_allocated: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_actual: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Assigned
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    project = relationship("Project", back_populates="wbs_nodes")
    children = relationship("WBSNode", back_populates="parent")
    parent = relationship("WBSNode", back_populates="children", remote_side="WBSNode.id")

    __table_args__ = (
        Index("ix_wbs_project", "project_id"),
    )


# ─── Tasks / Gantt — F070, F083, F084 ────────────────────────────────────────

class Task(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Gantt task linked to WBS nodes.
    F070: Gantt forecast + dual-layer (baseline vs actual).
    F073: Task status (ToDo→InProgress→Blocked→Done).
    """
    __tablename__ = "tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    wbs_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )

    # Blocked reason — F073
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Schedule — Baseline (plan)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Schedule — Actual
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Progress
    percent_complete: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Time estimates
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Cost
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Assignment
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Critical path
    is_critical_path: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="tasks")
    children = relationship("Task", back_populates="parent_task")
    parent_task = relationship("Task", back_populates="children", remote_side="Task.id")
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
    )

    __table_args__ = (
        Index("ix_task_project_status", "project_id", "status"),
        Index("ix_task_assigned", "assigned_to"),
    )


class TaskDependency(Base, BasePKMixin):
    """
    Dependencies between Gantt tasks (FS/SS/FF/SF).
    F070: Gantt dependencies.
    """
    __tablename__ = "task_dependencies"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    depends_on_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    dependency_type: Mapped[str] = mapped_column(
        Enum(TaskDependencyType), default=TaskDependencyType.FS, nullable=False
    )
    lag_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on = relationship("Task", foreign_keys=[depends_on_id])


# ─── Deviz — F071, F074, F125 ────────────────────────────────────────────────

class DevizItem(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Cost estimate / budget line items (Deviz estimativ & execuție).
    F071: Quantities, unit prices (materials + labor), totals per WBS chapter.
    F125: Work Tracker — hierarchical work items, quantities inline.
    """
    __tablename__ = "deviz_items"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    wbs_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deviz_items.id"), nullable=True
    )

    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)

    # Estimated (plan)
    estimated_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_unit_price_material: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_unit_price_labor: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Actual (execution) — F125
    actual_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_unit_price_material: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_unit_price_labor: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Alert threshold
    over_budget_alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Import source — F123
    import_source: Mapped[str | None] = mapped_column(Enum(ImportSourceType), nullable=True)
    import_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    project = relationship("Project", back_populates="deviz_items")
    children = relationship("DevizItem", back_populates="parent_item")
    parent_item = relationship("DevizItem", back_populates="children", remote_side="DevizItem.id")

    __table_args__ = (
        Index("ix_deviz_project", "project_id"),
    )


# ─── Timesheet — F072, F073 ──────────────────────────────────────────────────

class TimesheetEntry(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Time logging per task.
    F072: Logging hours (estimated vs actual, cost = hours × hourly rate).
    F073: Task status with mandatory blocked reason.
    """
    __tablename__ = "timesheet_entries"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    work_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    hourly_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum(TimesheetStatus), default=TimesheetStatus.DRAFT, nullable=False
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_timesheet_project_date", "project_id", "work_date"),
        Index("ix_timesheet_user_date", "user_id", "work_date"),
    )

    project = relationship("Project", back_populates="timesheets")


# ─── Material Consumption — F074, F075 ───────────────────────────────────────

class MaterialConsumption(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Material consumption records per WBS.
    F074: Real consumption tracking, delivery tracking, overshoot alert.
    """
    __tablename__ = "material_consumptions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    wbs_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )
    deviz_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deviz_items.id"), nullable=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )

    material_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)
    planned_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    consumed_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    consumption_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    registered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    project = relationship("Project", back_populates="material_consumptions")

    __table_args__ = (
        Index("ix_material_consumption_project", "project_id"),
    )


# ─── Subcontractor — F075 ────────────────────────────────────────────────────

class Subcontractor(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Subcontractor tracking per project.
    F075: Contracts, activities, values, invoices, % completion.
    """
    __tablename__ = "subcontractors"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contract_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    scope_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    percent_complete: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    invoiced_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    project = relationship("Project", back_populates="subcontractors")

    __table_args__ = (
        Index("ix_subcontractor_project", "project_id"),
    )


# ─── Daily Report (RZS) — F077 ───────────────────────────────────────────────

class DailyReport(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Daily site report (Raport Zilnic de Șantier).
    F077: Activities, personnel, equipment, weather, observations.
    """
    __tablename__ = "daily_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    report_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Weather
    weather: Mapped[str | None] = mapped_column(String(100), nullable=True)
    temperature_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_max: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Content
    activities_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    personnel_present: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    equipment_used: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    materials_received: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    issues: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos: Mapped[list | None] = mapped_column(JSON, nullable=True)

    reported_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    project = relationship("Project", back_populates="daily_reports")

    __table_args__ = (
        Index("ix_daily_report_project_date", "project_id", "report_date"),
    )


# ─── Work Situation (SdL) — F079 ─────────────────────────────────────────────

class WorkSituation(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Situație de Lucrări — monthly quantities, contracted vs executed vs cumulated.
    F079: Auto-generation from deviz, export, link to billing (F035).
    """
    __tablename__ = "work_situations"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    sdl_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Totals
    contracted_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    executed_current: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    executed_cumulated: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    remaining: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Status
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Billing link — F035
    is_invoiced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Line items stored as JSON (or separate table if needed)
    line_items: Mapped[list | None] = mapped_column(JSON, nullable=True)

    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    project = relationship("Project", back_populates="work_situations")

    __table_args__ = (
        Index("ix_work_situation_project", "project_id"),
    )


# ─── Risk Register — F084 ────────────────────────────────────────────────────

class Risk(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Project risk register (RIEM methodology).
    F084: Identification, P×I evaluation, mitigation, export.
    """
    __tablename__ = "risks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    probability: Mapped[str] = mapped_column(Enum(RiskProbability), nullable=False)
    impact: Mapped[str] = mapped_column(Enum(RiskImpact), nullable=False)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # P × I

    status: Mapped[str] = mapped_column(
        Enum(RiskStatus), default=RiskStatus.IDENTIFIED, nullable=False
    )

    mitigation_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    contingency_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    identified_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="risks")


# ─── Reception & Punch List — F086, F103 ─────────────────────────────────────

class PunchItem(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Punch list / defect tracking for project closeout.
    F086: Closeout — reception, punch list, warranty.
    F103: Close/cancel project flow.
    """
    __tablename__ = "punch_items"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        Enum(PunchItemSeverity), default=PunchItemSeverity.MEDIUM, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(PunchItemStatus), default=PunchItemStatus.OPEN, nullable=False
    )
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    photos: Mapped[list | None] = mapped_column(JSON, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    project = relationship("Project", back_populates="punch_items")

    __table_args__ = (
        Index("ix_punch_project_status", "project_id", "status"),
    )


# ─── Warranty Tracking — F086 ────────────────────────────────────────────────

class Warranty(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Warranty tracking with alerts.
    """
    __tablename__ = "warranties"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responsible_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    alert_before_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Intervention log
    interventions: Mapped[list | None] = mapped_column(JSON, nullable=True)


# ─── Energy Impact — F088, F090, F105, F161 ──────────────────────────────────

class EnergyImpact(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Energy impact measurements per project (PRE/POST).
    F088: kWh pre/post, estimated vs real, savings + CO₂.
    F090: Completed projects database.
    F105: Data → ML mapping.
    F161: Energy Portfolio aggregated dashboard.
    """
    __tablename__ = "energy_impacts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False
    )
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True
    )

    # PRE measurements
    pre_kwh_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    pre_gas_mc_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    pre_co2_kg_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    pre_u_value_avg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # POST measurements
    post_kwh_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    post_gas_mc_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    post_co2_kg_annual: Mapped[float | None] = mapped_column(Float, nullable=True)
    post_u_value_avg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Estimated savings
    estimated_kwh_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_co2_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Actual savings
    actual_kwh_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_co2_reduction: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Areas
    total_area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    treated_area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Materials used summary
    materials_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Cost data
    total_project_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ML data mapping — F105
    ml_data_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ml_dataset_exported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ml_export_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="energy_impact")


# ─── Project Finance — F091, F092, F093, F094 ────────────────────────────────

class ProjectFinanceEntry(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Project P&L and Cash Flow entries.
    F091: Project P&L (Actual vs Forecast).
    F092: Project Cash Flow (Actual vs Forecast).
    """
    __tablename__ = "project_finance_entries"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)  # revenue, cost
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # personnel, materials, subcontractors, invoices
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)

    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)

    forecast_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    variance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Source reference
    source_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("ix_finance_project_period", "project_id", "period_year", "period_month"),
    )


class ProjectCashFlowEntry(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Cash flow tracking (actual cash in/out).
    F092: Intrări = încasări, Ieșiri = plăți efective.
    """
    __tablename__ = "project_cash_flow_entries"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)  # inflow, outflow
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Reference
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("ix_cashflow_project_date", "project_id", "transaction_date"),
    )


# ─── Import Job — F123 ───────────────────────────────────────────────────────

class ImportJob(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Import Engine job tracking.
    F123: Wizard upload → preview → mapping → internal structure.
    """
    __tablename__ = "import_jobs"

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(Enum(ImportSourceType), nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, mapping, importing, completed, error
    mapping_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preview_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_log: Mapped[list | None] = mapped_column(JSON, nullable=True)
    records_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ─── Wiki / Documentation — F144, F145, F146 ─────────────────────────────────

class WikiPost(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Wiki timeline posts with nested comments.
    F144: Posts with title, text, attachments + threaded comments.
    F145: File management per department.
    F146: Official documents with versioning.
    """
    __tablename__ = "wiki_posts"

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    post_type: Mapped[str] = mapped_column(
        Enum(WikiPostType), default=WikiPostType.POST, nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # F146
    document_type_badge: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Versioning — F146
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wiki_posts.id"), nullable=True
    )

    # File attachment — F145
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Author
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    project = relationship("Project", back_populates="wiki_posts")
    comments = relationship("WikiComment", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_wiki_project", "project_id"),
        Index("ix_wiki_department", "department"),
    )


class WikiComment(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Nested/threaded comments on wiki posts.
    F144: Reply-uri indendate, threaded.
    """
    __tablename__ = "wiki_comments"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wiki_posts.id"), nullable=False
    )
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wiki_comments.id"), nullable=True
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    post = relationship("WikiPost", back_populates="comments")
    replies = relationship("WikiComment", back_populates="parent_comment")
    parent_comment = relationship("WikiComment", back_populates="replies", remote_side="WikiComment.id")
