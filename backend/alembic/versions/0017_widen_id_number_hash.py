"""widen students.id_number_hash VARCHAR 32→64

Revision ID: 0017
Revises: 0016
Create Date: 2026-06-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("students", "id_number_hash", type_=sa.String(64), existing_type=sa.String(32), nullable=False)


def downgrade() -> None:
    op.alter_column("students", "id_number_hash", type_=sa.String(32), existing_type=sa.String(64), nullable=False)
