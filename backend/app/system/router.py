"""
System module router — auth, health, user management, RBAC admin, configurators,
currencies, notifications, reports, sync.

F040: RBAC Admin  |  F041: Audit Logs  |  F039: Custom Fields  |  F106: Doc Templates
F136: Pipeline Stages + Feature Flags  |  F139: Currencies  |  F140: TrueCast
F141: Notifications  |  F142: Report Export  |  F143: Sync Journal
"""

import uuid
from datetime import datetime, timezone

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
    CurrencyCreate,
    CurrencyOut,
    CurrencyUpdate,
    CustomFieldCreate,
    CustomFieldOut,
    CustomFieldUpdate,
    DocumentTemplateCreate,
    DocumentTemplateOut,
    DocumentTemplateUpdate,
    ExchangeRateCreate,
    ExchangeRateOut,
    FeatureFlagOut,
    FeatureFlagUpdate,
    HealthResponse,
    LoginRequest,
    Meta,
    NotificationCreate,
    NotificationOut,
    NotificationTemplateCreate,
    NotificationTemplateOut,
    PermissionOut,
    PipelineStageConfigCreate,
    PipelineStageConfigOut,
    PipelineStageConfigUpdate,
    RefreshRequest,
    RegisterRequest,
    ReportExportOut,
    ReportExportRequest,
    RoleCreate,
    RoleOut,
    RolePermissionAssign,
    RoleUpdate,
    SyncStatusOut,
    TokenResponse,
    TrueCastOut,
    UserOut,
    UserRoleAssign,
    UserUpdate,
)

# ─── Public routers (no auth) ────────────────────────────────────────────────

health_router = APIRouter(tags=["Health"])
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

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


# ═══════════════════════════════════════════════════════════════════════════════
# F040 — RBAC Admin CRUD
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.post(
    "/roles",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_role(
    body: RoleCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom role."""
    req_info = await get_request_info(request)
    role = await service.create_role(
        db, current_user.organization_id,
        name=body.name, code=body.code, description=body.description,
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=RoleOut.model_validate(role))


@system_router.put(
    "/roles/{role_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a role."""
    req_info = await get_request_info(request)
    role = await service.update_role(
        db, current_user.organization_id, role_id,
        name=body.name, description=body.description,
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return ApiResponse(data=RoleOut.model_validate(role))


@system_router.delete(
    "/roles/{role_id}",
    status_code=204,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_role(
    role_id: uuid.UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a non-system role."""
    req_info = await get_request_info(request)
    ok = await service.delete_role(
        db, current_user.organization_id, role_id,
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Role not found or is a system role")


@system_router.get(
    "/permissions",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_permissions(
    db: AsyncSession = Depends(get_db),
):
    """List all available permissions."""
    perms = await service.list_permissions(db)
    return ApiResponse(
        data=[PermissionOut.model_validate(p) for p in perms],
        meta=Meta(total=len(perms)),
    )


@system_router.put(
    "/roles/{role_id}/permissions",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def assign_permissions(
    role_id: uuid.UUID,
    body: RolePermissionAssign,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace permissions for a role."""
    req_info = await get_request_info(request)
    ok = await service.assign_permissions_to_role(
        db, current_user.organization_id, role_id, body.permission_ids,
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Role not found")
    return ApiResponse(data={"status": "ok"})


@system_router.put(
    "/users/{target_user_id}/roles",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def assign_user_roles(
    target_user_id: uuid.UUID,
    body: UserRoleAssign,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace roles for a user."""
    req_info = await get_request_info(request)
    ok = await service.assign_roles_to_user(
        db, current_user.organization_id, target_user_id, body.role_ids,
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(data={"status": "ok"})


# ═══════════════════════════════════════════════════════════════════════════════
# F041 — Audit Logs (filtered)
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/audit-logs/search",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def search_audit_logs(
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search audit logs with filters."""
    from datetime import datetime
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    logs, total = await service.list_audit_logs_filtered(
        db, current_user.organization_id,
        entity_type=entity_type, entity_id=entity_id,
        audit_user_id=str(user_id) if user_id else None,
        action=action, date_from=df, date_to=dt,
        page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[AuditLogOut.model_validate(log) for log in logs],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# F039 — Custom Fields
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/custom-fields",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_custom_fields(
    entity_type: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List custom field definitions."""
    fields = await service.list_custom_fields(db, current_user.organization_id, entity_type)
    return ApiResponse(
        data=[CustomFieldOut.model_validate(f) for f in fields],
        meta=Meta(total=len(fields)),
    )


@system_router.post(
    "/custom-fields",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_custom_field(
    body: CustomFieldCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a custom field definition."""
    req_info = await get_request_info(request)
    field = await service.create_custom_field(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=CustomFieldOut.model_validate(field))


@system_router.put(
    "/custom-fields/{field_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_custom_field(
    field_id: uuid.UUID,
    body: CustomFieldUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a custom field definition."""
    req_info = await get_request_info(request)
    field = await service.update_custom_field(
        db, current_user.organization_id, field_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not field:
        raise HTTPException(status_code=404, detail="Custom field not found")
    return ApiResponse(data=CustomFieldOut.model_validate(field))


# ═══════════════════════════════════════════════════════════════════════════════
# F106 — Document Templates
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/document-templates",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_document_templates(
    template_type: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List document templates."""
    templates = await service.list_document_templates(db, current_user.organization_id, template_type)
    return ApiResponse(
        data=[DocumentTemplateOut.model_validate(t) for t in templates],
        meta=Meta(total=len(templates)),
    )


@system_router.post(
    "/document-templates",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_document_template(
    body: DocumentTemplateCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a document template."""
    req_info = await get_request_info(request)
    tmpl = await service.create_document_template(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=DocumentTemplateOut.model_validate(tmpl))


@system_router.put(
    "/document-templates/{template_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_document_template(
    template_id: uuid.UUID,
    body: DocumentTemplateUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a document template."""
    req_info = await get_request_info(request)
    tmpl = await service.update_document_template(
        db, current_user.organization_id, template_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not tmpl:
        raise HTTPException(status_code=404, detail="Document template not found")
    return ApiResponse(data=DocumentTemplateOut.model_validate(tmpl))


# ═══════════════════════════════════════════════════════════════════════════════
# F136 — Pipeline Stage Configs + Feature Flags
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/pipeline-stages",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_pipeline_stages(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pipeline stage configurations."""
    stages = await service.list_pipeline_stage_configs(db, current_user.organization_id)
    return ApiResponse(
        data=[PipelineStageConfigOut.model_validate(s) for s in stages],
        meta=Meta(total=len(stages)),
    )


@system_router.post(
    "/pipeline-stages",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_pipeline_stage(
    body: PipelineStageConfigCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a pipeline stage configuration."""
    req_info = await get_request_info(request)
    stage = await service.create_pipeline_stage_config(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=PipelineStageConfigOut.model_validate(stage))


@system_router.put(
    "/pipeline-stages/{stage_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_pipeline_stage(
    stage_id: uuid.UUID,
    body: PipelineStageConfigUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a pipeline stage configuration."""
    req_info = await get_request_info(request)
    stage = await service.update_pipeline_stage_config(
        db, current_user.organization_id, stage_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not stage:
        raise HTTPException(status_code=404, detail="Pipeline stage not found")
    return ApiResponse(data=PipelineStageConfigOut.model_validate(stage))


@system_router.get(
    "/feature-flags",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_feature_flags(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List feature flags for the organization."""
    flags = await service.list_feature_flags(db, current_user.organization_id)
    return ApiResponse(
        data=[FeatureFlagOut.model_validate(f) for f in flags],
        meta=Meta(total=len(flags)),
    )


@system_router.put(
    "/feature-flags/{flag_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_feature_flag(
    flag_id: uuid.UUID,
    body: FeatureFlagUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a feature flag."""
    req_info = await get_request_info(request)
    flag = await service.update_feature_flag(
        db, current_user.organization_id, flag_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return ApiResponse(data=FeatureFlagOut.model_validate(flag))


# ═══════════════════════════════════════════════════════════════════════════════
# F139 — Currencies + Exchange Rates
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/currencies",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_currencies(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List currencies."""
    currencies = await service.list_currencies(db, current_user.organization_id)
    return ApiResponse(
        data=[CurrencyOut.model_validate(c) for c in currencies],
        meta=Meta(total=len(currencies)),
    )


@system_router.post(
    "/currencies",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_currency(
    body: CurrencyCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a currency."""
    req_info = await get_request_info(request)
    cur = await service.create_currency(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=CurrencyOut.model_validate(cur))


@system_router.put(
    "/currencies/{currency_id}",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_currency(
    currency_id: uuid.UUID,
    body: CurrencyUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a currency."""
    req_info = await get_request_info(request)
    cur = await service.update_currency(
        db, current_user.organization_id, currency_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    if not cur:
        raise HTTPException(status_code=404, detail="Currency not found")
    return ApiResponse(data=CurrencyOut.model_validate(cur))


@system_router.get(
    "/exchange-rates",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_exchange_rates(
    from_currency: str | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List exchange rates."""
    rates = await service.list_exchange_rates(db, current_user.organization_id, from_currency)
    return ApiResponse(
        data=[ExchangeRateOut.model_validate(r) for r in rates],
        meta=Meta(total=len(rates)),
    )


@system_router.post(
    "/exchange-rates",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_exchange_rate(
    body: ExchangeRateCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an exchange rate."""
    req_info = await get_request_info(request)
    rate = await service.create_exchange_rate(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=ExchangeRateOut.model_validate(rate))


# ═══════════════════════════════════════════════════════════════════════════════
# F140 — TrueCast
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/truecast",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def get_truecast(
    project_id: uuid.UUID | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """TrueCast: Actual vs Forecast comparison across modules."""
    data = await service.get_truecast_data(db, current_user.organization_id, project_id)
    return ApiResponse(
        data=[TrueCastOut(**d) for d in data],
        meta=Meta(total=len(data)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# F141 — Notifications
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/notifications",
    response_model=ApiResponse,
)
async def list_notifications(
    notification_status: str | None = None,
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    notifs, total = await service.list_notifications(
        db, current_user.id, current_user.organization_id,
        status=notification_status, page=page, per_page=per_page,
    )
    return ApiResponse(
        data=[NotificationOut.model_validate(n) for n in notifs],
        meta=Meta(total=total, page=page, per_page=per_page),
    )


@system_router.post(
    "/notifications",
    response_model=ApiResponse,
    status_code=201,
)
async def create_notification(
    body: NotificationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a notification for the current user."""
    notif = await service.create_notification(
        db, current_user.organization_id, current_user.id,
        data=body.model_dump(exclude_unset=True),
    )
    return ApiResponse(data=NotificationOut.model_validate(notif))


@system_router.put(
    "/notifications/{notification_id}/read",
    response_model=ApiResponse,
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    notif = await service.mark_notification_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return ApiResponse(data=NotificationOut.model_validate(notif))


@system_router.get(
    "/notification-templates",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def list_notification_templates(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notification templates."""
    templates = await service.list_notification_templates(db, current_user.organization_id)
    return ApiResponse(
        data=[NotificationTemplateOut.model_validate(t) for t in templates],
        meta=Meta(total=len(templates)),
    )


@system_router.post(
    "/notification-templates",
    response_model=ApiResponse,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_notification_template(
    body: NotificationTemplateCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a notification template."""
    req_info = await get_request_info(request)
    tmpl = await service.create_notification_template(
        db, current_user.organization_id,
        data=body.model_dump(exclude_unset=True),
        user_id=current_user.id, ip_address=req_info["ip_address"], user_agent=req_info["user_agent"],
    )
    return ApiResponse(data=NotificationTemplateOut.model_validate(tmpl))


@system_router.post(
    "/notifications/follow-up",
    response_model=ApiResponse,
)
async def generate_follow_ups(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate follow-up reminder notifications for overdue activities and stale contacts."""
    created = await service.generate_follow_up_notifications(
        db, current_user.organization_id, current_user.id,
    )
    return ApiResponse(
        data=[NotificationOut.model_validate(n) for n in created],
        meta=Meta(total=len(created)),
    )


@system_router.put(
    "/notifications/read-all",
    response_model=ApiResponse,
)
async def mark_all_notifications_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for the current user."""
    from app.system.models import Notification
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.organization_id == current_user.organization_id,
            Notification.status == "unread",
        )
    )
    notifs = result.scalars().all()
    now = datetime.now(timezone.utc)
    for n in notifs:
        n.status = "read"
        n.read_at = now
    await db.flush()
    return ApiResponse(data={"marked_read": len(notifs)}, meta=Meta(total=len(notifs)))


# ═══════════════════════════════════════════════════════════════════════════════
# F142 — Report Export
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.post(
    "/reports/export",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def export_report(
    body: ReportExportRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export report data."""
    result = await service.export_report(
        db, current_user.organization_id,
        report_type=body.report_type, format=body.format,
        filters=body.filters, project_id=body.project_id,
    )
    return ApiResponse(data=ReportExportOut(**result))


# ═══════════════════════════════════════════════════════════════════════════════
# F143 — Sync Journal
# ═══════════════════════════════════════════════════════════════════════════════


@system_router.get(
    "/sync-status",
    response_model=ApiResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def get_sync_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cross-module sync status."""
    data = await service.get_sync_status(db, current_user.organization_id)
    return ApiResponse(
        data=[SyncStatusOut(**d) for d in data],
        meta=Meta(total=len(data)),
    )
