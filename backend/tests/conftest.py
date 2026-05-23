import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.models.student import Student

# SQLite 内存库（不依赖 PostgreSQL）
TEST_DATABASE_URL = "sqlite:///:memory:"
_test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine, class_=Session)


@pytest.fixture(autouse=True)
def _create_tables():
    """每个测试前重建 Student 表。"""
    Student.__table__.create(bind=_test_engine, checkfirst=True)
    yield
    Student.__table__.drop(bind=_test_engine, checkfirst=True)


@pytest.fixture(autouse=True)
def _clear_login_guard():
    """每个测试后清除 login_guard 内存状态，避免测试间锁定传递。"""
    yield
    from app.services.login_guard import _store
    _store.clear()


@pytest.fixture
def db() -> Session:
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    from app.main import app

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_student(db: Session) -> Student:
    """写入一个测试学生，返回 ORM 对象。"""
    s = Student(
        name="张三",
        student_id="20260901001",
        id_number="410105200509010011",
        class_name="计算机科学2026-1班",
        role="student",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
