"""认证端点测试"""


class TestVerifyLogin:
    def test_verify_success(self, client, db):
        from app.models.student import Student
        db.add(Student(
            name="张三", student_id="2026001", id_number="410105200509010011",
            class_name="计算机班", dormitory="北苑3号",
            advisor_name="李老师", advisor_phone="138-0000-1111",
            class_teacher_name="赵老师", class_teacher_phone="137-0000-7777",
            role="student",
        ))
        db.commit()

        resp = client.post("/api/verify", json={
            "name": "张三", "student_id": "2026001", "id_number": "410105200509010011",
        })
        data = resp.json()

        assert data["success"] is True
        assert "token" in data
        assert data["data"]["name"] == "张三"
        assert data["data"]["advisor"]["name"] == "李老师"
        assert data["data"]["class_teacher"]["name"] == "赵老师"
        assert data["data"]["role"] == "student"

    def test_verify_wrong_name(self, client, db):
        from app.models.student import Student
        db.add(Student(
            name="张三", student_id="2026001", id_number="410105200509010011",
            role="student",
        ))
        db.commit()

        resp = client.post("/api/verify", json={
            "name": "李四", "student_id": "2026001", "id_number": "410105200509010011",
        })
        data = resp.json()
        assert data["success"] is False

    def test_verify_wrong_id_number(self, client, db):
        from app.models.student import Student
        db.add(Student(
            name="张三", student_id="2026001", id_number="410105200509010011",
            role="student",
        ))
        db.commit()

        resp = client.post("/api/verify", json={
            "name": "张三", "student_id": "2026001", "id_number": "000000000000000000",
        })
        data = resp.json()
        assert data["success"] is False

    def test_verify_admin_role(self, client, db):
        from app.models.student import Student
        db.add(Student(
            name="管理员", student_id="adm001", id_number="410105200509010011",
            role="admin",
        ))
        db.commit()

        resp = client.post("/api/verify", json={
            "name": "管理员", "student_id": "adm001", "id_number": "410105200509010011",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["role"] == "admin"

    def test_verify_empty_name(self, client):
        resp = client.post("/api/verify", json={
            "name": "", "student_id": "2026001", "id_number": "410105200509010011",
        })
        assert resp.status_code == 422


class TestAuthMe:
    def test_auth_me_valid_token(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        data = resp.json()
        assert data["success"] is True
        assert "sub" in data["data"]
        assert data["data"]["role"] == "admin"

    def test_auth_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_auth_me_invalid_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401
