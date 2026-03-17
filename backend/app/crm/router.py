"""
CRM module router — F001–F024.

Endpoints:
  # Contacts — F001, F003
  GET    /api/v1/crm/contacts                    — List contacts (search, filter, paginate)
  POST   /api/v1/crm/contacts                    — Create contact
  GET    /api/v1/crm/contacts/{id}               — Get contact detail
  PUT    /api/v1/crm/contacts/{id}               — Update contact
  DELETE /api/v1/crm/contacts/{id}               — Soft-delete contact

  # Contact Persons — F001
  POST   /api/v1/crm/contacts/{id}/persons       — Add person
  PUT    /api/v1/crm/contacts/{id}/persons/{pid}  — Update person
  DELETE /api/v1/crm/contacts/{id}/persons/{pid}  — Delete person

  # Interactions — F002
  GET    /api/v1/crm/contacts/{id}/interactions   — List interactions (timeline)
  POST   /api/v1/crm/contacts/{id}/interactions   — Create interaction

  # Product Categories — F007
  GET    /api/v1/crm/product-categories           — List categories
  POST   /api/v1/crm/product-categories           — Create category
  PUT    /api/v1/crm/product-categories/{id}      — Update category
  DELETE /api/v1/crm/product-categories/{id}      — Delete category

  # Products — F005, F006
  GET    /api/v1/crm/products                     — List products
  POST   /api/v1/crm/products                     — Create product
  GET    /api/v1/crm/products/{id}                — Get product detail
  PUT    /api/v1/crm/products/{id}                — Update product
  DELETE /api/v1/crm/products/{id}                — Delete product

  # Offers — F008, F009, F010, F012, F014, F015, F016
  GET    /api/v1/crm/offers                       — List offers
  POST   /api/v1/crm/offers                       — Create offer
  GET    /api/v1/crm/offers/{id}                  — Get offer detail
  PUT    /api/v1/crm/offers/{id}                  — Update offer
  DELETE /api/v1/crm/offers/{id}                  — Delete offer
  POST   /api/v1/crm/offers/{id}/submit           — Submit for approval (F014)
  POST   /api/v1/crm/offers/{id}/approve          — Approve/reject offer (F014)

  # Contracts — F017, F018, F019, F021, F022
  GET    /api/v1/crm/contracts                    — List contracts
  POST   /api/v1/crm/contracts                    — Create contract
  POST   /api/v1/crm/contracts/from-offer         — Create from offer (F018)
  GET    /api/v1/crm/contracts/{id}               — Get contract detail
  PUT    /api/v1/crm/contracts/{id}               — Update contract
  DELETE /api/v1/crm/contracts/{id}               — Delete contract

  # Invoices — F021
  GET    /api/v1/crm/invoices                     — List invoices
  POST   /api/v1/crm/invoices                     — Create invoice from contract

  # KPI & Reports — F023, F024
  GET    /api/v1/crm/kpi/sales                    — Sales KPI dashboard
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.core.rbac import require_min_role, require_role
from app.crm import service
from app.crm.schemas import (
    ContactCreate,
    ContactListOut,
    ContactOut,
    ContactPersonCreate,
    ContactPersonOut,
    ContactPersonUpdate,
    ContactUpdate,
    ContractCreate,
    ContractFromOffer,
    ContractListOut,
    ContractOut,
    ContractUpdate,
    InteractionCreate,
    InteractionOut,
    InvoiceCreate,
    InvoiceOut,
    OfferApprovalDecision,
    OfferApprovalRequest,
    OfferCreate,
    OfferListOut,
    OfferOut,
    OfferUpdate,
    ProductCategoryCreate,
    ProductCategoryOut,
    ProductCategoryUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    SalesKPIOut,
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
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F001: List contacts with search, filter, pagination."""
    contacts, total = await service.list_contacts(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        search=search,
        stage=stage,
        contact_type=contact_type,
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
# PRODUCTS — F005, F006
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
    """F005: List products/services catalog."""
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
    """F005/F006: Create a product/article."""
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
    """F005: Get product detail with sub-products."""
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
    """F005/F006: Update a product."""
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
    """F005: Soft-delete a product."""
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


# ═══════════════════════════════════════════════════════════════════════════════
# OFFERS — F008, F009, F010, F012, F014, F015, F016
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/offers", response_model=ApiResponse)
async def list_offers(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F016: List offers with filtering."""
    offers, total = await service.list_offers(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        status=status,
        contact_id=contact_id,
        search=search,
    )
    return ApiResponse(
        data=[OfferListOut.model_validate(o) for o in offers],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post("/offers", response_model=ApiResponse, status_code=201)
async def create_offer(
    body: OfferCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F008/F009: Create an offer with line items."""
    # Verify contact exists
    contact = await service.get_contact(
        db, current_user.organization_id, body.contact_id
    )
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found")

    req_info = await get_request_info(request)
    offer = await service.create_offer(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    offer = await service.get_offer(db, current_user.organization_id, offer.id)
    return ApiResponse(data=OfferOut.model_validate(offer))


@crm_router.get("/offers/{offer_id}", response_model=ApiResponse)
async def get_offer(
    offer_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F008: Get offer detail with line items."""
    offer = await service.get_offer(db, current_user.organization_id, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return ApiResponse(data=OfferOut.model_validate(offer))


@crm_router.put("/offers/{offer_id}", response_model=ApiResponse)
async def update_offer(
    offer_id: uuid.UUID,
    body: OfferUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F008: Update an offer (draft only)."""
    req_info = await get_request_info(request)
    offer = await service.update_offer(
        db,
        current_user.organization_id,
        current_user.id,
        offer_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if offer is None:
        raise HTTPException(
            status_code=400, detail="Offer not found or not in draft status"
        )
    offer = await service.get_offer(db, current_user.organization_id, offer_id)
    return ApiResponse(data=OfferOut.model_validate(offer))


@crm_router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(
    offer_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F008: Soft-delete an offer (draft only)."""
    req_info = await get_request_info(request)
    deleted = await service.delete_offer(
        db,
        current_user.organization_id,
        current_user.id,
        offer_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(
            status_code=400, detail="Offer not found or not in draft status"
        )


@crm_router.post("/offers/{offer_id}/submit", response_model=ApiResponse)
async def submit_offer(
    offer_id: uuid.UUID,
    body: OfferApprovalRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F014: Submit offer for approval."""
    req_info = await get_request_info(request)
    offer = await service.submit_offer_for_approval(
        db,
        current_user.organization_id,
        current_user.id,
        offer_id,
        body.comment,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if offer is None:
        raise HTTPException(
            status_code=400, detail="Offer not found or not in draft status"
        )
    offer = await service.get_offer(db, current_user.organization_id, offer_id)
    return ApiResponse(data=OfferOut.model_validate(offer))


@crm_router.post(
    "/offers/{offer_id}/approve",
    response_model=ApiResponse,
    dependencies=[Depends(require_min_role("manager_vanzari"))],
)
async def approve_offer(
    offer_id: uuid.UUID,
    body: OfferApprovalDecision,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F014: Approve or reject an offer (manager+ only)."""
    req_info = await get_request_info(request)
    offer = await service.approve_or_reject_offer(
        db,
        current_user.organization_id,
        current_user.id,
        offer_id,
        body.approved,
        body.comment,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if offer is None:
        raise HTTPException(
            status_code=400,
            detail="Offer not found or not pending approval",
        )
    offer = await service.get_offer(db, current_user.organization_id, offer_id)
    return ApiResponse(data=OfferOut.model_validate(offer))


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTS — F017, F018, F019, F021, F022
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/contracts", response_model=ApiResponse)
async def list_contracts(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F022: List contracts with filtering."""
    contracts, total = await service.list_contracts(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        status=status,
        contact_id=contact_id,
        search=search,
    )
    return ApiResponse(
        data=[ContractListOut.model_validate(c) for c in contracts],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post("/contracts", response_model=ApiResponse, status_code=201)
async def create_contract(
    body: ContractCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F017: Create a contract."""
    contact = await service.get_contact(
        db, current_user.organization_id, body.contact_id
    )
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found")

    req_info = await get_request_info(request)
    contract = await service.create_contract(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ContractOut.model_validate(contract))


@crm_router.post(
    "/contracts/from-offer",
    response_model=ApiResponse,
    status_code=201,
)
async def create_contract_from_offer(
    body: ContractFromOffer,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F018: Create contract from accepted offer (auto-populate)."""
    req_info = await get_request_info(request)
    contract = await service.create_contract_from_offer(
        db,
        current_user.organization_id,
        current_user.id,
        body.offer_id,
        title=body.title,
        start_date=body.start_date,
        end_date=body.end_date,
        additional_terms=body.additional_terms,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if contract is None:
        raise HTTPException(
            status_code=400,
            detail="Offer not found or not in accepted/approved status",
        )
    return ApiResponse(data=ContractOut.model_validate(contract))


@crm_router.get("/contracts/{contract_id}", response_model=ApiResponse)
async def get_contract(
    contract_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F017: Get contract detail."""
    contract = await service.get_contract(
        db, current_user.organization_id, contract_id
    )
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ApiResponse(data=ContractOut.model_validate(contract))


@crm_router.put("/contracts/{contract_id}", response_model=ApiResponse)
async def update_contract(
    contract_id: uuid.UUID,
    body: ContractUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F017: Update a contract (draft only)."""
    req_info = await get_request_info(request)
    contract = await service.update_contract(
        db,
        current_user.organization_id,
        current_user.id,
        contract_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if contract is None:
        raise HTTPException(
            status_code=400,
            detail="Contract not found or not in draft status",
        )
    contract = await service.get_contract(
        db, current_user.organization_id, contract_id
    )
    return ApiResponse(data=ContractOut.model_validate(contract))


@crm_router.delete("/contracts/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F017: Soft-delete a contract (draft only)."""
    req_info = await get_request_info(request)
    deleted = await service.delete_contract(
        db,
        current_user.organization_id,
        current_user.id,
        contract_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Contract not found or not in draft status",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICES — F021
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/invoices", response_model=ApiResponse)
async def list_invoices(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contract_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F021: List invoices."""
    invoices, total = await service.list_invoices(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        status=status,
        contract_id=contract_id,
    )
    return ApiResponse(
        data=[InvoiceOut.model_validate(i) for i in invoices],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@crm_router.post("/invoices", response_model=ApiResponse, status_code=201)
async def create_invoice(
    body: InvoiceCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F021: Create invoice from contract."""
    req_info = await get_request_info(request)
    invoice = await service.create_invoice_from_contract(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if invoice is None:
        raise HTTPException(
            status_code=400,
            detail="Contract not found or not in active/signed status",
        )
    return ApiResponse(data=InvoiceOut.model_validate(invoice))


# ═══════════════════════════════════════════════════════════════════════════════
# SALES KPI & REPORTS — F023, F024
# ═══════════════════════════════════════════════════════════════════════════════


@crm_router.get("/kpi/sales", response_model=ApiResponse)
async def get_sales_kpi(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F023: Sales KPI dashboard."""
    kpi = await service.get_sales_kpi(db, current_user.organization_id)
    return ApiResponse(data=SalesKPIOut(**kpi))
