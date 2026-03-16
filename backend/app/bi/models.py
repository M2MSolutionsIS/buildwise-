"""
BI (Business Intelligence) module models — F132, F133, F135, F148, F152.

Covers: KPI Builder, KPI Dashboard, Executive Dashboard config,
AI Assistant conversations, Predictive Analytics, Reports Builder.
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
    OrgMixin,
    PrototypeFlagMixin,
    TimestampMixin,
)
from app.database import Base

import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class KPIThresholdColor(str, enum.Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class DashboardWidgetType(str, enum.Enum):
    KPI_CARD = "kpi_card"
    CHART = "chart"
    TABLE = "table"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    MAP = "map"
    CUSTOM = "custom"


# ─── KPI — F148, F152 ────────────────────────────────────────────────────────

class KPIDefinition(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    KPI Builder — formula, thresholds, assignment.
    F148: Wizard with drag-block formula, color thresholds, per-user assignment.
    F152: KPI Dashboard grid + gauge + drill-down.
    """
    __tablename__ = "kpi_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Formula — F148
    formula: Mapped[dict] = mapped_column(JSON, nullable=False)  # drag-block formula definition
    formula_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # human-readable
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Thresholds — F148
    thresholds: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Example: [{"color": "red", "min": 0, "max": 50}, {"color": "yellow", "min": 50, "max": 80}, {"color": "green", "min": 80, "max": 100}]

    # Display config
    display_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # gauge, card, chart
    drill_down_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Assignment
    assigned_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)
    assigned_users: Mapped[list | None] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    values = relationship("KPIValue", back_populates="kpi_definition")

    __table_args__ = (
        Index("ix_kpi_org", "organization_id"),
    )


class KPIValue(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Computed KPI values stored for historical tracking and dashboard display.
    """
    __tablename__ = "kpi_values"

    kpi_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kpi_definitions.id"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_color: Mapped[str | None] = mapped_column(Enum(KPIThresholdColor), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Context
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Raw data used for computation
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    kpi_definition = relationship("KPIDefinition", back_populates="values")

    __table_args__ = (
        Index("ix_kpi_value_def_date", "kpi_definition_id", "computed_at"),
    )


# ─── Dashboard Config — F133 ─────────────────────────────────────────────────

class Dashboard(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Executive Dashboard configuration.
    F133: Cross-module (CRM+Pipeline+PM+RM) dashboards.
    """
    __tablename__ = "dashboards"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dashboard_type: Mapped[str] = mapped_column(String(50), default="executive", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    layout_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Visibility
    visible_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardWidget(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Individual widget on a dashboard.
    """
    __tablename__ = "dashboard_widgets"

    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False
    )
    widget_type: Mapped[str] = mapped_column(Enum(DashboardWidgetType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    data_source: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Position in layout grid
    position_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    position_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # KPI link
    kpi_definition_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kpi_definitions.id"), nullable=True
    )

    dashboard = relationship("Dashboard", back_populates="widgets")


# ─── Reports Builder — F142, F148, F152 (P3) ─────────────────────────────────

class ReportDefinition(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Custom report definitions (Reports Builder — P3 specific).
    F142: Export reports (Excel & PDF).
    """
    __tablename__ = "report_definitions"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # schedule, financial, kpi, custom
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Report config — drag & drop builder (P3)
    query_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    columns_config: Mapped[list | None] = mapped_column(JSON, nullable=True)
    filters_config: Mapped[list | None] = mapped_column(JSON, nullable=True)
    grouping_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    chart_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Scheduling
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recipients: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Template
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class ReportExecution(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    History of generated reports.
    """
    __tablename__ = "report_executions"

    report_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("report_definitions.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(Enum(ReportFormat), nullable=False)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)


# ─── AI Assistant — F132 ─────────────────────────────────────────────────────

class AIConversation(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    AI chatbot conversation history.
    F132: Integrated chatbot — assistance, FAQ, navigation, suggestions.
    """
    __tablename__ = "ai_conversations"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")


class AIMessage(Base, BasePKMixin, TimestampMixin):
    """
    Individual messages in an AI conversation.
    """
    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    conversation = relationship("AIConversation", back_populates="messages")


# ─── ML Data Mapping — F105 ──────────────────────────────────────────────────

class MLModelConfig(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    ML model configurations for data → ML mapping.
    F105: Matrix of which data feeds which AI/ML models.
    """
    __tablename__ = "ml_model_configs"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Data source mapping
    data_sources: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Maps: F-code → field mapping

    # Status
    status: Mapped[str] = mapped_column(String(50), default="configured", nullable=False)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_metric: Mapped[float | None] = mapped_column(Float, nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # History
    training_history: Mapped[list | None] = mapped_column(JSON, nullable=True)
