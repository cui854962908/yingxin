from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student

ROLE_STUDENT = "student"
ROLE_ADMIN = "admin"


def admin_verify_display(s: Student) -> Dict[str, Any]:
    """管理员经 /api/verify 登录时的 data，返回完整学生信息供前端展示。"""
    data = student_to_student_display(s)
    data["role"] = ROLE_ADMIN
    return data


def student_to_student_display(s: Student) -> Dict[str, Any]:
    return {
        "id": s.id,
        "name": s.name,
        "student_id": s.student_id,
        "photo": s.photo or "",
        "class_name": s.class_name,
        "dormitory": s.dormitory or "",
        "advisor": {"name": s.advisor_name, "phone": s.advisor_phone},
        "class_teacher": {"name": s.class_teacher_name, "phone": s.class_teacher_phone},
        "assistants": [
            {
                "name": s.assistant_name,
                "phone": s.assistant_phone,
                "class_name": s.assistant_class_name,
            }
        ],
        "role": s.role or ROLE_STUDENT,
    }


def get_by_student_id(db: Session, student_id: str) -> Student | None:
    return db.scalars(select(Student).where(Student.student_id == student_id)).first()
