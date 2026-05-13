from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import openpyxl

from app.core.students import (
    verify_student,
    list_students_grouped,
    add_student,
    update_student,
    delete_student,
    find_student,
    batch_import,
)
from app.core.auth import create_token, get_current_user, require_admin
from app.core.faq import list_faq, add_faq, delete_faq

app = FastAPI(title="迎新系统 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 验证登录 ──

class VerifyRequest(BaseModel):
    name: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    id_number: str = Field(..., min_length=1)


@app.post("/api/verify")
def verify(req: VerifyRequest):
    student = verify_student(req.name, req.student_id, req.id_number)
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


# ── 验证 token / 自动登录 ──

@app.get("/api/auth/me")
def auth_me(user: dict = Depends(get_current_user)):
    return {"success": True, "data": user}


# ── 管理员：按班级分组的学生列表 ──

@app.get("/api/admin/students")
def admin_students(_admin: dict = Depends(require_admin)):
    return {"success": True, "data": list_students_grouped()}


# ── 管理员：按学号搜索 ──

@app.get("/api/admin/students/search")
def admin_search_student(q: str = "", _admin: dict = Depends(require_admin)):
    s = find_student(q)
    if s is None:
        return {"success": False, "message": "未找到该学生"}
    return {"success": True, "data": {
        "name": s["name"],
        "student_id": s["student_id"],
        "photo": s.get("photo", ""),
        "class_name": s["class_name"],
        "dormitory": s["dormitory"],
        "advisor": s["advisor"],
        "class_teacher": s["class_teacher"],
        "assistants": s["assistants"],
    }}


# ── 管理员：新增学生 ──

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    id_number: str = ""
    photo: str = ""
    class_name: str = ""
    dormitory: str = ""
    advisor: dict = {"name": "", "phone": ""}
    class_teacher: dict = {"name": "", "phone": ""}
    assistants: list = [{"name": "", "phone": "", "class_name": ""}]


@app.post("/api/admin/students")
def admin_add_student(data: StudentCreate, _admin: dict = Depends(require_admin)):
    existing = find_student(data.student_id)
    if existing:
        raise HTTPException(400, "该学号已存在")
    result = add_student(data.model_dump())
    return {"success": True, "data": result}


# ── 管理员：更新学生 ──

@app.put("/api/admin/students/{student_id}")
def admin_update_student(student_id: str, data: dict, _admin: dict = Depends(require_admin)):
    result = update_student(student_id, data)
    if result is None:
        raise HTTPException(404, "学生不存在")
    return {"success": True, "data": result}


# ── 管理员：删除学生 ──

@app.delete("/api/admin/students/{student_id}")
def admin_delete_student(student_id: str, _admin: dict = Depends(require_admin)):
    ok = delete_student(student_id)
    if not ok:
        raise HTTPException(404, "学生不存在")
    return {"success": True, "message": "已删除"}


# ── 管理员：Excel 批量导入 ──

# 中文列名 → 内部字段名映射
EXCEL_COL_MAP = {
    "姓名": "name",
    "学号": "student_id",
    "身份证号": "id_number",
    "班级": "class_name",
    "宿舍": "dormitory",
    "辅导员": "advisor_name",
    "辅导员电话": "advisor_phone",
    "班主任": "class_teacher_name",
    "班主任电话": "class_teacher_phone",
    "代班": "assistant_name",
    "代班电话": "assistant_phone",
    "代班班级": "assistant_class",
}


@app.post("/api/admin/students/import")
async def admin_import_excel(file: UploadFile = File(...), _admin: dict = Depends(require_admin)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "仅支持 .xlsx 或 .xls 格式的 Excel 文件")

    wb = openpyxl.load_workbook(file.file, read_only=True)
    ws = wb.active

    # 第一行作为表头
    headers: list[str] = []
    rows: list[dict] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        cells = [str(c).strip() if c is not None else "" for c in row]
        if i == 0:
            headers = cells
        else:
            if not any(cells):  # 跳过空行
                continue
            row_data: dict[str, str] = {}
            for j, h in enumerate(headers):
                key = EXCEL_COL_MAP.get(h)
                if key:
                    row_data[key] = cells[j] if j < len(cells) else ""
            if row_data.get("student_id"):
                rows.append(row_data)
    wb.close()

    result = batch_import(rows)
    return {
        "success": True,
        "message": f"导入完成：成功 {result['imported']} 人，跳过 {result['skipped']} 人（学号重复或已存在）",
        "data": result,
    }


# ── FAQ：所有人可查看 ──

@app.get("/api/faq")
def get_faq():
    return {"success": True, "data": list_faq()}


# ── FAQ：管理员新增 ──

class FaqCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


@app.post("/api/admin/faq")
def admin_add_faq(data: FaqCreate, _admin: dict = Depends(require_admin)):
    item = add_faq(data.question, data.answer)
    return {"success": True, "data": item}


# ── FAQ：管理员删除 ──

@app.delete("/api/admin/faq/{faq_id}")
def admin_delete_faq(faq_id: str, _admin: dict = Depends(require_admin)):
    ok = delete_faq(faq_id)
    if not ok:
        raise HTTPException(404, "问题不存在")
    return {"success": True, "message": "已删除"}
