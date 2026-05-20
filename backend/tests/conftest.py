"""测试 fixtures：TestClient + 数据库事务回滚"""

import os
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

from app.main import app
from app.core.database import Base, get_db
from app.models.student import Student, Assistant


engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """每个测试前重建干净的数据库。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client, db):
    admin = Student(
        name="管理员",
        student_id="admin001",
        id_number="410105200509010099",
        class_name="管理班",
        dormitory="办公室",
        advisor_name="导师",
        advisor_phone="138-0000-0000",
        class_teacher_name="班主任",
        class_teacher_phone="137-0000-0000",
        role="admin",
    )
    db.add(admin)
    db.commit()

    resp = client.post("/api/verify", json={
        "name": "管理员",
        "student_id": "admin001",
        "id_number": "410105200509010099",
    })
    return resp.json()["token"]


@pytest.fixture
def student_token(client, db):
    student = Student(
        name="测试学生",
        student_id="test001",
        id_number="410105200509010001",
        class_name="测试班",
        dormitory="测试宿舍",
        advisor_name="测试导师",
        advisor_phone="138-0000-1111",
        class_teacher_name="测试班主任",
        class_teacher_phone="137-0000-2222",
        role="student",
    )
    db.add(student)
    db.commit()

    resp = client.post("/api/verify", json={
        "name": "测试学生",
        "student_id": "test001",
        "id_number": "410105200509010001",
    })
    return resp.json()["token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}
