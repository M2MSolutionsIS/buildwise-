"""
CRM module router — F001–F005, F007, F010, F012, F016, F018.

Endpoints:
  # Contacts — F001, F003
  GET    /api/v1/crm/contacts                              — List contacts (search, filter, paginate)
  POST   /api/v1/crm/contacts                              — Create contact
  GET    /api/v1/crm/contacts/{id}                         — Get contact detail
  PUT    /api/v1/crm/contacts/{id}                         — Update contact
  DELETE /api/v1/crm/contacts/{id}                         — Soft-delete contact

  # F005: Duplicate Check
  POST   /api/v1/crm/contacts/check-duplicates             — Check for duplicates

  # Contact Persons — F001
  POST   /api/v1/crm/contacts/{id}/persons                 — Add person
  PUT    /api/v1/crm/contacts/{id}/persons/{pid}           — Update person
  DELETE /api/v1/crm/contacts/{id}/persons/{pid}           — Delete person

  # Interactions — F002
  GET    /api/v1/crm/contacts/{id}/interactions            — List interactions (timeline)
  POST   /api/v1/crm/contacts/{id}/interactions            — Create interaction

  # Properties — F010
  GET    /api/v1/crm/contacts/{id}/properties              — List properties for contact
  POST   /api/v1/crm/contacts/{id}/properties              — Create property
  GET    /api/v1/crm/properties/{id}                       — Get property detail
  PUT    /api/v1/crm/properties/{id}                       — Update property
  DELETE /api/v1/crm/properties/{id}                       — Delete property

  # Energy Profile — F012
  GET    /api/v1/crm/properties/{id}/energy-profile        — Get energy profile
  PUT    /api/v1/crm/properties/{id}/energy-profile        — Create/update energy profile
  POST   /api/v1/crm/energy/calculator                     — Energy savings calculator

  # Work History — F016
  GET    /api/v1/crm/properties/{id}/work-history          — List work history
  POST   /api/v1/crm/properties/{id}/work-history          — Add work history entry
  PUT    /api/v1/crm/work-history/{id}                     — Update entry
  DELETE /api/v1/crm/work-history/{id}                     — Delete entry

  # Product Categories — F007
  GET    /api/v1/crm/product-categories                    — List categories
  POST   /api/v1/crm/product-categories                    — Create category
  PUT    /api/v1/crm/product-categories/{id}               — Update category
  DELETE /api/v1/crm/product-categories/{id}               — Delete category

  # Products — F007
  GET    /api/v1/crm/products                              — List products
  POST   /api/v1/crm/products                              — Create product
  GET    /api/v1/crm/products/{id}                         — Get product detail
  PUT    /api/v1/crm/products/{id}                         — Update product
  DELETE /api/v1/crm/products/{id}                         — Delete product
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.crm import service
from app.crm.schemas import (
    ContactCreate,
    ContactListOut,
    ContactOut,
    ContactPersonCreate,
    ContactPersonOut,
    ContactPersonUpdate,
    ContactUpdate,
    DuplicateCheckResponse,
    DuplicateMatch,
    EnergyCalculatorRequest,
    EnergyCalculatorResponse,
    EnergyProfileCreate,
    EnergyProfileOut,
    EnergyProfileUpdate,
    InteractionCreate,
    InteractionOut,
    ProductCategoryCreate,
    ProductCategoryOut,
    ProductCategoryUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    PropertyCreate,
    PropertyListOut,
    PropertyOut,
    PropertyUpdate,
    WorkHistoryCreate,
    WorkHistoryOut,
    WorkHistoryUpdate,
)
from app.system.schemas import ApiResponse, Meta

crm_router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACTS — F001, F003
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/contacts", response_model=ApiResponse)
async def list_contacts(
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    stage: str | None = None,
    contact_type: str | None = None,
    # F018: segmentation filters
    city: str | None = None,
    county: str | None = None,
    source: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001/F018: List contacts with search, filter, segmentation, pagination."""
    contacts, total = await service.list_contacts(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        search=search,
        stage=stage,
        contact_type=contact_type,
        city=city,
        county=county,
        source=source,
    )
    return ApiResponse(
        data=[ContactListOut.model_validate(c) for c in contacts],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post("/contacts", response_model=ApiResponse, status_code=201)
async def create_contact(
    body: ContactCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Create a new contact."""
    req_info = await get_request_info(request)
    contact = await service.create_contact(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    # Re-fetch with persons
    contact = await service.get_contact(db, current_user.organization_id, contact.id)
    return ApiResponse(data=ContactOut.model_validate(contact))


@crm_router.get("/contacts/{contact_id}", response_model=ApiResponse)
async def get_contact(
    contact_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Get contact detail with persons."""
    contact = await service.get_contact(db, current_user.organization_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ApiResponse(data=ContactOut.model_validate(contact))


@crm_router.put("/contacts/{contact_id}", response_model=ApiResponse)
async def update_contact(
    contact_id: uuid.UUID,
    body: ContactUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Update a contact."""
    req_info = await get_request_info(request)
    contact = await service.update_contact(
        db,
        current_user.organization_id,
        current_user.id,
        contact_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact = await service.get_contact(db, current_user.organization_id, contact_id)
    return ApiResponse(data=ContactOut.model_validate(contact))


@crm_router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Soft-delete a contact."""
    req_info = await get_request_info(request)
    deleted = await service.delete_contact(
        db,
        current_user.organization_id,
        current_user.id,
        contact_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")


# ═══════════════════════════════════════════════════════════════════════════════
# F005: DUPLICATE CHECK
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.post("/contacts/check-duplicates", response_model=ApiResponse)
async def check_duplicates(
    body: ContactCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F005: Check for duplicate contacts by CUI, email, phone."""
    matches = await service.check_duplicates(
        db,
        current_user.organization_id,
        cui=body.cui,
        email=str(body.email) if body.email else None,
        phone=body.phone,
    )
    return ApiResponse(
        data=DuplicateCheckResponse(
            has_duplicates=len(matches) > 0,
            matches=[DuplicateMatch(**m) for m in matches],
        )
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACT PERSONS — F001
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.post(
    "/contacts/{contact_id}/persons",
    response_model=ApiResponse,
    status_code=201,
)
async def add_person(
    contact_id: uuid.UUID,
    body: ContactPersonCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Add a person to a contact."""
    person = await service.add_contact_person(
        db,
        current_user.organization_id,
        current_user.id,
        contact_id,
        body.model_dump(),
    )
    if person is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ApiResponse(data=ContactPersonOut.model_validate(person))


@crm_router.put(
    "/contacts/{contact_id}/persons/{person_id}",
    response_model=ApiResponse,
)
async def update_person(
    contact_id: uuid.UUID,
    person_id: uuid.UUID,
    body: ContactPersonUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Update a contact person."""
    person = await service.update_contact_person(
        db,
        current_user.organization_id,
        contact_id,
        person_id,
        body.model_dump(exclude_unset=True),
    )
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return ApiResponse(data=ContactPersonOut.model_validate(person))


@crm_router.delete(
    "/contacts/{contact_id}/persons/{person_id}",
    status_code=204,
)
async def delete_person(
    contact_id: uuid.UUID,
    person_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: Delete a contact person."""
    deleted = await service.delete_contact_person(
        db,
        current_user.organization_id,
        contact_id,
        person_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")


# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIONS — F002
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get(
    "/contacts/{contact_id}/interactions",
    response_model=ApiResponse,
)
async def list_interactions(
    contact_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
    interaction_type: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F002: List interactions for a contact (timeline)."""
    interactions, total = await service.list_interactions(
        db,
        current_user.organization_id,
        contact_id,
        page=page,
        per_page=per_page,
        interaction_type=interaction_type,
    )
    return ApiResponse(
        data=[InteractionOut.model_validate(i) for i in interactions],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post(
    "/contacts/{contact_id}/interactions",
    response_model=ApiResponse,
    status_code=201,
)
async def create_interaction(
    contact_id: uuid.UUID,
    body: InteractionCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F002: Create an interaction for a contact."""
    # Verify contact exists
    contact = await service.get_contact(db, current_user.organization_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    req_info = await get_request_info(request)
    interaction = await service.create_interaction(
        db,
        current_user.organization_id,
        current_user.id,
        contact_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=InteractionOut.model_validate(interaction))


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTIES — F010
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get(
    "/contacts/{contact_id}/properties",
    response_model=ApiResponse,
)
async def list_properties(
    contact_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
    property_type: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F010: List properties for a contact."""
    properties, total = await service.list_properties(
        db,
        current_user.organization_id,
        contact_id,
        page=page,
        per_page=per_page,
        property_type=property_type,
    )
    return ApiResponse(
        data=[PropertyListOut.model_validate(p) for p in properties],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post(
    "/contacts/{contact_id}/properties",
    response_model=ApiResponse,
    status_code=201,
)
async def create_property(
    contact_id: uuid.UUID,
    body: PropertyCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F010: Create a property for a contact."""
    # Verify contact exists
    contact = await service.get_contact(db, current_user.organization_id, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    data = body.model_dump(exclude_unset=True)
    data["contact_id"] = contact_id  # Override from URL

    req_info = await get_request_info(request)
    prop = await service.create_property(
        db,
        current_user.organization_id,
        current_user.id,
        data,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=PropertyOut.model_validate(prop))


@crm_router.get("/properties/{property_id}", response_model=ApiResponse)
async def get_property(
    property_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F010: Get property detail with energy profile and work history."""
    prop = await service.get_property(
        db, current_user.organization_id, property_id
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return ApiResponse(data=PropertyOut.model_validate(prop))


@crm_router.put("/properties/{property_id}", response_model=ApiResponse)
async def update_property(
    property_id: uuid.UUID,
    body: PropertyUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F010: Update a property."""
    req_info = await get_request_info(request)
    prop = await service.update_property(
        db,
        current_user.organization_id,
        current_user.id,
        property_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")
    prop = await service.get_property(db, current_user.organization_id, property_id)
    return ApiResponse(data=PropertyOut.model_validate(prop))


@crm_router.delete("/properties/{property_id}", status_code=204)
async def delete_property(
    property_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F010: Soft-delete a property."""
    req_info = await get_request_info(request)
    deleted = await service.delete_property(
        db,
        current_user.organization_id,
        current_user.id,
        property_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Property not found")


# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY PROFILE — F012
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get(
    "/properties/{property_id}/energy-profile",
    response_model=ApiResponse,
)
async def get_energy_profile(
    property_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F012: Get energy profile for a property."""
    # Verify property exists
    prop = await service.get_property(
        db, current_user.organization_id, property_id
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    profile = await service.get_energy_profile(
        db, current_user.organization_id, property_id
    )
    if profile is None:
        return ApiResponse(data=None)
    return ApiResponse(data=EnergyProfileOut.model_validate(profile))


@crm_router.put(
    "/properties/{property_id}/energy-profile",
    response_model=ApiResponse,
)
async def upsert_energy_profile(
    property_id: uuid.UUID,
    body: EnergyProfileCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F012: Create or update energy profile for a property."""
    # Verify property exists
    prop = await service.get_property(
        db, current_user.organization_id, property_id
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    req_info = await get_request_info(request)
    profile = await service.create_or_update_energy_profile(
        db,
        current_user.organization_id,
        current_user.id,
        property_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=EnergyProfileOut.model_validate(profile))


@crm_router.post("/energy/calculator", response_model=ApiResponse)
async def energy_calculator(
    body: EnergyCalculatorRequest,
    current_user=Depends(get_current_user),
):
    """F012: Energy savings calculator."""
    result = service.calculate_energy_savings(
        total_area_sqm=body.total_area_sqm,
        u_value_current=body.u_value_current,
        u_value_proposed=body.u_value_proposed,
        heating_degree_days=body.heating_degree_days,
    )
    return ApiResponse(data=EnergyCalculatorResponse(**result))


# ═══════════════════════════════════════════════════════════════════════════════
# WORK HISTORY — F016
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get(
    "/properties/{property_id}/work-history",
    response_model=ApiResponse,
)
async def list_work_history(
    property_id: uuid.UUID,
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F016: List work history for a property."""
    prop = await service.get_property(
        db, current_user.organization_id, property_id
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    entries, total = await service.list_work_history(
        db,
        current_user.organization_id,
        property_id,
        page=page,
        per_page=per_page,
    )
    return ApiResponse(
        data=[WorkHistoryOut.model_validate(e) for e in entries],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post(
    "/properties/{property_id}/work-history",
    response_model=ApiResponse,
    status_code=201,
)
async def create_work_history(
    property_id: uuid.UUID,
    body: WorkHistoryCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F016: Add a work history entry for a property."""
    prop = await service.get_property(
        db, current_user.organization_id, property_id
    )
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    req_info = await get_request_info(request)
    entry = await service.create_work_history(
        db,
        current_user.organization_id,
        current_user.id,
        property_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=WorkHistoryOut.model_validate(entry))


@crm_router.put("/work-history/{entry_id}", response_model=ApiResponse)
async def update_work_history(
    entry_id: uuid.UUID,
    body: WorkHistoryUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F016: Update a work history entry."""
    req_info = await get_request_info(request)
    entry = await service.update_work_history(
        db,
        current_user.organization_id,
        current_user.id,
        entry_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Work history entry not found")
    return ApiResponse(data=WorkHistoryOut.model_validate(entry))


@crm_router.delete("/work-history/{entry_id}", status_code=204)
async def delete_work_history(
    entry_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F016: Delete a work history entry."""
    req_info = await get_request_info(request)
    deleted = await service.delete_work_history(
        db,
        current_user.organization_id,
        current_user.id,
        entry_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Work history entry not found")


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT CATEGORIES — F007
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/product-categories", response_model=ApiResponse)
async def list_product_categories(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: List product categories."""
    categories = await service.list_product_categories(
        db, current_user.organization_id
    )
    return ApiResponse(
        data=[ProductCategoryOut.model_validate(c) for c in categories],
        meta=Meta(total=len(categories)),
    )


@crm_router.post(
    "/product-categories",
    response_model=ApiResponse,
    status_code=201,
)
async def create_product_category(
    body: ProductCategoryCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Create a product category."""
    cat = await service.create_product_category(
        db, current_user.organization_id, body.model_dump()
    )
    return ApiResponse(data=ProductCategoryOut.model_validate(cat))


@crm_router.put("/product-categories/{cat_id}", response_model=ApiResponse)
async def update_product_category(
    cat_id: uuid.UUID,
    body: ProductCategoryUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Update a product category."""
    cat = await service.update_product_category(
        db, current_user.organization_id, cat_id, body.model_dump(exclude_unset=True)
    )
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return ApiResponse(data=ProductCategoryOut.model_validate(cat))


@crm_router.delete("/product-categories/{cat_id}", status_code=204)
async def delete_product_category(
    cat_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Delete a product category (only if no products)."""
    deleted = await service.delete_product_category(
        db, current_user.organization_id, cat_id
    )
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Category not found or has products attached",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTS — F007
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/products", response_model=ApiResponse)
async def list_products(
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
    product_type: str | None = None,
    category_id: uuid.UUID | None = None,
    parent_only: bool = False,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: List products/services catalog."""
    products, total = await service.list_products(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        search=search,
        product_type=product_type,
        category_id=category_id,
        parent_only=parent_only,
    )
    return ApiResponse(
        data=[ProductOut.model_validate(p) for p in products],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post("/products", response_model=ApiResponse, status_code=201)
async def create_product(
    body: ProductCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Create a product/article."""
    req_info = await get_request_info(request)
    product = await service.create_product(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ProductOut.model_validate(product))


@crm_router.get("/products/{product_id}", response_model=ApiResponse)
async def get_product(
    product_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Get product detail with sub-products."""
    product = await service.get_product(
        db, current_user.organization_id, product_id
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ApiResponse(data=ProductOut.model_validate(product))


@crm_router.put("/products/{product_id}", response_model=ApiResponse)
async def update_product(
    product_id: uuid.UUID,
    body: ProductUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Update a product."""
    req_info = await get_request_info(request)
    product = await service.update_product(
        db,
        current_user.organization_id,
        current_user.id,
        product_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ApiResponse(data=ProductOut.model_validate(product))


@crm_router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F007: Soft-delete a product."""
    req_info = await get_request_info(request)
    deleted = await service.delete_product(
        db,
        current_user.organization_id,
        current_user.id,
        product_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
