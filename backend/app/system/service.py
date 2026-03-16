"""
System module service layer — auth, user management, organization setup.
"""

import uuid
from datetime import datetime, timezone

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
    Organization,
    Permission,
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
        .where(User.email == email, User.is_active.is_(True), User.is_deleted.is_(False))
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
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
