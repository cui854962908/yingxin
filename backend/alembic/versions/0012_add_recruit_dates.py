"""add recruit_start / recruit_end to clubs

Revision ID: 0012
Revises: 0011
Create Date: 2026-05-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clubs", sa.Column("recruit_start", sa.Date(), nullable=True))
    op.add_column("clubs", sa.Column("recruit_end", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("clubs", "recruit_end")
    op.drop_column("clubs", "recruit_start")
