"""Module tables — CRM, Pipeline, PM, RM, BI.

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all module tables (CRM, Pipeline, PM, RM, BI)."""

    op.execute("""CREATE TABLE IF NOT EXISTScontacts (
	company_name VARCHAR(255) NOT NULL, 
	cui VARCHAR(20), 
	registration_number VARCHAR(50), 
	stage contactstage NOT NULL, 
	contact_type contacttype NOT NULL, 
	address TEXT, 
	city VARCHAR(100), 
	county VARCHAR(100), 
	postal_code VARCHAR(20), 
	country VARCHAR(100) NOT NULL, 
	phone VARCHAR(30), 
	email VARCHAR(255), 
	website VARCHAR(255), 
	vat_payer BOOLEAN NOT NULL, 
	bank_account VARCHAR(50), 
	bank_name VARCHAR(100), 
	gdpr_consent BOOLEAN NOT NULL, 
	gdpr_consent_date TIMESTAMP WITH TIME ZONE, 
	tags JSON, 
	custom_data JSON, 
	is_duplicate_checked BOOLEAN NOT NULL, 
	merged_from_id UUID, 
	source VARCHAR(100), 
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

    op.execute("""CREATE TABLE IF NOT EXISTSequipment (
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

    op.execute("""CREATE TABLE IF NOT EXISTSai_conversations (
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

    op.execute("""CREATE TABLE IF NOT EXISTScontact_persons (
	contact_id UUID NOT NULL, 
	first_name VARCHAR(100) NOT NULL, 
	last_name VARCHAR(100) NOT NULL, 
	role VARCHAR(100), 
	email VARCHAR(255), 
	phone VARCHAR(30), 
	is_primary BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	deleted_by UUID, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSdashboards (
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

    op.execute("""CREATE TABLE IF NOT EXISTSemployees (
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

    op.execute("""CREATE TABLE IF NOT EXISTSinteractions (
	contact_id UUID NOT NULL, 
	interaction_type interactiontype NOT NULL, 
	subject VARCHAR(500), 
	description TEXT, 
	interaction_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	duration_minutes INTEGER, 
	opportunity_id UUID, 
	offer_id UUID, 
	contract_id UUID, 
	user_id UUID, 
	metadata_json JSON, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSkpi_values (
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

    op.execute("""CREATE TABLE IF NOT EXISTSmilestone_templates (
	name VARCHAR(255) NOT NULL, 
	product_category_id UUID, 
	template_data JSON NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_category_id) REFERENCES product_categories (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSopportunities (
	contact_id UUID NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	stage opportunitystage NOT NULL, 
	stage_entered_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	estimated_value FLOAT, 
	currency VARCHAR(3) NOT NULL, 
	win_probability FLOAT, 
	weighted_value FLOAT, 
	expected_close_date TIMESTAMP WITH TIME ZONE, 
	actual_close_date TIMESTAMP WITH TIME ZONE, 
	owner_id UUID, 
	loss_reason lossreason, 
	loss_reason_detail TEXT, 
	won_reason TEXT, 
	qualification_checklist JSON, 
	is_qualified BOOLEAN NOT NULL, 
	rm_validated BOOLEAN NOT NULL, 
	source VARCHAR(100), 
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
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSproducts (
	category_id UUID, 
	code VARCHAR(50), 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	product_type productcategory NOT NULL, 
	unit_of_measure VARCHAR(20) NOT NULL, 
	unit_price FLOAT, 
	currency VARCHAR(3) NOT NULL, 
	vat_rate FLOAT NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	parent_product_id UUID, 
	price_history JSON, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	deleted_by UUID, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES product_categories (id), 
	FOREIGN KEY(parent_product_id) REFERENCES products (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSproperties (
	contact_id UUID NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	property_type propertytype NOT NULL, 
	address TEXT, 
	city VARCHAR(100), 
	county VARCHAR(100), 
	country VARCHAR(100) NOT NULL, 
	total_area_sqm FLOAT, 
	heated_area_sqm FLOAT, 
	floors_count INTEGER, 
	year_built INTEGER, 
	year_renovated INTEGER, 
	structure_material VARCHAR(100), 
	facade_material VARCHAR(100), 
	roof_type VARCHAR(100), 
	energy_certificate VARCHAR(50), 
	energy_class VARCHAR(10), 
	custom_data JSON, 
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
	FOREIGN KEY(contact_id) REFERENCES contacts (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSreport_definitions (
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

    op.execute("""CREATE TABLE IF NOT EXISTSactivities (
	activity_type activitytype NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	status activitystatus NOT NULL, 
	scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	scheduled_end_date TIMESTAMP WITH TIME ZONE, 
	duration_minutes INTEGER, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	contact_id UUID, 
	opportunity_id UUID, 
	owner_id UUID, 
	visit_data JSON, 
	measurements JSON, 
	call_duration_seconds INTEGER, 
	call_outcome VARCHAR(100), 
	email_subject VARCHAR(500), 
	email_tracked BOOLEAN NOT NULL, 
	is_recurring BOOLEAN NOT NULL, 
	recurrence_rule JSON, 
	template_id UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSai_messages (
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

    op.execute("""CREATE TABLE IF NOT EXISTSdashboard_widgets (
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

    op.execute("""CREATE TABLE IF NOT EXISTSdocuments (
	entity_type VARCHAR(50) NOT NULL, 
	entity_id UUID NOT NULL, 
	contact_id UUID, 
	property_id UUID, 
	file_name VARCHAR(500) NOT NULL, 
	file_path VARCHAR(1000) NOT NULL, 
	file_size INTEGER, 
	mime_type VARCHAR(100), 
	category documentcategory NOT NULL, 
	description TEXT, 
	version INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(property_id) REFERENCES properties (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSenergy_profiles (
	property_id UUID NOT NULL, 
	u_value_walls FLOAT, 
	u_value_roof FLOAT, 
	u_value_floor FLOAT, 
	u_value_windows FLOAT, 
	u_value_doors FLOAT, 
	u_value_treated_glass FLOAT, 
	hvac_type VARCHAR(100), 
	hvac_capacity_kw FLOAT, 
	hvac_efficiency FLOAT, 
	hvac_year_installed INTEGER, 
	heating_source VARCHAR(100), 
	cooling_source VARCHAR(100), 
	annual_consumption_kwh FLOAT, 
	annual_consumption_gas_mc FLOAT, 
	estimated_savings_kwh FLOAT, 
	estimated_co2_reduction_kg FLOAT, 
	climate_zone VARCHAR(50), 
	extended_data JSON, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	UNIQUE (property_id), 
	FOREIGN KEY(property_id) REFERENCES properties (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTShr_planning_entries (
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

    op.execute("""CREATE TABLE IF NOT EXISTSleaves (
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

    op.execute("""CREATE TABLE IF NOT EXISTSmaterial_stocks (
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

    op.execute("""CREATE TABLE IF NOT EXISTSmilestones (
	opportunity_id UUID NOT NULL, 
	parent_id UUID, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	status milestonestatus NOT NULL, 
	sort_order INTEGER NOT NULL, 
	estimated_duration_days INTEGER, 
	start_date TIMESTAMP WITH TIME ZONE, 
	end_date TIMESTAMP WITH TIME ZONE, 
	estimated_resources JSON, 
	estimated_cost FLOAT, 
	currency VARCHAR(3) NOT NULL, 
	rm_validated BOOLEAN NOT NULL, 
	assigned_to UUID, 
	deadline TIMESTAMP WITH TIME ZONE, 
	template_id UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id), 
	FOREIGN KEY(parent_id) REFERENCES milestones (id), 
	FOREIGN KEY(assigned_to) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSoffers (
	contact_id UUID NOT NULL, 
	opportunity_id UUID, 
	property_id UUID, 
	offer_number VARCHAR(50) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	status offerstatus NOT NULL, 
	version INTEGER NOT NULL, 
	parent_offer_id UUID, 
	is_snapshot BOOLEAN NOT NULL, 
	subtotal FLOAT NOT NULL, 
	discount_percent FLOAT NOT NULL, 
	discount_amount FLOAT NOT NULL, 
	vat_amount FLOAT NOT NULL, 
	total_amount FLOAT NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	terms_and_conditions TEXT, 
	validity_days INTEGER NOT NULL, 
	valid_until TIMESTAMP WITH TIME ZONE, 
	sent_at TIMESTAMP WITH TIME ZONE, 
	accepted_at TIMESTAMP WITH TIME ZONE, 
	rejected_at TIMESTAMP WITH TIME ZONE, 
	next_follow_up TIMESTAMP WITH TIME ZONE, 
	follow_up_count INTEGER NOT NULL, 
	owner_id UUID, 
	template_id UUID, 
	is_quick_quote BOOLEAN NOT NULL, 
	pdf_path VARCHAR(1000), 
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
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id), 
	FOREIGN KEY(property_id) REFERENCES properties (id), 
	FOREIGN KEY(parent_offer_id) REFERENCES offers (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id), 
	FOREIGN KEY(template_id) REFERENCES document_templates (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSproperty_work_history (
	property_id UUID NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	work_type VARCHAR(100), 
	performed_by VARCHAR(255), 
	start_date TIMESTAMP WITH TIME ZONE, 
	end_date TIMESTAMP WITH TIME ZONE, 
	cost FLOAT, 
	currency VARCHAR(3) NOT NULL, 
	project_id UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(property_id) REFERENCES properties (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSreport_executions (
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

    op.execute("""CREATE TABLE IF NOT EXISTSsurface_calculations (
	property_id UUID NOT NULL, 
	floor_name VARCHAR(100) NOT NULL, 
	floor_number INTEGER NOT NULL, 
	surface_type VARCHAR(50) NOT NULL, 
	area_sqm FLOAT NOT NULL, 
	material VARCHAR(100), 
	u_value FLOAT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(property_id) REFERENCES properties (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTScontracts (
	contact_id UUID NOT NULL, 
	offer_id UUID, 
	opportunity_id UUID, 
	contract_number VARCHAR(50) NOT NULL, 
	title VARCHAR(500) NOT NULL, 
	description TEXT, 
	status contractstatus NOT NULL, 
	total_value FLOAT NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	start_date TIMESTAMP WITH TIME ZONE, 
	end_date TIMESTAMP WITH TIME ZONE, 
	signed_date TIMESTAMP WITH TIME ZONE, 
	terminated_date TIMESTAMP WITH TIME ZONE, 
	termination_reason TEXT, 
	terms_and_conditions TEXT, 
	standard_clauses JSON, 
	owner_id UUID, 
	template_id UUID, 
	project_id UUID, 
	pdf_path VARCHAR(1000), 
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
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(offer_id) REFERENCES offers (id), 
	FOREIGN KEY(opportunity_id) REFERENCES opportunities (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id), 
	FOREIGN KEY(template_id) REFERENCES document_templates (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSenergy_measurements (
	energy_profile_id UUID NOT NULL, 
	measurement_type VARCHAR(10) NOT NULL, 
	parameter_name VARCHAR(100) NOT NULL, 
	value FLOAT NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	measured_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	measured_by UUID, 
	project_id UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(energy_profile_id) REFERENCES energy_profiles (id), 
	FOREIGN KEY(measured_by) REFERENCES users (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSmilestone_dependencies (
	milestone_id UUID NOT NULL, 
	depends_on_id UUID NOT NULL, 
	dependency_type dependencytype NOT NULL, 
	lag_days INTEGER NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(milestone_id) REFERENCES milestones (id), 
	FOREIGN KEY(depends_on_id) REFERENCES milestones (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSoffer_line_items (
	offer_id UUID NOT NULL, 
	product_id UUID, 
	description TEXT NOT NULL, 
	quantity FLOAT NOT NULL, 
	unit_of_measure VARCHAR(20) NOT NULL, 
	unit_price FLOAT NOT NULL, 
	discount_percent FLOAT NOT NULL, 
	vat_rate FLOAT NOT NULL, 
	total_price FLOAT NOT NULL, 
	sort_order INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(offer_id) REFERENCES offers (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSbilling_schedules (
	contract_id UUID NOT NULL, 
	installment_number INTEGER NOT NULL, 
	description VARCHAR(500), 
	amount FLOAT NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	due_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	is_invoiced BOOLEAN NOT NULL, 
	invoice_id UUID, 
	work_situation_id UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contract_id) REFERENCES contracts (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSinvoices (
	contract_id UUID NOT NULL, 
	invoice_number VARCHAR(50) NOT NULL, 
	status invoicestatus NOT NULL, 
	amount FLOAT NOT NULL, 
	vat_amount FLOAT NOT NULL, 
	total_amount FLOAT NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	issue_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	due_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	paid_date TIMESTAMP WITH TIME ZONE, 
	paid_amount FLOAT, 
	pdf_path VARCHAR(1000), 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	organization_id UUID NOT NULL, 
	created_by UUID, 
	updated_by UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contract_id) REFERENCES contracts (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTSprojects (
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

    op.execute("""CREATE TABLE IF NOT EXISTSbudget_entries (
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

    op.execute("""CREATE TABLE IF NOT EXISTSdaily_reports (
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

    op.execute("""CREATE TABLE IF NOT EXISTSenergy_impacts (
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

    op.execute("""CREATE TABLE IF NOT EXISTSimport_jobs (
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

    op.execute("""CREATE TABLE IF NOT EXISTSproject_cash_flow_entries (
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

    op.execute("""CREATE TABLE IF NOT EXISTSproject_finance_entries (
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

    op.execute("""CREATE TABLE IF NOT EXISTSpunch_items (
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

    op.execute("""CREATE TABLE IF NOT EXISTSrisks (
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

    op.execute("""CREATE TABLE IF NOT EXISTSsubcontractors (
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

    op.execute("""CREATE TABLE IF NOT EXISTSwarranties (
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

    op.execute("""CREATE TABLE IF NOT EXISTSwbs_nodes (
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

    op.execute("""CREATE TABLE IF NOT EXISTSwiki_posts (
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

    op.execute("""CREATE TABLE IF NOT EXISTSwork_situations (
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

    op.execute("""CREATE TABLE IF NOT EXISTSdeviz_items (
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

    op.execute("""CREATE TABLE IF NOT EXISTSprocurement_orders (
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

    op.execute("""CREATE TABLE IF NOT EXISTStasks (
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

    op.execute("""CREATE TABLE IF NOT EXISTSwiki_comments (
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

    op.execute("""CREATE TABLE IF NOT EXISTSmaterial_consumptions (
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

    op.execute("""CREATE TABLE IF NOT EXISTSprocurement_documents (
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

    op.execute("""CREATE TABLE IF NOT EXISTSprocurement_line_items (
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

    op.execute("""CREATE TABLE IF NOT EXISTSresource_allocations (
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

    op.execute("""CREATE TABLE IF NOT EXISTStask_dependencies (
	task_id UUID NOT NULL, 
	depends_on_id UUID NOT NULL, 
	dependency_type taskdependencytype NOT NULL, 
	lag_days INTEGER NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES tasks (id), 
	FOREIGN KEY(depends_on_id) REFERENCES tasks (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTStimesheet_entries (
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

    # Indexes
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_cui ON contacts (cui)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_stage ON contacts (organization_id, stage)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_phone ON contacts (phone)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_email ON contacts (email)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_organization_id ON contacts (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_type ON contacts (organization_id, contact_type)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_code ON equipment (code)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_org_status ON equipment (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_organization_id ON equipment (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ai_conversations_organization_id ON ai_conversations (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_persons_organization_id ON contact_persons (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboards_organization_id ON dashboards (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_employees_organization_id ON employees (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_employee_department ON employees (organization_id, department)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_employees_employee_number ON employees (employee_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_employee_org_status ON employees (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_interactions_organization_id ON interactions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_interaction_contact_date ON interactions (contact_id, interaction_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_values_organization_id ON kpi_values (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_value_def_date ON kpi_values (kpi_definition_id, computed_at)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_milestone_templates_organization_id ON milestone_templates (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunities_organization_id ON opportunities (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_contact ON opportunities (contact_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_org_stage ON opportunities (organization_id, stage)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_owner ON opportunities (owner_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_products_code ON products (code)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_product_org_type ON products (organization_id, product_type)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_products_organization_id ON products (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_properties_organization_id ON properties (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_contact ON properties (contact_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_org_type ON properties (organization_id, property_type)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_definitions_organization_id ON report_definitions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_activity_owner_date ON activities (owner_id, scheduled_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_activity_org_date ON activities (organization_id, scheduled_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_activities_organization_id ON activities (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_dashboard_widgets_organization_id ON dashboard_widgets (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_document_entity ON documents (entity_type, entity_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_documents_organization_id ON documents (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_profiles_organization_id ON energy_profiles (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_hr_planning_entries_organization_id ON hr_planning_entries (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_leave_employee_dates ON leaves (employee_id, start_date, end_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_leaves_organization_id ON leaves (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stocks_organization_id ON material_stocks (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stocks_code ON material_stocks (code)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_stock_org ON material_stocks (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_milestones_organization_id ON milestones (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_offers_organization_id ON offers (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_offers_offer_number ON offers (offer_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_org_status ON offers (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_contact ON offers (contact_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_work_history_organization_id ON property_work_history (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_report_executions_organization_id ON report_executions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_surface_calculations_organization_id ON surface_calculations (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contract_contact ON contracts (contact_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contracts_contract_number ON contracts (contract_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contracts_organization_id ON contracts (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contract_org_status ON contracts (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_measurements_organization_id ON energy_measurements (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_line_items_organization_id ON offer_line_items (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_billing_schedules_organization_id ON billing_schedules (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoices_invoice_number ON invoices (invoice_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoice_org_status ON invoices (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoices_organization_id ON invoices (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_projects_organization_id ON projects (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_projects_project_number ON projects (project_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_org_status ON projects (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_pm ON projects (project_manager_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_org_period ON budget_entries (organization_id, period_year, period_month)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_entries_organization_id ON budget_entries (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_budget_cost_center ON budget_entries (organization_id, cost_center)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_daily_report_project_date ON daily_reports (project_id, report_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_daily_reports_organization_id ON daily_reports (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_impacts_organization_id ON energy_impacts (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_import_jobs_organization_id ON import_jobs (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_cash_flow_entries_organization_id ON project_cash_flow_entries (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_cashflow_project_date ON project_cash_flow_entries (project_id, transaction_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_project_finance_entries_organization_id ON project_finance_entries (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_finance_project_period ON project_finance_entries (project_id, period_year, period_month)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_punch_items_organization_id ON punch_items (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_punch_project_status ON punch_items (project_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_risks_organization_id ON risks (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_subcontractor_project ON subcontractors (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_subcontractors_organization_id ON subcontractors (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_warranties_organization_id ON warranties (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wbs_nodes_organization_id ON wbs_nodes (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wbs_project ON wbs_nodes (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_posts_organization_id ON wiki_posts (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_department ON wiki_posts (department)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_project ON wiki_posts (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_work_situations_organization_id ON work_situations (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_work_situation_project ON work_situations (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_deviz_project ON deviz_items (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_deviz_items_organization_id ON deviz_items (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_orders_order_number ON procurement_orders (order_number)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_org_status ON procurement_orders (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_orders_organization_id ON procurement_orders (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_task_assigned ON tasks (assigned_to)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_tasks_organization_id ON tasks (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_task_project_status ON tasks (project_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_wiki_comments_organization_id ON wiki_comments (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_consumption_project ON material_consumptions (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_material_consumptions_organization_id ON material_consumptions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_documents_organization_id ON procurement_documents (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_procurement_line_items_organization_id ON procurement_line_items (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_resource_allocations_organization_id ON resource_allocations (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_project ON resource_allocations (project_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_employee ON resource_allocations (employee_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_allocation_dates ON resource_allocations (start_date, end_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_entries_organization_id ON timesheet_entries (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_user_date ON timesheet_entries (user_id, work_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_timesheet_project_date ON timesheet_entries (project_id, work_date)""")



def downgrade() -> None:
    """Drop all module tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS timesheet_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS task_dependencies CASCADE")
    op.execute("DROP TABLE IF EXISTS resource_allocations CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_line_items CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_documents CASCADE")
    op.execute("DROP TABLE IF EXISTS material_consumptions CASCADE")
    op.execute("DROP TABLE IF EXISTS wiki_comments CASCADE")
    op.execute("DROP TABLE IF EXISTS tasks CASCADE")
    op.execute("DROP TABLE IF EXISTS procurement_orders CASCADE")
    op.execute("DROP TABLE IF EXISTS deviz_items CASCADE")
    op.execute("DROP TABLE IF EXISTS work_situations CASCADE")
    op.execute("DROP TABLE IF EXISTS wiki_posts CASCADE")
    op.execute("DROP TABLE IF EXISTS wbs_nodes CASCADE")
    op.execute("DROP TABLE IF EXISTS warranties CASCADE")
    op.execute("DROP TABLE IF EXISTS subcontractors CASCADE")
    op.execute("DROP TABLE IF EXISTS risks CASCADE")
    op.execute("DROP TABLE IF EXISTS punch_items CASCADE")
    op.execute("DROP TABLE IF EXISTS project_finance_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS project_cash_flow_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS import_jobs CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_impacts CASCADE")
    op.execute("DROP TABLE IF EXISTS daily_reports CASCADE")
    op.execute("DROP TABLE IF EXISTS budget_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS projects CASCADE")
    op.execute("DROP TABLE IF EXISTS invoices CASCADE")
    op.execute("DROP TABLE IF EXISTS billing_schedules CASCADE")
    op.execute("DROP TABLE IF EXISTS offer_line_items CASCADE")
    op.execute("DROP TABLE IF EXISTS milestone_dependencies CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_measurements CASCADE")
    op.execute("DROP TABLE IF EXISTS contracts CASCADE")
    op.execute("DROP TABLE IF EXISTS surface_calculations CASCADE")
    op.execute("DROP TABLE IF EXISTS report_executions CASCADE")
    op.execute("DROP TABLE IF EXISTS property_work_history CASCADE")
    op.execute("DROP TABLE IF EXISTS offers CASCADE")
    op.execute("DROP TABLE IF EXISTS milestones CASCADE")
    op.execute("DROP TABLE IF EXISTS material_stocks CASCADE")
    op.execute("DROP TABLE IF EXISTS leaves CASCADE")
    op.execute("DROP TABLE IF EXISTS hr_planning_entries CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS documents CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboard_widgets CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS activities CASCADE")
    op.execute("DROP TABLE IF EXISTS report_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS properties CASCADE")
    op.execute("DROP TABLE IF EXISTS products CASCADE")
    op.execute("DROP TABLE IF EXISTS opportunities CASCADE")
    op.execute("DROP TABLE IF EXISTS milestone_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_values CASCADE")
    op.execute("DROP TABLE IF EXISTS interactions CASCADE")
    op.execute("DROP TABLE IF EXISTS employees CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboards CASCADE")
    op.execute("DROP TABLE IF EXISTS contact_persons CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS equipment CASCADE")
    op.execute("DROP TABLE IF EXISTS contacts CASCADE")
