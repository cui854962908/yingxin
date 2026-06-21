"""forum_posts and forum_answers

Revision ID: 0014_forum_tables
Revises: 0013_add_club_recruit_fields
Create Date: 2026-06-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_forum_tables"
down_revision: Union[str, None] = "0013_add_club_recruit_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forum_posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="其他"),
        sa.Column("answer_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("has_accepted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_forum_posts_author_id", "forum_posts", ["author_id"])
    op.create_index("ix_forum_posts_created_at", "forum_posts", ["created_at"])

    op.create_table(
        "forum_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_accepted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["forum_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_forum_answers_post_id", "forum_answers", ["post_id"])


def downgrade() -> None:
    op.drop_index("ix_forum_answers_post_id", table_name="forum_answers")
    op.drop_table("forum_answers")
    op.drop_index("ix_forum_posts_created_at", table_name="forum_posts")
    op.drop_index("ix_forum_posts_author_id", table_name="forum_posts")
    op.drop_table("forum_posts")
