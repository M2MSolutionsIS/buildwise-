"""Initial schema — all 6 modules (CRM, Pipeline, PM, RM, BI, System).

77 tables covering 108 functionalities (F001-F161) across 3 prototypes (P1, P2, P3).

Revision ID: 0001
Revises:
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all 77 tables for the BuildWise ERP platform."""

    # ==========================================
    # CREATE ALL ENUM TYPES BEFORE ANY TABLES
    # ==========================================

    # CRM enums
    op.execute("CREATE TYPE contactstage AS ENUM ('PROSPECT', 'POTENTIAL_CLIENT', 'ACTIVE', 'INACTIVE', 'PARTNER')")
    op.execute("CREATE TYPE contacttype AS ENUM ('PF', 'IMM', 'PJ', 'CORPORATION')")
    op.execute("CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING', 'OFFER', 'CONTRACT', 'NOTE', 'VISIT')")
    op.execute("CREATE TYPE propertytype AS ENUM ('BLOC_PANOU', 'BLOC_CARAMIDA', 'CASA_INTERBELICA', 'CASA_POST_1990', 'SPATIU_INDUSTRIAL', 'CLADIRE_COMERCIALA', 'CLADIRE_PUBLICA', 'OTHER')")
    op.execute("CREATE TYPE productcategory AS ENUM ('PRODUCT', 'SERVICE', 'REVENUE', 'EXPENSE')")
    op.execute("CREATE TYPE documentcategory AS ENUM ('CERTIFICATE', 'PHOTO', 'TECHNICAL', 'CONTRACT', 'OFFER', 'INVOICE', 'OTHER')")

    # Pipeline enums
    op.execute("CREATE TYPE opportunitystage AS ENUM ('NEW', 'QUALIFIED', 'SCOPING', 'OFFERING', 'SENT', 'NEGOTIATION', 'WON', 'LOST')")
    op.execute("CREATE TYPE milestonestatus AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE dependencytype AS ENUM ('FS', 'SS', 'FF', 'SF')")
    op.execute("CREATE TYPE activitytype AS ENUM ('CALL', 'MEETING', 'FOLLOW_UP', 'TECHNICAL_VISIT', 'EMAIL', 'TASK')")
    op.execute("CREATE TYPE activitystatus AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'OVERDUE')")
    op.execute("CREATE TYPE offerstatus AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT', 'NEGOTIATION', 'ACCEPTED', 'REJECTED', 'EXPIRED')")
    op.execute("CREATE TYPE contractstatus AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT', 'SIGNED', 'ACTIVE', 'SUSPENDED', 'TERMINATED', 'COMPLETED')")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('DRAFT', 'ISSUED', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED')")
    op.execute("CREATE TYPE approvalstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED')")
    op.execute("CREATE TYPE lossreason AS ENUM ('PRICE', 'COMPETITION', 'TIMING', 'NO_BUDGET', 'NO_NEED', 'NO_RESPONSE', 'OTHER')")

    # PM enums
    op.execute("CREATE TYPE projectstatus AS ENUM ('DRAFT', 'KICKOFF', 'PLANNING', 'IN_PROGRESS', 'ON_HOLD', 'POST_EXECUTION', 'CLOSING', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE projecttype AS ENUM ('CLIENT', 'INTERNAL')")
    op.execute("CREATE TYPE wbsnodetype AS ENUM ('CHAPTER', 'SUBCHAPTER', 'ARTICLE')")
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE')")
    op.execute("CREATE TYPE taskdependencytype AS ENUM ('FS', 'SS', 'FF', 'SF')")
    op.execute("CREATE TYPE riskprobability AS ENUM ('VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')")
    op.execute("CREATE TYPE riskimpact AS ENUM ('NEGLIGIBLE', 'MINOR', 'MODERATE', 'MAJOR', 'CRITICAL')")
    op.execute("CREATE TYPE riskstatus AS ENUM ('IDENTIFIED', 'ASSESSED', 'MITIGATING', 'RESOLVED', 'ACCEPTED')")
    op.execute("CREATE TYPE punchitemstatus AS ENUM ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'VERIFIED')")
    op.execute("CREATE TYPE punchitemseverity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')")
    op.execute("CREATE TYPE timesheetstatus AS ENUM ('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED')")
    op.execute("CREATE TYPE wikiposttype AS ENUM ('POST', 'FILE', 'DOCUMENT')")
    op.execute("CREATE TYPE importsourcetype AS ENUM ('INTERSOFT', 'EDEVIZE', 'CSV', 'EXCEL', 'API')")

    # RM enums
    op.execute("CREATE TYPE employeestatus AS ENUM ('ACTIVE', 'ON_LEAVE', 'SUSPENDED', 'TERMINATED')")
    op.execute("CREATE TYPE contracttype AS ENUM ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'FREELANCE')")
    op.execute("CREATE TYPE leavetype AS ENUM ('ANNUAL', 'SICK', 'PERSONAL', 'MATERNITY', 'UNPAID', 'OTHER')")
    op.execute("CREATE TYPE leavestatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')")
    op.execute("CREATE TYPE equipmentstatus AS ENUM ('AVAILABLE', 'ALLOCATED', 'IN_MAINTENANCE', 'OUT_OF_SERVICE')")
    op.execute("CREATE TYPE procurementstatus AS ENUM ('DRAFT', 'REQUESTED', 'APPROVED', 'ORDERED', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')")
    op.execute("CREATE TYPE allocationstatus AS ENUM ('PLANNED', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE resourcetype AS ENUM ('EMPLOYEE', 'EQUIPMENT', 'MATERIAL', 'EXTERNAL')")
    op.execute("CREATE TYPE documenttype_rm AS ENUM ('INVOICE', 'NIR', 'CONSUMPTION_VOUCHER', 'DELIVERY_NOTE')")

    # BI enums
    op.execute("CREATE TYPE kpithresholdcolor AS ENUM ('RED', 'YELLOW', 'GREEN')")
    op.execute("CREATE TYPE reportformat AS ENUM ('PDF', 'EXCEL', 'CSV')")
    op.execute("CREATE TYPE dashboardwidgettype AS ENUM ('KPI_CARD', 'CHART', 'TABLE', 'GAUGE', 'FUNNEL', 'MAP', 'CUSTOM')")

    # System enums
    op.execute("CREATE TYPE prototypeenum AS ENUM ('P1', 'P2', 'P3')")
    op.execute("CREATE TYPE roleenum AS ENUM ('ADMIN', 'MANAGER_VANZARI', 'AGENT_COMERCIAL', 'TEHNICIAN')")
    op.execute("CREATE TYPE notificationchannel AS ENUM ('EMAIL', 'IN_APP', 'BOTH')")
    op.execute("CREATE TYPE notificationstatus AS ENUM ('UNREAD', 'READ', 'ARCHIVED')")
    op.execute("CREATE TYPE customfieldtype AS ENUM ('TEXT', 'NUMBER', 'DATE', 'SELECT', 'MULTISELECT', 'BOOLEAN', 'URL', 'EMAIL', 'PHONE')")

    # ==========================================
    # CREATE ALL TABLES
    # ==========================================

    op.execute("""CREATE TABLE contacts (
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

    op.execute("""CREATE TABLE currencies (
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

    op.execute("""CREATE TABLE custom_field_definitions (
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

    op.execute("""CREATE TABLE document_templates (
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

    op.execute("""CREATE TABLE equipment (
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

    op.execute("""CREATE TABLE exchange_rates (
	from_currency VARCHAR(3) NOT NULL, 
	to_currency VARCHAR(3) NOT NULL, 
	rate FLOAT NOT NULL, 
	effective_date TIMESTAMP WITH TIME ZONE NOT NULL, 
	id UUID NOT NULL, 
	organization_id UUID NOT NULL, 
	PRIMARY KEY (id)
)""")

    op.execute("""CREATE TABLE feature_flags (
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

    op.execute("""CREATE TABLE kpi_definitions (
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

    op.execute("""CREATE TABLE ml_model_configs (
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

    op.execute("""CREATE TABLE notification_templates (
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

    op.execute("""CREATE TABLE organizations (
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

    op.execute("""CREATE TABLE permissions (
	module VARCHAR(50) NOT NULL, 
	action VARCHAR(50) NOT NULL, 
	description TEXT, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_permission_module_action UNIQUE (module, action)
)""")

    op.execute("""CREATE TABLE pipeline_stage_configs (
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

    op.execute("""CREATE TABLE product_categories (
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

    op.execute("""CREATE TABLE roles (
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

    op.execute("""CREATE TABLE users (
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

    op.execute("""CREATE TABLE ai_conversations (
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

    op.execute("""CREATE TABLE approval_workflows (
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

    op.execute("""CREATE TABLE audit_logs (
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

    op.execute("""CREATE TABLE contact_persons (
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

    op.execute("""CREATE TABLE custom_field_values (
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

    op.execute("""CREATE TABLE dashboards (
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

    op.execute("""CREATE TABLE employees (
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

    op.execute("""CREATE TABLE interactions (
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

    op.execute("""CREATE TABLE kpi_values (
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

    op.execute("""CREATE TABLE milestone_templates (
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

    op.execute("""CREATE TABLE notifications (
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

    op.execute("""CREATE TABLE opportunities (
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

    op.execute("""CREATE TABLE products (
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

    op.execute("""CREATE TABLE properties (
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

    op.execute("""CREATE TABLE report_definitions (
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

    op.execute("""CREATE TABLE role_permissions (
	role_id UUID NOT NULL, 
	permission_id UUID NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	FOREIGN KEY(permission_id) REFERENCES permissions (id)
)""")

    op.execute("""CREATE TABLE user_roles (
	user_id UUID NOT NULL, 
	role_id UUID NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_role UNIQUE (user_id, role_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
)""")

    op.execute("""CREATE TABLE activities (
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

    op.execute("""CREATE TABLE ai_messages (
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

    op.execute("""CREATE TABLE approval_steps (
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

    op.execute("""CREATE TABLE dashboard_widgets (
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

    op.execute("""CREATE TABLE documents (
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

    op.execute("""CREATE TABLE energy_profiles (
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

    op.execute("""CREATE TABLE hr_planning_entries (
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

    op.execute("""CREATE TABLE leaves (
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

    op.execute("""CREATE TABLE material_stocks (
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

    op.execute("""CREATE TABLE milestones (
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

    op.execute("""CREATE TABLE offers (
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

    op.execute("""CREATE TABLE property_work_history (
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

    op.execute("""CREATE TABLE report_executions (
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

    op.execute("""CREATE TABLE surface_calculations (
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

    op.execute("""CREATE TABLE contracts (
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

    op.execute("""CREATE TABLE energy_measurements (
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

    op.execute("""CREATE TABLE milestone_dependencies (
	milestone_id UUID NOT NULL, 
	depends_on_id UUID NOT NULL, 
	dependency_type dependencytype NOT NULL, 
	lag_days INTEGER NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(milestone_id) REFERENCES milestones (id), 
	FOREIGN KEY(depends_on_id) REFERENCES milestones (id)
)""")

    op.execute("""CREATE TABLE offer_line_items (
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

    op.execute("""CREATE TABLE billing_schedules (
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

    op.execute("""CREATE TABLE invoices (
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

    op.execute("""CREATE TABLE projects (
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

    op.execute("""CREATE TABLE budget_entries (
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

    op.execute("""CREATE TABLE daily_reports (
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

    op.execute("""CREATE TABLE energy_impacts (
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

    op.execute("""CREATE TABLE import_jobs (
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

    op.execute("""CREATE TABLE project_cash_flow_entries (
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

    op.execute("""CREATE TABLE project_finance_entries (
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

    op.execute("""CREATE TABLE punch_items (
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

    op.execute("""CREATE TABLE risks (
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

    op.execute("""CREATE TABLE subcontractors (
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

    op.execute("""CREATE TABLE warranties (
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

    op.execute("""CREATE TABLE wbs_nodes (
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

    op.execute("""CREATE TABLE wiki_posts (
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

    op.execute("""CREATE TABLE work_situations (
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

    op.execute("""CREATE TABLE deviz_items (
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

    op.execute("""CREATE TABLE procurement_orders (
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

    op.execute("""CREATE TABLE tasks (
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

    op.execute("""CREATE TABLE wiki_comments (
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

    op.execute("""CREATE TABLE material_consumptions (
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

    op.execute("""CREATE TABLE procurement_documents (
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

    op.execute("""CREATE TABLE procurement_line_items (
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

    op.execute("""CREATE TABLE resource_allocations (
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

    op.execute("""CREATE TABLE task_dependencies (
	task_id UUID NOT NULL, 
	depends_on_id UUID NOT NULL, 
	dependency_type taskdependencytype NOT NULL, 
	lag_days INTEGER NOT NULL, 
	id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES tasks (id), 
	FOREIGN KEY(depends_on_id) REFERENCES tasks (id)
)""")

    op.execute("""CREATE TABLE timesheet_entries (
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

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_cui ON contacts (cui)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_stage ON contacts (organization_id, stage)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_phone ON contacts (phone)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_email ON contacts (email)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_organization_id ON contacts (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_type ON contacts (organization_id, contact_type)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_currencies_organization_id ON currencies (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_custom_field_definitions_organization_id ON custom_field_definitions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_document_templates_organization_id ON document_templates (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_code ON equipment (code)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_org_status ON equipment (organization_id, status)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_equipment_organization_id ON equipment (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_exchange_rate_date ON exchange_rates (from_currency, to_currency, effective_date)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_exchange_rates_organization_id ON exchange_rates (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_feature_flags_organization_id ON feature_flags (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_org ON kpi_definitions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_kpi_definitions_organization_id ON kpi_definitions (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ml_model_configs_organization_id ON ml_model_configs (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_notification_templates_organization_id ON notification_templates (organization_id)""")

    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS ix_organizations_slug ON organizations (slug)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_pipeline_stage_configs_organization_id ON pipeline_stage_configs (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_product_categories_organization_id ON product_categories (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_roles_organization_id ON roles (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_users_organization_id ON users (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_ai_conversations_organization_id ON ai_conversations (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_approval_entity ON approval_workflows (entity_type, entity_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_approval_workflows_organization_id ON approval_workflows (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_audit_entity ON audit_logs (entity_type, entity_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_audit_logs_organization_id ON audit_logs (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_audit_timestamp ON audit_logs (timestamp)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_persons_organization_id ON contact_persons (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_custom_field_values_organization_id ON custom_field_values (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_custom_field_entity ON custom_field_values (entity_type, entity_id)""")

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

    op.execute("""CREATE INDEX IF NOT EXISTS ix_notifications_organization_id ON notifications (organization_id)""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_notification_user_status ON notifications (user_id, status)""")

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
    """Drop all tables in reverse dependency order."""

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
    op.execute("DROP TABLE IF EXISTS approval_steps CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS activities CASCADE")
    op.execute("DROP TABLE IF EXISTS user_roles CASCADE")
    op.execute("DROP TABLE IF EXISTS role_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS report_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS properties CASCADE")
    op.execute("DROP TABLE IF EXISTS products CASCADE")
    op.execute("DROP TABLE IF EXISTS opportunities CASCADE")
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS milestone_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_values CASCADE")
    op.execute("DROP TABLE IF EXISTS interactions CASCADE")
    op.execute("DROP TABLE IF EXISTS employees CASCADE")
    op.execute("DROP TABLE IF EXISTS dashboards CASCADE")
    op.execute("DROP TABLE IF EXISTS custom_field_values CASCADE")
    op.execute("DROP TABLE IF EXISTS contact_persons CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
    op.execute("DROP TABLE IF EXISTS approval_workflows CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS roles CASCADE")
    op.execute("DROP TABLE IF EXISTS product_categories CASCADE")
    op.execute("DROP TABLE IF EXISTS pipeline_stage_configs CASCADE")
    op.execute("DROP TABLE IF EXISTS permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS organizations CASCADE")
    op.execute("DROP TABLE IF EXISTS notification_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS ml_model_configs CASCADE")
    op.execute("DROP TABLE IF EXISTS kpi_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS feature_flags CASCADE")
    op.execute("DROP TABLE IF EXISTS exchange_rates CASCADE")
    op.execute("DROP TABLE IF EXISTS equipment CASCADE")
    op.execute("DROP TABLE IF EXISTS document_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS custom_field_definitions CASCADE")
    op.execute("DROP TABLE IF EXISTS currencies CASCADE")
    op.execute("DROP TABLE IF EXISTS contacts CASCADE")

    # Drop all enum types
    op.execute("DROP TYPE IF EXISTS contactstage CASCADE")
    op.execute("DROP TYPE IF EXISTS contacttype CASCADE")
    op.execute("DROP TYPE IF EXISTS interactiontype CASCADE")
    op.execute("DROP TYPE IF EXISTS propertytype CASCADE")
    op.execute("DROP TYPE IF EXISTS productcategory CASCADE")
    op.execute("DROP TYPE IF EXISTS documentcategory CASCADE")
    op.execute("DROP TYPE IF EXISTS opportunitystage CASCADE")
    op.execute("DROP TYPE IF EXISTS milestonestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS dependencytype CASCADE")
    op.execute("DROP TYPE IF EXISTS activitytype CASCADE")
    op.execute("DROP TYPE IF EXISTS activitystatus CASCADE")
    op.execute("DROP TYPE IF EXISTS offerstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS contractstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS invoicestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS approvalstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS lossreason CASCADE")
    op.execute("DROP TYPE IF EXISTS projectstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS projecttype CASCADE")
    op.execute("DROP TYPE IF EXISTS wbsnodetype CASCADE")
    op.execute("DROP TYPE IF EXISTS taskstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS taskdependencytype CASCADE")
    op.execute("DROP TYPE IF EXISTS riskprobability CASCADE")
    op.execute("DROP TYPE IF EXISTS riskimpact CASCADE")
    op.execute("DROP TYPE IF EXISTS riskstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS punchitemstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS punchitemseverity CASCADE")
    op.execute("DROP TYPE IF EXISTS timesheetstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS wikiposttype CASCADE")
    op.execute("DROP TYPE IF EXISTS importsourcetype CASCADE")
    op.execute("DROP TYPE IF EXISTS employeestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS contracttype CASCADE")
    op.execute("DROP TYPE IF EXISTS leavetype CASCADE")
    op.execute("DROP TYPE IF EXISTS leavestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS equipmentstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS procurementstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS allocationstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS resourcetype CASCADE")
    op.execute("DROP TYPE IF EXISTS documenttype_rm CASCADE")
    op.execute("DROP TYPE IF EXISTS kpithresholdcolor CASCADE")
    op.execute("DROP TYPE IF EXISTS reportformat CASCADE")
    op.execute("DROP TYPE IF EXISTS dashboardwidgettype CASCADE")
    op.execute("DROP TYPE IF EXISTS prototypeenum CASCADE")
    op.execute("DROP TYPE IF EXISTS roleenum CASCADE")
    op.execute("DROP TYPE IF EXISTS notificationchannel CASCADE")
    op.execute("DROP TYPE IF EXISTS notificationstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS customfieldtype CASCADE")
