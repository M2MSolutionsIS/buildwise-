"""
Common FastAPI dependencies — get_db, get_current_user, get_current_org.

Used across all modules for database sessions, authentication, and multi-tenant isolation.
"""

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import decode_token
from app.database import async_session

security = HTTPBearer()


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract and validate JWT from Authorization header.
    Returns the User ORM object with roles eagerly loaded.
    """
    from app.system.models import User, UserRole

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.id == user_uuid, User.is_active.is_(True), User.is_deleted.is_(False))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Alias that also verifies user is active (already checked in get_current_user)."""
    return current_user


def get_org_id(current_user=Depends(get_current_user)) -> uuid.UUID:
    """Extract organization_id from the authenticated user for multi-tenant queries."""
    return current_user.organization_id


async def get_request_info(request: Request) -> dict:
    """Extract IP and User-Agent from request for audit logging."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
