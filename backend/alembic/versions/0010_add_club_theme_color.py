"""add theme_color to clubs

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clubs",
        sa.Column("theme_color", sa.String(20), nullable=True, server_default="green"),
    )


def downgrade() -> None:
    op.drop_column("clubs", "theme_color")
