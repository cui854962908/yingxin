from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.response import fail_envelope, ok_envelope
from app.core.security import hash_id_number, require_admin, require_any_admin
from app.db.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.services.import_service import import_students_xlsx
from app.services.student_service import (
    get_by_student_id,
    group_students_by_class,
    is_admin_record,
    search_students_by_student_id,
    student_to_admin_detail,
)

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin-students"])


@router.get("/classes")
def admin_list_classes(
    db: Session = Depends(get_db),
    _: dict = Depends(require_any_admin),
):
    """返回已有班级名列表，供表单自动补全"""
    from sqlalchemy import distinct, select as sa_select
    rows = db.execute(
        sa_select(distinct(Student.class_name)).where(Student.class_name.isnot(None)).order_by(Student.class_name)
    ).scalars().all()
    return ok_envelope(message="操作成功", data=rows)


@router.get("/students")
def admin_list_students_grouped(
    db: Session = Depends(get_db),
    _: dict = Depends(require_any_admin),
):
    data = group_students_by_class(db)
    return ok_envelope(message="操作成功", data=data)


@router.get("/students/search")
def admin_search_students(
    q: str = "",
    db: Session = Depends(get_db),
    _: dict = Depends(require_any_admin),
):
    if not q.strip():
        return ok_envelope(message="请输入搜索内容", data=[])
    data = search_students_by_student_id(db, q)
    return ok_envelope(message="操作成功", data=data)


@router.post("/students/import")
async def admin_import_students(
    file: UploadFile = File(..., description="xlsx"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        return fail_envelope(message="只支持 .xlsx 文件", data=None)
    raw = await file.read()
    try:
        result = import_students_xlsx(db, raw)
    except ValueError as exc:
        return fail_envelope(message=f"导入失败：{exc}", data=None)
    except Exception:
        logger.exception("import_students_xlsx 异常")
        return fail_envelope(message="导入失败：服务内部错误，请检查文件格式后重试", data=None)

    msg = f"导入完成：新增 {result.imported} 人，更新 {result.updated} 人，跳过 {result.skipped} 人"
    return ok_envelope(
        message=msg,
        data={
            "imported": result.imported,
            "updated": result.updated,
            "skipped": result.skipped,
            "errors": result.errors,
        },
    )


@router.post("/students")
def admin_create_student(
    body: StudentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    if body.student_id.strip().lower() == "admin":
        return fail_envelope(message="学号 admin 为系统保留，不可用于普通学生", data=None)
    if get_by_student_id(db, body.student_id.strip()):
        return fail_envelope(message="学号已存在", data=None)
    st = Student(
        name=body.name.strip(),
        student_id=body.student_id.strip(),
        id_number_hash=hash_id_number(body.id_number),
        photo=body.photo or None,
        class_name=body.class_name.strip(),
        dormitory=body.dormitory or None,
        advisor_name=body.advisor_name,
        advisor_phone=body.advisor_phone,
        class_teacher_name=body.class_teacher_name,
        class_teacher_phone=body.class_teacher_phone,
        assistant_name=body.assistant_name,
        assistant_phone=body.assistant_phone,
        assistant_class_name=body.assistant_class_name,
        role="student",
    )
    db.add(st)
    db.commit()
    db.refresh(st)
    detail = student_to_admin_detail(st)
    return ok_envelope(message="新增成功", data=detail)


@router.put("/students/{student_id}")
def admin_update_student(
    student_id: str,
    body: StudentUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    st = get_by_student_id(db, student_id)
    if not st:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    if is_admin_record(st):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不允许修改管理员账号行")
    patch = body.model_dump(exclude_unset=True)
    # 记录需要同步到同班同学的辅导员/班主任字段
    sync_fields = {}
    teacher_keys = {'advisor_name', 'advisor_phone', 'class_teacher_name', 'class_teacher_phone'}
    for k in list(patch.keys()):
        if k in teacher_keys:
            sync_fields[k] = patch[k]
    for k, v in patch.items():
        if k == "id_number":
            k = "id_number_hash"
            v = hash_id_number(v) if v else v
        elif isinstance(v, str):
            v = v.strip() if v else v
        setattr(st, k, v)
    # 同班同步：修改辅导员/班主任时，同班其他同学一并更新
    if sync_fields and st.class_name:
        db.query(Student).filter(
            Student.class_name == st.class_name,
            Student.student_id != st.student_id,
        ).update(sync_fields, synchronize_session=False)
    db.commit()
    db.refresh(st)
    return ok_envelope(message="更新成功", data=student_to_admin_detail(st))


@router.delete("/students/{student_id}")
def admin_delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    st = get_by_student_id(db, student_id)
    if not st:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    if is_admin_record(st):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不允许删除管理员账号")
    db.delete(st)
    db.commit()
    return ok_envelope(message="删除成功", data=None)

