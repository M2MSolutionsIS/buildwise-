"""
CRM module models — F001–F005, F007, F010, F012, F016, F018.

Covers: Contacts, Contact Persons, Interaction History, Properties/Assets,
Energy Profiles, Products & Services catalog, Documents.
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
    NoteMixin,
    OrgMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.database import Base

import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class ContactStage(str, enum.Enum):
    PROSPECT = "prospect"
    POTENTIAL_CLIENT = "potential_client"
    ACTIVE = "active"
    INACTIVE = "inactive"
    PARTNER = "partner"


class ContactType(str, enum.Enum):
    PF = "pf"          # Persoana fizică
    IMM = "imm"        # IMM
    PJ = "pj"          # Persoana juridică
    CORPORATION = "corporation"


class InteractionType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    OFFER = "offer"
    CONTRACT = "contract"
    NOTE = "note"
    VISIT = "visit"


class PropertyType(str, enum.Enum):
    BLOC_PANOU = "bloc_panou_prefabricat"
    BLOC_CARAMIDA = "bloc_caramida"
    CASA_INTERBELICA = "casa_interbelica"
    CASA_POST_1990 = "casa_post_1990"
    SPATIU_INDUSTRIAL = "spatiu_industrial"
    CLADIRE_COMERCIALA = "cladire_comerciala"
    CLADIRE_PUBLICA = "cladire_publica"
    OTHER = "other"


class ProductCategory(str, enum.Enum):
    PRODUCT = "product"
    SERVICE = "service"
    REVENUE = "revenue"
    EXPENSE = "expense"


class DocumentCategory(str, enum.Enum):
    CERTIFICATE = "certificate"
    PHOTO = "photo"
    TECHNICAL = "technical"
    CONTRACT = "contract"
    OFFER = "offer"
    INVOICE = "invoice"
    OTHER = "other"


# ─── Contact — F001, F003, F004, F005 ────────────────────────────────────────

class Contact(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Main contact/company entity.
    F001: CRUD contacts (name, address, CUI, fiscal data).
    F003: Classification by stage + typology.
    F004: Import/Export/Merge.
    F005: Duplicate validation (email, CUI, phone).
    """
    __tablename__ = "contacts"

    # Core data
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cui: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    registration_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Classification — F003
    stage: Mapped[str] = mapped_column(
        Enum(ContactStage), default=ContactStage.PROSPECT, nullable=False
    )
    contact_type: Mapped[str] = mapped_column(
        Enum(ContactType), default=ContactType.PJ, nullable=False
    )

    # Address
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="Romania", nullable=False)

    # Contact info
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Fiscal data
    vat_payer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bank_account: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # GDPR
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gdpr_consent_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Segmentation — F018
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    custom_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Duplicate tracking — F005
    is_duplicate_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    merged_from_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Source tracking
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    persons = relationship("ContactPerson", back_populates="contact", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="contact", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="contact", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="contact")

    __table_args__ = (
        Index("ix_contact_org_stage", "organization_id", "stage"),
        Index("ix_contact_org_type", "organization_id", "contact_type"),
    )


# ─── Contact Person — F001, F003 ─────────────────────────────────────────────

class ContactPerson(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin):
    """
    Individual persons within a contact/company.
    """
    __tablename__ = "contact_persons"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    contact = relationship("Contact", back_populates="persons")


# ─── Interaction History — F002, F005 ─────────────────────────────────────────

class Interaction(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Timeline of interactions with a contact.
    F002: Istoric interacțiuni per contact.
    """
    __tablename__ = "interactions"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(Enum(InteractionType), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Link to other entities
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    offer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # User who logged this
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    contact = relationship("Contact", back_populates="interactions")

    __table_args__ = (
        Index("ix_interaction_contact_date", "contact_id", "interaction_date"),
    )


# ─── Property / Asset — F010 ─────────────────────────────────────────────────

class Property(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Property/Asset profile linked to a contact.
    F010: Property Profile — address, surface, year, type, materials, certifications.
    """
    __tablename__ = "properties"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(
        Enum(PropertyType), default=PropertyType.OTHER, nullable=False
    )

    # Address
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="Romania", nullable=False)

    # Physical specs
    total_area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    heated_area_sqm: Mapped[float | None] = mapped_column(Float, nullable=True)
    floors_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_renovated: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Construction
    structure_material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    facade_material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    roof_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Certifications
    energy_certificate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    energy_class: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Flexible fields
    custom_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    contact = relationship("Contact", back_populates="properties")
    energy_profile = relationship("EnergyProfile", back_populates="property", uselist=False)
    work_history = relationship("PropertyWorkHistory", back_populates="property")
    documents = relationship("Document", back_populates="property")
    surface_calculations = relationship("SurfaceCalculation", back_populates="property")

    __table_args__ = (
        Index("ix_property_contact", "contact_id"),
        Index("ix_property_org_type", "organization_id", "property_type"),
    )


# ─── Energy Profile — F012 (P1 core, common to all) ──────────────────────────

class EnergyProfile(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Energy-specific parameters per property.
    F012: Energy Profile — U-value, HVAC, calculator, consumption estimates.
    This is the core differentiator for P1 (BuildWise TRL5).
    """
    __tablename__ = "energy_profiles"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), unique=True, nullable=False
    )

    # Thermal coefficients
    u_value_walls: Mapped[float | None] = mapped_column(Float, nullable=True)
    u_value_roof: Mapped[float | None] = mapped_column(Float, nullable=True)
    u_value_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    u_value_windows: Mapped[float | None] = mapped_column(Float, nullable=True)
    u_value_doors: Mapped[float | None] = mapped_column(Float, nullable=True)
    # BAHM special: 0.3 W/m²K for treated glass
    u_value_treated_glass: Mapped[float | None] = mapped_column(Float, nullable=True)

    # HVAC — F012
    hvac_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hvac_capacity_kw: Mapped[float | None] = mapped_column(Float, nullable=True)
    hvac_efficiency: Mapped[float | None] = mapped_column(Float, nullable=True)
    hvac_year_installed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heating_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cooling_source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Consumption estimates
    annual_consumption_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_consumption_gas_mc: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_savings_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_co2_reduction_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Climate zone
    climate_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Extended data
    extended_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    property = relationship("Property", back_populates="energy_profile")
    measurements = relationship("EnergyMeasurement", back_populates="energy_profile")


class EnergyMeasurement(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Historical energy measurements (PRE/POST intervention).
    Part of F012 and linked to F088 (Energy Impact) in PM module.
    """
    __tablename__ = "energy_measurements"

    energy_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("energy_profiles.id"), nullable=False
    )
    measurement_type: Mapped[str] = mapped_column(String(10), nullable=False)  # PRE or POST
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    measured_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    energy_profile = relationship("EnergyProfile", back_populates="measurements")


# ─── Surface Calculator — F018 ───────────────────────────────────────────────

class SurfaceCalculation(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Dynamic surface area calculations per property (levels × surfaces).
    F018: Calculator suprafețe.
    """
    __tablename__ = "surface_calculations"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    floor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    surface_type: Mapped[str] = mapped_column(String(50), nullable=False)  # wall, window, floor, roof
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    u_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    property = relationship("Property", back_populates="surface_calculations")


# ─── Property Work History — F016 ────────────────────────────────────────────

class PropertyWorkHistory(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Historic interventions/works on a property.
    F016: Istoric lucrări + documente per proprietate.
    """
    __tablename__ = "property_work_history"

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    work_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    property = relationship("Property", back_populates="work_history")


# ─── Products & Services Catalog — F007 ──────────────────────────────────────

class ProductCategory_DB(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Hierarchical product categories.
    """
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    children = relationship("ProductCategory_DB", back_populates="parent")
    parent = relationship("ProductCategory_DB", back_populates="children", remote_side="ProductCategory_DB.id")
    products = relationship("Product", back_populates="category")


class Product(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin):
    """
    Products and services catalog.
    F007: Nomenclator ierarhic. CRUD articole + sub-articole.
    """
    __tablename__ = "products"

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_type: Mapped[str] = mapped_column(
        Enum(ProductCategory), default=ProductCategory.PRODUCT, nullable=False
    )
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="buc", nullable=False)
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    vat_rate: Mapped[float] = mapped_column(Float, default=0.19, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Sub-article parent reference
    parent_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )

    # Price history stored as JSON
    price_history: Mapped[list | None] = mapped_column(JSON, nullable=True)

    category = relationship("ProductCategory_DB", back_populates="products")
    sub_products = relationship("Product", back_populates="parent_product")
    parent_product = relationship("Product", back_populates="sub_products", remote_side="Product.id")

    __table_args__ = (
        Index("ix_product_org_type", "organization_id", "product_type"),
    )


# ─── Document — F005, F016 ───────────────────────────────────────────────────

class Document(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    File/document storage metadata. Can be attached to contacts, properties, projects, etc.
    """
    __tablename__ = "documents"

    # Polymorphic link
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # contact, property, project...
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Explicit FK for common associations
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )
    property_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True
    )

    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(
        Enum(DocumentCategory), default=DocumentCategory.OTHER, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    contact = relationship("Contact", back_populates="documents")
    property = relationship("Property", back_populates="documents")

    __table_args__ = (
        Index("ix_document_entity", "entity_type", "entity_id"),
    )
