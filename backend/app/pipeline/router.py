"""
Sales Pipeline module router — F019, F028, F031, F035.

Endpoints:
  # Offers — F019 (Offer Builder), F028 (Approval)
  GET    /api/v1/pipeline/offers                    — List offers
  POST   /api/v1/pipeline/offers                    — Create offer
  GET    /api/v1/pipeline/offers/{id}               — Get offer detail
  PUT    /api/v1/pipeline/offers/{id}               — Update offer
  DELETE /api/v1/pipeline/offers/{id}               — Delete offer
  POST   /api/v1/pipeline/offers/{id}/submit        — Submit for approval (F028)
  POST   /api/v1/pipeline/offers/{id}/approve       — Approve/reject offer (F028)

  # Contracts — F031 (Contract Builder)
  GET    /api/v1/pipeline/contracts                 — List contracts
  POST   /api/v1/pipeline/contracts                 — Create contract
  POST   /api/v1/pipeline/contracts/from-offer      — Create from offer (F031)
  GET    /api/v1/pipeline/contracts/{id}            — Get contract detail
  PUT    /api/v1/pipeline/contracts/{id}            — Update contract
  DELETE /api/v1/pipeline/contracts/{id}            — Delete contract

  # Invoices — F035 (Billing)
  GET    /api/v1/pipeline/invoices                  — List invoices
  POST   /api/v1/pipeline/invoices                  — Create invoice from contract

  # KPI
  GET    /api/v1/pipeline/kpi/sales                 — Sales KPI dashboard
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.core.rbac import require_min_role
from app.crm import service as crm_service
from app.pipeline import service
from app.pipeline.schemas import (
    ContractCreate,
    ContractFromOffer,
    ContractListOut,
    ContractOut,
    ContractUpdate,
    InvoiceCreate,
    InvoiceOut,
    OfferApprovalDecision,
    OfferApprovalRequest,
    OfferCreate,
    OfferListOut,
    OfferOut,
    OfferUpdate,
    SalesKPIOut,
)
from app.system.schemas import ApiResponse, Meta

pipeline_router = APIRouter(prefix="/api/v1/pipeline", tags=["Sales Pipeline"])


# ═══════════════════════════════════════════════════════════════════════════════
# OFFERS — F019, F028
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/offers", response_model=ApiResponse)
async def list_offers(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F019: List offers with filtering."""
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


@pipeline_router.post("/offers", response_model=ApiResponse, status_code=201)
async def create_offer(
    body: OfferCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F019: Create an offer with line items."""
    # Verify contact exists
    contact = await crm_service.get_contact(
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


@pipeline_router.get("/offers/{offer_id}", response_model=ApiResponse)
async def get_offer(
    offer_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F019: Get offer detail with line items."""
    offer = await service.get_offer(db, current_user.organization_id, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return ApiResponse(data=OfferOut.model_validate(offer))


@pipeline_router.put("/offers/{offer_id}", response_model=ApiResponse)
async def update_offer(
    offer_id: uuid.UUID,
    body: OfferUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F019: Update an offer (draft only)."""
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


@pipeline_router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(
    offer_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F019: Soft-delete an offer (draft only)."""
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


@pipeline_router.post("/offers/{offer_id}/submit", response_model=ApiResponse)
async def submit_offer(
    offer_id: uuid.UUID,
    body: OfferApprovalRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F028: Submit offer for approval."""
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


@pipeline_router.post(
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
    """F028: Approve or reject an offer (manager+ only)."""
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
# CONTRACTS — F031
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/contracts", response_model=ApiResponse)
async def list_contracts(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: List contracts with filtering."""
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


@pipeline_router.post("/contracts", response_model=ApiResponse, status_code=201)
async def create_contract(
    body: ContractCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: Create a contract."""
    contact = await crm_service.get_contact(
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


@pipeline_router.post(
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
    """F031: Create contract from accepted offer (auto-populate)."""
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


@pipeline_router.get("/contracts/{contract_id}", response_model=ApiResponse)
async def get_contract(
    contract_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: Get contract detail."""
    contract = await service.get_contract(
        db, current_user.organization_id, contract_id
    )
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ApiResponse(data=ContractOut.model_validate(contract))


@pipeline_router.put("/contracts/{contract_id}", response_model=ApiResponse)
async def update_contract(
    contract_id: uuid.UUID,
    body: ContractUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: Update a contract (draft only)."""
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


@pipeline_router.delete("/contracts/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: Soft-delete a contract (draft only)."""
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
# INVOICES — F035
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/invoices", response_model=ApiResponse)
async def list_invoices(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contract_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F035: List invoices."""
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


@pipeline_router.post("/invoices", response_model=ApiResponse, status_code=201)
async def create_invoice(
    body: InvoiceCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F035: Create invoice from contract."""
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
# SALES KPI
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/kpi/sales", response_model=ApiResponse)
async def get_sales_kpi(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sales KPI dashboard."""
    kpi = await service.get_sales_kpi(db, current_user.organization_id)
    return ApiResponse(data=SalesKPIOut(**kpi))
