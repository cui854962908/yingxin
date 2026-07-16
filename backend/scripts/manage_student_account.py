"""Create or update a local student account and its independent forum identity."""

from __future__ import annotations

import argparse
import getpass

from sqlalchemy import select

from app.core.security import DEFAULT_INITIAL_PASSWORD, hash_password
from app.db.database import SessionLocal
from app.models.student import Student

SYSTEM_ROLES = ("student", "admin", "club_admin")
FORUM_ROLES = ("teacher", "assistant")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建或维护学生账号与论坛身份")
    parser.add_argument("--student-id", required=True, help="学号或管理员账号标识")
    parser.add_argument(
        "--new-student-id",
        help="将账号登录标识（student_id）改为新学号；与 --student-id 联用",
    )
    parser.add_argument("--name", help="姓名；新建账号时必填")
    parser.add_argument("--class-name", help="班级；新建账号时必填")
    parser.add_argument("--system-role", choices=SYSTEM_ROLES, help="系统权限；未指定则保留原值")
    parser.add_argument(
        "--forum-role",
        choices=(*FORUM_ROLES, "none"),
        help="论坛身份；none 清除身份，未指定则保留原值",
    )
    parser.add_argument("--reset-password", action="store_true", help="交互式重设登录密码")
    return parser.parse_args()


def prompt_password(label: str = "新密码") -> str:
    value = getpass.getpass(f"{label}（不回显）：").strip()
    if len(value) < 8:
        raise ValueError("密码至少 8 位")
    return value


def require_create_fields(args: argparse.Namespace) -> tuple[str, str]:
    if not args.name or not args.class_name:
        raise ValueError("新建账号必须提供 --name 和 --class-name")
    return args.name.strip(), args.class_name.strip()


def apply_forum_role(student: Student, requested: str | None) -> None:
    if requested is None:
        return
    student.forum_role = None if requested == "none" else requested


def rename_student_id(db, student: Student, new_id: str) -> None:
    new_id = new_id.strip()
    if not new_id:
        raise ValueError("新学号不能为空")
    if new_id == student.student_id:
        return
    taken = db.scalars(select(Student).where(Student.student_id == new_id)).first()
    if taken:
        raise ValueError(f"学号 {new_id} 已被 {taken.name} 占用")
    student.student_id = new_id


def main() -> None:
    args = parse_args()
    student_id = args.student_id.strip()
    db = SessionLocal()
    try:
        student = db.scalars(select(Student).where(Student.student_id == student_id)).first()
        creating = student is None
        if creating:
            name, class_name = require_create_fields(args)
            student = Student(
                name=name,
                student_id=student_id,
                class_name=class_name,
                password_hash=hash_password(DEFAULT_INITIAL_PASSWORD),
                role=args.system_role or "student",
            )
            db.add(student)
        else:
            if args.name:
                student.name = args.name.strip()
            if args.class_name:
                student.class_name = args.class_name.strip()
            if args.system_role:
                student.role = args.system_role
            if args.reset_password:
                student.password_hash = hash_password(prompt_password())
            if args.new_student_id:
                rename_student_id(db, student, args.new_student_id)

        apply_forum_role(student, args.forum_role)
        db.commit()
        print(
            f"已{'创建' if creating else '更新'}账号：{student.student_id} "
            f"（系统权限：{student.role}；论坛身份：{student.forum_role or '无'}）"
        )
        if creating:
            print(f"  初始密码：{DEFAULT_INITIAL_PASSWORD}（请提醒用户登录后修改）")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
