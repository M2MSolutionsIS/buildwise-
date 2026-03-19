"""PM (Project Management) tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create PM tables."""

    op.execute("""CREATE TABLE IF NOT EXISTS projects (
	contract_id UUID,
	contact_id UUID,
	project_number VARCHAR(50) NOT NULL,
	name VARCHAR(500) NOT NULL,
	description TEXT,
	project_type projecttype NOT NULL,
	status projectstatus NOT NULL,
	health_score FLOAT,
	health_indicator VARCHAR(20),
	planned_start_date TIMESTAMP WITH TIME ZONE,
	planned_end_date TIMESTAMP WITH TIME ZONE,
	actual_start_date TIMESTAMP WITH TIME ZONE,
	actual_end_date TIMESTAMP WITH TIME ZONE,
	budget_allocated FLOAT,
	budget_committed FLOAT,
	budget_actual FLOAT,
	currency VARCHAR(3) NOT NULL,
	cpi FLOAT,
	spi FLOAT,
	percent_complete FLOAT NOT NULL,
	project_manager_id UUID,
	kickoff_checklist JSON,
	kickoff_completed BOOLEAN NOT NULL,
	close_date TIMESTAMP WITH TIME ZONE,
	grace_period_end TIMESTAMP WITH TIME ZONE,
	cancellation_reason TEXT,
	tags JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	is_deleted BOOLEAN NOT NULL,
	deleted_at TIMESTAMP WITH TIME ZONE,
	deleted_by UUID,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	notes TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(contract_id) REFERENCES contracts (id),
	FOREIGN KEY(contact_id) REFERENCES contacts (id),
	FOREIGN KEY(project_manager_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS wbs_nodes (
	project_id UUID NOT NULL,
	parent_id UUID,
	code VARCHAR(50) NOT NULL,
	name VARCHAR(500) NOT NULL,
	description TEXT,
	node_type wbsnodetype NOT NULL,
	sort_order INTEGER NOT NULL,
	level INTEGER NOT NULL,
	budget_allocated FLOAT,
	budget_actual FLOAT,
	responsible_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(parent_id) REFERENCES wbs_nodes (id),
	FOREIGN KEY(responsible_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS tasks (
	project_id UUID NOT NULL,
	wbs_node_id UUID,
	parent_task_id UUID,
	title VARCHAR(500) NOT NULL,
	description TEXT,
	status taskstatus NOT NULL,
	blocked_reason TEXT,
	escalated BOOLEAN NOT NULL,
	planned_start TIMESTAMP WITH TIME ZONE,
	planned_end TIMESTAMP WITH TIME ZONE,
	planned_duration_days INTEGER,
	actual_start TIMESTAMP WITH TIME ZONE,
	actual_end TIMESTAMP WITH TIME ZONE,
	percent_complete FLOAT NOT NULL,
	estimated_hours FLOAT,
	actual_hours FLOAT,
	estimated_cost FLOAT,
	actual_cost FLOAT,
	assigned_to UUID,
	is_critical_path BOOLEAN NOT NULL,
	is_milestone BOOLEAN NOT NULL,
	sort_order INTEGER NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	notes TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(wbs_node_id) REFERENCES wbs_nodes (id),
	FOREIGN KEY(parent_task_id) REFERENCES tasks (id),
	FOREIGN KEY(assigned_to) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS task_dependencies (
	task_id UUID NOT NULL,
	depends_on_id UUID NOT NULL,
	dependency_type taskdependencytype NOT NULL,
	lag_days INTEGER NOT NULL,
	id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(task_id) REFERENCES tasks (id),
	FOREIGN KEY(depends_on_id) REFERENCES tasks (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS deviz_items (
	project_id UUID NOT NULL,
	wbs_node_id UUID,
	parent_id UUID,
	code VARCHAR(50),
	description TEXT NOT NULL,
	unit_of_measure VARCHAR(20) NOT NULL,
	estimated_quantity FLOAT NOT NULL,
	estimated_unit_price_material FLOAT NOT NULL,
	estimated_unit_price_labor FLOAT NOT NULL,
	estimated_total FLOAT NOT NULL,
	actual_quantity FLOAT NOT NULL,
	actual_unit_price_material FLOAT NOT NULL,
	actual_unit_price_labor FLOAT NOT NULL,
	actual_total FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	sort_order INTEGER NOT NULL,
	over_budget_alert BOOLEAN NOT NULL,
	import_source importsourcetype,
	import_reference VARCHAR(255),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(wbs_node_id) REFERENCES wbs_nodes (id),
	FOREIGN KEY(parent_id) REFERENCES deviz_items (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS daily_reports (
	project_id UUID NOT NULL,
	report_date TIMESTAMP WITH TIME ZONE NOT NULL,
	weather VARCHAR(100),
	temperature_min FLOAT,
	temperature_max FLOAT,
	activities_summary TEXT,
	personnel_present JSON,
	equipment_used JSON,
	materials_received JSON,
	observations TEXT,
	issues TEXT,
	photos JSON,
	reported_by UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(reported_by) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS work_situations (
	project_id UUID NOT NULL,
	period_month INTEGER NOT NULL,
	period_year INTEGER NOT NULL,
	sdl_number VARCHAR(50) NOT NULL,
	contracted_total FLOAT NOT NULL,
	executed_current FLOAT NOT NULL,
	executed_cumulated FLOAT NOT NULL,
	remaining FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	is_approved BOOLEAN NOT NULL,
	approved_by UUID,
	approved_at TIMESTAMP WITH TIME ZONE,
	is_invoiced BOOLEAN NOT NULL,
	line_items JSON,
	pdf_path VARCHAR(1000),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS budget_entries (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	cost_center VARCHAR(100) NOT NULL,
	category VARCHAR(100) NOT NULL,
	description TEXT,
	period_month INTEGER NOT NULL,
	period_year INTEGER NOT NULL,
	budgeted_amount FLOAT NOT NULL,
	actual_amount FLOAT NOT NULL,
	variance FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	project_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS punch_items (
	project_id UUID NOT NULL,
	title VARCHAR(500) NOT NULL,
	description TEXT,
	severity punchitemseverity NOT NULL,
	status punchitemstatus NOT NULL,
	responsible_id UUID,
	due_date TIMESTAMP WITH TIME ZONE,
	resolved_at TIMESTAMP WITH TIME ZONE,
	photos JSON,
	location VARCHAR(255),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(responsible_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS risks (
	project_id UUID NOT NULL,
	title VARCHAR(500) NOT NULL,
	description TEXT,
	category VARCHAR(100),
	probability riskprobability NOT NULL,
	impact riskimpact NOT NULL,
	risk_score FLOAT,
	status riskstatus NOT NULL,
	mitigation_plan TEXT,
	contingency_plan TEXT,
	owner_id UUID,
	identified_date TIMESTAMP WITH TIME ZONE,
	review_date TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	notes TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(owner_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS subcontractors (
	project_id UUID NOT NULL,
	contact_id UUID,
	company_name VARCHAR(255) NOT NULL,
	contract_number VARCHAR(50),
	contract_value FLOAT,
	currency VARCHAR(3) NOT NULL,
	scope_description TEXT,
	start_date TIMESTAMP WITH TIME ZONE,
	end_date TIMESTAMP WITH TIME ZONE,
	percent_complete FLOAT NOT NULL,
	invoiced_amount FLOAT NOT NULL,
	paid_amount FLOAT NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	notes TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(contact_id) REFERENCES contacts (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS warranties (
	project_id UUID NOT NULL,
	description TEXT NOT NULL,
	start_date TIMESTAMP WITH TIME ZONE NOT NULL,
	end_date TIMESTAMP WITH TIME ZONE NOT NULL,
	responsible_id UUID,
	alert_before_days INTEGER NOT NULL,
	is_active BOOLEAN NOT NULL,
	interventions JSON,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(responsible_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS energy_impacts (
	project_id UUID NOT NULL,
	property_id UUID,
	pre_kwh_annual FLOAT,
	pre_gas_mc_annual FLOAT,
	pre_co2_kg_annual FLOAT,
	pre_u_value_avg FLOAT,
	post_kwh_annual FLOAT,
	post_gas_mc_annual FLOAT,
	post_co2_kg_annual FLOAT,
	post_u_value_avg FLOAT,
	estimated_kwh_savings FLOAT,
	estimated_co2_reduction FLOAT,
	actual_kwh_savings FLOAT,
	actual_co2_reduction FLOAT,
	total_area_sqm FLOAT,
	treated_area_sqm FLOAT,
	materials_summary JSON,
	total_project_cost FLOAT,
	duration_days INTEGER,
	ml_data_mapping JSON,
	ml_dataset_exported BOOLEAN NOT NULL,
	ml_export_date TIMESTAMP WITH TIME ZONE,
	is_verified BOOLEAN NOT NULL,
	verified_by UUID,
	verified_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	UNIQUE (project_id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(property_id) REFERENCES properties (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS import_jobs (
	project_id UUID,
	source_type importsourcetype NOT NULL,
	file_name VARCHAR(500) NOT NULL,
	file_path VARCHAR(1000) NOT NULL,
	status VARCHAR(20) NOT NULL,
	mapping_config JSON,
	preview_data JSON,
	error_log JSON,
	records_imported INTEGER NOT NULL,
	records_total INTEGER NOT NULL,
	completed_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS project_cash_flow_entries (
	project_id UUID NOT NULL,
	entry_type VARCHAR(20) NOT NULL,
	description TEXT,
	amount FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
	invoice_id UUID,
	source_entity_type VARCHAR(50),
	source_entity_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS project_finance_entries (
	project_id UUID NOT NULL,
	entry_type VARCHAR(20) NOT NULL,
	category VARCHAR(50) NOT NULL,
	subcategory VARCHAR(100),
	period_month INTEGER NOT NULL,
	period_year INTEGER NOT NULL,
	forecast_amount FLOAT NOT NULL,
	actual_amount FLOAT NOT NULL,
	variance FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	source_entity_type VARCHAR(50),
	source_entity_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS timesheet_entries (
	project_id UUID NOT NULL,
	task_id UUID,
	user_id UUID NOT NULL,
	work_date TIMESTAMP WITH TIME ZONE NOT NULL,
	hours FLOAT NOT NULL,
	hourly_rate FLOAT,
	cost FLOAT,
	description TEXT,
	status timesheetstatus NOT NULL,
	approved_by UUID,
	approved_at TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(task_id) REFERENCES tasks (id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(approved_by) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS material_consumptions (
	project_id UUID NOT NULL,
	wbs_node_id UUID,
	deviz_item_id UUID,
	product_id UUID,
	material_name VARCHAR(255) NOT NULL,
	unit_of_measure VARCHAR(20) NOT NULL,
	planned_quantity FLOAT NOT NULL,
	consumed_quantity FLOAT NOT NULL,
	unit_price FLOAT,
	total_cost FLOAT,
	consumption_date TIMESTAMP WITH TIME ZONE NOT NULL,
	registered_by UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(wbs_node_id) REFERENCES wbs_nodes (id),
	FOREIGN KEY(deviz_item_id) REFERENCES deviz_items (id),
	FOREIGN KEY(product_id) REFERENCES products (id),
	FOREIGN KEY(registered_by) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS wiki_posts (
	project_id UUID,
	department VARCHAR(100),
	post_type wikiposttype NOT NULL,
	title VARCHAR(500) NOT NULL,
	content TEXT,
	is_official BOOLEAN NOT NULL,
	document_type_badge VARCHAR(50),
	version INTEGER NOT NULL,
	parent_version_id UUID,
	file_path VARCHAR(1000),
	file_name VARCHAR(500),
	file_size INTEGER,
	mime_type VARCHAR(100),
	author_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(parent_version_id) REFERENCES wiki_posts (id),
	FOREIGN KEY(author_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS wiki_comments (
	post_id UUID NOT NULL,
	parent_comment_id UUID,
	author_id UUID,
	content TEXT NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(post_id) REFERENCES wiki_posts (id),
	FOREIGN KEY(parent_comment_id) REFERENCES wiki_comments (id),
	FOREIGN KEY(author_id) REFERENCES users (id)
)""")

    # ── Indexes PM ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_projects_organization_id ON projects (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_projects_project_number ON projects (project_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_org_status ON projects (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_pm ON projects (project_manager_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wbs_nodes_organization_id ON wbs_nodes (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wbs_project ON wbs_nodes (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_tasks_organization_id ON tasks (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_task_project_status ON tasks (project_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_task_assigned ON tasks (assigned_to)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_deviz_project ON deviz_items (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_deviz_items_organization_id ON deviz_items (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_daily_report_project_date ON daily_reports (project_id, report_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_daily_reports_organization_id ON daily_reports (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_work_situations_organization_id ON work_situations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_work_situation_project ON work_situations (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_org_period ON budget_entries (organization_id, period_year, period_month)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_entries_organization_id ON budget_entries (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_cost_center ON budget_entries (organization_id, cost_center)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_punch_items_organization_id ON punch_items (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_punch_project_status ON punch_items (project_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_risks_organization_id ON risks (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_subcontractor_project ON subcontractors (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_subcontractors_organization_id ON subcontractors (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_warranties_organization_id ON warranties (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_impacts_organization_id ON energy_impacts (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_import_jobs_organization_id ON import_jobs (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_cash_flow_entries_organization_id ON project_cash_flow_entries (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_cashflow_project_date ON project_cash_flow_entries (project_id, transaction_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_finance_entries_organization_id ON project_finance_entries (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_finance_project_period ON project_finance_entries (project_id, period_year, period_month)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_entries_organization_id ON timesheet_entries (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_user_date ON timesheet_entries (user_id, work_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_project_date ON timesheet_entries (project_id, work_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_consumption_project ON material_consumptions (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_consumptions_organization_id ON material_consumptions (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_posts_organization_id ON wiki_posts (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_department ON wiki_posts (department)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_project ON wiki_posts (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_comments_organization_id ON wiki_comments (organization_id)""")


def downgrade() -> None:
    """Drop PM tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS wiki_comments CASCADE")
    op.execute("DROP TABLE IF EXISTS wiki_posts CASCADE")
    op.execute("DROP TABLE IF EXISTS material_consumptions CASCADE")
    op.execute("DROP TABLE IF EXISTS timesheet_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS project_finance_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS project_cash_flow_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS import_jobs CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_impacts CASCADE")
    op.execute("DROP TABLE IF EXISTS warranties CASCADE")
    op.execute("DROP TABLE IF EXISTS subcontractors CASCADE")
    op.execute("DROP TABLE IF EXISTS risks CASCADE")
    op.execute("DROP TABLE IF EXISTS punch_items CASCADE")
    op.execute("DROP TABLE IF EXISTS budget_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS work_situations CASCADE")
    op.execute("DROP TABLE IF EXISTS daily_reports CASCADE")
    op.execute("DROP TABLE IF EXISTS deviz_items CASCADE")
    op.execute("DROP TABLE IF EXISTS task_dependencies CASCADE")
    op.execute("DROP TABLE IF EXISTS tasks CASCADE")
    op.execute("DROP TABLE IF EXISTS wbs_nodes CASCADE")
    op.execute("DROP TABLE IF EXISTS projects CASCADE")
