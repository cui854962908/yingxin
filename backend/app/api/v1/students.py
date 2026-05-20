"""学生管理路由 — 6 个管理员端点"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import openpyxl

from app.api.deps import get_db, require_admin
from app.crud.student import (
    list_students_grouped,
    search_students,
    create_student,
    update_student,
    delete_student,
    batch_import_students,
)
from app.schemas.student import StudentCreate, StudentUpdate

router = APIRouter()


@router.get("/admin/students")
def admin_list_students(db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    return {"success": True, "data": list_students_grouped(db)}


@router.get("/admin/students/search")
def admin_search_students(q: str = "", db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    results = search_students(db, q)
    return {"success": True, "data": results}


@router.post("/admin/students")
def admin_add_student(data: StudentCreate, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    from app.models.student import Student
    existing = db.query(Student).filter(Student.student_id == data.student_id).first()
    if existing:
        raise HTTPException(400, "该学号已存在")
    return {"success": True, "data": create_student(db, data)}


@router.put("/admin/students/{student_id}")
def admin_update_student(
    student_id: str,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    result = update_student(db, student_id, data)
    if result is None:
        raise HTTPException(404, "学生不存在")
    return {"success": True, "data": result}


@router.delete("/admin/students/{student_id}")
def admin_delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    ok = delete_student(db, student_id)
    if not ok:
        raise HTTPException(404, "学生不存在")
    return {"success": True, "message": "已删除"}


# ── Excel 批量导入 ──

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


@router.post("/admin/students/import")
async def admin_import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "仅支持 .xlsx 或 .xls 格式的 Excel 文件")

    wb = openpyxl.load_workbook(file.file, read_only=True)
    ws = wb.active

    headers: list[str] = []
    rows: list[dict] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        cells = [str(c).strip() if c is not None else "" for c in row]
        if i == 0:
            headers = cells
        else:
            if not any(cells):
                continue
            row_data: dict[str, str] = {}
            for j, h in enumerate(headers):
                key = EXCEL_COL_MAP.get(h)
                if key:
                    row_data[key] = cells[j] if j < len(cells) else ""
            if row_data.get("student_id"):
                rows.append(row_data)
    wb.close()

    result = batch_import_students(db, rows)
    return {
        "success": True,
        "message": f"导入完成：成功 {result['imported']} 人，跳过 {result['skipped']} 人（学号重复或已存在）",
        "data": result,
    }
