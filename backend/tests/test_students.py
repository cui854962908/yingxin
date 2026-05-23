"""管理员学生管理 API 集成测试。"""

from unittest.mock import patch

import pytest


class TestAdminListStudents:
    """GET /api/admin/students —— 按班级分组列表。"""

    def test_returns_empty_when_no_students(self, client, admin_headers):
        resp = client.get("/api/admin/students", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == {}

    def test_returns_students_grouped_by_class(self, client, admin_headers, seed_student):
        resp = client.get("/api/admin/students", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        assert "计算机科学2026-1班" in data["data"]
        students = data["data"]["计算机科学2026-1班"]
        assert len(students) == 1
        assert students[0]["name"] == "张三"

    def test_admin_record_excluded_from_list(self, client, admin_headers, seed_student, seed_admin):
        resp = client.get("/api/admin/students", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        all_names = [
            s["name"]
            for class_students in data["data"].values()
            for s in class_students
        ]
        assert "管理员" not in all_names

    def test_unauthorized_without_token(self, client):
        resp = client.get("/api/admin/students")
        assert resp.status_code == 401

    def test_forbidden_for_student_role(self, client, seed_student):
        from app.core.security import create_access_token
        token = create_access_token(subject="20260901001", name="张三", role="student")
        resp = client.get("/api/admin/students", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestAdminSearchStudents:
    """GET /api/admin/students/search —— 按学号搜索。"""

    def test_search_by_student_id_fragment(self, client, admin_headers, seed_student):
        resp = client.get("/api/admin/students/search?q=202609", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "张三"

    def test_search_no_match(self, client, admin_headers):
        resp = client.get("/api/admin/students/search?q=nonexistent", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_search_empty_query(self, client, admin_headers):
        resp = client.get("/api/admin/students/search?q=", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []


class TestAdminCreateStudent:
    """POST /api/admin/students —— 新增学生。"""

    def test_create_student_success(self, client, admin_headers):
        resp = client.post("/api/admin/students", headers=admin_headers, json={
            "name": "李四",
            "student_id": "20260901002",
            "id_number": "410105200509010022",
            "class_name": "软件工程2026-1班",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "李四"
        assert data["data"]["student_id"] == "20260901002"

    def test_create_duplicate_student_id(self, client, admin_headers, seed_student):
        resp = client.post("/api/admin/students", headers=admin_headers, json={
            "name": "王五",
            "student_id": "20260901001",  # 与 seed_student 重复
            "id_number": "410105200509010033",
            "class_name": "计算机科学2026-1班",
        })
        data = resp.json()
        assert data["success"] is False
        assert "已存在" in data["message"]

    def test_create_reserved_admin_id(self, client, admin_headers):
        resp = client.post("/api/admin/students", headers=admin_headers, json={
            "name": "假管理员",
            "student_id": "admin",
            "id_number": "410105200509010044",
            "class_name": "计算机科学2026-1班",
        })
        data = resp.json()
        assert data["success"] is False
        assert "系统保留" in data["message"]


class TestAdminUpdateStudent:
    """PUT /api/admin/students/{student_id} —— 编辑学生。"""

    def test_update_student_class(self, client, admin_headers, seed_student):
        resp = client.put("/api/admin/students/20260901001", headers=admin_headers, json={
            "class_name": "物联网工程2026-2班",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["class_name"] == "物联网工程2026-2班"

    def test_update_nonexistent_student(self, client, admin_headers):
        resp = client.put("/api/admin/students/99999999", headers=admin_headers, json={
            "class_name": "某某班",
        })
        assert resp.status_code == 404

    def test_cannot_update_admin_record(self, client, admin_headers, seed_admin):
        resp = client.put("/api/admin/students/admin", headers=admin_headers, json={
            "class_name": "某班",
        })
        assert resp.status_code == 403


class TestAdminDeleteStudent:
    """DELETE /api/admin/students/{student_id} —— 删除学生。"""

    def test_delete_student_success(self, client, admin_headers, seed_student):
        resp = client.delete("/api/admin/students/20260901001", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True

        # 确认已删除
        resp2 = client.get("/api/admin/students", headers=admin_headers)
        assert resp2.json()["data"] == {}

    def test_delete_nonexistent_student(self, client, admin_headers):
        resp = client.delete("/api/admin/students/99999999", headers=admin_headers)
        assert resp.status_code == 404

    def test_cannot_delete_admin_record(self, client, admin_headers, seed_admin):
        resp = client.delete("/api/admin/students/admin", headers=admin_headers)
        assert resp.status_code == 403


class TestAdminImportStudents:
    """POST /api/admin/students/import —— Excel 批量导入。"""

    def test_import_rejects_non_xlsx(self, client, admin_headers):
        resp = client.post(
            "/api/admin/students/import",
            headers=admin_headers,
            files={"file": ("test.csv", b"a,b,c", "text/csv")},
        )
        data = resp.json()
        assert data["success"] is False
        assert ".xlsx" in data["message"]

    def test_import_xlsx_success(self, client, admin_headers):
        from app.services.import_service import ImportResult
        fake_result = ImportResult(imported=3, updated=1, skipped=2, errors=["行5: 学号为空"])

        with patch("app.api.students.import_students_xlsx", return_value=fake_result):
            resp = client.post(
                "/api/admin/students/import",
                headers=admin_headers,
                files={"file": ("students.xlsx", b"fake-xlsx-content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["imported"] == 3
        assert data["data"]["updated"] == 1
        assert data["data"]["skipped"] == 2
        assert "行5" in data["data"]["errors"][0]
