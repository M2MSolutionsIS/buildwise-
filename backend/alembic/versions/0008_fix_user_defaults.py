"""Fix users table — add DEFAULT for is_active and is_deleted.

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-19

"""
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users "
        "ALTER COLUMN is_active SET DEFAULT true, "
        "ALTER COLUMN is_deleted SET DEFAULT false"
    )
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET is_deleted = false WHERE is_deleted IS NULL")


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users "
        "ALTER COLUMN is_active DROP DEFAULT, "
        "ALTER COLUMN is_deleted DROP DEFAULT"
    )
