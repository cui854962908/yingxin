"""学生管理端点测试"""

import io

import openpyxl


class TestListStudents:
    def test_list_grouped_as_admin(self, client, db, auth_headers):
        from app.models.student import Student
        db.add_all([
            Student(name="张三", student_id="s001", id_number="1", class_name="一班", role="student"),
            Student(name="李四", student_id="s002", id_number="2", class_name="一班", role="student"),
            Student(name="王五", student_id="s003", id_number="3", class_name="二班", role="student"),
        ])
        db.commit()

        resp = client.get("/api/admin/students", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert "一班" in data["data"]
        assert len(data["data"]["一班"]) == 2
        assert len(data["data"]["二班"]) == 1

    def test_list_denied_for_student(self, client, student_headers):
        resp = client.get("/api/admin/students", headers=student_headers)
        assert resp.status_code == 403

    def test_list_no_token(self, client):
        resp = client.get("/api/admin/students")
        assert resp.status_code == 401


class TestSearchStudents:
    def test_search_found(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(name="张三", student_id="20260901001", id_number="1", role="student"))
        db.commit()

        resp = client.get("/api/admin/students/search?q=20260901", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert data["data"][0]["student_id"] == "20260901001"

    def test_search_not_found_returns_empty_list(self, client, auth_headers):
        resp = client.get("/api/admin/students/search?q=nonexistent", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_search_denied_for_student(self, client, student_headers):
        resp = client.get("/api/admin/students/search?q=test", headers=student_headers)
        assert resp.status_code == 403


class TestCreateStudent:
    def test_create_with_flat_fields(self, client, db, auth_headers):
        resp = client.post("/api/admin/students", headers=auth_headers, json={
            "name": "新生",
            "student_id": "new001",
            "id_number": "410105200509010022",
            "class_name": "软件工程班",
            "dormitory": "南苑1号",
            "advisor_name": "张老师",
            "advisor_phone": "139-0000-1111",
            "class_teacher_name": "王老师",
            "class_teacher_phone": "139-0000-2222",
            "assistant_name": "代班同学",
            "assistant_phone": "139-0000-3333",
            "assistant_class_name": "软件工程2025",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "新生"
        assert data["data"]["advisor"]["name"] == "张老师"
        assert data["data"]["advisor"]["phone"] == "139-0000-1111"
        assert data["data"]["class_teacher"]["name"] == "王老师"
        assert len(data["data"]["assistants"]) == 1
        assert data["data"]["assistants"][0]["name"] == "代班同学"

    def test_create_duplicate_student_id(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(name="已存在", student_id="dup001", id_number="1", role="student"))
        db.commit()

        resp = client.post("/api/admin/students", headers=auth_headers, json={
            "name": "重复", "student_id": "dup001", "id_number": "2",
        })
        assert resp.status_code == 400

    def test_create_missing_name(self, client, auth_headers):
        resp = client.post("/api/admin/students", headers=auth_headers, json={
            "name": "", "student_id": "new002",
        })
        assert resp.status_code == 422

    def test_create_as_student_denied(self, client, student_headers):
        resp = client.post("/api/admin/students", headers=student_headers, json={
            "name": "新生", "student_id": "new003",
        })
        assert resp.status_code == 403


class TestUpdateStudent:
    def test_update_partial(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(name="原姓名", student_id="upd001", id_number="1", dormitory="旧宿舍", role="student"))
        db.commit()

        resp = client.put("/api/admin/students/upd001", headers=auth_headers, json={
            "dormitory": "新宿舍",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["dormitory"] == "新宿舍"
        assert data["data"]["name"] == "原姓名"  # 未改

    def test_update_advisor_info(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(
            name="学生", student_id="upd002", id_number="1",
            advisor_name="旧导师", advisor_phone="111",
            role="student",
        ))
        db.commit()

        resp = client.put("/api/admin/students/upd002", headers=auth_headers, json={
            "advisor_name": "新导师",
            "advisor_phone": "999",
        })
        data = resp.json()
        assert data["data"]["advisor"]["name"] == "新导师"
        assert data["data"]["advisor"]["phone"] == "999"

    def test_update_nonexistent(self, client, auth_headers):
        resp = client.put("/api/admin/students/nonexistent", headers=auth_headers, json={
            "name": "xxx",
        })
        assert resp.status_code == 404


class TestDeleteStudent:
    def test_delete_success(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(name="待删", student_id="del001", id_number="1", role="student"))
        db.commit()

        resp = client.delete("/api/admin/students/del001", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert "已删除" in data["message"]

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/api/admin/students/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestImportExcel:
    def test_import_success(self, client, db, auth_headers):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["姓名", "学号", "身份证号", "班级", "宿舍", "辅导员", "辅导员电话", "班主任", "班主任电话", "代班", "代班电话", "代班班级"])
        ws.append(["导入生", "imp001", "410105200509010033", "导入班", "宿舍1", "导1", "111", "班1", "222", "代1", "333", "代班班级1"])
        ws.append(["导入生2", "imp002", "410105200509010044", "导入班2", "宿舍2", "导2", "444", "班2", "555", "代2", "666", "代班班级2"])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = client.post(
            "/api/admin/students/import",
            headers=auth_headers,
            files={"file": ("test.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["imported"] == 2
        assert data["data"]["skipped"] == 0

    def test_import_skips_duplicates(self, client, db, auth_headers):
        from app.models.student import Student
        db.add(Student(name="已存在", student_id="imp001", id_number="1", role="student"))
        db.commit()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["姓名", "学号", "身份证号", "班级", "宿舍"])
        ws.append(["导入生", "imp001", "410105200509010033", "导入班", "宿舍1"])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = client.post(
            "/api/admin/students/import",
            headers=auth_headers,
            files={"file": ("test.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        data = resp.json()
        assert data["data"]["skipped"] == 1

    def test_import_wrong_format(self, client, auth_headers):
        resp = client.post(
            "/api/admin/students/import",
            headers=auth_headers,
            files={"file": ("test.txt", io.BytesIO(b"not excel"), "text/plain")},
        )
        assert resp.status_code == 400
