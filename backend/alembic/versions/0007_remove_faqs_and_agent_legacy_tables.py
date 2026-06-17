"""移除 faqs/agent 遗留：`knowledge_chunks`、`agent_chat_logs`、`faqs` 及外挂键列。

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS knowledge_chunks CASCADE"))
    op.execute(sa.text("DROP TABLE IF EXISTS agent_chat_logs CASCADE"))

    op.execute(sa.text('DROP INDEX IF EXISTS "uq_documents_agent_faq_id"'))
    op.execute(sa.text("ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_source_faq_id_fkey"))
    op.execute(sa.text('DROP INDEX IF EXISTS "ix_documents_source_faq_id"'))
    op.execute(sa.text("ALTER TABLE documents DROP COLUMN IF EXISTS source_faq_id"))

    op.execute(sa.text("ALTER TABLE faq DROP CONSTRAINT IF EXISTS fk_faq_agent_faq_id_faqs"))
    op.execute(sa.text('DROP INDEX IF EXISTS "ix_faq_agent_faq_id"'))
    op.execute(sa.text("ALTER TABLE faq DROP COLUMN IF EXISTS agent_faq_id"))

    op.execute(sa.text("DROP TABLE IF EXISTS faqs CASCADE"))

    op.alter_column(
        "documents",
        "source_kind",
        server_default=sa.text("'student_faq'"),
    )


def downgrade() -> None:
    raise NotImplementedError("0007 is one-way: legacy faqs / knowledge_chunks removal cannot be rebuilt safely.")
