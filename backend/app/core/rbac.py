"""
RBAC middleware — F040.

Provides role and permission checking decorators/dependencies for FastAPI endpoints.

4 roles: SuperAdmin, OrgAdmin, Manager, User
- SuperAdmin: full platform access (is_superuser=True)
- OrgAdmin: full access within their organization (role code = "admin")
- Manager: CRM + Pipeline + Reports + Dashboards, read PM (role code = "manager_vanzari")
- User: limited access based on assigned permissions (role codes = "agent_comercial", "tehnician")
"""

from functools import wraps
from typing import Sequence

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user

# Canonical role codes (mapped to RoleEnum in system/models.py)
SUPERADMIN = "superadmin"
ORG_ADMIN = "admin"
MANAGER = "manager_vanzari"
AGENT = "agent_comercial"
TECHNICIAN = "tehnician"

# Role hierarchy: higher index = more privileges
ROLE_HIERARCHY = {
    TECHNICIAN: 0,
    AGENT: 1,
    MANAGER: 2,
    ORG_ADMIN: 3,
    SUPERADMIN: 4,
}


def _get_user_role_codes(user) -> set[str]:
    """Extract role codes from a user's loaded relationships."""
    if user.is_superuser:
        return {SUPERADMIN}
    codes = set()
    for ur in user.user_roles:
        if ur.role:
            codes.add(ur.role.code)
    return codes


def _get_max_role_level(role_codes: set[str]) -> int:
    """Get the highest role level from a set of role codes."""
    return max((ROLE_HIERARCHY.get(c, -1) for c in role_codes), default=-1)


def require_role(*allowed_roles: str):
    """
    FastAPI dependency that checks if the current user has one of the allowed roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin", "superadmin"))])
        async def admin_endpoint(): ...

    Or as a parameter dependency:
        async def endpoint(user=Depends(require_role("admin"))):
            ...
    """

    async def role_checker(current_user=Depends(get_current_user)):
        # Superusers bypass all role checks
        if current_user.is_superuser:
            return current_user

        user_roles = _get_user_role_codes(current_user)
        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required roles: "
                + ", ".join(allowed_roles),
            )
        return current_user

    return role_checker


def require_min_role(min_role: str):
    """
    FastAPI dependency that checks if user's highest role meets a minimum level.

    Usage:
        @router.get("/managers-up", dependencies=[Depends(require_min_role("manager_vanzari"))])
    """
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.is_superuser:
            return current_user

        user_roles = _get_user_role_codes(current_user)
        if _get_max_role_level(user_roles) < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires minimum role: {min_role}",
            )
        return current_user

    return role_checker


def require_permission(module: str, action: str):
    """
    FastAPI dependency that checks if user has a specific module+action permission.

    Usage:
        @router.post("/contacts", dependencies=[Depends(require_permission("crm", "create"))])
    """

    async def permission_checker(current_user=Depends(get_current_user)):
        # Superusers bypass
        if current_user.is_superuser:
            return current_user

        # Check through user_roles -> role -> permissions -> permission
        for ur in current_user.user_roles:
            if ur.role:
                for rp in ur.role.permissions:
                    if rp.permission and rp.permission.module == module and rp.permission.action == action:
                        return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {module}.{action}",
        )

    return permission_checker


def require_same_org(resource_org_id):
    """
    Utility to check that a resource belongs to the user's organization.
    Raises 404 (not 403) to avoid leaking info about other tenants.
    """

    def checker(current_user=Depends(get_current_user)):
        if current_user.is_superuser:
            return current_user
        if current_user.organization_id != resource_org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return current_user

    return checker
