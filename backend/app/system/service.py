"""
System module service layer — auth, user management, organization setup.
"""

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.audit import log_audit, model_to_dict
from app.config import settings
from app.system.models import (
    AuditLog,
    Currency,
    CustomFieldDefinition,
    DocumentTemplate,
    ExchangeRate,
    FeatureFlag,
    Notification,
    NotificationTemplate,
    Organization,
    Permission,
    PipelineStageConfig,
    Role,
    RolePermission,
    User,
    UserRole,
)


# ─── Auth Service ─────────────────────────────────────────────────────────────


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """Verify email+password and return User or None."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.email == email, User.is_active.is_not(False), User.is_deleted.is_not(True))
    )
    user = result.scalar_one_or_none()
    if user is None:
        logger.error("LOGIN DIAG — user not found or inactive/deleted: %s", email)
        return None
    verified = verify_password(password, user.password_hash)
    logger.error(
        "LOGIN DIAG — user=%s is_active=%s is_deleted=%s hash_prefix=%s verified=%s",
        email,
        user.is_active,
        user.is_deleted,
        user.password_hash[:20] if user.password_hash else "NULL",
        verified,
    )
    if not verified:
        return None
    return user


async def login_user(
    db: AsyncSession,
    user: User,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    """
    Generate tokens for an authenticated user and update last_login.
    Returns token dict.
    """
    role_codes = [ur.role.code for ur in user.user_roles if ur.role]

    token_data = {
        "sub": str(user.id),
        "org": str(user.organization_id),
        "roles": role_codes,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token & update last_login
    user.refresh_token = refresh_token
    user.last_login = datetime.now(timezone.utc)
    db.add(user)

    # Audit
    await log_audit(
        db,
        user_id=user.id,
        organization_id=user.organization_id,
        action="LOGIN",
        entity_type="users",
        entity_id=user.id,
        new_values={"login_at": user.last_login.isoformat()},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict | None:
    """Validate refresh token and issue new token pair."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(
            User.id == uuid.UUID(user_id),
            User.is_active.is_(True),
            User.is_deleted.is_(False),
            User.refresh_token == refresh_token,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None

    return await login_user(db, user)


async def logout_user(db: AsyncSession, user: User) -> None:
    """Invalidate the user's refresh token."""
    user.refresh_token = None
    db.add(user)

    await log_audit(
        db,
        user_id=user.id,
        organization_id=user.organization_id,
        action="LOGOUT",
        entity_type="users",
        entity_id=user.id,
    )


# ─── User Registration ───────────────────────────────────────────────────────


async def register_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone: str | None = None,
    organization_name: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> User:
    """
    Register a new user. If organization_name is provided, create a new org
    and make the user its admin. Otherwise, validation should ensure an org context.
    """
    # Check duplicate email
    existing = await db.execute(
        select(func.count()).select_from(User).where(User.email == email)
    )
    if existing.scalar() > 0:
        raise ValueError("Email already registered")

    # Create organization if needed
    if organization_name:
        slug = organization_name.lower().replace(" ", "-")[:100]
        # Ensure unique slug
        slug_check = await db.execute(
            select(func.count()).select_from(Organization).where(Organization.slug == slug)
        )
        if slug_check.scalar() > 0:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        org = Organization(
            id=uuid.uuid4(),
            name=organization_name,
            slug=slug,
            active_prototype=settings.DEFAULT_PROTOTYPE,
        )
        db.add(org)
        await db.flush()
        org_id = org.id
    else:
        raise ValueError("organization_name is required for registration")

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        organization_id=org_id,
        is_active=True,
        gdpr_consent=True,
        gdpr_consent_date=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    # Assign default admin role
    await _ensure_default_roles(db, org_id)
    admin_role = await db.execute(
        select(Role).where(Role.code == "admin", Role.organization_id == org_id)
    )
    admin_role = admin_role.scalar_one_or_none()
    if admin_role:
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=user.id,
            role_id=admin_role.id,
        )
        db.add(user_role)

    # Audit
    await log_audit(
        db,
        user_id=user.id,
        organization_id=org_id,
        action="CREATE",
        entity_type="users",
        entity_id=user.id,
        new_values=model_to_dict(user),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return user


# ─── Default Roles & Permissions ──────────────────────────────────────────────

DEFAULT_ROLES = [
    {"code": "admin", "name": "Administrator", "description": "Full access within organization"},
    {"code": "manager_vanzari", "name": "Manager Vânzări", "description": "CRM + Pipeline + Reports + Dashboards, read PM"},
    {"code": "agent_comercial", "name": "Agent Comercial", "description": "CRM + own Pipeline + Activities"},
    {"code": "tehnician", "name": "Tehnician", "description": "PM + Execution + Measurements, read-only CRM"},
]

DEFAULT_PERMISSIONS = [
    # CRM
    ("crm", "create"), ("crm", "read"), ("crm", "update"), ("crm", "delete"),
    # Pipeline
    ("pipeline", "create"), ("pipeline", "read"), ("pipeline", "update"), ("pipeline", "delete"),
    # PM
    ("pm", "create"), ("pm", "read"), ("pm", "update"), ("pm", "delete"),
    # RM
    ("rm", "create"), ("rm", "read"), ("rm", "update"), ("rm", "delete"),
    # BI
    ("bi", "create"), ("bi", "read"), ("bi", "update"), ("bi", "delete"),
    # System
    ("system", "create"), ("system", "read"), ("system", "update"), ("system", "delete"),
]

ROLE_PERMISSION_MAP = {
    "admin": [
        ("crm", "create"), ("crm", "read"), ("crm", "update"), ("crm", "delete"),
        ("pipeline", "create"), ("pipeline", "read"), ("pipeline", "update"), ("pipeline", "delete"),
        ("pm", "create"), ("pm", "read"), ("pm", "update"), ("pm", "delete"),
        ("rm", "create"), ("rm", "read"), ("rm", "update"), ("rm", "delete"),
        ("bi", "create"), ("bi", "read"), ("bi", "update"), ("bi", "delete"),
        ("system", "create"), ("system", "read"), ("system", "update"), ("system", "delete"),
    ],
    "manager_vanzari": [
        ("crm", "create"), ("crm", "read"), ("crm", "update"), ("crm", "delete"),
        ("pipeline", "create"), ("pipeline", "read"), ("pipeline", "update"), ("pipeline", "delete"),
        ("pm", "read"),
        ("bi", "read"),
        ("system", "read"),
    ],
    "agent_comercial": [
        ("crm", "create"), ("crm", "read"), ("crm", "update"),
        ("pipeline", "create"), ("pipeline", "read"), ("pipeline", "update"),
    ],
    "tehnician": [
        ("crm", "read"),
        ("pm", "create"), ("pm", "read"), ("pm", "update"),
    ],
}


async def _ensure_default_roles(db: AsyncSession, org_id: uuid.UUID) -> None:
    """Create default roles and permissions for a new organization."""
    # Check if roles already exist
    existing = await db.execute(
        select(func.count()).select_from(Role).where(Role.organization_id == org_id)
    )
    if existing.scalar() > 0:
        return

    # Ensure global permissions exist
    for module, action in DEFAULT_PERMISSIONS:
        check = await db.execute(
            select(Permission).where(
                Permission.module == module, Permission.action == action
            )
        )
        if check.scalar_one_or_none() is None:
            db.add(
                Permission(
                    id=uuid.uuid4(),
                    module=module,
                    action=action,
                    description=f"{action.title()} access to {module} module",
                )
            )
    await db.flush()

    # Create roles
    for role_data in DEFAULT_ROLES:
        role = Role(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=role_data["name"],
            code=role_data["code"],
            description=role_data["description"],
            is_system=True,
        )
        db.add(role)
        await db.flush()

        # Assign permissions to role
        for module, action in ROLE_PERMISSION_MAP.get(role_data["code"], []):
            perm = await db.execute(
                select(Permission).where(
                    Permission.module == module, Permission.action == action
                )
            )
            perm = perm.scalar_one_or_none()
            if perm:
                db.add(
                    RolePermission(
                        id=uuid.uuid4(),
                        role_id=role.id,
                        permission_id=perm.id,
                    )
                )

    await db.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# F040 — RBAC Admin (CRUD roles, permissions, user-role assignment)
# ═══════════════════════════════════════════════════════════════════════════════


async def create_role(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    name: str,
    code: str,
    description: str | None = None,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Role:
    role = Role(
        id=uuid.uuid4(),
        organization_id=org_id,
        name=name,
        code=code,
        description=description,
        is_system=False,
    )
    db.add(role)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="roles", entity_id=role.id,
                    new_values=model_to_dict(role), ip_address=ip_address, user_agent=user_agent)
    return role


async def update_role(
    db: AsyncSession,
    org_id: uuid.UUID,
    role_id: uuid.UUID,
    *,
    name: str | None = None,
    description: str | None = None,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Role | None:
    result = await db.execute(
        select(Role).where(Role.id == role_id, Role.organization_id == org_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        return None
    old = model_to_dict(role)
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="roles", entity_id=role.id,
                    old_values=old, new_values=model_to_dict(role),
                    ip_address=ip_address, user_agent=user_agent)
    return role


async def delete_role(
    db: AsyncSession,
    org_id: uuid.UUID,
    role_id: uuid.UUID,
    *,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(Role).where(Role.id == role_id, Role.organization_id == org_id, Role.is_system.is_(False))
    )
    role = result.scalar_one_or_none()
    if not role:
        return False
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="DELETE", entity_type="roles", entity_id=role.id,
                    old_values=model_to_dict(role), ip_address=ip_address, user_agent=user_agent)
    await db.delete(role)
    return True


async def list_permissions(db: AsyncSession) -> list[Permission]:
    result = await db.execute(select(Permission))
    return list(result.scalars().all())


async def assign_permissions_to_role(
    db: AsyncSession,
    org_id: uuid.UUID,
    role_id: uuid.UUID,
    permission_ids: list[uuid.UUID],
    *,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(Role).where(Role.id == role_id, Role.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        return False
    existing = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role_id)
    )
    for rp in existing.scalars().all():
        await db.delete(rp)
    await db.flush()
    for pid in permission_ids:
        db.add(RolePermission(id=uuid.uuid4(), role_id=role_id, permission_id=pid))
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="role_permissions", entity_id=role_id,
                    new_values={"permission_ids": [str(p) for p in permission_ids]},
                    ip_address=ip_address, user_agent=user_agent)
    return True


async def assign_roles_to_user(
    db: AsyncSession,
    org_id: uuid.UUID,
    target_user_id: uuid.UUID,
    role_ids: list[uuid.UUID],
    *,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> bool:
    result = await db.execute(
        select(User).where(User.id == target_user_id, User.organization_id == org_id)
    )
    if not result.scalar_one_or_none():
        return False
    existing = await db.execute(
        select(UserRole).where(UserRole.user_id == target_user_id)
    )
    for ur in existing.scalars().all():
        await db.delete(ur)
    await db.flush()
    for rid in role_ids:
        db.add(UserRole(id=uuid.uuid4(), user_id=target_user_id, role_id=rid))
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="user_roles", entity_id=target_user_id,
                    new_values={"role_ids": [str(r) for r in role_ids]},
                    ip_address=ip_address, user_agent=user_agent)
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# F041 — Audit Log (filtered)
# ═══════════════════════════════════════════════════════════════════════════════


async def list_audit_logs_filtered(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    audit_user_id: str | None = None,
    action: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AuditLog], int]:
    q = select(AuditLog).where(AuditLog.organization_id == org_id)
    count_q = select(func.count()).select_from(AuditLog).where(AuditLog.organization_id == org_id)
    if entity_type:
        q = q.where(AuditLog.entity_type == entity_type)
        count_q = count_q.where(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.where(AuditLog.entity_id == entity_id)
        count_q = count_q.where(AuditLog.entity_id == entity_id)
    if audit_user_id:
        q = q.where(AuditLog.user_id == uuid.UUID(audit_user_id))
        count_q = count_q.where(AuditLog.user_id == uuid.UUID(audit_user_id))
    if action:
        q = q.where(AuditLog.action == action)
        count_q = count_q.where(AuditLog.action == action)
    if date_from:
        q = q.where(AuditLog.timestamp >= date_from)
        count_q = count_q.where(AuditLog.timestamp >= date_from)
    if date_to:
        q = q.where(AuditLog.timestamp <= date_to)
        count_q = count_q.where(AuditLog.timestamp <= date_to)

    total = (await db.execute(count_q)).scalar()
    result = await db.execute(
        q.order_by(AuditLog.timestamp.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ═══════════════════════════════════════════════════════════════════════════════
# F039 — Custom Fields CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def list_custom_fields(
    db: AsyncSession, org_id: uuid.UUID, entity_type: str | None = None
) -> list[CustomFieldDefinition]:
    q = select(CustomFieldDefinition).where(CustomFieldDefinition.organization_id == org_id)
    if entity_type:
        q = q.where(CustomFieldDefinition.entity_type == entity_type)
    result = await db.execute(q.order_by(CustomFieldDefinition.sort_order))
    return list(result.scalars().all())


async def create_custom_field(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> CustomFieldDefinition:
    field = CustomFieldDefinition(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(field)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="custom_field_definitions", entity_id=field.id,
                    new_values=model_to_dict(field), ip_address=ip_address, user_agent=user_agent)
    return field


async def update_custom_field(
    db: AsyncSession, org_id: uuid.UUID, field_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> CustomFieldDefinition | None:
    result = await db.execute(
        select(CustomFieldDefinition).where(
            CustomFieldDefinition.id == field_id, CustomFieldDefinition.organization_id == org_id
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        return None
    old = model_to_dict(field)
    for k, v in data.items():
        if v is not None:
            setattr(field, k, v)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="custom_field_definitions", entity_id=field.id,
                    old_values=old, new_values=model_to_dict(field),
                    ip_address=ip_address, user_agent=user_agent)
    return field


# ═══════════════════════════════════════════════════════════════════════════════
# F106 — Document Templates CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def list_document_templates(
    db: AsyncSession, org_id: uuid.UUID, template_type: str | None = None
) -> list[DocumentTemplate]:
    q = select(DocumentTemplate).where(DocumentTemplate.organization_id == org_id)
    if template_type:
        q = q.where(DocumentTemplate.template_type == template_type)
    result = await db.execute(q.order_by(DocumentTemplate.created_at.desc()))
    return list(result.scalars().all())


async def create_document_template(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> DocumentTemplate:
    tmpl = DocumentTemplate(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(tmpl)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="document_templates", entity_id=tmpl.id,
                    new_values=model_to_dict(tmpl), ip_address=ip_address, user_agent=user_agent)
    return tmpl


async def update_document_template(
    db: AsyncSession, org_id: uuid.UUID, tmpl_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> DocumentTemplate | None:
    result = await db.execute(
        select(DocumentTemplate).where(
            DocumentTemplate.id == tmpl_id, DocumentTemplate.organization_id == org_id
        )
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        return None
    old = model_to_dict(tmpl)
    for k, v in data.items():
        if v is not None:
            setattr(tmpl, k, v)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="document_templates", entity_id=tmpl.id,
                    old_values=old, new_values=model_to_dict(tmpl),
                    ip_address=ip_address, user_agent=user_agent)
    return tmpl


# ═══════════════════════════════════════════════════════════════════════════════
# F136 — Pipeline Stage Config + Feature Flags
# ═══════════════════════════════════════════════════════════════════════════════


async def list_pipeline_stage_configs(db: AsyncSession, org_id: uuid.UUID) -> list[PipelineStageConfig]:
    result = await db.execute(
        select(PipelineStageConfig).where(PipelineStageConfig.organization_id == org_id)
        .order_by(PipelineStageConfig.sort_order)
    )
    return list(result.scalars().all())


async def create_pipeline_stage_config(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> PipelineStageConfig:
    stage = PipelineStageConfig(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(stage)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="pipeline_stage_configs", entity_id=stage.id,
                    new_values=model_to_dict(stage), ip_address=ip_address, user_agent=user_agent)
    return stage


async def update_pipeline_stage_config(
    db: AsyncSession, org_id: uuid.UUID, stage_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> PipelineStageConfig | None:
    result = await db.execute(
        select(PipelineStageConfig).where(
            PipelineStageConfig.id == stage_id, PipelineStageConfig.organization_id == org_id
        )
    )
    stage = result.scalar_one_or_none()
    if not stage:
        return None
    old = model_to_dict(stage)
    for k, v in data.items():
        if v is not None:
            setattr(stage, k, v)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="pipeline_stage_configs", entity_id=stage.id,
                    old_values=old, new_values=model_to_dict(stage),
                    ip_address=ip_address, user_agent=user_agent)
    return stage


async def list_feature_flags(db: AsyncSession, org_id: uuid.UUID) -> list[FeatureFlag]:
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.organization_id == org_id)
    )
    return list(result.scalars().all())


async def update_feature_flag(
    db: AsyncSession, org_id: uuid.UUID, flag_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> FeatureFlag | None:
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id, FeatureFlag.organization_id == org_id)
    )
    flag = result.scalar_one_or_none()
    if not flag:
        return None
    old = model_to_dict(flag)
    for k, v in data.items():
        if v is not None:
            setattr(flag, k, v)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="feature_flags", entity_id=flag.id,
                    old_values=old, new_values=model_to_dict(flag),
                    ip_address=ip_address, user_agent=user_agent)
    return flag


# ═══════════════════════════════════════════════════════════════════════════════
# F139 — Currency + Exchange Rate CRUD
# ═══════════════════════════════════════════════════════════════════════════════


async def list_currencies(db: AsyncSession, org_id: uuid.UUID) -> list[Currency]:
    result = await db.execute(
        select(Currency).where(Currency.organization_id == org_id)
    )
    return list(result.scalars().all())


async def create_currency(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> Currency:
    cur = Currency(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(cur)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="currencies", entity_id=cur.id,
                    new_values=model_to_dict(cur), ip_address=ip_address, user_agent=user_agent)
    return cur


async def update_currency(
    db: AsyncSession, org_id: uuid.UUID, cur_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> Currency | None:
    result = await db.execute(
        select(Currency).where(Currency.id == cur_id, Currency.organization_id == org_id)
    )
    cur = result.scalar_one_or_none()
    if not cur:
        return None
    old = model_to_dict(cur)
    for k, v in data.items():
        if v is not None:
            setattr(cur, k, v)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="UPDATE", entity_type="currencies", entity_id=cur.id,
                    old_values=old, new_values=model_to_dict(cur),
                    ip_address=ip_address, user_agent=user_agent)
    return cur


async def list_exchange_rates(
    db: AsyncSession, org_id: uuid.UUID, from_currency: str | None = None
) -> list[ExchangeRate]:
    q = select(ExchangeRate).where(ExchangeRate.organization_id == org_id)
    if from_currency:
        q = q.where(ExchangeRate.from_currency == from_currency)
    result = await db.execute(q.order_by(ExchangeRate.effective_date.desc()))
    return list(result.scalars().all())


async def create_exchange_rate(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> ExchangeRate:
    rate = ExchangeRate(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(rate)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="exchange_rates", entity_id=rate.id,
                    new_values=model_to_dict(rate), ip_address=ip_address, user_agent=user_agent)
    return rate


# ═══════════════════════════════════════════════════════════════════════════════
# F140 — TrueCast (Actual vs Forecast)
# ═══════════════════════════════════════════════════════════════════════════════


async def get_truecast_data(db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID | None = None) -> list[dict]:
    """Cross-module Actual vs Forecast comparison."""
    from app.pm.models import Project, Task, DevizItem
    q = select(Project).where(Project.organization_id == org_id, Project.is_deleted.is_(False))
    if project_id:
        q = q.where(Project.id == project_id)
    projects = (await db.execute(q)).scalars().all()
    results = []
    for proj in projects:
        tasks = (await db.execute(
            select(Task).where(Task.project_id == proj.id)
        )).scalars().all()
        hours_est = sum(t.estimated_hours or 0 for t in tasks)
        hours_act = sum(t.actual_hours or 0 for t in tasks)
        deviz_items = (await db.execute(
            select(DevizItem).where(DevizItem.project_id == proj.id)
        )).scalars().all()
        deviz_est = sum((d.quantity or 0) * (d.unit_price or 0) for d in deviz_items)
        deviz_act = sum(d.actual_total or 0 for d in deviz_items)
        budget_forecast = proj.budget_allocated or 0
        budget_actual = proj.budget_actual or 0
        cpi = (budget_forecast / budget_actual) if budget_actual and budget_actual > 0 else None
        results.append({
            "project_id": proj.id,
            "project_name": proj.name,
            "planned_start": proj.planned_start_date,
            "planned_end": proj.planned_end_date,
            "actual_start": proj.actual_start_date,
            "actual_end": proj.actual_end_date,
            "schedule_variance_days": (
                (proj.actual_end_date - proj.planned_end_date).days
                if proj.actual_end_date and proj.planned_end_date else None
            ),
            "budget_forecast": budget_forecast,
            "budget_actual": budget_actual,
            "budget_variance": budget_forecast - (budget_actual or 0),
            "hours_estimated": hours_est,
            "hours_actual": hours_act,
            "hours_variance": hours_est - hours_act,
            "deviz_estimated": deviz_est,
            "deviz_actual": deviz_act,
            "deviz_variance": deviz_est - deviz_act,
            "cpi": cpi,
            "spi": None,
            "invoiced_forecast": 0.0,
            "invoiced_actual": 0.0,
            "invoiced_variance": 0.0,
        })
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# F141 — Notifications
# ═══════════════════════════════════════════════════════════════════════════════


async def list_notifications(
    db: AsyncSession, user_id: uuid.UUID, org_id: uuid.UUID,
    status: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[Notification], int]:
    q = select(Notification).where(
        Notification.user_id == user_id, Notification.organization_id == org_id
    )
    count_q = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id, Notification.organization_id == org_id
    )
    if status:
        q = q.where(Notification.status == status)
        count_q = count_q.where(Notification.status == status)
    total = (await db.execute(count_q)).scalar()
    result = await db.execute(
        q.order_by(Notification.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def create_notification(
    db: AsyncSession, org_id: uuid.UUID, target_user_id: uuid.UUID, *, data: dict,
) -> Notification:
    notif = Notification(
        id=uuid.uuid4(), organization_id=org_id, user_id=target_user_id, **data
    )
    db.add(notif)
    await db.flush()
    return notif


async def mark_notification_read(
    db: AsyncSession, notif_id: uuid.UUID, user_id: uuid.UUID,
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == user_id)
    )
    notif = result.scalar_one_or_none()
    if not notif:
        return None
    notif.status = "read"
    notif.read_at = datetime.now(timezone.utc)
    await db.flush()
    return notif


async def list_notification_templates(
    db: AsyncSession, org_id: uuid.UUID,
) -> list[NotificationTemplate]:
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.organization_id == org_id)
    )
    return list(result.scalars().all())


async def create_notification_template(
    db: AsyncSession, org_id: uuid.UUID, *, data: dict,
    user_id: uuid.UUID | None = None, ip_address: str | None = None, user_agent: str | None = None,
) -> NotificationTemplate:
    tmpl = NotificationTemplate(id=uuid.uuid4(), organization_id=org_id, **data)
    db.add(tmpl)
    await db.flush()
    await log_audit(db, user_id=user_id, organization_id=org_id,
                    action="CREATE", entity_type="notification_templates", entity_id=tmpl.id,
                    new_values=model_to_dict(tmpl), ip_address=ip_address, user_agent=user_agent)
    return tmpl


async def generate_follow_up_notifications(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID,
) -> list[Notification]:
    """
    F141: Auto-generate follow-up reminder notifications.
    Checks activities and interactions that need follow-up and creates notifications.
    """
    from app.pipeline.models import Activity
    from app.crm.models import Interaction

    now = datetime.now(timezone.utc)
    created = []

    # Check overdue activities (scheduled in the past, still planned)
    overdue_q = select(Activity).where(
        Activity.organization_id == org_id,
        Activity.status == "planned",
        Activity.scheduled_date < now,
    ).limit(50)
    overdue_activities = (await db.execute(overdue_q)).scalars().all()

    for act in overdue_activities:
        # Check if notification already exists for this entity
        existing = await db.execute(
            select(Notification).where(
                Notification.organization_id == org_id,
                Notification.entity_type == "activity",
                Notification.entity_id == act.id,
                Notification.status == "unread",
            )
        )
        if existing.scalar_one_or_none():
            continue

        notif = Notification(
            id=uuid.uuid4(),
            organization_id=org_id,
            user_id=act.owner_id or user_id,
            title=f"Activitate restantă: {act.title}",
            message=f"Activitatea '{act.title}' programată pentru {act.scheduled_date.strftime('%d.%m.%Y')} nu a fost finalizată.",
            entity_type="activity",
            entity_id=act.id,
            link=f"/pipeline/opportunities/{act.opportunity_id}" if act.opportunity_id else None,
        )
        db.add(notif)
        created.append(notif)

    # Check contacts without recent interactions (>30 days)
    thirty_days_ago = now - __import__("datetime").timedelta(days=30)
    from sqlalchemy import and_
    from app.crm.models import Contact

    stale_contacts_q = (
        select(Contact)
        .where(
            Contact.organization_id == org_id,
            Contact.is_deleted.is_(False),
            Contact.stage.in_(["prospect", "active", "lead"]),
        )
        .outerjoin(
            Interaction,
            and_(
                Interaction.contact_id == Contact.id,
                Interaction.interaction_date > thirty_days_ago,
            ),
        )
        .where(Interaction.id.is_(None))
        .limit(20)
    )
    stale_contacts = (await db.execute(stale_contacts_q)).scalars().all()

    for contact in stale_contacts:
        existing = await db.execute(
            select(Notification).where(
                Notification.organization_id == org_id,
                Notification.entity_type == "contact",
                Notification.entity_id == contact.id,
                Notification.status == "unread",
            )
        )
        if existing.scalar_one_or_none():
            continue

        notif = Notification(
            id=uuid.uuid4(),
            organization_id=org_id,
            user_id=contact.created_by or user_id,
            title=f"Follow-up necesar: {contact.company_name}",
            message=f"Contactul '{contact.company_name}' nu a avut interacțiuni în ultimele 30 de zile.",
            entity_type="contact",
            entity_id=contact.id,
            link=f"/crm/contacts/{contact.id}",
        )
        db.add(notif)
        created.append(notif)

    await db.flush()
    return created


# ═══════════════════════════════════════════════════════════════════════════════
# F142 — Report Export
# ═══════════════════════════════════════════════════════════════════════════════


async def export_report(
    db: AsyncSession, org_id: uuid.UUID, *,
    report_type: str, format: str = "json", filters: dict | None = None,
    project_id: uuid.UUID | None = None,
) -> dict:
    """Generate report data for export."""
    data = []
    record_count = 0
    if report_type == "contacts":
        from app.crm.models import Contact
        q = select(Contact).where(Contact.organization_id == org_id, Contact.is_deleted.is_(False))
        contacts = (await db.execute(q)).scalars().all()
        data = [model_to_dict(c) for c in contacts]
        record_count = len(data)
    elif report_type == "projects":
        from app.pm.models import Project
        q = select(Project).where(Project.organization_id == org_id, Project.is_deleted.is_(False))
        projects = (await db.execute(q)).scalars().all()
        data = [model_to_dict(p) for p in projects]
        record_count = len(data)
    elif report_type == "pipeline":
        from app.pipeline.models import Opportunity
        q = select(Opportunity).where(Opportunity.organization_id == org_id, Opportunity.is_deleted.is_(False))
        opps = (await db.execute(q)).scalars().all()
        data = [model_to_dict(o) for o in opps]
        record_count = len(data)
    elif report_type == "audit_logs":
        q = select(AuditLog).where(AuditLog.organization_id == org_id).limit(1000)
        logs = (await db.execute(q)).scalars().all()
        data = [model_to_dict(lg) for lg in logs]
        record_count = len(data)
    return {
        "report_type": report_type,
        "format": format,
        "generated_at": datetime.now(timezone.utc),
        "record_count": record_count,
        "data": data,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# F143 — Sync Journal
# ═══════════════════════════════════════════════════════════════════════════════


async def get_sync_status(db: AsyncSession, org_id: uuid.UUID) -> list[dict]:
    """Cross-module sync status."""
    modules = [
        ("crm", "contacts", "app.crm.models", "Contact"),
        ("pipeline", "opportunities", "app.pipeline.models", "Opportunity"),
        ("pm", "projects", "app.pm.models", "Project"),
    ]
    results = []
    for mod, entity, mod_path, cls_name in modules:
        import importlib
        m = importlib.import_module(mod_path)
        model_cls = getattr(m, cls_name)
        count_q = select(func.count()).select_from(model_cls).where(
            model_cls.organization_id == org_id
        )
        total = (await db.execute(count_q)).scalar()
        last_audit = await db.execute(
            select(AuditLog.timestamp).where(
                AuditLog.organization_id == org_id,
                AuditLog.entity_type == entity,
            ).order_by(AuditLog.timestamp.desc()).limit(1)
        )
        last_ts = last_audit.scalar_one_or_none()
        results.append({
            "module": mod,
            "entity_type": entity,
            "total_records": total,
            "last_sync": last_ts,
            "errors": [],
            "status": "ok",
        })
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# GDPR — Data Export, Deletion, Audit Trail
# ═══════════════════════════════════════════════════════════════════════════════


async def gdpr_export_my_data(
    db: AsyncSession, user: User,
) -> dict:
    """GDPR: Export all personal data for the requesting user."""
    from app.crm.models import Contact
    from app.pipeline.models import Opportunity

    org_id = user.organization_id

    # User profile data (exclude sensitive fields)
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization_id": str(org_id),
        "is_active": user.is_active,
        "gdpr_consent": user.gdpr_consent,
        "gdpr_consent_date": user.gdpr_consent_date.isoformat() if user.gdpr_consent_date else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }

    # Contacts created by this user
    contacts_q = await db.execute(
        select(Contact).where(
            Contact.organization_id == org_id,
            Contact.created_by == user.id,
            Contact.is_deleted.is_(False),
        )
    )
    contacts = [model_to_dict(c) for c in contacts_q.scalars().all()]

    # Opportunities owned by this user
    opps_q = await db.execute(
        select(Opportunity).where(
            Opportunity.organization_id == org_id,
            Opportunity.owner_id == user.id,
            Opportunity.is_deleted.is_(False),
        )
    )
    opportunities = [model_to_dict(o) for o in opps_q.scalars().all()]

    # Audit entries for this user
    audit_q = await db.execute(
        select(AuditLog).where(
            AuditLog.user_id == user.id,
        ).order_by(AuditLog.timestamp.desc()).limit(500)
    )
    audit_entries = [model_to_dict(a) for a in audit_q.scalars().all()]

    # Log this export as an audit entry
    await log_audit(
        db, user_id=user.id, organization_id=org_id,
        action="GDPR_EXPORT", entity_type="users", entity_id=user.id,
        new_values={"exported_fields": ["profile", "contacts", "opportunities", "audit"]},
    )

    return {
        "user": user_data,
        "contacts_owned": contacts,
        "opportunities_owned": opportunities,
        "audit_entries": audit_entries,
        "exported_at": datetime.now(timezone.utc),
    }


async def gdpr_delete_my_data(
    db: AsyncSession, user: User,
    ip_address: str | None = None, user_agent: str | None = None,
) -> dict:
    """GDPR: Anonymize/delete personal data for the requesting user (right to erasure)."""
    org_id = user.organization_id
    anonymized = {"user": False, "contacts": 0, "notifications": 0}

    # Anonymize user data (keep record for audit, but remove PII)
    old_data = model_to_dict(user)
    user.email = f"deleted-{user.id}@anonymized.local"
    user.first_name = "DELETED"
    user.last_name = "USER"
    user.phone = None
    user.is_active = False
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    user.gdpr_consent = False
    user.refresh_token = None
    anonymized["user"] = True

    # Remove user's notifications
    notifs_q = await db.execute(
        select(Notification).where(
            Notification.user_id == user.id,
            Notification.organization_id == org_id,
        )
    )
    notifs = notifs_q.scalars().all()
    for n in notifs:
        await db.delete(n)
    anonymized["notifications"] = len(notifs)

    await db.flush()

    # Log the deletion
    await log_audit(
        db, user_id=user.id, organization_id=org_id,
        action="GDPR_DELETE", entity_type="users", entity_id=user.id,
        old_values=old_data,
        new_values={"status": "anonymized"},
        ip_address=ip_address, user_agent=user_agent,
    )

    return {
        "anonymized_entities": anonymized,
        "deleted_at": datetime.now(timezone.utc),
        "message": "Datele personale au fost anonimizate conform GDPR.",
    }


async def gdpr_audit_trail(
    db: AsyncSession, user: User,
    page: int = 1, per_page: int = 50,
) -> tuple[list[dict], int]:
    """GDPR: Show audit trail of all operations involving the user's data."""
    count_q = select(func.count()).select_from(AuditLog).where(
        AuditLog.user_id == user.id,
    )
    total = (await db.execute(count_q)).scalar()

    q = (
        select(AuditLog)
        .where(AuditLog.user_id == user.id)
        .order_by(AuditLog.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    entries = [model_to_dict(a) for a in result.scalars().all()]
    return entries, total
