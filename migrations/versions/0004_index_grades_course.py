"""add index on grades.course_id

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-30 19:30:00

Отчёты по курсам выполняют JOIN по grades.course_id; индекс
позволяет не просматривать всю таблицу оценок.
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_grades_course_id", "grades", ["course_id"])


def downgrade():
    op.drop_index("ix_grades_course_id", table_name="grades")
