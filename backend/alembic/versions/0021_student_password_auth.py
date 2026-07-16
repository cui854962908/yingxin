"""replace id_number_hash with password_hash

Revision ID: 0021
Revises: 0020
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels = None
depends_on = None


def _default_password_hash() -> str:
    from app.core.security import DEFAULT_INITIAL_PASSWORD, hash_password

    return hash_password(DEFAULT_INITIAL_PASSWORD)


def upgrade() -> None:
    op.add_column("students", sa.Column("password_hash", sa.String(length=128), nullable=True))
    conn = op.get_bind()
    default_hash = _default_password_hash()
    conn.execute(sa.text("UPDATE students SET password_hash = :h WHERE password_hash IS NULL"), {"h": default_hash})
    op.drop_column("students", "id_number_hash")
    op.alter_column("students", "password_hash", existing_type=sa.String(length=128), nullable=False)


def downgrade() -> None:
    op.add_column("students", sa.Column("id_number_hash", sa.String(length=64), nullable=True))
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE students SET id_number_hash = '' WHERE id_number_hash IS NULL"))
    op.drop_column("students", "password_hash")
    op.alter_column("students", "id_number_hash", existing_type=sa.String(length=64), nullable=False)
