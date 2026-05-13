# 迎新系统 — 示例学生数据（demo 阶段，后续迁移至 PostgreSQL）
# 所有身份证号均为虚构，仅用于开发测试

from typing import Any

STUDENTS: list[dict[str, Any]] = [
    {
        "name": "张三",
        "student_id": "20260901001",
        "id_number": "410105200509010011",
        "photo": "",
        "class_name": "计算机科学与技术 2026-1班",
        "dormitory": "北苑 3号楼 412室",
        "advisor": {"name": "李明辉", "phone": "138-0000-1111"},
        "class_teacher": {"name": "赵文博", "phone": "137-0000-7777"},
        "assistants": [
            {"name": "王浩", "phone": "139-0000-2222", "class_name": "计算机科学 2025-1班"},
        ],
        "role": "student",
    },
    {
        "name": "李四",
        "student_id": "20260901002",
        "id_number": "410105200510150022",
        "photo": "",
        "class_name": "软件工程 2026-2班",
        "dormitory": "北苑 5号楼 208室",
        "advisor": {"name": "张丽华", "phone": "138-0000-3333"},
        "class_teacher": {"name": "孙建国", "phone": "137-0000-8888"},
        "assistants": [
            {"name": "刘洋", "phone": "139-0000-4444", "class_name": "软件工程 2025-2班"},
        ],
        "role": "student",
    },
    {
        "name": "王五",
        "student_id": "20260901003",
        "id_number": "410105200508200033",
        "photo": "",
        "class_name": "数据科学与大数据 2026-1班",
        "dormitory": "南苑 2号楼 515室",
        "advisor": {"name": "陈刚", "phone": "138-0000-5555"},
        "class_teacher": {"name": "周敏", "phone": "137-0000-9999"},
        "assistants": [
            {"name": "赵雪", "phone": "139-0000-6666", "class_name": "大数据 2025-1班"},
        ],
        "role": "student",
    },
]

ADMINS: list[dict[str, Any]] = [
    {
        "name": "崔志远",
        "student_id": "2502160306002",
        "id_number": "411103200712010177",
        "photo": "",
        "class_name": "25级物联网工程06班",
        "dormitory": "12号楼419",
        "advisor": {"name": "王子钰", "phone": "—"},
        "class_teacher": {"name": "张红红", "phone": "—"},
        "assistants": [
            {"name": "袁振康", "phone": "—", "class_name": "24级物联网工程05班"},
            {"name": "周沫言", "phone": "—", "class_name": "24级软件工程11班"},
        ],
        "role": "admin",
    },
]

ALL_USERS = STUDENTS + ADMINS


def _public(s: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": s["name"],
        "student_id": s["student_id"],
        "photo": s.get("photo", ""),
        "class_name": s["class_name"],
        "dormitory": s["dormitory"],
        "advisor": s["advisor"],
        "class_teacher": s["class_teacher"],
        "assistants": s["assistants"],
    }


def verify_student(name: str, student_id: str, id_number: str) -> dict[str, Any] | None:
    for u in ALL_USERS:
        if u["name"] == name and u["student_id"] == student_id and u["id_number"] == id_number:
            return {**_public(u), "role": u["role"]}
    return None


def list_students_grouped() -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for s in STUDENTS:
        cls = s["class_name"]
        groups.setdefault(cls, []).append(_public(s))
    return groups


def find_student(student_id: str) -> dict[str, Any] | None:
    for s in STUDENTS:
        if s["student_id"] == student_id:
            return s
    return None


def add_student(data: dict[str, Any]) -> dict[str, Any]:
    s = {
        "name": data["name"],
        "student_id": data["student_id"],
        "id_number": data.get("id_number", ""),
        "photo": data.get("photo", ""),
        "class_name": data.get("class_name", ""),
        "dormitory": data.get("dormitory", ""),
        "advisor": data.get("advisor", {"name": "", "phone": ""}),
        "class_teacher": data.get("class_teacher", {"name": "", "phone": ""}),
        "assistants": data.get("assistants", [{"name": "", "phone": "", "class_name": ""}]),
        "role": "student",
    }
    STUDENTS.append(s)
    return _public(s)


def update_student(student_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    s = find_student(student_id)
    if s is None:
        return None
    for field in ("name", "id_number", "photo", "class_name", "dormitory"):
        if field in data:
            s[field] = data[field]
    for field in ("advisor", "class_teacher"):
        if field in data and isinstance(data[field], dict):
            s[field].update(data[field])
    if "assistants" in data and isinstance(data["assistants"], list):
        s["assistants"] = data["assistants"]
    return _public(s)


def delete_student(student_id: str) -> bool:
    s = find_student(student_id)
    if s is None:
        return False
    STUDENTS.remove(s)
    return True


def batch_import(rows: list[dict[str, Any]]) -> dict[str, int]:
    imported = 0
    skipped = 0
    for row in rows:
        sid = row.get("student_id", "").strip()
        if not sid or find_student(sid):
            skipped += 1
            continue
        STUDENTS.append({
            "name": row.get("name", "").strip(),
            "student_id": sid,
            "id_number": row.get("id_number", "").strip(),
            "photo": row.get("photo", ""),
            "class_name": row.get("class_name", "").strip(),
            "dormitory": row.get("dormitory", "").strip(),
            "advisor": {"name": row.get("advisor_name", "").strip(), "phone": row.get("advisor_phone", "").strip()},
            "class_teacher": {"name": row.get("class_teacher_name", "").strip(), "phone": row.get("class_teacher_phone", "").strip()},
            "assistants": [{"name": row.get("assistant_name", "").strip(), "phone": row.get("assistant_phone", "").strip(), "class_name": row.get("assistant_class", "").strip()}],
            "role": "student",
        })
        imported += 1
    return {"imported": imported, "skipped": skipped}
