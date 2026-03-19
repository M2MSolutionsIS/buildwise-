"""Fix users table — add DEFAULT for is_active and is_deleted.

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add column defaults and backfill NULL values."""
    op.execute("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT true")
    op.execute("ALTER TABLE users ALTER COLUMN is_deleted SET DEFAULT false")
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET is_deleted = false WHERE is_deleted IS NULL")


def downgrade() -> None:
    """Remove column defaults."""
    op.execute("ALTER TABLE users ALTER COLUMN is_active DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN is_deleted DROP DEFAULT")
