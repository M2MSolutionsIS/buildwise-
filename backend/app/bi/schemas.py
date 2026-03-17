"""
BI (Business Intelligence) module schemas — F132, F133, F135, F148, F152.

Covers: KPI Builder, KPI Dashboard, Executive Dashboard,
AI Chatbot, Reports, Predictive Analytics.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ─── KPI — F148, F152 ──────────────────────────────────────────────────────


class KPIDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    module: str | None = None
    formula: dict
    formula_text: str | None = None
    unit: str | None = None
    thresholds: list | None = None
    display_type: str | None = None
    drill_down_config: dict | None = None
    assigned_roles: list | None = None
    assigned_users: list | None = None
    sort_order: int = 0


class KPIDefinitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    formula: dict | None = None
    formula_text: str | None = None
    unit: str | None = None
    thresholds: list | None = None
    display_type: str | None = None
    drill_down_config: dict | None = None
    assigned_roles: list | None = None
    assigned_users: list | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class KPIDefinitionOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    module: str | None = None
    formula: dict
    formula_text: str | None = None
    unit: str | None = None
    thresholds: list | None = None
    display_type: str | None = None
    drill_down_config: dict | None = None
    assigned_roles: list | None = None
    assigned_users: list | None = None
    is_active: bool
    sort_order: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class KPIValueCreate(BaseModel):
    kpi_definition_id: uuid.UUID
    value: float
    threshold_color: str | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    project_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    raw_data: dict | None = None


class KPIValueOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    kpi_definition_id: uuid.UUID
    value: float
    threshold_color: str | None = None
    computed_at: datetime | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    project_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    raw_data: dict | None = None

    model_config = {"from_attributes": True}


class KPIDashboardItem(BaseModel):
    """F152: Single KPI card for dashboard grid."""
    kpi: KPIDefinitionOut
    current_value: float | None = None
    threshold_color: str | None = None
    trend: list[KPIValueOut] = []


# ─── Dashboard — F133 ──────────────────────────────────────────────────────


class DashboardWidgetCreate(BaseModel):
    widget_type: str
    title: str = Field(..., min_length=1, max_length=255)
    config: dict
    data_source: dict | None = None
    position_x: int = 0
    position_y: int = 0
    width: int = 4
    height: int = 3
    sort_order: int = 0
    kpi_definition_id: uuid.UUID | None = None


class DashboardWidgetOut(BaseModel):
    id: uuid.UUID
    dashboard_id: uuid.UUID
    widget_type: str
    title: str
    config: dict
    data_source: dict | None = None
    position_x: int
    position_y: int
    width: int
    height: int
    sort_order: int
    kpi_definition_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class DashboardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    dashboard_type: str = "executive"
    is_default: bool = False
    layout_config: dict | None = None
    visible_roles: list | None = None
    widgets: list[DashboardWidgetCreate] = []


class DashboardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_default: bool | None = None
    layout_config: dict | None = None
    visible_roles: list | None = None


class DashboardOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    dashboard_type: str
    is_default: bool
    is_template: bool
    layout_config: dict | None = None
    visible_roles: list | None = None
    owner_id: uuid.UUID | None = None
    widgets: list[DashboardWidgetOut] = []
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── AI Chatbot — F132 ────────────────────────────────────────────────────


class AIMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class AIMessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    metadata_json: dict | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AIConversationCreate(BaseModel):
    title: str | None = None


class AIConversationListOut(BaseModel):
    """For list view — no messages loaded."""
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    title: str | None = None
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AIConversationOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    title: str | None = None
    is_active: bool
    messages: list[AIMessageOut] = []
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Reports — F142 ───────────────────────────────────────────────────────


class ReportDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    report_type: str = "custom"
    module: str | None = None
    query_config: dict | None = None
    columns_config: list | None = None
    filters_config: list | None = None
    grouping_config: dict | None = None
    chart_config: dict | None = None
    is_scheduled: bool = False
    schedule_cron: str | None = None
    recipients: list | None = None


class ReportDefinitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    query_config: dict | None = None
    columns_config: list | None = None
    filters_config: list | None = None
    grouping_config: dict | None = None
    chart_config: dict | None = None
    is_scheduled: bool | None = None
    schedule_cron: str | None = None
    recipients: list | None = None


class ReportDefinitionOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    report_type: str
    module: str | None = None
    query_config: dict | None = None
    columns_config: list | None = None
    filters_config: list | None = None
    grouping_config: dict | None = None
    chart_config: dict | None = None
    is_scheduled: bool
    schedule_cron: str | None = None
    recipients: list | None = None
    is_template: bool
    owner_id: uuid.UUID | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReportExecutionOut(BaseModel):
    id: uuid.UUID
    report_definition_id: uuid.UUID
    format: str
    generated_by: uuid.UUID | None = None
    file_path: str | None = None
    file_size: int | None = None
    parameters: dict | None = None
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ─── Executive Summary — F133 ─────────────────────────────────────────────


class ExecutiveSummaryOut(BaseModel):
    """F133: Cross-module aggregated data for executive dashboard."""
    total_contacts: int = 0
    total_opportunities: int = 0
    pipeline_value: float = 0.0
    active_projects: int = 0
    total_employees: int = 0
    total_allocations: int = 0
    kpi_summary: list[KPIDashboardItem] = []
