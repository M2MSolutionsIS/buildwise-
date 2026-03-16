"""
System module router — auth endpoints, health, user management.

Endpoints:
  POST /api/auth/login        — JWT login
  POST /api/auth/refresh      — Refresh token pair
  POST /api/auth/logout       — Invalidate refresh token
  POST /api/auth/register     — Register new user + organization
  GET  /api/health            — Health check
  GET  /api/v1/me             — Current user profile
  GET  /api/v1/system/roles   — List roles (admin)
  GET  /api/v1/system/audit-logs — List audit logs (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_user, get_db, get_request_info
from app.core.rbac import require_role
from app.system import service
from app.system.models import AuditLog, Role, UserRole
from app.system.schemas import (
    ApiResponse,
    AuditLogOut,
    ChangePasswordRequest,
    HealthResponse,
    LoginRequest,
    Meta,
    RefreshRequest,
    RegisterRequest,
    RoleOut,
    TokenResponse,
    UserOut,
    UserUpdate,
)

# ─── Public routers (no auth) ────────────────────────────────────────────────

health_router = APIRouter(tags=["Health"])
auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ─── Protected routers ───────────────────────────────────────────────────────

user_router = APIRouter(prefix="/api/v1", tags=["Users"])
system_router = APIRouter(prefix="/api/v1/system", tags=["System"])


# ─── Health ───────────────────────────────────────────────────────────────────


@health_router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint — returns {status: ok}."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        prototype=settings.DEFAULT_PROTOTYPE,
    )


# ─── Auth ─────────────────────────────────────────────────────────────────────


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT token pair."""
    user = await service.authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    req_info = await get_request_info(request)
    tokens = await service.login_user(
        db, user, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"]
    )
    return TokenResponse(**tokens)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh the JWT token pair using a valid refresh token."""
    tokens = await service.refresh_tokens(db, body.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return TokenResponse(**tokens)


@auth_router.post("/register", response_model=ApiResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user and organization."""
    req_info = await get_request_info(request)
    try:
        user = await service.register_user(
            db,
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
            organization_name=body.organization_name or f"{body.first_name}'s Organization",
            ip_address=req_info["ip_address"],
            user_agent=req_info["user_agent"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ApiResponse(data=UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
        language=user.language,
        last_login=user.last_login,
        created_at=user.created_at,
        roles=["admin"],
    ))


@auth_router.post("/logout", status_code=204)
async def logout(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invalidate the current user's refresh token."""
    await service.logout_user(db, current_user)


# ─── Current User ────────────────────────────────────────────────────────────


@user_router.get("/me", response_model=ApiResponse)
async def get_me(current_user=Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    roles = [ur.role.code for ur in current_user.user_roles if ur.role]
    return ApiResponse(data=UserOut(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        organization_id=current_user.organization_id,
        language=current_user.language,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        roles=roles,
    ))


# ─── System Admin endpoints ──────────────────────────────────────────────────


@system_router.get(
    "/roles",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_roles(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all roles for the current organization."""
    result = await db.execute(
        select(Role).where(Role.organization_id == current_user.organization_id)
    )
    roles = result.scalars().all()
    return ApiResponse(
        data=[RoleOut.model_validate(r) for r in roles],
        meta=Meta(total=len(roles)),
    )


@system_router.get(
    "/audit-logs",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_audit_logs(
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs for the current organization (admin only)."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.organization_id == current_user.organization_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(per_page)
    )
    logs = result.scalars().all()

    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.organization_id == current_user.organization_id)
    )
    total = count_result.scalar()

    return ApiResponse(
        data=[AuditLogOut.model_validate(log) for log in logs],
        meta=Meta(total=total, page=page, per_page=per_page),
    )
