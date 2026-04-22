"""Add allowed_prototypes JSON column to organizations.

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-17

"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "allowed_prototypes",
            sa.JSON(),
            nullable=False,
            server_default='["P1", "P2", "P3"]',
        ),
    )


def downgrade() -> None:
    op.drop_column("organizations", "allowed_prototypes")
