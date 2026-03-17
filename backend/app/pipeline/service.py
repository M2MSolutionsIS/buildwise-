"""
Sales Pipeline module service layer — F019, F028, F031, F035.

CRUD operations for Offers, Contracts, Invoices, Sales KPI.
All operations include audit trail and multi-tenant isolation.
"""

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.audit import log_audit, model_to_dict
from app.crm.models import Contact, ContactStage
from app.pipeline.models import (
    ApprovalStatus,
    ApprovalStep,
    ApprovalWorkflow,
    BillingSchedule,
    Contract,
    ContractStatus,
    Invoice,
    InvoiceStatus,
    Offer,
    OfferLineItem,
    OfferStatus,
)


# ═══════════════════════════════════════════════════════════════════════════════
# OFFERS — F019, F028
# ═══════════════════════════════════════════════════════════════════════════════


def _compute_offer_totals(line_items_data: list[dict]) -> dict:
    """Calculate subtotal, VAT, total from line items."""
    subtotal = 0.0
    vat_amount = 0.0
    for item in line_items_data:
        qty = item.get("quantity", 1.0)
        price = item.get("unit_price", 0.0)
        discount = item.get("discount_percent", 0.0)
        vat_rate = item.get("vat_rate", 0.19)
        line_total = qty * price * (1 - discount / 100)
        subtotal += line_total
        vat_amount += line_total * vat_rate
    return {
        "subtotal": round(subtotal, 2),
        "vat_amount": round(vat_amount, 2),
        "total_amount": round(subtotal + vat_amount, 2),
    }


async def _generate_offer_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    """Generate next offer number: OF-YYYY-NNNN."""
    year = datetime.now(timezone.utc).year
    prefix = f"OF-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Offer)
        .where(
            Offer.organization_id == org_id,
            Offer.offer_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def list_offers(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Offer], int]:
    """List offers with filtering."""
    query = select(Offer).where(
        Offer.organization_id == org_id,
        Offer.is_deleted.is_(False),
    )
    if status:
        query = query.where(Offer.status == status)
    if contact_id:
        query = query.where(Offer.contact_id == contact_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Offer.title.ilike(pattern) | Offer.offer_number.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Offer.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_offer(
    db: AsyncSession, org_id: uuid.UUID, offer_id: uuid.UUID
) -> Offer | None:
    """Get a single offer with line items."""
    result = await db.execute(
        select(Offer)
        .options(selectinload(Offer.line_items))
        .where(
            Offer.id == offer_id,
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer:
    """F019: Create an offer with line items and financial estimates."""
    line_items_data = data.pop("line_items", [])
    offer_number = await _generate_offer_number(db, org_id)

    totals = _compute_offer_totals(line_items_data)
    valid_until = datetime.now(timezone.utc) + timedelta(days=data.get("validity_days", 30))

    offer = Offer(
        id=uuid.uuid4(),
        organization_id=org_id,
        offer_number=offer_number,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        valid_until=valid_until,
        **totals,
        **data,
    )
    db.add(offer)
    await db.flush()

    for item_data in line_items_data:
        qty = item_data.get("quantity", 1.0)
        price = item_data.get("unit_price", 0.0)
        discount = item_data.get("discount_percent", 0.0)
        line_total = round(qty * price * (1 - discount / 100), 2)
        line_item = OfferLineItem(
            id=uuid.uuid4(),
            offer_id=offer.id,
            organization_id=org_id,
            total_price=line_total,
            **item_data,
        )
        db.add(line_item)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def update_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """Update an offer (only in draft status)."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None:
        return None
    if offer.status != OfferStatus.DRAFT.value:
        return None  # Only draft offers can be edited

    old_values = model_to_dict(offer)
    for key, val in data.items():
        if val is not None:
            setattr(offer, key, val)
    offer.updated_by = user_id

    if data.get("validity_days"):
        offer.valid_until = datetime.now(timezone.utc) + timedelta(days=data["validity_days"])

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        old_values=old_values,
        new_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def submit_offer_for_approval(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    comment: str | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """F028: Submit offer for approval."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.DRAFT.value:
        return None

    offer.status = OfferStatus.PENDING_APPROVAL.value
    offer.updated_by = user_id

    workflow = ApprovalWorkflow(
        id=uuid.uuid4(),
        organization_id=org_id,
        entity_type="offer",
        entity_id=offer.id,
        submitted_by=user_id,
    )
    db.add(workflow)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values={"status": "pending_approval", "comment": comment},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def approve_or_reject_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    approved: bool,
    comment: str | None = None,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Offer | None:
    """F028: Approve or reject an offer."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.PENDING_APPROVAL.value:
        return None

    if approved:
        offer.status = OfferStatus.APPROVED.value
    else:
        offer.status = OfferStatus.REJECTED.value
        offer.rejected_at = datetime.now(timezone.utc)

    offer.updated_by = user_id

    # Update the workflow
    wf_result = await db.execute(
        select(ApprovalWorkflow).where(
            ApprovalWorkflow.entity_type == "offer",
            ApprovalWorkflow.entity_id == offer_id,
            ApprovalWorkflow.organization_id == org_id,
            ApprovalWorkflow.status == ApprovalStatus.PENDING.value,
        )
    )
    workflow = wf_result.scalar_one_or_none()
    if workflow:
        workflow.status = ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value
        step = ApprovalStep(
            id=uuid.uuid4(),
            workflow_id=workflow.id,
            approver_id=user_id,
            step_order=1,
            status=ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value,
            comment=comment,
            decided_at=datetime.now(timezone.utc),
        )
        db.add(step)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="offers",
        entity_id=offer.id,
        new_values={
            "status": offer.status,
            "approved": approved,
            "comment": comment,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return offer


async def delete_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """Soft-delete an offer (only draft)."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None or offer.status != OfferStatus.DRAFT.value:
        return False

    offer.is_deleted = True
    offer.deleted_at = datetime.now(timezone.utc)
    offer.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="offers",
        entity_id=offer.id,
        old_values=model_to_dict(offer),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTS — F031, F035
# ═══════════════════════════════════════════════════════════════════════════════


async def _generate_contract_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    """Generate next contract number: CT-YYYY-NNNN."""
    year = datetime.now(timezone.utc).year
    prefix = f"CT-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Contract)
        .where(
            Contract.organization_id == org_id,
            Contract.contract_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def list_contracts(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contact_id: uuid.UUID | None = None,
    search: str | None = None,
) -> tuple[list[Contract], int]:
    """List contracts with filtering."""
    query = select(Contract).where(
        Contract.organization_id == org_id,
        Contract.is_deleted.is_(False),
    )
    if status:
        query = query.where(Contract.status == status)
    if contact_id:
        query = query.where(Contract.contact_id == contact_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            Contract.title.ilike(pattern) | Contract.contract_number.ilike(pattern)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Contract.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_contract(
    db: AsyncSession, org_id: uuid.UUID, contract_id: uuid.UUID
) -> Contract | None:
    """Get a single contract."""
    result = await db.execute(
        select(Contract)
        .options(
            selectinload(Contract.billing_schedule),
            selectinload(Contract.invoices),
        )
        .where(
            Contract.id == contract_id,
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def create_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract:
    """F031: Create a contract."""
    contract_number = await _generate_contract_number(db, org_id)

    contract = Contract(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_number=contract_number,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
        **data,
    )
    db.add(contract)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="contracts",
        entity_id=contract.id,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def create_contract_from_offer(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    offer_id: uuid.UUID,
    *,
    title: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    additional_terms: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    """F031: Auto-populate contract from accepted offer."""
    offer = await get_offer(db, org_id, offer_id)
    if offer is None:
        return None
    if offer.status not in (OfferStatus.ACCEPTED.value, OfferStatus.APPROVED.value):
        return None

    contract_number = await _generate_contract_number(db, org_id)

    terms = offer.terms_and_conditions or ""
    if additional_terms:
        terms = f"{terms}\n\n{additional_terms}"

    contract = Contract(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_number=contract_number,
        contact_id=offer.contact_id,
        offer_id=offer.id,
        opportunity_id=offer.opportunity_id,
        title=title or f"Contract - {offer.title}",
        total_value=offer.total_amount,
        currency=offer.currency,
        start_date=start_date,
        end_date=end_date,
        terms_and_conditions=terms,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(contract)

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="contracts",
        entity_id=contract.id,
        new_values={"from_offer": str(offer_id), **model_to_dict(contract)},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def update_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Contract | None:
    """Update a contract (only in draft status)."""
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status != ContractStatus.DRAFT.value:
        return None

    old_values = model_to_dict(contract)
    for key, val in data.items():
        if val is not None:
            setattr(contract, key, val)
    contract.updated_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="UPDATE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=old_values,
        new_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return contract


async def delete_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    """Soft-delete a contract (only draft)."""
    contract = await get_contract(db, org_id, contract_id)
    if contract is None or contract.status != ContractStatus.DRAFT.value:
        return False

    contract.is_deleted = True
    contract.deleted_at = datetime.now(timezone.utc)
    contract.deleted_by = user_id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="DELETE",
        entity_type="contracts",
        entity_id=contract.id,
        old_values=model_to_dict(contract),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICES — F035
# ═══════════════════════════════════════════════════════════════════════════════


async def _generate_invoice_number(db: AsyncSession, org_id: uuid.UUID) -> str:
    """Generate next invoice number: INV-YYYY-NNNN."""
    year = datetime.now(timezone.utc).year
    prefix = f"INV-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Invoice)
        .where(
            Invoice.organization_id == org_id,
            Invoice.invoice_number.like(f"{prefix}%"),
        )
    )
    count = result.scalar() + 1
    return f"{prefix}{count:04d}"


async def create_invoice_from_contract(
    db: AsyncSession,
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict,
    *,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Invoice | None:
    """F035: Create invoice from contract."""
    contract_id = data["contract_id"]
    contract = await get_contract(db, org_id, contract_id)
    if contract is None:
        return None
    if contract.status not in (
        ContractStatus.ACTIVE.value,
        ContractStatus.SIGNED.value,
    ):
        return None

    invoice_number = await _generate_invoice_number(db, org_id)
    amount = data["amount"]
    vat_amount = data.get("vat_amount", 0.0)

    invoice = Invoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        contract_id=contract_id,
        invoice_number=invoice_number,
        amount=amount,
        vat_amount=vat_amount,
        total_amount=round(amount + vat_amount, 2),
        currency=data.get("currency", contract.currency),
        issue_date=data["issue_date"],
        due_date=data["due_date"],
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(invoice)

    # If billing_schedule_id provided, mark it as invoiced
    billing_id = data.get("billing_schedule_id")
    if billing_id:
        bs_result = await db.execute(
            select(BillingSchedule).where(
                BillingSchedule.id == billing_id,
                BillingSchedule.contract_id == contract_id,
            )
        )
        bs = bs_result.scalar_one_or_none()
        if bs:
            bs.is_invoiced = True
            bs.invoice_id = invoice.id

    await log_audit(
        db,
        user_id=user_id,
        organization_id=org_id,
        action="CREATE",
        entity_type="invoices",
        entity_id=invoice.id,
        new_values=model_to_dict(invoice),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.flush()
    return invoice


async def list_invoices(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    contract_id: uuid.UUID | None = None,
) -> tuple[list[Invoice], int]:
    """List invoices with filtering."""
    query = select(Invoice).where(Invoice.organization_id == org_id)
    if status:
        query = query.where(Invoice.status == status)
    if contract_id:
        query = query.where(Invoice.contract_id == contract_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(Invoice.issue_date.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


# ═══════════════════════════════════════════════════════════════════════════════
# SALES KPI
# ═══════════════════════════════════════════════════════════════════════════════


async def get_sales_kpi(db: AsyncSession, org_id: uuid.UUID) -> dict:
    """Sales KPI — aggregate metrics."""
    # Contacts
    total_contacts = (await db.execute(
        select(func.count()).select_from(Contact).where(
            Contact.organization_id == org_id, Contact.is_deleted.is_(False)
        )
    )).scalar()

    active_contacts = (await db.execute(
        select(func.count()).select_from(Contact).where(
            Contact.organization_id == org_id,
            Contact.is_deleted.is_(False),
            Contact.stage == ContactStage.ACTIVE.value,
        )
    )).scalar()

    # Offers
    total_offers = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id, Offer.is_deleted.is_(False)
        )
    )).scalar()

    offers_sent = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.SENT.value,
        )
    )).scalar()

    offers_accepted = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.ACCEPTED.value,
        )
    )).scalar()

    offers_rejected = (await db.execute(
        select(func.count()).select_from(Offer).where(
            Offer.organization_id == org_id,
            Offer.is_deleted.is_(False),
            Offer.status == OfferStatus.REJECTED.value,
        )
    )).scalar()

    conversion_rate = (offers_accepted / total_offers * 100) if total_offers > 0 else 0.0

    # Contracts
    total_contracts = (await db.execute(
        select(func.count()).select_from(Contract).where(
            Contract.organization_id == org_id, Contract.is_deleted.is_(False)
        )
    )).scalar()

    active_contracts = (await db.execute(
        select(func.count()).select_from(Contract).where(
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
            Contract.status == ContractStatus.ACTIVE.value,
        )
    )).scalar()

    total_revenue = (await db.execute(
        select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
            Contract.organization_id == org_id,
            Contract.is_deleted.is_(False),
            Contract.status.in_([
                ContractStatus.ACTIVE.value,
                ContractStatus.SIGNED.value,
                ContractStatus.COMPLETED.value,
            ]),
        )
    )).scalar()

    # Invoices
    total_invoiced = (await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0.0)).where(
            Invoice.organization_id == org_id,
            Invoice.status != InvoiceStatus.CANCELLED.value,
        )
    )).scalar()

    total_paid = (await db.execute(
        select(func.coalesce(func.sum(Invoice.paid_amount), 0.0)).where(
            Invoice.organization_id == org_id,
            Invoice.status == InvoiceStatus.PAID.value,
        )
    )).scalar()

    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "total_offers": total_offers,
        "offers_sent": offers_sent,
        "offers_accepted": offers_accepted,
        "offers_rejected": offers_rejected,
        "conversion_rate": round(conversion_rate, 2),
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "total_revenue": round(total_revenue, 2),
        "total_invoiced": round(total_invoiced, 2),
        "total_paid": round(total_paid, 2),
        "currency": "RON",
    }
