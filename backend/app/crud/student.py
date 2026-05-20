"""学生 CRUD — 平字段存储 → 嵌套输出转换"""

from sqlalchemy.orm import Session

from app.models.student import Student, Assistant
from app.schemas.student import StudentCreate, StudentUpdate


def _student_to_dict(student: Student, assistants: list[Assistant]) -> dict:
    """核心转换：平字段 ORM + assistants 行 → 嵌套响应格式"""
    return {
        "name": student.name,
        "student_id": student.student_id,
        "photo": student.photo or "",
        "class_name": student.class_name or "",
        "dormitory": student.dormitory or "",
        "advisor": {
            "name": student.advisor_name or "",
            "phone": student.advisor_phone or "",
        },
        "class_teacher": {
            "name": student.class_teacher_name or "",
            "phone": student.class_teacher_phone or "",
        },
        "assistants": [
            {"name": a.name or "", "phone": a.phone or "", "class_name": a.class_name or ""}
            for a in assistants
        ],
        "role": student.role or "student",
    }


def get_student_by_credentials(db: Session, name: str, student_id: str, id_number: str) -> dict | None:
    student = (
        db.query(Student)
        .filter(
            Student.name == name,
            Student.student_id == student_id,
            Student.id_number == id_number,
        )
        .first()
    )
    if student is None:
        return None
    return _student_to_dict(student, student.assistants)


def list_students_grouped(db: Session) -> dict[str, list[dict]]:
    students = db.query(Student).filter(Student.role == "student").all()
    groups: dict[str, list[dict]] = {}
    for s in students:
        cls = s.class_name or "未分班"
        groups.setdefault(cls, []).append(_student_to_dict(s, s.assistants))
    return groups


def search_students(db: Session, q: str) -> list[dict]:
    students = db.query(Student).filter(Student.student_id.like(f"%{q}%")).all()
    return [_student_to_dict(s, s.assistants) for s in students]


def create_student(db: Session, data: StudentCreate) -> dict:
    student = Student(
        name=data.name,
        student_id=data.student_id,
        id_number=data.id_number,
        class_name=data.class_name,
        dormitory=data.dormitory,
        advisor_name=data.advisor_name,
        advisor_phone=data.advisor_phone,
        class_teacher_name=data.class_teacher_name,
        class_teacher_phone=data.class_teacher_phone,
        role="student",
    )
    db.add(student)
    db.flush()

    assistant = Assistant(
        student_id=data.student_id,
        name=data.assistant_name,
        phone=data.assistant_phone,
        class_name=data.assistant_class_name,
    )
    db.add(assistant)
    db.commit()
    db.refresh(student)
    return _student_to_dict(student, student.assistants)


def update_student(db: Session, student_id: str, data: StudentUpdate) -> dict | None:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    assistant_fields = {"assistant_name", "assistant_phone", "assistant_class_name"}
    student_fields = {k: v for k, v in update_data.items() if k not in assistant_fields}

    for field, value in student_fields.items():
        setattr(student, field, value)

    if assistant_fields & set(update_data):
        ast = db.query(Assistant).filter(Assistant.student_id == student_id).first()
        if ast is None:
            ast = Assistant(student_id=student_id)
            db.add(ast)
        if data.assistant_name is not None:
            ast.name = data.assistant_name
        if data.assistant_phone is not None:
            ast.phone = data.assistant_phone
        if data.assistant_class_name is not None:
            ast.class_name = data.assistant_class_name

    db.commit()
    db.refresh(student)
    return _student_to_dict(student, student.assistants)


def delete_student(db: Session, student_id: str) -> bool:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        return False
    db.delete(student)
    db.commit()
    return True


def batch_import_students(db: Session, rows: list[dict]) -> dict[str, int]:
    imported = 0
    skipped = 0
    for row in rows:
        sid = row.get("student_id", "").strip()
        if not sid:
            skipped += 1
            continue
        existing = db.query(Student).filter(Student.student_id == sid).first()
        if existing:
            skipped += 1
            continue

        student = Student(
            name=row.get("name", "").strip(),
            student_id=sid,
            id_number=row.get("id_number", "").strip(),
            class_name=row.get("class_name", "").strip(),
            dormitory=row.get("dormitory", "").strip(),
            advisor_name=row.get("advisor_name", "").strip(),
            advisor_phone=row.get("advisor_phone", "").strip(),
            class_teacher_name=row.get("class_teacher_name", "").strip(),
            class_teacher_phone=row.get("class_teacher_phone", "").strip(),
            role="student",
        )
        db.add(student)
        db.flush()

        ast_name = row.get("assistant_name", "").strip()
        if ast_name:
            db.add(Assistant(
                student_id=sid,
                name=ast_name,
                phone=row.get("assistant_phone", "").strip(),
                class_name=row.get("assistant_class", "").strip(),
            ))

        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped}
