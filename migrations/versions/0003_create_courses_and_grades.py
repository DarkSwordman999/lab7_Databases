"""create courses and grades tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30 19:20:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(100), nullable=False, unique=True),
        sa.Column("hours", sa.Integer, nullable=False),
        sa.CheckConstraint("hours > 0", name="ck_courses_hours_positive"),
    )
    op.create_table(
        "grades",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("student_id", sa.Integer,
                  sa.ForeignKey("students.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("course_id", sa.Integer,
                  sa.ForeignKey("courses.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("value", sa.Integer, nullable=False),
        sa.CheckConstraint("value BETWEEN 2 AND 5",
                           name="ck_grades_value_range"),
        sa.UniqueConstraint("student_id", "course_id",
                            name="uq_grades_student_course"),
    )


def downgrade():
    op.drop_table("grades")
    op.drop_table("courses")
