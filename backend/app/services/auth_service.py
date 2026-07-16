from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.student import Student
from app.services.student_service import admin_verify_display, student_to_student_display
from app.services.token_service import issue_refresh_token, revoke_all_for_student


def verify_student_login(db: Session, *, name: str, student_id: str, password: str):
    s = db.scalars(
        select(Student).where(
            Student.name == name,
            Student.student_id == student_id,
        )
    ).first()
    if not s or not verify_password(password, s.password_hash):
        return None
    role = (s.role or "student").strip().lower()
    token = create_access_token(subject=s.student_id, name=s.name, role=role)
    refresh_raw, _ = issue_refresh_token(db, student_id=s.id)
    if role == "admin":
        data = admin_verify_display(s)
    else:
        data = student_to_student_display(s)
    return token, refresh_raw, data, role


def change_student_password(
    db: Session,
    *,
    student_id: str,
    current_password: str,
    new_password: str,
) -> None:
    s = db.scalars(select(Student).where(Student.student_id == student_id)).first()
    if not s:
        raise ValueError("用户不存在")
    if not verify_password(current_password, s.password_hash):
        raise ValueError("当前密码不正确")
    if len(new_password.strip()) < 8:
        raise ValueError("新密码至少 8 位")
    if new_password.strip() == current_password.strip():
        raise ValueError("新密码不能与当前密码相同")
    s.password_hash = hash_password(new_password)
    revoke_all_for_student(db, student_id=s.id)
