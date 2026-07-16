"""社团 API 集成测试：公开列表/详情 + 管理端 CRUD。"""

import uuid

import pytest


class TestPublicListClubs:
    """GET /api/clubs —— 公开列表，无需认证。"""

    def test_empty_list(self, client):
        resp = client.get("/api/clubs")
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_list_with_items(self, client, admin_headers):
        client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "街舞社",
            "category": "兴趣社团",
            "intro": "零基础也能炸场",
        })
        client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "学生会",
            "category": "团学会",
            "intro": "服务同学，锻炼自我",
        })

        resp = client.get("/api/clubs")
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        names = [item["name"] for item in data["data"]]
        assert "街舞社" in names
        assert "学生会" in names


class TestPublicGetClub:
    """GET /api/clubs/{id} —— 公开详情。"""

    def test_get_club_detail(self, client, admin_headers):
        create_resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "街舞社",
            "category": "兴趣社团",
            "intro": "零基础也能炸场",
            "founded_year": 2020,
            "member_count": 60,
            "advisor_name": "李老师",
        })
        club_id = create_resp.json()["data"]["id"]

        resp = client.get(f"/api/clubs/{club_id}")
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "街舞社"
        assert data["data"]["founded_year"] == 2020
        assert data["data"]["member_count"] == 60
        assert data["data"]["advisor_name"] == "李老师"

    def test_get_nonexistent_club(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/clubs/{fake_id}")
        assert resp.status_code == 404
        assert "不存在" in resp.json()["message"]


class TestAdminCreateClub:
    """POST /api/admin/clubs —— 管理员新增社团。"""

    def test_create_minimal(self, client, admin_headers):
        resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "街舞社",
            "category": "兴趣社团",
            "intro": "零基础也能炸场",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["name"] == "街舞社"
        assert data["data"]["status"] == "招新中"
        assert data["data"]["id"] is not None

    def test_create_full(self, client, admin_headers):
        resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "学生会",
            "category": "团学会",
            "intro": "服务同学",
            "status": "招新中",
            "carousel_images": '["/img/a.jpg","/img/b.jpg"]',
            "founded_year": 2015,
            "member_count": 120,
            "advisor_name": "王老师",
            "description": "<p>校学生会介绍</p>",
            "leader_name": "赵明",
            "leader_phone": "13800001111",
            "qq_group": "123456789",
            "wechat_qr": "/img/qr.png",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["founded_year"] == 2015
        assert data["data"]["leader_name"] == "赵明"

    def test_create_unauthorized(self, client):
        resp = client.post("/api/admin/clubs", json={
            "name": "test",
            "category": "兴趣社团",
            "intro": "test",
        })
        assert resp.status_code == 401


class TestAdminUpdateClub:
    """PUT /api/admin/clubs/{id} —— 管理员更新社团。"""

    def test_update_partial(self, client, admin_headers):
        create_resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "街舞社",
            "category": "兴趣社团",
            "intro": "零基础也能炸场",
        })
        club_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/api/admin/clubs/{club_id}", headers=admin_headers, json={
            "member_count": 80,
            "status": "已结束",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["member_count"] == 80
        assert data["data"]["status"] == "已结束"
        assert data["data"]["name"] == "街舞社"

    def test_update_nonexistent(self, client, admin_headers):
        fake_id = str(uuid.uuid4())
        resp = client.put(f"/api/admin/clubs/{fake_id}", headers=admin_headers, json={
            "intro": "new",
        })
        assert resp.status_code == 404


class TestAdminDeleteClub:
    """DELETE /api/admin/clubs/{id} —— 管理员删除社团。"""

    def test_delete_success(self, client, admin_headers):
        create_resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "待删除社团",
            "category": "兴趣社团",
            "intro": "将被删除",
        })
        club_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/api/admin/clubs/{club_id}", headers=admin_headers)
        assert resp.json()["success"] is True

        list_resp = client.get("/api/clubs")
        assert len(list_resp.json()["data"]) == 0

    def test_delete_nonexistent(self, client, admin_headers):
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/api/admin/clubs/{fake_id}", headers=admin_headers)
        assert resp.status_code == 404


class TestAdminClubRecruitFields:
    def test_create_and_detail_return_recruit_fields(self, client, admin_headers):
        resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "招新测试社团",
            "category": "兴趣社团",
            "intro": "测试招新字段",
            "recruit_target": "全校新生",
            "recruit_count": 30,
            "recruit_require": "热爱社团活动，积极参与",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["recruit_target"] == "全校新生"
        assert data["data"]["recruit_count"] == 30
        assert data["data"]["recruit_require"] == "热爱社团活动，积极参与"

        club_id = data["data"]["id"]
        detail_resp = client.get(f"/api/clubs/{club_id}")
        detail = detail_resp.json()["data"]
        assert detail["recruit_target"] == "全校新生"
        assert detail["recruit_count"] == 30
        assert detail["recruit_require"] == "热爱社团活动，积极参与"

    def test_update_and_clear_recruit_fields(self, client, admin_headers):
        create_resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "招新清空社团",
            "category": "兴趣社团",
            "intro": "测试清空招新字段",
            "recruit_target": "全校新生",
            "recruit_count": 20,
            "recruit_require": "积极参加活动",
        })
        club_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/api/admin/clubs/{club_id}", headers=admin_headers, json={
            "recruit_target": "",
            "recruit_count": None,
            "recruit_require": "   ",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["recruit_target"] is None
        assert data["data"]["recruit_count"] is None
        assert data["data"]["recruit_require"] is None

    def test_zero_recruit_count_is_preserved(self, client, admin_headers):
        resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "Zero Recruit Club",
            "category": "Interest Club",
            "intro": "Regression test for zero recruit count",
            "recruit_count": 0,
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["recruit_count"] == 0

        club_id = data["data"]["id"]
        detail_resp = client.get(f"/api/clubs/{club_id}")
        assert detail_resp.json()["data"]["recruit_count"] == 0

    def test_rejects_negative_recruit_count(self, client, admin_headers):
        resp = client.post("/api/admin/clubs", headers=admin_headers, json={
            "name": "负数招新社团",
            "category": "兴趣社团",
            "intro": "测试负数招新人数",
            "recruit_count": -1,
        })
        assert resp.status_code == 422


class TestClubAdminOwnership:
    """club_admin 创建/编辑自己名下社团（修复 get_student_id_from_payload 调用）。"""

    @pytest.fixture
    def club_admin_headers(self, db):
        from app.core.security import DEFAULT_INITIAL_PASSWORD, create_access_token, hash_password
        from app.models.student import Student

        s = Student(
            name="社团长",
            student_id="20260909999",
            password_hash=hash_password(DEFAULT_INITIAL_PASSWORD),
            class_name="动科2026-1班",
            role="club_admin",
        )
        db.add(s)
        db.commit()
        token = create_access_token(subject="20260909999", name="社团长", role="club_admin")
        return {"Authorization": f"Bearer {token}"}

    def test_club_admin_create_club(self, client, club_admin_headers):
        resp = client.post(
            "/api/admin/clubs",
            headers=club_admin_headers,
            json={"name": "摄影社", "category": "兴趣社团", "intro": "记录校园"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "摄影社"
