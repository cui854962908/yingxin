"""Alembic 运行环境：从项目 `.env` 读取 `DATABASE_URL`。"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from app.db.database import Base  # noqa: E402
from app.models import (  # noqa: F401, E402
    Announcement,
    Club,
    Document,
    FAQ,
    Student,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL 未设置，请检查 backend/.env")
    return url


def _db_connect_timeout_seconds() -> int:
    raw = os.getenv("DATABASE_CONNECT_TIMEOUT", "60")
    try:
        return max(int(raw), 10)
    except ValueError:
        return 60


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": _db_connect_timeout_seconds()},
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
