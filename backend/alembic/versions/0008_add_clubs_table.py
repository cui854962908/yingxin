"""add clubs table

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clubs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("cover_image", sa.String(500), nullable=True),
        sa.Column("intro", sa.String(300), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="招新中"),
        sa.Column("carousel_images", sa.Text(), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("member_count", sa.Integer(), nullable=True),
        sa.Column("advisor_name", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("activity_photos", sa.Text(), nullable=True),
        sa.Column("leader_name", sa.String(100), nullable=True),
        sa.Column("leader_phone", sa.String(50), nullable=True),
        sa.Column("qq_group", sa.String(50), nullable=True),
        sa.Column("wechat_qr", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("clubs")
