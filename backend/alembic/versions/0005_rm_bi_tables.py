"""RM (Resource Management) + BI (Business Intelligence) tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create RM + BI tables."""

    # ── RM ──

    op.execute("""CREATE TABLE IF NOT EXISTS employees (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	user_id UUID,
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR(100) NOT NULL,
	email VARCHAR(255),
	phone VARCHAR(30),
	employee_number VARCHAR(50),
	position VARCHAR(100),
	department VARCHAR(100),
	cost_center VARCHAR(50),
	status employeestatus NOT NULL,
	contract_type contracttype NOT NULL,
	hire_date TIMESTAMP WITH TIME ZONE,
	termination_date TIMESTAMP WITH TIME ZONE,
	gross_salary FLOAT,
	net_salary FLOAT,
	benefits JSON,
	hourly_rate FLOAT,
	standard_hours_month FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	skills JSON,
	qualifications JSON,
	certifications JSON,
	is_external BOOLEAN NOT NULL,
	external_company VARCHAR(255),
	external_contract_ref VARCHAR(100),
	external_daily_rate FLOAT,
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
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS equipment (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	name VARCHAR(255) NOT NULL,
	code VARCHAR(50),
	category VARCHAR(100),
	description TEXT,
	status equipmentstatus NOT NULL,
	manufacturer VARCHAR(255),
	model VARCHAR(255),
	serial_number VARCHAR(100),
	purchase_date TIMESTAMP WITH TIME ZONE,
	purchase_cost FLOAT,
	daily_rate FLOAT,
	currency VARCHAR(3) NOT NULL,
	location VARCHAR(255),
	next_maintenance_date TIMESTAMP WITH TIME ZONE,
	maintenance_history JSON,
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
	PRIMARY KEY (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS material_stocks (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	product_id UUID,
	name VARCHAR(255) NOT NULL,
	code VARCHAR(50),
	unit_of_measure VARCHAR(20) NOT NULL,
	current_quantity FLOAT NOT NULL,
	minimum_quantity FLOAT NOT NULL,
	reserved_quantity FLOAT NOT NULL,
	location VARCHAR(255),
	warehouse VARCHAR(100),
	unit_cost FLOAT,
	total_value FLOAT,
	currency VARCHAR(3) NOT NULL,
	is_below_minimum BOOLEAN NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(product_id) REFERENCES products (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS leaves (
	employee_id UUID NOT NULL,
	leave_type leavetype NOT NULL,
	start_date TIMESTAMP WITH TIME ZONE NOT NULL,
	end_date TIMESTAMP WITH TIME ZONE NOT NULL,
	status leavestatus NOT NULL,
	approved_by UUID,
	reason TEXT,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(employee_id) REFERENCES employees (id),
	FOREIGN KEY(approved_by) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS hr_planning_entries (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	entry_type VARCHAR(20) NOT NULL,
	position VARCHAR(100) NOT NULL,
	department VARCHAR(100),
	target_date TIMESTAMP WITH TIME ZONE NOT NULL,
	status VARCHAR(20) NOT NULL,
	description TEXT,
	employee_id UUID,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(employee_id) REFERENCES employees (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS procurement_orders (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	order_number VARCHAR(50) NOT NULL,
	supplier_contact_id UUID,
	project_id UUID,
	wbs_node_id UUID,
	status procurementstatus NOT NULL,
	total_amount FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	order_date TIMESTAMP WITH TIME ZONE,
	expected_delivery TIMESTAMP WITH TIME ZONE,
	actual_delivery TIMESTAMP WITH TIME ZONE,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	notes TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(supplier_contact_id) REFERENCES contacts (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(wbs_node_id) REFERENCES wbs_nodes (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS procurement_line_items (
	order_id UUID NOT NULL,
	material_stock_id UUID,
	product_id UUID,
	description TEXT NOT NULL,
	quantity FLOAT NOT NULL,
	unit_of_measure VARCHAR(20) NOT NULL,
	unit_price FLOAT NOT NULL,
	total_price FLOAT NOT NULL,
	received_quantity FLOAT NOT NULL,
	id UUID NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(order_id) REFERENCES procurement_orders (id),
	FOREIGN KEY(material_stock_id) REFERENCES material_stocks (id),
	FOREIGN KEY(product_id) REFERENCES products (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS procurement_documents (
	order_id UUID NOT NULL,
	document_type documenttype_rm NOT NULL,
	document_number VARCHAR(50) NOT NULL,
	document_date TIMESTAMP WITH TIME ZONE NOT NULL,
	amount FLOAT NOT NULL,
	currency VARCHAR(3) NOT NULL,
	file_path VARCHAR(1000),
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(order_id) REFERENCES procurement_orders (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS resource_allocations (
	is_p1 BOOLEAN NOT NULL,
	is_p2 BOOLEAN NOT NULL,
	is_p3 BOOLEAN NOT NULL,
	resource_type resourcetype NOT NULL,
	employee_id UUID,
	equipment_id UUID,
	project_id UUID NOT NULL,
	wbs_node_id UUID,
	task_id UUID,
	start_date TIMESTAMP WITH TIME ZONE NOT NULL,
	end_date TIMESTAMP WITH TIME ZONE NOT NULL,
	allocated_hours FLOAT,
	actual_hours FLOAT,
	planned_cost FLOAT,
	actual_cost FLOAT,
	currency VARCHAR(3) NOT NULL,
	status allocationstatus NOT NULL,
	has_conflict BOOLEAN NOT NULL,
	conflict_details JSON,
	allocation_percent FLOAT NOT NULL,
	id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	organization_id UUID NOT NULL,
	created_by UUID,
	updated_by UUID,
	PRIMARY KEY (id),
	FOREIGN KEY(employee_id) REFERENCES employees (id),
	FOREIGN KEY(equipment_id) REFERENCES equipment (id),
	FOREIGN KEY(project_id) REFERENCES projects (id),
	FOREIGN KEY(wbs_node_id) REFERENCES wbs_nodes (id),
	FOREIGN KEY(task_id) REFERENCES tasks (id)
)""")

    # ── BI ──

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

    # ── Indexes RM ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_employees_organization_id ON employees (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_employee_department ON employees (organization_id, department)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_employees_employee_number ON employees (employee_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_employee_org_status ON employees (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_code ON equipment (code)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_org_status ON equipment (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_organization_id ON equipment (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stocks_organization_id ON material_stocks (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stocks_code ON material_stocks (code)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stock_org ON material_stocks (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_leave_employee_dates ON leaves (employee_id, start_date, end_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_leaves_organization_id ON leaves (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_hr_planning_entries_organization_id ON hr_planning_entries (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_orders_order_number ON procurement_orders (order_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_org_status ON procurement_orders (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_orders_organization_id ON procurement_orders (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_line_items_organization_id ON procurement_line_items (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_documents_organization_id ON procurement_documents (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_resource_allocations_organization_id ON resource_allocations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_project ON resource_allocations (project_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_employee ON resource_allocations (employee_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_dates ON resource_allocations (start_date, end_date)""")

    # ── Indexes BI ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ai_conversations_organization_id ON ai_conversations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboards_organization_id ON dashboards (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboard_widgets_organization_id ON dashboard_widgets (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_values_organization_id ON kpi_values (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_value_def_date ON kpi_values (kpi_definition_id, computed_at)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_definitions_organization_id ON report_definitions (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_executions_organization_id ON report_executions (organization_id)""")


def downgrade() -> None:
    """Drop RM + BI tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS report_executions CASCADE")
    op.execute("DROP TABLE IF EXISTS report_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_values CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboard_widgets CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboards CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS resource_allocations CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_documents CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_line_items CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_orders CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_planning_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS leaves CASCADE")
    op.execute("DROP TABLE IF EXISTS material_stocks CASCADE")
    op.execute("DROP TABLE IF EXISTS equipment CASCADE")
    op.execute("DROP TABLE IF EXISTS employees CASCADE")
