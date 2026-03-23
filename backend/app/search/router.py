"""
E-026 / F137, F138: Global Search — search across contacts, opportunities,
projects, and offers.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.crm.models import Contact
from app.pipeline.models import Opportunity, Offer
from app.pm.models import Project

search_router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@search_router.get("")
async def global_search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """F137: Search across contacts, opportunities, projects, offers."""
    org_id = current_user.organization_id
    pattern = f"%{q}%"

    # Contacts
    contacts_q = (
        select(Contact)
        .where(
            Contact.organization_id == org_id,
            Contact.deleted_at.is_(None),
            or_(
                func.lower(Contact.company_name).like(func.lower(pattern)),
                func.lower(Contact.email).like(func.lower(pattern)),
                func.lower(Contact.city).like(func.lower(pattern)),
                func.lower(Contact.cui).like(func.lower(pattern)),
            ),
        )
        .limit(limit)
    )
    contacts_result = await db.execute(contacts_q)
    contacts = [
        {
            "id": str(c.id),
            "company_name": c.company_name,
            "stage": c.stage or "",
            "city": c.city,
        }
        for c in contacts_result.scalars().all()
    ]

    # Opportunities
    opps_q = (
        select(Opportunity)
        .where(
            Opportunity.organization_id == org_id,
            Opportunity.deleted_at.is_(None),
            or_(
                func.lower(Opportunity.title).like(func.lower(pattern)),
                func.lower(Opportunity.description).like(func.lower(pattern)),
            ),
        )
        .limit(limit)
    )
    opps_result = await db.execute(opps_q)
    opportunities = [
        {
            "id": str(o.id),
            "title": o.title,
            "stage": o.stage or "",
            "estimated_value": float(o.estimated_value) if o.estimated_value else None,
        }
        for o in opps_result.scalars().all()
    ]

    # Projects
    projects_q = (
        select(Project)
        .where(
            Project.organization_id == org_id,
            Project.deleted_at.is_(None),
            or_(
                func.lower(Project.name).like(func.lower(pattern)),
                func.lower(Project.project_number).like(func.lower(pattern)),
            ),
        )
        .limit(limit)
    )
    projects_result = await db.execute(projects_q)
    projects = [
        {
            "id": str(p.id),
            "name": p.name,
            "project_number": p.project_number,
            "status": p.status or "",
        }
        for p in projects_result.scalars().all()
    ]

    # Offers
    offers_q = (
        select(Offer)
        .where(
            Offer.organization_id == org_id,
            Offer.deleted_at.is_(None),
            or_(
                func.lower(Offer.title).like(func.lower(pattern)),
                func.lower(Offer.offer_number).like(func.lower(pattern)),
            ),
        )
        .limit(limit)
    )
    offers_result = await db.execute(offers_q)
    offers = [
        {
            "id": str(o.id),
            "title": o.title,
            "offer_number": o.offer_number,
            "status": o.status or "",
        }
        for o in offers_result.scalars().all()
    ]

    return {
        "data": {
            "contacts": contacts,
            "opportunities": opportunities,
            "projects": projects,
            "offers": offers,
        }
    }
