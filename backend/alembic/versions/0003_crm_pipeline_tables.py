"""CRM + Pipeline tables.

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
    """Create CRM + Pipeline tables."""

    # ── CRM ──

    op.execute("""CREATE TABLE IF NOT EXISTS contacts (
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

    op.execute("""CREATE TABLE IF NOT EXISTS contact_persons (
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

    op.execute("""CREATE TABLE IF NOT EXISTS properties (
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

    op.execute("""CREATE TABLE IF NOT EXISTS products (
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

    op.execute("""CREATE TABLE IF NOT EXISTS interactions (
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

    op.execute("""CREATE TABLE IF NOT EXISTS documents (
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

    op.execute("""CREATE TABLE IF NOT EXISTS energy_profiles (
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

    op.execute("""CREATE TABLE IF NOT EXISTS surface_calculations (
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

    op.execute("""CREATE TABLE IF NOT EXISTS property_work_history (
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

    op.execute("""CREATE TABLE IF NOT EXISTS energy_measurements (
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

    # ── Pipeline ──

    op.execute("""CREATE TABLE IF NOT EXISTS opportunities (
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

    op.execute("""CREATE TABLE IF NOT EXISTS milestone_templates (
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

    op.execute("""CREATE TABLE IF NOT EXISTS milestones (
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

    op.execute("""CREATE TABLE IF NOT EXISTS milestone_dependencies (
	milestone_id UUID NOT NULL,
	depends_on_id UUID NOT NULL,
	dependency_type dependencytype NOT NULL,
	lag_days INTEGER NOT NULL,
	id UUID NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(milestone_id) REFERENCES milestones (id),
	FOREIGN KEY(depends_on_id) REFERENCES milestones (id)
)""")

    op.execute("""CREATE TABLE IF NOT EXISTS activities (
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

    op.execute("""CREATE TABLE IF NOT EXISTS offers (
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

    op.execute("""CREATE TABLE IF NOT EXISTS offer_line_items (
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

    op.execute("""CREATE TABLE IF NOT EXISTS contracts (
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

    op.execute("""CREATE TABLE IF NOT EXISTS billing_schedules (
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

    op.execute("""CREATE TABLE IF NOT EXISTS invoices (
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

    # ── Indexes CRM ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_cui ON contacts (cui)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_stage ON contacts (organization_id, stage)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_phone ON contacts (phone)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_email ON contacts (email)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contacts_organization_id ON contacts (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_org_type ON contacts (organization_id, contact_type)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contact_persons_organization_id ON contact_persons (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_properties_organization_id ON properties (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_contact ON properties (contact_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_org_type ON properties (organization_id, property_type)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_products_code ON products (code)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_product_org_type ON products (organization_id, product_type)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_products_organization_id ON products (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_interactions_organization_id ON interactions (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_interaction_contact_date ON interactions (contact_id, interaction_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_document_entity ON documents (entity_type, entity_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_documents_organization_id ON documents (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_profiles_organization_id ON energy_profiles (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_surface_calculations_organization_id ON surface_calculations (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_property_work_history_organization_id ON property_work_history (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_energy_measurements_organization_id ON energy_measurements (organization_id)""")

    # ── Indexes Pipeline ──

    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunities_organization_id ON opportunities (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_contact ON opportunities (contact_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_org_stage ON opportunities (organization_id, stage)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_opportunity_owner ON opportunities (owner_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_milestone_templates_organization_id ON milestone_templates (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_milestones_organization_id ON milestones (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_activity_owner_date ON activities (owner_id, scheduled_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_activity_org_date ON activities (organization_id, scheduled_date)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_activities_organization_id ON activities (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_offers_organization_id ON offers (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_offers_offer_number ON offers (offer_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_org_status ON offers (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_contact ON offers (contact_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_offer_line_items_organization_id ON offer_line_items (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contract_contact ON contracts (contact_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contracts_contract_number ON contracts (contract_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contracts_organization_id ON contracts (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_contract_org_status ON contracts (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_billing_schedules_organization_id ON billing_schedules (organization_id)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoices_invoice_number ON invoices (invoice_number)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoice_org_status ON invoices (organization_id, status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_invoices_organization_id ON invoices (organization_id)""")


def downgrade() -> None:
    """Drop CRM + Pipeline tables in reverse dependency order."""
    op.execute("DROP TABLE IF EXISTS invoices CASCADE")
    op.execute("DROP TABLE IF EXISTS billing_schedules CASCADE")
    op.execute("DROP TABLE IF EXISTS contracts CASCADE")
    op.execute("DROP TABLE IF EXISTS offer_line_items CASCADE")
    op.execute("DROP TABLE IF EXISTS offers CASCADE")
    op.execute("DROP TABLE IF EXISTS activities CASCADE")
    op.execute("DROP TABLE IF EXISTS milestone_dependencies CASCADE")
    op.execute("DROP TABLE IF EXISTS milestones CASCADE")
    op.execute("DROP TABLE IF EXISTS milestone_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS opportunities CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_measurements CASCADE")
    op.execute("DROP TABLE IF EXISTS property_work_history CASCADE")
    op.execute("DROP TABLE IF EXISTS surface_calculations CASCADE")
    op.execute("DROP TABLE IF EXISTS energy_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS documents CASCADE")
    op.execute("DROP TABLE IF EXISTS interactions CASCADE")
    op.execute("DROP TABLE IF EXISTS products CASCADE")
    op.execute("DROP TABLE IF EXISTS properties CASCADE")
    op.execute("DROP TABLE IF EXISTS contact_persons CASCADE")
    op.execute("DROP TABLE IF EXISTS contacts CASCADE")
