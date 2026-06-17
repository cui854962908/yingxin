from typing import Any, Dict, List

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


def _nested_from_student(s: Student, *, include_id_number: bool) -> Dict[str, Any]:
    base: Dict[str, Any] = {
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
    if include_id_number:
        base["id_number"] = ""  # 身份证号已哈希存储，管理端不再展示明文
    return base


def student_to_student_display(s: Student) -> Dict[str, Any]:
    return _nested_from_student(s, include_id_number=False)


def student_to_admin_detail(s: Student) -> Dict[str, Any]:
    return _nested_from_student(s, include_id_number=True)


def _student_only_filter():
    return Student.role == ROLE_STUDENT


def group_students_by_class(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    rows = db.scalars(
        select(Student)
        .where(_student_only_filter())
        .order_by(Student.class_name, Student.student_id)
    ).all()
    out: Dict[str, List[Dict[str, Any]]] = {}
    for s in rows:
        out.setdefault(s.class_name, []).append(student_to_admin_detail(s))
    return out


def search_students_by_student_id(db: Session, q: str) -> List[Dict[str, Any]]:
    if not q or not q.strip():
        return []
    pattern = f"%{q.strip()}%"
    rows = db.scalars(
        select(Student)
        .where(Student.student_id.ilike(pattern), _student_only_filter())
        .order_by(Student.student_id)
    ).all()
    return [student_to_admin_detail(s) for s in rows]


def get_by_student_id(db: Session, student_id: str) -> Student | None:
    return db.scalars(select(Student).where(Student.student_id == student_id)).first()


def is_admin_record(s: Student) -> bool:
    return (s.role or "").strip().lower() == ROLE_ADMIN
