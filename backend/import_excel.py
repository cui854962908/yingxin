"""命令行 Excel 批量导入工具
用法：uv run python import_excel.py 学生名单.xlsx
"""
import sys
import openpyxl
from app.core.database import SessionLocal
from app.crud.student import batch_import_students

COL_MAP = {
    "姓名": "name", "学号": "student_id", "身份证号": "id_number",
    "班级": "class_name", "宿舍": "dormitory",
    "辅导员": "advisor_name", "辅导员电话": "advisor_phone",
    "班主任": "class_teacher_name", "班主任电话": "class_teacher_phone",
    "代班": "assistant_name", "代班电话": "assistant_phone", "代班班级": "assistant_class",
}


def main(path: str):
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = []
    headers: list[str] = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        cells = [str(c).strip() if c is not None else "" for c in row]
        if i == 0:
            headers = cells
            continue
        if not any(cells):
            continue
        row_data: dict[str, str] = {}
        for j, h in enumerate(headers):
            key = COL_MAP.get(h)
            if key:
                row_data[key] = cells[j] if j < len(cells) else ""
        if row_data.get("student_id"):
            rows.append(row_data)
    wb.close()

    db = SessionLocal()
    try:
        result = batch_import_students(db, rows)
        print(f"导入完成：成功 {result['imported']} 人，跳过 {result['skipped']} 人（学号已存在）")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：uv run python import_excel.py <Excel文件路径>")
        sys.exit(1)
    main(sys.argv[1])
