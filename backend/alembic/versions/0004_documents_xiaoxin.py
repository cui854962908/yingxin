"""小信 SSE 对话：`documents` 表存 Ollama 向量 JSON（余弦检索，与 pgvector 知识块并存）。

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "embedding_json",
            sa.Text(),
            nullable=True,
            comment="JSON 数组：Ollama embedding 向量，维度随模型而定",
        ),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "source_faq_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["source_faq_id"],
            ["faqs.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(op.f("ix_documents_source_faq_id"), "documents", ["source_faq_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_source_faq_id"), table_name="documents")
    op.drop_table("documents")
