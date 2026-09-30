"""add email column to students

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-30 19:10:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("students") as batch:
        batch.add_column(sa.Column("email", sa.String(120), nullable=True))
        batch.create_index("ix_students_email", ["email"], unique=True)


def downgrade():
    # SQLite не поддерживает DROP COLUMN для всех случаев,
    # batch-режим пересоздаёт таблицу без столбца
    with op.batch_alter_table("students") as batch:
        batch.drop_index("ix_students_email")
        batch.drop_column("email")
