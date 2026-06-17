"""add recruit_target, recruit_count, recruit_require to clubs

Revision ID: 0013_add_club_recruit_fields
Revises: a1b2c3d4e5f6
Create Date: 2026-06-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_add_club_recruit_fields"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clubs", sa.Column("recruit_target", sa.String(200), nullable=True))
    op.add_column("clubs", sa.Column("recruit_count", sa.Integer(), nullable=True))
    op.add_column("clubs", sa.Column("recruit_require", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("clubs", "recruit_require")
    op.drop_column("clubs", "recruit_count")
    op.drop_column("clubs", "recruit_target")
