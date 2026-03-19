"""BI (Business Intelligence) tables.

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create BI tables."""

    op.execute("""CREATE TABLE IF NOT EXISTS ai_conversations (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	user_id UUID NOT NULL,
	title VARCHAR(500),
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS ai_messages (
	conversation_id UUID NOT NULL,
	role VARCHAR(20) NOT NULL,
	content TEXT NOT NULL,
	metadata_json JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conversation_id) REFERENCES ai_conversations (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS dashboards (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	name VARCHAR(255) NOT NULL,
	description TEXT,
	dashboard_type VARCHAR(50) NOT NULL,
	is_default BOOLEAN NOT NULL,
	is_template BOOLEAN NOT NULL,
	layout_config JSON,
	visible_roles JSON,
	owner_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(owner_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS dashboard_widgets (
	dashboard_id UUID NOT NULL,
	widget_type dashboardwidgettype NOT NULL,
	title VARCHAR(255) NOT NULL,
	config JSON NOT NULL,
	data_source JSON,
	position_x INTEGER NOT NULL,
	position_y INTEGER NOT NULL,
	width INTEGER NOT NULL,
	height INTEGER NOT NULL,
	sort_order INTEGER NOT NULL,
	kpi_definition_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(dashboard_id) REFERENCES dashboards (id),
	FOREIGN KEY(kpi_definition_id) REFERENCES kpi_definitions (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS kpi_values (
	kpi_definition_id UUID NOT NULL,
	value FLOAT NOT NULL,
	threshold_color kpithresholdcolor,
	computed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	period_start TIMESTAMP WITH TIME ZONE,
	period_end TIMESTAMP WITH TIME ZONE,
	project_id UUID,
	user_id UUID,
	raw_data JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(kpi_definition_id) REFERENCES kpi_definitions (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS report_definitions (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	name VARCHAR(255) NOT NULL,
	description TEXT,
	report_type VARCHAR(50) NOT NULL,
	module VARCHAR(50),
	query_config JSON,
	columns_config JSON,
	filters_config JSON,
	grouping_config JSON,
	chart_config JSON,
	is_scheduled BOOLEAN NOT NULL,
	schedule_cron VARCHAR(50),
	recipients JSON,
	is_template BOOLEAN NOT NULL,
	owner_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(owner_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS report_executions (
	report_definition_id UUID NOT NULL,
	format reportformat NOT NULL,
	generated_by UUID,
	file_path VARCHAR(1000),
	file_size INTEGER,
	parameters JSON,
	status VARCHAR(20) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(report_definition_id) REFERENCES report_definitions (id),
	FOREIGN KEY(generated_by) REFERENCES users (id)
)""")

    # ── Indexes BI ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ai_conversations_organization_id ON ai_conversations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboards_organization_id ON dashboards (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboard_widgets_organization_id ON dashboard_widgets (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_values_organization_id ON kpi_values (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_value_def_date ON kpi_values (kpi_definition_id, computed_at)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_definitions_organization_id ON report_definitions (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_executions_organization_id ON report_executions (organization_id)""")


def downgrade() -> None:
    """Drop BI tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS report_executions CASCADE")
    op.execute("DROP TABLE IF EXISTS report_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_values CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboard_widgets CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboards CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE")
