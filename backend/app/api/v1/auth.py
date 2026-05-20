"""认证路由 — POST /verify, GET /auth/me"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import create_token, get_current_user
from app.core.database import get_db
from app.crud.student import get_student_by_credentials

router = APIRouter()


class VerifyRequest(BaseModel):
    name: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    id_number: str = Field(..., min_length=1)


@router.post("/verify")
def verify(req: VerifyRequest, db: Session = Depends(get_db)):
    student = get_student_by_credentials(db, req.name, req.student_id, req.id_number)
    if student is None:
        return {"success": False, "message": "信息验证失败，请检查姓名、学号和身份证号是否正确"}
    token = create_token({
        "sub": student["student_id"],
        "name": student["name"],
        "role": student["role"],
    })
    return {
        "success": True,
        "message": f"欢迎你，{student['name']}同学！",
        "data": student,
        "token": token,
    }


@router.get("/auth/me")
def auth_me(user: dict = Depends(get_current_user)):
    return {"success": True, "data": user}
