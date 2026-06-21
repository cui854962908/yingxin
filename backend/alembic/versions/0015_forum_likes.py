"""forum likes on posts and answers

Revision ID: 0015_forum_likes
Revises: 0014_forum_tables
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_forum_likes"
down_revision: Union[str, None] = "0014_forum_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "forum_posts",
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "forum_answers",
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "forum_post_likes",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", sa.Uuid(), sa.ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "post_id"),
    )
    op.create_table(
        "forum_answer_likes",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer_id", sa.Uuid(), sa.ForeignKey("forum_answers.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "answer_id"),
    )


def downgrade() -> None:
    op.drop_table("forum_answer_likes")
    op.drop_table("forum_post_likes")
    op.drop_column("forum_answers", "like_count")
    op.drop_column("forum_posts", "like_count")
