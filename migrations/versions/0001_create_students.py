"""create students table

Revision ID: 0001
Revises:
Create Date: 2026-09-30 19:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("group_name", sa.String(20), nullable=False),
    )


def downgrade():
    op.drop_table("students")
