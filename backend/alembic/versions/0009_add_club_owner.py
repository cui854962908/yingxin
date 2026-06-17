"""add owner_student_id to clubs

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clubs",
        sa.Column("owner_student_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_clubs_owner_student_id",
        "clubs",
        "students",
        ["owner_student_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_clubs_owner_student_id", "clubs", type_="foreignkey")
    op.drop_column("clubs", "owner_student_id")
