"""
Audit trail — F041.

Automatic logging of all CRUD operations: who, what, when, old/new values.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.system.models import AuditLog


async def log_audit(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    organization_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """
    Create an audit log entry.

    Args:
        db: Async database session
        user_id: Who performed the action
        organization_id: Tenant isolation
        action: CREATE, UPDATE, DELETE
        entity_type: Table/model name (e.g., "contacts", "users")
        entity_id: PK of the affected record
        old_values: Previous values (for UPDATE/DELETE)
        new_values: New values (for CREATE/UPDATE)
        ip_address: Client IP
        user_agent: Client user agent string
    """
    entry = AuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(entry)
    return entry


def model_to_dict(obj, exclude: set[str] | None = None) -> dict:
    """
    Convert a SQLAlchemy model instance to a dict for audit logging.
    Excludes password_hash and other sensitive fields.
    """
    exclude = (exclude or set()) | {"password_hash", "refresh_token"}
    result = {}
    for col in obj.__table__.columns:
        if col.name in exclude:
            continue
        val = getattr(obj, col.name, None)
        # Convert UUID and datetime to string for JSON serialization
        if isinstance(val, uuid.UUID):
            val = str(val)
        elif isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return result
