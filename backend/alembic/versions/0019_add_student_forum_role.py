"""add independent forum role to students

Revision ID: 0019
Revises: 0018
Create Date: 2026-07-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("students", sa.Column("forum_role", sa.String(length=32), nullable=True))
    op.create_check_constraint(
        "ck_students_forum_role",
        "students",
        "forum_role IN ('teacher', 'assistant') OR forum_role IS NULL",
    )


def downgrade() -> None:
    op.drop_constraint("ck_students_forum_role", "students", type_="check")
    op.drop_column("students", "forum_role")
