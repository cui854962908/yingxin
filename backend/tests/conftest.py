import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.core.security import create_access_token, hash_id_number
from app.models.student import Student

# SQLite 临时文件库（不依赖 PostgreSQL）。:memory: 在不同连接间不共享，FastAPI
# 在 asyncio 线程池中运行端点时会打开新连接导致 "no such table"。
import tempfile, os
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="pytest_")
TEST_DATABASE_URL = f"sqlite:///{_test_db_path}"
_test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine, class_=Session)


def _ensure_tables():
    """确保所有模型表已在测试引擎中创建（幂等）。"""
    from app.models import Announcement, Document, FAQ, Student  # noqa: F401
    Base.metadata.create_all(bind=_test_engine)


@pytest.fixture(autouse=True)
def _create_tables():
    """每个测试前重建全部表。"""
    _ensure_tables()
    yield
    Base.metadata.drop_all(bind=_test_engine)


def pytest_sessionfinish(session: pytest.Session) -> None:
    """测试结束后清理临时 SQLite 文件。"""
    try:
        os.close(_test_db_fd)
        os.unlink(_test_db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _clear_login_guard():
    """每个测试后清除 login_guard 内存状态，避免测试间锁定传递。"""
    yield
    from app.services.login_guard import _store
    _store.clear()


@pytest.fixture(autouse=True)
def _clear_faq_cache():
    """每个测试后清除 FAQ 进程内缓存。"""
    yield
    from app.services import faq_service
    faq_service.clear_faq_cache()


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
    # 先触发 app 导入链，确保所有模型已注册到 Base.metadata
    from app.main import app
    _ensure_tables()

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
    from app.models.student import Student
    s = Student(
        name="张三",
        student_id="20260901001",
        id_number_hash=hash_id_number("410105200509010011"),
        class_name="计算机科学2026-1班",
        role="student",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@pytest.fixture
def seed_admin(db: Session) -> Student:
    a = Student(
        name="管理员",
        student_id="admin",
        id_number_hash=hash_id_number("410105199001010000"),
        class_name="信息工程学院",
        role="admin",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def admin_token(seed_admin: Student) -> str:
    return create_access_token(
        subject=seed_admin.student_id,
        name=seed_admin.name,
        role="admin",
    )


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
