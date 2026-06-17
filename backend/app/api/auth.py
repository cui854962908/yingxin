from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.response import fail_envelope, ok_envelope, verify_ok
from app.core.security import get_current_payload
from app.db.database import get_db
from app.schemas.auth import StudentVerifyRequest
from app.services.auth_service import verify_student_login
from app.services import login_guard

router = APIRouter(tags=["auth"])


@router.post("/verify")
def verify_student(body: StudentVerifyRequest, db: Session = Depends(get_db)):
    sid = body.student_id.strip()

    # 检查是否在锁定期
    locked_sec = login_guard.check_locked(sid)
    if locked_sec > 0:
        minutes = max(1, locked_sec // 60)
        return fail_envelope(
            message=f"账户已锁定，请 {minutes} 分钟后重试",
            data={"locked_seconds": locked_sec},
        )

    result = verify_student_login(
        db,
        name=body.name.strip(),
        student_id=sid,
        id_number=body.id_number.strip(),
    )
    if not result:
        remaining = login_guard.record_failure(sid)
        if remaining > 0:
            return fail_envelope(
                message=f"信息不匹配，还剩 {remaining} 次尝试机会",
                data={"remaining_attempts": remaining},
            )
        return fail_envelope(
            message="连续错误 5 次，账户已锁定 5 分钟",
            data={"locked_seconds": 300},
        )

    # 验证成功，清除错误记录
    login_guard.clear_record(sid)
    token, data, role = result
    if role == "admin":
        return verify_ok(message="管理员登录成功", token=token, data=data)
    return verify_ok(message=f"欢迎你，{data['name']}同学！", token=token, data=data)


@router.get("/auth/me")
def auth_me(
    payload: dict = Depends(get_current_payload),
    db: Session = Depends(get_db),
):
    """返回完整学生记录（数据库最新值），前端每次刷新页面时调用以保持数据同步。"""
    from app.models.student import Student
    from app.services.student_service import student_to_student_display

    sid = str(payload.get("sub", "")).strip()
    if sid:
        row = db.scalars(select(Student).where(Student.student_id == sid)).first()
        if row:
            detail = student_to_student_display(row)
            return ok_envelope(message="操作成功", data=detail)
    # 兜底：查不到学生记录时返回完整结构，前端 {{ student.advisor.name }} 等不会因字段缺失崩溃
    return ok_envelope(message="操作成功", data={
        "name": str(payload.get("name", "")),
        "student_id": sid or str(payload.get("sub", "")),
        "role": str(payload.get("role", "student")),
        "class_name": "",
        "dormitory": "",
        "advisor": {"name": "", "phone": ""},
        "class_teacher": {"name": "", "phone": ""},
        "assistants": [],
        "photo": "",
    })

