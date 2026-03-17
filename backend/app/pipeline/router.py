"""
Sales Pipeline module router — F019, F023, F026–F029, F031, F033, F035, F037,
F042–F056, F058, F049.

Endpoints:
  # Opportunities — F042, F050, F051, F052, F053
  GET    /api/v1/pipeline/opportunities                — List opportunities
  POST   /api/v1/pipeline/opportunities                — Create opportunity (CRM handover)
  GET    /api/v1/pipeline/opportunities/{id}           — Get opportunity detail
  PUT    /api/v1/pipeline/opportunities/{id}           — Update opportunity
  DELETE /api/v1/pipeline/opportunities/{id}           — Delete opportunity
  POST   /api/v1/pipeline/opportunities/{id}/transition — Stage transition (F051)
  POST   /api/v1/pipeline/opportunities/{id}/qualify    — Qualify (F042)
  GET    /api/v1/pipeline/board                        — Pipeline Kanban board (F050)

  # Milestones — F043, F044, F045, F046, F047, F048
  GET    /api/v1/pipeline/opportunities/{id}/milestones       — List milestones
  POST   /api/v1/pipeline/milestones                          — Create milestone
  GET    /api/v1/pipeline/milestones/{id}                     — Get milestone
  PUT    /api/v1/pipeline/milestones/{id}                     — Update milestone
  DELETE /api/v1/pipeline/milestones/{id}                     — Delete milestone
  POST   /api/v1/pipeline/milestones/{id}/dependencies        — Add dependency (F047)
  GET    /api/v1/pipeline/opportunities/{id}/time-summary     — Time summary (F044)
  GET    /api/v1/pipeline/milestone-templates                 — List templates (F048)
  POST   /api/v1/pipeline/milestone-templates                 — Create template (F048)
  POST   /api/v1/pipeline/milestone-templates/apply           — Apply template (F048)

  # Activities — F054, F055, F056
  GET    /api/v1/pipeline/activities                   — List activities
  POST   /api/v1/pipeline/activities                   — Create activity
  GET    /api/v1/pipeline/activities/{id}              — Get activity
  PUT    /api/v1/pipeline/activities/{id}              — Update activity
  DELETE /api/v1/pipeline/activities/{id}              — Delete activity

  # Offers — F019, F026, F028
  GET    /api/v1/pipeline/offers                       — List offers
  POST   /api/v1/pipeline/offers                       — Create offer
  GET    /api/v1/pipeline/offers/{id}                  — Get offer detail
  PUT    /api/v1/pipeline/offers/{id}                  — Update offer
  DELETE /api/v1/pipeline/offers/{id}                  — Delete offer
  POST   /api/v1/pipeline/offers/{id}/submit           — Submit for approval (F028)
  POST   /api/v1/pipeline/offers/{id}/approve          — Approve/reject (F028)
  POST   /api/v1/pipeline/offers/{id}/version          — Create new version (F026)

  # Contracts — F031, F035
  GET    /api/v1/pipeline/contracts                    — List contracts
  POST   /api/v1/pipeline/contracts                    — Create contract
  POST   /api/v1/pipeline/contracts/from-offer         — Create from offer (F031)
  GET    /api/v1/pipeline/contracts/{id}               — Get contract detail
  PUT    /api/v1/pipeline/contracts/{id}               — Update contract
  DELETE /api/v1/pipeline/contracts/{id}               — Delete contract
  POST   /api/v1/pipeline/contracts/{id}/sign          — Sign contract (F031)
  POST   /api/v1/pipeline/contracts/{id}/terminate     — Terminate contract (F035)
  POST   /api/v1/pipeline/contracts/{id}/billing       — Add billing schedule (F035)

  # Invoices — F035
  GET    /api/v1/pipeline/invoices                     — List invoices
  POST   /api/v1/pipeline/invoices                     — Create invoice

  # Analytics & KPI — F029, F037, F058
  GET    /api/v1/pipeline/kpi/sales                    — Sales Dashboard (F058)
  GET    /api/v1/pipeline/analytics/offers             — Offers analytics (F029)
  GET    /api/v1/pipeline/analytics/contracts          — Contracts analytics (F037)
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_request_info
from app.core.rbac import require_min_role
from app.crm import service as crm_service
from app.pipeline import service
from app.pipeline.schemas import (
    ActivityCreate,
    ActivityListOut,
    ActivityOut,
    ActivityUpdate,
    BillingScheduleCreate,
    BillingScheduleOut,
    ContractAnalyticsOut,
    ContractCreate,
    ContractFromOffer,
    ContractListOut,
    ContractOut,
    ContractSignRequest,
    ContractTerminateRequest,
    ContractUpdate,
    DocumentGenerateOut,
    DocumentGenerateRequest,
    InvoiceCreate,
    InvoiceOut,
    MilestoneCreate,
    MilestoneDependencyCreate,
    MilestoneDependencyOut,
    MilestoneOut,
    MilestoneTemplateApply,
    MilestoneTemplateCreate,
    MilestoneTemplateOut,
    MilestoneUpdate,
    OfferAnalyticsOut,
    OfferApprovalDecision,
    OfferApprovalRequest,
    OfferCreate,
    OfferListOut,
    OfferOut,
    OfferUpdate,
    OfferVersionCreate,
    OpportunityCreate,
    OpportunityListOut,
    OpportunityOut,
    OpportunityQualify,
    OpportunityStageTransition,
    OpportunityUpdate,
    PipelineBoardOut,
    PipelineBoardStage,
    PredefinedLossReasonCreate,
    PredefinedLossReasonOut,
    PredefinedLossReasonUpdate,
    SalesKPIOut,
    SimplifiedOfferCreate,
    WeightedPipelineOut,
)
from app.system.schemas import ApiResponse, Meta

pipeline_router = APIRouter(prefix="/api/v1/pipeline", tags=["Sales Pipeline"])


# ═══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITIES — F042, F050, F051, F052, F053
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/opportunities", response_model=ApiResponse)
async def list_opportunities(
    page: int = 1,
    per_page: int = 20,
    stage: str | None = None,
    owner_id: uuid.UUID | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F050: List opportunities with filtering."""
    opps, total = await service.list_opportunities(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        stage=stage,
        owner_id=owner_id,
        contact_id=contact_id,
        search=search,
    )
    return ApiResponse(
        data=[OpportunityListOut.model_validate(o) for o in opps],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pipeline_router.post("/opportunities", response_model=ApiResponse, status_code=201)
async def create_opportunity(
    body: OpportunityCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F042: Create opportunity (CRM → Pipeline handover)."""
    contact = await crm_service.get_contact(
        db, current_user.organization_id, body.contact_id
    )
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found")

    req_info = await get_request_info(request)
    opp = await service.create_opportunity(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=OpportunityOut.model_validate(opp))


@pipeline_router.get("/opportunities/{opp_id}", response_model=ApiResponse)
async def get_opportunity(
    opp_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F050: Get opportunity detail."""
    opp = await service.get_opportunity(db, current_user.organization_id, opp_id)
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return ApiResponse(data=OpportunityOut.model_validate(opp))


@pipeline_router.put("/opportunities/{opp_id}", response_model=ApiResponse)
async def update_opportunity(
    opp_id: uuid.UUID,
    body: OpportunityUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update opportunity."""
    req_info = await get_request_info(request)
    opp = await service.update_opportunity(
        db,
        current_user.organization_id,
        current_user.id,
        opp_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp = await service.get_opportunity(db, current_user.organization_id, opp_id)
    return ApiResponse(data=OpportunityOut.model_validate(opp))


@pipeline_router.delete("/opportunities/{opp_id}", status_code=204)
async def delete_opportunity(
    opp_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete opportunity."""
    req_info = await get_request_info(request)
    deleted = await service.delete_opportunity(
        db,
        current_user.organization_id,
        current_user.id,
        opp_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Opportunity not found")


@pipeline_router.post("/opportunities/{opp_id}/transition", response_model=ApiResponse)
async def transition_opportunity(
    opp_id: uuid.UUID,
    body: OpportunityStageTransition,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F051: Stage transition with validation + F052: auto win probability."""
    req_info = await get_request_info(request)
    opp = await service.transition_opportunity_stage(
        db,
        current_user.organization_id,
        current_user.id,
        opp_id,
        body.new_stage,
        loss_reason=body.loss_reason,
        loss_reason_detail=body.loss_reason_detail,
        won_reason=body.won_reason,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if opp is None:
        raise HTTPException(
            status_code=400, detail="Invalid stage transition or opportunity not found"
        )
    opp = await service.get_opportunity(db, current_user.organization_id, opp_id)
    return ApiResponse(data=OpportunityOut.model_validate(opp))


@pipeline_router.post("/opportunities/{opp_id}/qualify", response_model=ApiResponse)
async def qualify_opportunity(
    opp_id: uuid.UUID,
    body: OpportunityQualify,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F042: Qualify opportunity (CRM → Pipeline handover)."""
    req_info = await get_request_info(request)
    opp = await service.qualify_opportunity(
        db,
        current_user.organization_id,
        current_user.id,
        opp_id,
        body.qualification_checklist,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp = await service.get_opportunity(db, current_user.organization_id, opp_id)
    return ApiResponse(data=OpportunityOut.model_validate(opp))


@pipeline_router.get("/board", response_model=ApiResponse)
async def get_pipeline_board(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F050: Pipeline Kanban board."""
    board = await service.get_pipeline_board(db, current_user.organization_id)
    # Serialize opportunities within stages
    for stage in board["stages"]:
        stage["opportunities"] = [
            OpportunityListOut.model_validate(o) for o in stage["opportunities"]
        ]
    return ApiResponse(data=board)


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONES — F043, F044, F045, F046, F047, F048
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/opportunities/{opp_id}/milestones", response_model=ApiResponse)
async def list_milestones(
    opp_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F043: List milestones for an opportunity."""
    milestones = await service.list_milestones(
        db, current_user.organization_id, opp_id
    )
    return ApiResponse(
        data=[MilestoneOut.model_validate(m) for m in milestones],
    )


@pipeline_router.post("/milestones", response_model=ApiResponse, status_code=201)
async def create_milestone(
    body: MilestoneCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F043: Create milestone."""
    req_info = await get_request_info(request)
    ms = await service.create_milestone(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=MilestoneOut.model_validate(ms))


@pipeline_router.get("/milestones/{milestone_id}", response_model=ApiResponse)
async def get_milestone(
    milestone_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F043: Get milestone detail."""
    ms = await service.get_milestone(
        db, current_user.organization_id, milestone_id
    )
    if ms is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return ApiResponse(data=MilestoneOut.model_validate(ms))


@pipeline_router.put("/milestones/{milestone_id}", response_model=ApiResponse)
async def update_milestone(
    milestone_id: uuid.UUID,
    body: MilestoneUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F043-F046: Update milestone (status, assignment, cost, time)."""
    req_info = await get_request_info(request)
    ms = await service.update_milestone(
        db,
        current_user.organization_id,
        current_user.id,
        milestone_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if ms is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    ms = await service.get_milestone(db, current_user.organization_id, milestone_id)
    return ApiResponse(data=MilestoneOut.model_validate(ms))


@pipeline_router.delete("/milestones/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete milestone."""
    req_info = await get_request_info(request)
    deleted = await service.delete_milestone(
        db,
        current_user.organization_id,
        current_user.id,
        milestone_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Milestone not found")


@pipeline_router.post(
    "/milestones/{milestone_id}/dependencies",
    response_model=ApiResponse,
    status_code=201,
)
async def add_milestone_dependency(
    milestone_id: uuid.UUID,
    body: MilestoneDependencyCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F047: Add dependency between milestones."""
    req_info = await get_request_info(request)
    dep = await service.add_milestone_dependency(
        db,
        current_user.organization_id,
        current_user.id,
        milestone_id,
        body.depends_on_id,
        body.dependency_type,
        body.lag_days,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if dep is None:
        raise HTTPException(status_code=400, detail="Milestone(s) not found")
    return ApiResponse(data=MilestoneDependencyOut.model_validate(dep))


@pipeline_router.get(
    "/opportunities/{opp_id}/time-summary", response_model=ApiResponse
)
async def get_time_summary(
    opp_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F044: Time estimation summary for all milestones."""
    summary = await service.get_milestone_time_summary(
        db, current_user.organization_id, opp_id
    )
    return ApiResponse(data=summary)


@pipeline_router.get("/milestone-templates", response_model=ApiResponse)
async def list_milestone_templates(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F048: List milestone templates."""
    templates = await service.list_milestone_templates(
        db, current_user.organization_id
    )
    return ApiResponse(
        data=[MilestoneTemplateOut.model_validate(t) for t in templates],
    )


@pipeline_router.post(
    "/milestone-templates", response_model=ApiResponse, status_code=201
)
async def create_milestone_template(
    body: MilestoneTemplateCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F048: Create milestone template."""
    req_info = await get_request_info(request)
    tmpl = await service.create_milestone_template(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=MilestoneTemplateOut.model_validate(tmpl))


@pipeline_router.post("/milestone-templates/apply", response_model=ApiResponse)
async def apply_milestone_template(
    body: MilestoneTemplateApply,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F048: Apply template to create milestones for opportunity."""
    req_info = await get_request_info(request)
    milestones = await service.apply_milestone_template(
        db,
        current_user.organization_id,
        current_user.id,
        body.template_id,
        body.opportunity_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(
        data=[MilestoneOut.model_validate(m) for m in milestones],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVITIES — F054, F055, F056
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/activities", response_model=ApiResponse)
async def list_activities(
    page: int = 1,
    per_page: int = 20,
    activity_type: str | None = None,
    status: str | None = None,
    owner_id: uuid.UUID | None = None,
    contact_id: uuid.UUID | None = None,
    opportunity_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F054: List activities with filtering."""
    activities, total = await service.list_activities(
        db,
        current_user.organization_id,
        page=page,
        per_page=per_page,
        activity_type=activity_type,
        status=status,
        owner_id=owner_id,
        contact_id=contact_id,
        opportunity_id=opportunity_id,
        date_from=date_from,
        date_to=date_to,
    )
    return ApiResponse(
        data=[ActivityListOut.model_validate(a) for a in activities],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@pipeline_router.post("/activities", response_model=ApiResponse, status_code=201)
async def create_activity(
    body: ActivityCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F054/F055/F056: Create activity."""
    req_info = await get_request_info(request)
    act = await service.create_activity(
        db,
        current_user.organization_id,
        current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ActivityOut.model_validate(act))


@pipeline_router.get("/activities/{activity_id}", response_model=ApiResponse)
async def get_activity(
    activity_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get activity detail."""
    act = await service.get_activity(
        db, current_user.organization_id, activity_id
    )
    if act is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ApiResponse(data=ActivityOut.model_validate(act))


@pipeline_router.put("/activities/{activity_id}", response_model=ApiResponse)
async def update_activity(
    activity_id: uuid.UUID,
    body: ActivityUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update activity."""
    req_info = await get_request_info(request)
    act = await service.update_activity(
        db,
        current_user.organization_id,
        current_user.id,
        activity_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if act is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    act = await service.get_activity(db, current_user.organization_id, activity_id)
    return ApiResponse(data=ActivityOut.model_validate(act))


@pipeline_router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete activity."""
    req_info = await get_request_info(request)
    deleted = await service.delete_activity(
        db,
        current_user.organization_id,
        current_user.id,
        activity_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Activity not found")


# ═══════════════════════════════════════════════════════════════════════════════
# OFFERS — F019, F026, F028
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


@pipeline_router.post("/offers/{offer_id}/version", response_model=ApiResponse, status_code=201)
async def create_offer_version(
    offer_id: uuid.UUID,
    body: OfferVersionCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F026: Create new version of an offer."""
    req_info = await get_request_info(request)
    new_offer = await service.create_offer_version(
        db,
        current_user.organization_id,
        current_user.id,
        offer_id,
        body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if new_offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    new_offer = await service.get_offer(db, current_user.organization_id, new_offer.id)
    return ApiResponse(data=OfferOut.model_validate(new_offer))


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTS — F031, F035
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


@pipeline_router.post("/contracts/{contract_id}/sign", response_model=ApiResponse)
async def sign_contract(
    contract_id: uuid.UUID,
    body: ContractSignRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F031: Sign contract → triggers Project Setup (F063)."""
    req_info = await get_request_info(request)
    contract = await service.sign_contract(
        db,
        current_user.organization_id,
        current_user.id,
        contract_id,
        body.signed_date,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if contract is None:
        raise HTTPException(
            status_code=400,
            detail="Contract not found or cannot be signed in current status",
        )
    contract = await service.get_contract(db, current_user.organization_id, contract_id)
    return ApiResponse(data=ContractOut.model_validate(contract))


@pipeline_router.post("/contracts/{contract_id}/terminate", response_model=ApiResponse)
async def terminate_contract(
    contract_id: uuid.UUID,
    body: ContractTerminateRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F035: Terminate contract."""
    req_info = await get_request_info(request)
    contract = await service.terminate_contract(
        db,
        current_user.organization_id,
        current_user.id,
        contract_id,
        body.termination_reason,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if contract is None:
        raise HTTPException(
            status_code=400,
            detail="Contract not found or already terminated/completed",
        )
    contract = await service.get_contract(db, current_user.organization_id, contract_id)
    return ApiResponse(data=ContractOut.model_validate(contract))


@pipeline_router.post(
    "/contracts/{contract_id}/billing",
    response_model=ApiResponse,
    status_code=201,
)
async def add_billing_schedule(
    contract_id: uuid.UUID,
    body: BillingScheduleCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F035: Add billing schedule item to contract."""
    req_info = await get_request_info(request)
    bs = await service.add_billing_schedule(
        db,
        current_user.organization_id,
        current_user.id,
        contract_id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if bs is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ApiResponse(data=BillingScheduleOut.model_validate(bs))


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
# ANALYTICS & KPI — F029, F037, F058
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/kpi/sales", response_model=ApiResponse)
async def get_sales_kpi(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F058: Sales Dashboard — KPIs, funnel, forecast."""
    kpi = await service.get_sales_kpi(db, current_user.organization_id)
    return ApiResponse(data=SalesKPIOut(**kpi))


@pipeline_router.get("/analytics/offers", response_model=ApiResponse)
async def get_offer_analytics(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F029: Offers Analytics."""
    analytics = await service.get_offer_analytics(db, current_user.organization_id)
    return ApiResponse(data=OfferAnalyticsOut(**analytics))


@pipeline_router.get("/analytics/contracts", response_model=ApiResponse)
async def get_contract_analytics(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F037: Contracts Analytics."""
    analytics = await service.get_contract_analytics(db, current_user.organization_id)
    return ApiResponse(data=ContractAnalyticsOut(**analytics))


# ═══════════════════════════════════════════════════════════════════════════════
# F023/F033 — Document Generation
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.post("/offers/{offer_id}/generate-document", response_model=ApiResponse)
async def generate_offer_document(
    offer_id: uuid.UUID,
    body: DocumentGenerateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F023: Generate document from offer (template-based)."""
    result = await service.generate_offer_document(
        db, current_user.organization_id, offer_id,
        template_id=body.template_id, format=body.format,
        include_line_items=body.include_line_items, include_terms=body.include_terms,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Offer not found")
    return ApiResponse(data=DocumentGenerateOut(**result))


@pipeline_router.post("/contracts/{contract_id}/generate-document", response_model=ApiResponse)
async def generate_contract_document(
    contract_id: uuid.UUID,
    body: DocumentGenerateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F033: Generate document from contract (template-based)."""
    result = await service.generate_contract_document(
        db, current_user.organization_id, contract_id,
        template_id=body.template_id, format=body.format,
        include_terms=body.include_terms,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ApiResponse(data=DocumentGenerateOut(**result))


# ═══════════════════════════════════════════════════════════════════════════════
# F049 — Simplified Offer Flow
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.post("/offers/quick", response_model=ApiResponse, status_code=201)
async def create_simplified_offer(
    body: SimplifiedOfferCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F049: Quick offer creation with minimal fields."""
    contact = await crm_service.get_contact(
        db, current_user.organization_id, body.contact_id
    )
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found")

    req_info = await get_request_info(request)
    offer = await service.create_simplified_offer(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    offer = await service.get_offer(db, current_user.organization_id, offer.id)
    return ApiResponse(data=OfferOut.model_validate(offer))


# ═══════════════════════════════════════════════════════════════════════════════
# F053 — PREDEFINED LOSS REASONS
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/loss-reasons", response_model=ApiResponse)
async def list_loss_reasons(
    active_only: bool = False,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: List predefined loss reasons (dropdown source)."""
    reasons = await service.list_loss_reasons(
        db, current_user.organization_id, active_only=active_only,
    )
    return ApiResponse(
        data=[PredefinedLossReasonOut.model_validate(r) for r in reasons],
        meta=Meta(total=len(reasons), page=1, per_page=len(reasons)),
    )


@pipeline_router.post("/loss-reasons", response_model=ApiResponse, status_code=201)
async def create_loss_reason(
    body: PredefinedLossReasonCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: Create a predefined loss reason."""
    req_info = await get_request_info(request)
    reason = await service.create_loss_reason(
        db, current_user.organization_id, current_user.id,
        body.model_dump(),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=PredefinedLossReasonOut.model_validate(reason))


@pipeline_router.get("/loss-reasons/{reason_id}", response_model=ApiResponse)
async def get_loss_reason(
    reason_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: Get a predefined loss reason."""
    reason = await service.get_loss_reason(db, current_user.organization_id, reason_id)
    if reason is None:
        raise HTTPException(status_code=404, detail="Loss reason not found")
    return ApiResponse(data=PredefinedLossReasonOut.model_validate(reason))


@pipeline_router.put("/loss-reasons/{reason_id}", response_model=ApiResponse)
async def update_loss_reason(
    reason_id: uuid.UUID,
    body: PredefinedLossReasonUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: Update a predefined loss reason."""
    req_info = await get_request_info(request)
    reason = await service.update_loss_reason(
        db, current_user.organization_id, current_user.id,
        reason_id, body.model_dump(exclude_unset=True),
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if reason is None:
        raise HTTPException(status_code=404, detail="Loss reason not found")
    return ApiResponse(data=PredefinedLossReasonOut.model_validate(reason))


@pipeline_router.delete("/loss-reasons/{reason_id}", response_model=ApiResponse)
async def delete_loss_reason(
    reason_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: Delete a predefined loss reason."""
    req_info = await get_request_info(request)
    deleted = await service.delete_loss_reason(
        db, current_user.organization_id, current_user.id, reason_id,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Loss reason not found")
    return ApiResponse(data={"deleted": True})


# ═══════════════════════════════════════════════════════════════════════════════
# F053 — WEIGHTED PIPELINE VALUE
# ═══════════════════════════════════════════════════════════════════════════════


@pipeline_router.get("/weighted-value", response_model=ApiResponse)
async def get_weighted_pipeline(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """F053: Aggregated weighted pipeline value by stage."""
    data = await service.get_weighted_pipeline(db, current_user.organization_id)
    return ApiResponse(data=WeightedPipelineOut(**data))
