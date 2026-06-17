"""initial welcome system tables

Revision ID: 0001
Revises:
Create Date: 2026-05-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=32), server_default="admin", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_users_username"), "admin_users", ["username"], unique=True)

    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "faq",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("student_id", sa.String(length=32), nullable=False),
        sa.Column("id_number", sa.String(length=32), nullable=False),
        sa.Column("photo", sa.String(length=500), nullable=True),
        sa.Column("class_name", sa.String(length=200), nullable=False),
        sa.Column("dormitory", sa.String(length=200), nullable=True),
        sa.Column("advisor_name", sa.String(length=100), nullable=True),
        sa.Column("advisor_phone", sa.String(length=50), nullable=True),
        sa.Column("class_teacher_name", sa.String(length=100), nullable=True),
        sa.Column("class_teacher_phone", sa.String(length=50), nullable=True),
        sa.Column("assistant_name", sa.String(length=100), nullable=True),
        sa.Column("assistant_phone", sa.String(length=50), nullable=True),
        sa.Column("assistant_class_name", sa.String(length=200), nullable=True),
        sa.Column("role", sa.String(length=32), server_default="student", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_students_student_id"), "students", ["student_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_students_student_id"), table_name="students")
    op.drop_table("students")
    op.drop_table("faq")
    op.drop_table("announcements")
    op.drop_index(op.f("ix_admin_users_username"), table_name="admin_users")
    op.drop_table("admin_users")
