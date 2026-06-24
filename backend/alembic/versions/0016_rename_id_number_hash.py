"""rename students.id_number → id_number_hash + widen 32→64

Revision ID: 0016
Revises: 0015_forum_likes
Create Date: 2026-06-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015_forum_likes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: rename
    op.alter_column("students", "id_number", new_column_name="id_number_hash")
    # Step 2: widen to fit SHA-256 hash (64 chars)
    op.alter_column("students", "id_number_hash", type_=sa.String(64), existing_type=sa.String(32), nullable=False)


def downgrade() -> None:
    op.alter_column("students", "id_number_hash", type_=sa.String(32), existing_type=sa.String(64), nullable=False)
    op.alter_column("students", "id_number_hash", new_column_name="id_number")
