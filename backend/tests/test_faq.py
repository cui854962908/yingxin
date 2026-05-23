"""FAQ API 集成测试：公开列表 + 管理端 CRUD。"""

import uuid
from unittest.mock import patch


class TestPublicListFaq:
    """GET /api/faq —— 公开列表，无需认证。"""

    def test_empty_list(self, client):
        resp = client.get("/api/faq")
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_list_with_items(self, client, admin_headers):
        with patch("app.api.faq.incremental_embed_student_faq"), \
             patch("app.api.faq.clear_faq_cache"):
            client.post("/api/admin/faq", headers=admin_headers, json={
                "question": "快递站在哪？",
                "answer": "北苑食堂西侧。",
            })
            client.post("/api/admin/faq", headers=admin_headers, json={
                "question": "宿舍几点熄灯？",
                "answer": "周日到周四 23:00。",
            })

        resp = client.get("/api/faq")
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        questions = [item["question"] for item in data["data"]]
        assert "快递站在哪？" in questions
        assert "宿舍几点熄灯？" in questions


class TestAdminCreateFaq:
    """POST /api/admin/faq —— 管理员新增 FAQ。"""

    def test_create_faq_success(self, client, admin_headers):
        with patch("app.api.faq.incremental_embed_student_faq"):
            resp = client.post("/api/admin/faq", headers=admin_headers, json={
                "question": "如何报到？",
                "answer": "携带录取通知书到指定地点报到。",
            })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["question"] == "如何报到？"
        assert data["data"]["id"] is not None

    def test_create_faq_with_keywords(self, client, admin_headers):
        with patch("app.api.faq.incremental_embed_student_faq"):
            resp = client.post("/api/admin/faq", headers=admin_headers, json={
                "question": "学费怎么交？",
                "answer": "通过统一支付平台。",
                "keywords": "学费,缴费,支付",
                "category": "财务",
            })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["keywords"] == "学费,缴费,支付"
        assert data["data"]["category"] == "财务"

    def test_create_faq_unauthorized(self, client):
        resp = client.post("/api/admin/faq", json={
            "question": "test",
            "answer": "test",
        })
        assert resp.status_code == 401


class TestAdminDeleteFaq:
    """DELETE /api/admin/faq/{faq_id} —— 管理员删除 FAQ。"""

    def test_delete_faq_success(self, client, admin_headers):
        with patch("app.api.faq.incremental_embed_student_faq"):
            create_resp = client.post("/api/admin/faq", headers=admin_headers, json={
                "question": "待删除的问题",
                "answer": "待删除的答案。",
            })
        faq_id = create_resp.json()["data"]["id"]

        with patch("app.api.faq.delete_documents_for_student_faq"):
            resp = client.delete(f"/api/admin/faq/{faq_id}", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True

        # 确认已删除
        list_resp = client.get("/api/faq")
        assert len(list_resp.json()["data"]) == 0

    def test_delete_nonexistent_faq(self, client, admin_headers):
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/api/admin/faq/{fake_id}", headers=admin_headers)
        assert resp.status_code == 404
