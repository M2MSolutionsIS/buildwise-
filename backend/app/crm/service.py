"""
CRM module service layer — F001–F005, F007, F010, F012, F016, F018.

CRUD operations for Contacts, Interactions, Products, Properties,
EnergyProfiles, PropertyWorkHistory.
All operations include audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.crm.models import (
    Contact,
    ContactPerson,
    ContactStage,
    ContactType,
    Document,
    EnergyProfile,
    Interaction,
    InteractionType,
    Product,
    ProductCategory as ProductCategoryEnum,
    ProductCategory_DB,
    Property,
    PropertyWorkHistory,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACTS — F001, F003
# ═══════════════════════════════════════════════════════════════════════════════


async def list_contacts(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    stage: str | None = None,
    contact_type: str | None = None,
    # F018: Multi-criteria segmentation filters
    city: str | None = None,
    county: str | None = None,
    tags: list[str] | None = None,
    source: str | None = None,
) -> tuple[list[Contact], int]:
    """List contacts with pagination, search, and filtering."""
    query = select(Contact).where(
        Contact.organization_id == org_id,
        Contact.is_deleted.is_(False),
    )

    if search:
        pattern = f"%{search}%"
        query = query.where(
            Contact.company_name.ilike(pattern)
            | Contact.cui.ilike(pattern)
            | Contact.email.ilike(pattern)
            | Contact.phone.ilike(pattern)
        )
    if stage:
        query = query.where(Contact.stage == stage)
    if contact_type:
        query = query.where(Contact.contact_type == contact_type)

    # F018: Multi-criteria segmentation
    if city:
        query = query.where(Contact.city.ilike(f"%{city}%"))
    if county:
        query = query.where(Contact.county.ilike(f"%{county}%"))
    if source:
        query = query.where(Contact.source == source)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Contact.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_contact(
    db: AsyncSession, org_id: uuid.UUID, contact_id: uuid.UUID
) -> Contact | None:
    """Get a single contact with persons."""
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.persons))
        .where(
            Contact.id == contact_id,
            Contact.organization_id == org_id,
            Contact.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def check_duplicates(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    cui: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    exclude_id: uuid.UUID | None = None,
) -> list[dict]:
    """F005: Check for duplicate contacts by CUI, email, or phone."""
    matches = []

    for field_name, field_value, column in [
        ("cui", cui, Contact.cui),
        ("email", email, Contact.email),
        ("phone", phone, Contact.phone),
    ]:
        if not field_value:
            continue
        query = select(Contact).where(
            Contact.organization_id == org_id,
            Contact.is_deleted.is_(False),
            column == field_value,
        )
        if exclude_id:
            query = query.where(Contact.id != exclude_id)
        result = await db.execute(query)
        for contact in result.scalars().all():
            matches.append({
                "id": contact.id,
                "company_name": contact.company_name,
                "cui": contact.cui,
                "email": contact.email,
                "phone": contact.phone,
                "match_field": field_name,
                "match_value": field_value,
            })

    return matches


async def create_contact(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contact:
    """F001: Create a new contact."""
    persons_data = data.pop("persons", None) or []

    # F003: GDPR consent date
    if data.get("gdpr_consent"):
        data["gdpr_consent_date"] = datetime.now(timezone.utc)

    contact = Contact(
        id=uuid.uuid4(),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(contact)
    await db.flush()

    for p in persons_data:
        person = ContactPerson(
            id=uuid.uuid4(),
            contact_id=contact.id,
            organization_id=org_id,
            **p,
        )
        db.add(person)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="contacts",
        entity_id=contact.id,
        new_values=model_to_dict(contact),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contact


async def update_contact(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contact_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contact | None:
    """F001: Update a contact."""
    contact = await get_contact(db, org_id, contact_id)
    if contact is None:
        return None

    old_values = model_to_dict(contact)

    # F003: Update GDPR consent date if consent changes
    if data.get("gdpr_consent") and not contact.gdpr_consent:
        data["gdpr_consent_date"] = datetime.now(timezone.utc)

    for key, val in data.items():
        if val is not None:
            setattr(contact, key, val)
    contact.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="contacts",
        entity_id=contact.id,
        old_values=old_values,
        new_values=model_to_dict(contact),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contact


async def delete_contact(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contact_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """F001: Soft-delete a contact."""
    contact = await get_contact(db, org_id, contact_id)
    if contact is None:
        return False

    old_values = model_to_dict(contact)
    contact.is_deleted = True
    contact.deleted_at = datetime.now(timezone.utc)
    contact.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="contacts",
        entity_id=contact.id,
        old_values=old_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACT PERSONS — F001
# ═══════════════════════════════════════════════════════════════════════════════


async def add_contact_person(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contact_id: uuid.UUID,
    data: dict,
) -> ContactPerson | None:
    """Add a person to a contact."""
    contact = await get_contact(db, org_id, contact_id)
    if contact is None:
        return None

    person = ContactPerson(
        id=uuid.uuid4(),
        contact_id=contact_id,
        organization_id=org_id,
        **data,
    )
    db.add(person)
    await db.flush()
    return person


async def update_contact_person(
    db: AsyncSession,
    org_id: uuid.UUID,
    contact_id: uuid.UUID,
    person_id: uuid.UUID,
    data: dict,
) -> ContactPerson | None:
    """Update a contact person."""
    result = await db.execute(
        select(ContactPerson).where(
            ContactPerson.id == person_id,
            ContactPerson.contact_id == contact_id,
            ContactPerson.organization_id == org_id,
            ContactPerson.is_deleted.is_(False),
        )
    )
    person = result.scalar_one_or_none()
    if person is None:
        return None
    for key, val in data.items():
        if val is not None:
            setattr(person, key, val)
    await db.flush()
    return person


async def delete_contact_person(
    db: AsyncSession,
    org_id: uuid.UUID,
    contact_id: uuid.UUID,
    person_id: uuid.UUID,
) -> bool:
    """Delete a contact person."""
    result = await db.execute(
        select(ContactPerson).where(
            ContactPerson.id == person_id,
            ContactPerson.contact_id == contact_id,
            ContactPerson.organization_id == org_id,
            ContactPerson.is_deleted.is_(False),
        )
    )
    person = result.scalar_one_or_none()
    if person is None:
        return False
    person.is_deleted = True
    person.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIONS — F002
# ═══════════════════════════════════════════════════════════════════════════════


async def list_interactions(
    db: AsyncSession,
    org_id: uuid.UUID,
    contact_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    interaction_type: str | None = None,
) -> tuple[list[Interaction], int]:
    """List interactions for a contact (timeline)."""
    query = select(Interaction).where(
        Interaction.contact_id == contact_id,
        Interaction.organization_id == org_id,
    )
    if interaction_type:
        query = query.where(Interaction.interaction_type == interaction_type)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Interaction.interaction_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_interaction(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contact_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Interaction:
    """Create a new interaction for a contact."""
    interaction = Interaction(
        id=uuid.uuid4(),
        contact_id=contact_id,
        organization_id=org_id,
        user_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(interaction)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="interactions",
        entity_id=interaction.id,
        new_values=model_to_dict(interaction),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return interaction


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT CATEGORIES — F007
# ═══════════════════════════════════════════════════════════════════════════════


async def list_product_categories(
    db: AsyncSession, org_id: uuid.UUID
) -> list[ProductCategory_DB]:
    """List all product categories for an org."""
    result = await db.execute(
        select(ProductCategory_DB)
        .where(ProductCategory_DB.organization_id == org_id)
        .order_by(ProductCategory_DB.sort_order, ProductCategory_DB.name)
    )
    return result.scalars().all()


async def create_product_category(
    db: AsyncSession, org_id: uuid.UUID, data: dict
) -> ProductCategory_DB:
    """Create a product category."""
    cat = ProductCategory_DB(
        id=uuid.uuid4(),
        organization_id=org_id,
        **data,
    )
    db.add(cat)
    await db.flush()
    return cat


async def update_product_category(
    db: AsyncSession, org_id: uuid.UUID, cat_id: uuid.UUID, data: dict
) -> ProductCategory_DB | None:
    """Update a product category."""
    result = await db.execute(
        select(ProductCategory_DB).where(
            ProductCategory_DB.id == cat_id,
            ProductCategory_DB.organization_id == org_id,
        )
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        return None
    for key, val in data.items():
        if val is not None:
            setattr(cat, key, val)
    await db.flush()
    return cat


async def delete_product_category(
    db: AsyncSession, org_id: uuid.UUID, cat_id: uuid.UUID
) -> bool:
    """Delete a product category (hard delete, only if no products)."""
    result = await db.execute(
        select(ProductCategory_DB).where(
            ProductCategory_DB.id == cat_id,
            ProductCategory_DB.organization_id == org_id,
        )
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        return False

    # Check if products exist
    prod_count = await db.execute(
        select(func.count()).select_from(Product).where(Product.category_id == cat_id)
    )
    if prod_count.scalar() > 0:
        return False

    await db.delete(cat)
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTS — F007
# ═══════════════════════════════════════════════════════════════════════════════


async def list_products(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    product_type: str | None = None,
    category_id: uuid.UUID | None = None,
    parent_only: bool = False,
) -> tuple[list[Product], int]:
    """List products with pagination and filtering."""
    query = select(Product).where(
        Product.organization_id == org_id,
        Product.is_deleted.is_(False),
    )
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Product.name.ilike(pattern)
            | Product.code.ilike(pattern)
            | Product.description.ilike(pattern)
        )
    if product_type:
        query = query.where(Product.product_type == product_type)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if parent_only:
        query = query.where(Product.parent_product_id.is_(None))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Product.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_product(
    db: AsyncSession, org_id: uuid.UUID, product_id: uuid.UUID
) -> Product | None:
    """Get a single product with sub-products."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.sub_products))
        .where(
            Product.id == product_id,
            Product.organization_id == org_id,
            Product.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_product(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Product:
    """Create a product/service/article."""
    product = Product(
        id=uuid.uuid4(),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(product)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="products",
        entity_id=product.id,
        new_values=model_to_dict(product),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return product


async def update_product(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Product | None:
    """Update a product."""
    product = await get_product(db, org_id, product_id)
    if product is None:
        return None

    old_values = model_to_dict(product)

    # Track price history
    if "unit_price" in data and data["unit_price"] != product.unit_price:
        history = product.price_history or []
        history.append({
            "price": product.unit_price,
            "currency": product.currency,
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "changed_by": str(user_id),
        })
        product.price_history = history

    for key, val in data.items():
        if val is not None:
            setattr(product, key, val)
    product.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="products",
        entity_id=product.id,
        old_values=old_values,
        new_values=model_to_dict(product),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return product


async def delete_product(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """Soft-delete a product."""
    product = await get_product(db, org_id, product_id)
    if product is None:
        return False

    old_values = model_to_dict(product)
    product.is_deleted = True
    product.deleted_at = datetime.now(timezone.utc)
    product.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="products",
        entity_id=product.id,
        old_values=old_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTIES — F010
# ═══════════════════════════════════════════════════════════════════════════════


async def list_properties(
    db: AsyncSession,
    org_id: uuid.UUID,
    contact_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    property_type: str | None = None,
) -> tuple[list[Property], int]:
    """F010: List properties for a contact."""
    query = select(Property).where(
        Property.contact_id == contact_id,
        Property.organization_id == org_id,
        Property.is_deleted.is_(False),
    )
    if property_type:
        query = query.where(Property.property_type == property_type)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Property.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_property(
    db: AsyncSession, org_id: uuid.UUID, property_id: uuid.UUID
) -> Property | None:
    """F010: Get a single property with energy profile and work history."""
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.energy_profile),
            selectinload(Property.work_history),
        )
        .where(
            Property.id == property_id,
            Property.organization_id == org_id,
            Property.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_property(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Property:
    """F010: Create a property profile."""
    prop = Property(
        id=uuid.uuid4(),
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(prop)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="properties",
        entity_id=prop.id,
        new_values=model_to_dict(prop),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return prop


async def update_property(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    property_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Property | None:
    """F010: Update a property."""
    prop = await get_property(db, org_id, property_id)
    if prop is None:
        return None

    old_values = model_to_dict(prop)
    for key, val in data.items():
        if val is not None:
            setattr(prop, key, val)
    prop.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="properties",
        entity_id=prop.id,
        old_values=old_values,
        new_values=model_to_dict(prop),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return prop


async def delete_property(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    property_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """F010: Soft-delete a property."""
    prop = await get_property(db, org_id, property_id)
    if prop is None:
        return False

    old_values = model_to_dict(prop)
    prop.is_deleted = True
    prop.deleted_at = datetime.now(timezone.utc)
    prop.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="properties",
        entity_id=prop.id,
        old_values=old_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY PROFILE — F012
# ═══════════════════════════════════════════════════════════════════════════════


async def get_energy_profile(
    db: AsyncSession, org_id: uuid.UUID, property_id: uuid.UUID
) -> EnergyProfile | None:
    """F012: Get energy profile for a property."""
    result = await db.execute(
        select(EnergyProfile).where(
            EnergyProfile.property_id == property_id,
            EnergyProfile.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def create_or_update_energy_profile(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    property_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> EnergyProfile:
    """F012: Create or update energy profile for a property."""
    existing = await get_energy_profile(db, org_id, property_id)

    if existing:
        old_values = model_to_dict(existing)
        for key, val in data.items():
            if val is not None:
                setattr(existing, key, val)
        existing.updated_by = user_id

        await log_audit(
            db,
            user_id=user_id,
            organization_id=org_id,
            action="UPDATE",
            entity_type="energy_profiles",
            entity_id=existing.id,
            old_values=old_values,
            new_values=model_to_dict(existing),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await db.flush()
        return existing

    profile = EnergyProfile(
        id=uuid.uuid4(),
        property_id=property_id,
        organization_id=org_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(profile)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="energy_profiles",
        entity_id=profile.id,
        new_values=model_to_dict(profile),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return profile


def calculate_energy_savings(
    total_area_sqm: float,
    u_value_current: float,
    u_value_proposed: float,
    heating_degree_days: float = 3000.0,
) -> dict:
    """F012: Simple energy savings calculator.

    Formula: Q = U * A * HDD * 24 / 1000 (kWh/year)
    CO2 factor: 0.233 kg CO2/kWh (Romania grid average)
    """
    current_loss = u_value_current * total_area_sqm * heating_degree_days * 24 / 1000
    proposed_loss = u_value_proposed * total_area_sqm * heating_degree_days * 24 / 1000
    savings = current_loss - proposed_loss
    savings_pct = (savings / current_loss * 100) if current_loss > 0 else 0.0
    co2_reduction = savings * 0.233

    return {
        "current_loss_kwh": round(current_loss, 2),
        "proposed_loss_kwh": round(proposed_loss, 2),
        "savings_kwh": round(savings, 2),
        "savings_percent": round(savings_pct, 2),
        "estimated_co2_reduction_kg": round(co2_reduction, 2),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTY WORK HISTORY — F016
# ═══════════════════════════════════════════════════════════════════════════════


async def list_work_history(
    db: AsyncSession,
    org_id: uuid.UUID,
    property_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[PropertyWorkHistory], int]:
    """F016: List work history for a property."""
    query = select(PropertyWorkHistory).where(
        PropertyWorkHistory.property_id == property_id,
        PropertyWorkHistory.organization_id == org_id,
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(PropertyWorkHistory.start_date.desc().nulls_last())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def create_work_history(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    property_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PropertyWorkHistory:
    """F016: Add work history entry for a property."""
    entry = PropertyWorkHistory(
        id=uuid.uuid4(),
        property_id=property_id,
        organization_id=org_id,
        **data,
    )
    db.add(entry)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="property_work_history",
        entity_id=entry.id,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


async def update_work_history(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> PropertyWorkHistory | None:
    """F016: Update a work history entry."""
    result = await db.execute(
        select(PropertyWorkHistory).where(
            PropertyWorkHistory.id == entry_id,
            PropertyWorkHistory.organization_id == org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return None

    old_values = model_to_dict(entry)
    for key, val in data.items():
        if val is not None:
            setattr(entry, key, val)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="property_work_history",
        entity_id=entry.id,
        old_values=old_values,
        new_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return entry


async def delete_work_history(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """F016: Delete a work history entry."""
    result = await db.execute(
        select(PropertyWorkHistory).where(
            PropertyWorkHistory.id == entry_id,
            PropertyWorkHistory.organization_id == org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        return False

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="property_work_history",
        entity_id=entry.id,
        old_values=model_to_dict(entry),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.delete(entry)
    await db.flush()
    return True
