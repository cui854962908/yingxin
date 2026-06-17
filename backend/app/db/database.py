from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# connect_timeout：宿主机直连映射端口时，若库仍在启动或机器忙，过短会触发 psycopg ConnectionTimeout
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": settings.DATABASE_CONNECT_TIMEOUT},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
