from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_id_number
from app.models.student import Student
from app.services.student_service import admin_verify_display, student_to_student_display


def verify_student_login(db: Session, *, name: str, student_id: str, id_number: str):
    s = db.scalars(
        select(Student).where(
            Student.name == name,
            Student.student_id == student_id,
        )
    ).first()
    if not s:
        return None
    # 如果学生已设置身份证号，必须匹配
    if s.id_number_hash:
        if s.id_number_hash != hash_id_number(id_number):
            return None
    # 未设置身份证号的学生，跳过身份证验证
    role = (s.role or "student").strip().lower()
    token = create_access_token(subject=s.student_id, name=s.name, role=role)
    if role == "admin":
        data = admin_verify_display(s)
    else:
        data = student_to_student_display(s)
    return token, data, role

