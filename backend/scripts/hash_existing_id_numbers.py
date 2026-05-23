"""一次性脚本：将 students 表中现有的 id_number 明文哈希后存入 id_number_hash 列。"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_id_number
from app.db.database import SessionLocal
from app.models.student import Student
from sqlalchemy import select


def main():
    db = SessionLocal()
    try:
        students = db.scalars(
            select(Student).where(Student.id_number_hash == None)  # noqa: E711
        ).all()

        if not students:
            print("没有需要迁移的记录。")
            return

        print(f"找到 {len(students)} 条待迁移记录。")
        for s in students:
            # id_number 是旧列，即将被删除
            plain = getattr(s, "id_number", None)
            if plain:
                s.id_number_hash = hash_id_number(plain)
                print(f"  {s.student_id}: 已哈希")
            else:
                s.id_number_hash = ""
                print(f"  {s.student_id}: id_number 为空，设为空字符串")

        db.commit()
        print("迁移完成。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
