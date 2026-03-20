"""Core tables — System, Auth, Config (organizations, users, roles, permissions).

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create core/system tables — no FK dependencies on module tables."""

    # ── Organizations ──
    op.execute("""CREATE TABLE IF NOT EXISTS organizations (
	name VARCHAR(255) NOT NULL,
	slug VARCHAR(100) NOT NULL,
	cui VARCHAR(20),
	address TEXT,
	phone VARCHAR(30),
	email VARCHAR(255),
	website VARCHAR(255),
	logo_url VARCHAR(500),
	active_prototype prototypeenum NOT NULL,
	primary_color VARCHAR(7),
	secondary_color VARCHAR(7),
	custom_branding JSON,
	default_language VARCHAR(5) NOT NULL,
	supported_languages JSON,
	default_currency VARCHAR(3) NOT NULL,
	reference_currency VARCHAR(3),
	modules_enabled JSON,
	setup_completed BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	is_deleted BOOLEAN NOT NULL,
	deleted_at TIMESTAMP WITH TIME ZONE,
	deleted_by UUID,
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	PRIMARY KEY (id)
)""")

    # ── Permissions ──
    op.execute("""CREATE TABLE IF NOT EXISTS permissions (
	module VARCHAR(50) NOT NULL,
	action VARCHAR(50) NOT NULL,
	description TEXT,
	id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_permission_module_action UNIQUE (module, action)
)""")

    # ── Roles ──
    op.execute("""CREATE TABLE IF NOT EXISTS roles (
	name VARCHAR(100) NOT NULL,
	code VARCHAR(50) NOT NULL,
	description TEXT,
	is_system BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_role_code_org UNIQUE (code, organization_id)
)""")

    # ── Users ──
    op.execute("""CREATE TABLE IF NOT EXISTS users (
	email VARCHAR(255) NOT NULL,
	password_hash VARCHAR(255) NOT NULL,
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR(100) NOT NULL,
	phone VARCHAR(30),
	avatar_url VARCHAR(500),
	is_active BOOLEAN NOT NULL,
	is_superuser BOOLEAN NOT NULL,
	gdpr_consent BOOLEAN NOT NULL,
	gdpr_consent_date TIMESTAMP WITH TIME ZONE,
	last_login TIMESTAMP WITH TIME ZONE,
	refresh_token VARCHAR(500),
	notification_preferences JSON,
	language VARCHAR(5) NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	is_deleted BOOLEAN NOT NULL,
	deleted_at TIMESTAMP WITH TIME ZONE,
	deleted_by UUID,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_user_email_org UNIQUE (email, organization_id)
)""")

    # ── Role Permissions ──
    op.execute("""CREATE TABLE IF NOT EXISTS role_permissions (
	role_id UUID NOT NULL,
	permission_id UUID NOT NULL,
	id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id),
	FOREIGN KEY(role_id) REFERENCES roles (id),
	FOREIGN KEY(permission_id) REFERENCES permissions (id)
)""")

    # ── User Roles ──
    op.execute("""CREATE TABLE IF NOT EXISTS user_roles (
	user_id UUID NOT NULL,
	role_id UUID NOT NULL,
	id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_user_role UNIQUE (user_id, role_id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(role_id) REFERENCES roles (id)
)""")

    # ── Audit Logs ──
    op.execute("""CREATE TABLE IF NOT EXISTS audit_logs (
	user_id UUID,
	action VARCHAR(50) NOT NULL,
	entity_type VARCHAR(100) NOT NULL,
	entity_id UUID NOT NULL,
	old_values JSON,
	new_values JSON,
	ip_address VARCHAR(45),
	user_agent VARCHAR(500),
	timestamp TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	id UUID NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")

    # ── Currencies ──
    op.execute("""CREATE TABLE IF NOT EXISTS currencies (
	code VARCHAR(3) NOT NULL,
	name VARCHAR(100) NOT NULL,
	symbol VARCHAR(5) NOT NULL,
	is_default BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_currency_code_org UNIQUE (code, organization_id)
)""")

    # ── Exchange Rates ──
    op.execute("""CREATE TABLE IF NOT EXISTS exchange_rates (
	from_currency VARCHAR(3) NOT NULL,
	to_currency VARCHAR(3) NOT NULL,
	rate FLOAT NOT NULL,
	effective_date TIMESTAMP WITH TIME ZONE NOT NULL,
	id UUID NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id)
)""")

    # ── Feature Flags ──
    op.execute("""CREATE TABLE IF NOT EXISTS feature_flags (
	f_code VARCHAR(10) NOT NULL,
	name VARCHAR(255) NOT NULL,
	module VARCHAR(50) NOT NULL,
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	is_enabled BOOLEAN NOT NULL,
	config JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_feature_flag_org UNIQUE (f_code, organization_id)
)""")

    # ── Notification Templates ──
    op.execute("""CREATE TABLE IF NOT EXISTS notification_templates (
	name VARCHAR(255) NOT NULL,
	event_type VARCHAR(100) NOT NULL,
	channel notificationchannel NOT NULL,
	subject_template VARCHAR(500),
	body_template TEXT,
	is_active BOOLEAN NOT NULL,
	target_roles JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id)
)""")

    # ── Notifications (FK → users, notification_templates) ──
    op.execute("""CREATE TABLE IF NOT EXISTS notifications (
	user_id UUID NOT NULL,
	template_id UUID,
	title VARCHAR(255) NOT NULL,
	message TEXT NOT NULL,
	status notificationstatus NOT NULL,
	link VARCHAR(500),
	entity_type VARCHAR(100),
	entity_id UUID,
	read_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(template_id) REFERENCES notification_templates (id)
)""")

    # ── Custom Field Definitions ──
    op.execute("""CREATE TABLE IF NOT EXISTS custom_field_definitions (
	entity_type VARCHAR(100) NOT NULL,
	field_name VARCHAR(100) NOT NULL,
	field_label VARCHAR(255) NOT NULL,
	field_type customfieldtype NOT NULL,
	is_required BOOLEAN NOT NULL,
	default_value TEXT,
	options JSON,
	sort_order INTEGER NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_custom_field UNIQUE (organization_id, entity_type, field_name)
)""")

    # ── Custom Field Values ──
    op.execute("""CREATE TABLE IF NOT EXISTS custom_field_values (
	field_definition_id UUID NOT NULL,
	entity_type VARCHAR(100) NOT NULL,
	entity_id UUID NOT NULL,
	value TEXT,
	id UUID NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_custom_field_value UNIQUE (field_definition_id, entity_id),
	FOREIGN KEY(field_definition_id) REFERENCES custom_field_definitions (id)
)""")

    # ── Document Templates ──
    op.execute("""CREATE TABLE IF NOT EXISTS document_templates (
	name VARCHAR(255) NOT NULL,
	template_type VARCHAR(50) NOT NULL,
	content TEXT,
	placeholders JSON,
	layout_config JSON,
	is_default BOOLEAN NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id)
)""")

    # ── ML Model Configs ──
    op.execute("""CREATE TABLE IF NOT EXISTS ml_model_configs (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	name VARCHAR(255) NOT NULL,
	description TEXT,
	model_type VARCHAR(100) NOT NULL,
	data_sources JSON NOT NULL,
	status VARCHAR(50) NOT NULL,
	last_trained_at TIMESTAMP WITH TIME ZONE,
	error_metric FLOAT,
	parameters JSON,
	training_history JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id)
)""")

    # ── Pipeline Stage Configs ──
    op.execute("""CREATE TABLE IF NOT EXISTS pipeline_stage_configs (
	name VARCHAR(100) NOT NULL,
	code VARCHAR(50) NOT NULL,
	sort_order INTEGER NOT NULL,
	color VARCHAR(7),
	win_probability FLOAT,
	stagnation_days INTEGER,
	required_fields JSON,
	auto_advance_rules JSON,
	is_active BOOLEAN NOT NULL,
	is_closed_won BOOLEAN NOT NULL,
	is_closed_lost BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_pipeline_stage_code_org UNIQUE (code, organization_id)
)""")

    # ── Product Categories ──
    op.execute("""CREATE TABLE IF NOT EXISTS product_categories (
	name VARCHAR(255) NOT NULL,
	parent_id UUID,
	sort_order INTEGER NOT NULL,
	is_active BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(parent_id) REFERENCES product_categories (id)
)""")

    # ── KPI Definitions ──
    op.execute("""CREATE TABLE IF NOT EXISTS kpi_definitions (
	name VARCHAR(255) NOT NULL,
	code VARCHAR(50) NOT NULL,
	description TEXT,
	module VARCHAR(50),
	formula JSON NOT NULL,
	formula_text TEXT,
	unit VARCHAR(20),
	thresholds JSON,
	display_type VARCHAR(50),
	drill_down_config JSON,
	assigned_roles JSON,
	assigned_users JSON,
	is_active BOOLEAN NOT NULL,
	sort_order INTEGER NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id)
)""")

    # ── Approval Workflows ──
    op.execute("""CREATE TABLE IF NOT EXISTS approval_workflows (
	entity_type VARCHAR(50) NOT NULL,
	entity_id UUID NOT NULL,
	status approvalstatus NOT NULL,
	submitted_by UUID NOT NULL,
	submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	threshold_rule JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(submitted_by) REFERENCES users (id)
)""")

    # ── Approval Steps ──
    op.execute("""CREATE TABLE IF NOT EXISTS approval_steps (
	workflow_id UUID NOT NULL,
	approver_id UUID NOT NULL,
	step_order INTEGER NOT NULL,
	status approvalstatus NOT NULL,
	comment TEXT,
	decided_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(workflow_id) REFERENCES approval_workflows (id),
	FOREIGN KEY(approver_id) REFERENCES users (id)
)""")

    # ── Indexes for core tables ──
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_organizations_slug ON organizations (slug)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_organization_id ON users (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_roles_organization_id ON roles (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_entity ON audit_logs (entity_type, entity_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_organization_id ON audit_logs (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_timestamp ON audit_logs (timestamp)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_currencies_organization_id ON currencies (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_exchange_rate_date ON exchange_rates (from_currency, to_currency, effective_date)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_exchange_rates_organization_id ON exchange_rates (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feature_flags_organization_id ON feature_flags (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notification_templates_organization_id ON notification_templates (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_organization_id ON notifications (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notification_user_status ON notifications (user_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custom_field_definitions_organization_id ON custom_field_definitions (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custom_field_values_organization_id ON custom_field_values (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custom_field_entity ON custom_field_values (entity_type, entity_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_document_templates_organization_id ON document_templates (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ml_model_configs_organization_id ON ml_model_configs (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_pipeline_stage_configs_organization_id ON pipeline_stage_configs (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_categories_organization_id ON product_categories (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_kpi_org ON kpi_definitions (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_kpi_definitions_organization_id ON kpi_definitions (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_approval_entity ON approval_workflows (entity_type, entity_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_approval_workflows_organization_id ON approval_workflows (organization_id)")


def downgrade() -> None:
    """Drop core tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS approval_steps CASCADE")
    op.execute("DROP TABLE IF EXISTS approval_workflows CASCADE")
    op.execute("DROP TABLE IF EXISTS custom_field_values CASCADE")
    op.execute("DROP TABLE IF EXISTS custom_field_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS notification_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS user_roles CASCADE")
    op.execute("DROP TABLE IF EXISTS role_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS product_categories CASCADE")
    op.execute("DROP TABLE IF EXISTS pipeline_stage_configs CASCADE")
    op.execute("DROP TABLE IF EXISTS ml_model_configs CASCADE")
    op.execute("DROP TABLE IF EXISTS document_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS feature_flags CASCADE")
    op.execute("DROP TABLE IF EXISTS exchange_rates CASCADE")
    op.execute("DROP TABLE IF EXISTS currencies CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS roles CASCADE")
    op.execute("DROP TABLE IF EXISTS permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS organizations CASCADE")
