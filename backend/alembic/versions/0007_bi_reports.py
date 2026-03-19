"""BI — AI conversations, reports.

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ai_conversations, ai_messages, report_definitions, report_executions."""

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

    # ── Indexes ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ai_conversations_organization_id ON ai_conversations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_definitions_organization_id ON report_definitions (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_executions_organization_id ON report_executions (organization_id)""")


def downgrade() -> None:
    """Drop AI/report tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS report_executions CASCADE")
    op.execute("DROP TABLE IF EXISTS report_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE")
