"""faq：承接 faqs 合并字段（关键词、分类、原 agent 主键可追溯）

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "faq",
        "question",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=False,
    )

    op.add_column("faq", sa.Column("keywords", sa.Text(), nullable=True))
    op.add_column("faq", sa.Column("category", sa.String(length=128), nullable=True))
    op.add_column("faq", sa.Column("agent_faq_id", sa.Integer(), nullable=True))

    op.create_foreign_key(
        "fk_faq_agent_faq_id_faqs",
        "faq",
        "faqs",
        ["agent_faq_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_faq_agent_faq_id",
        "faq",
        ["agent_faq_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_faq_agent_faq_id", table_name="faq")
    op.drop_constraint("fk_faq_agent_faq_id_faqs", "faq", type_="foreignkey")
    op.drop_column("faq", "agent_faq_id")
    op.drop_column("faq", "category")
    op.drop_column("faq", "keywords")

    op.alter_column(
        "faq",
        "question",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=False,
        postgresql_using="left(question::text, 500)",
    )
