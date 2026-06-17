"""documents：来源类型（agent_faq / student_faq / announcement）与多端外键。

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("source_kind", sa.String(length=32), nullable=True))
    op.execute(sa.text("UPDATE documents SET source_kind = 'agent_faq'"))
    op.alter_column(
        "documents",
        "source_kind",
        nullable=False,
        server_default=sa.text("'agent_faq'"),
    )

    faq_uid = postgresql.UUID(as_uuid=True)
    op.add_column("documents", sa.Column("source_student_faq_id", faq_uid, nullable=True))
    op.add_column("documents", sa.Column("source_announcement_id", faq_uid, nullable=True))

    op.create_foreign_key(
        "fk_documents_student_faq",
        "documents",
        "faq",
        ["source_student_faq_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_documents_announcement",
        "documents",
        "announcements",
        ["source_announcement_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_documents_source_student_faq_id",
        "documents",
        ["source_student_faq_id"],
        unique=False,
    )
    op.create_index(
        "ix_documents_source_announcement_id",
        "documents",
        ["source_announcement_id"],
        unique=False,
    )

    op.create_index(
        "uq_documents_agent_faq_id",
        "documents",
        ["source_faq_id"],
        unique=True,
        postgresql_where=sa.text("source_kind = 'agent_faq' AND source_faq_id IS NOT NULL"),
    )
    op.create_index(
        "uq_documents_student_faq_id",
        "documents",
        ["source_student_faq_id"],
        unique=True,
        postgresql_where=sa.text("source_kind = 'student_faq' AND source_student_faq_id IS NOT NULL"),
    )
    op.create_index(
        "uq_documents_announcement_id",
        "documents",
        ["source_announcement_id"],
        unique=True,
        postgresql_where=sa.text("source_kind = 'announcement' AND source_announcement_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_documents_announcement_id", table_name="documents")
    op.drop_index("uq_documents_student_faq_id", table_name="documents")
    op.drop_index("uq_documents_agent_faq_id", table_name="documents")
    op.drop_constraint("fk_documents_announcement", "documents", type_="foreignkey")
    op.drop_constraint("fk_documents_student_faq", "documents", type_="foreignkey")
    op.drop_index("ix_documents_source_announcement_id", table_name="documents")
    op.drop_index("ix_documents_source_student_faq_id", table_name="documents")
    op.drop_column("documents", "source_announcement_id")
    op.drop_column("documents", "source_student_faq_id")
    op.drop_column("documents", "source_kind")
