"""公告 API 集成测试：公开列表 + 管理端发布/删除。"""

import uuid
from unittest.mock import patch


class TestPublicListAnnouncements:
    """GET /api/announcements —— 公开列表，无需认证。"""

    def test_empty_list(self, client):
        resp = client.get("/api/announcements")
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_list_with_items(self, client, admin_headers):
        with patch("app.api.announcements.incremental_embed_announcement"):
            client.post("/api/admin/announcements", headers=admin_headers, json={
                "title": "2026新生报到须知",
                "content": "请于 9 月 1 日前完成报到。",
            })
            client.post("/api/admin/announcements", headers=admin_headers, json={
                "title": "军训通知",
                "content": "军训自 9 月 2 日开始。",
            })

        resp = client.get("/api/announcements")
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        titles = [item["title"] for item in data["data"]]
        assert "2026新生报到须知" in titles
        assert "军训通知" in titles


class TestAdminCreateAnnouncement:
    """POST /api/admin/announcements —— 管理员发布公告。"""

    def test_create_announcement_success(self, client, admin_headers):
        with patch("app.api.announcements.incremental_embed_announcement"):
            resp = client.post("/api/admin/announcements", headers=admin_headers, json={
                "title": "迎新系统上线通知",
                "content": "迎新系统已正式上线运行。",
            })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["title"] == "迎新系统上线通知"
        assert data["data"]["id"] is not None

    def test_create_announcement_with_date(self, client, admin_headers):
        with patch("app.api.announcements.incremental_embed_announcement"):
            resp = client.post("/api/admin/announcements", headers=admin_headers, json={
                "title": "限期公告",
                "content": "本公告有日期。",
                "date": "2026-09-01",
            })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["date"] == "2026-09-01"

    def test_create_announcement_unauthorized(self, client):
        resp = client.post("/api/admin/announcements", json={
            "title": "test",
            "content": "test",
        })
        assert resp.status_code == 401


class TestAdminDeleteAnnouncement:
    """DELETE /api/admin/announcements/{ann_id} —— 管理员删除公告。"""

    def test_delete_announcement_success(self, client, admin_headers):
        with patch("app.api.announcements.incremental_embed_announcement"):
            create_resp = client.post("/api/admin/announcements", headers=admin_headers, json={
                "title": "待删除公告",
                "content": "这条即将被删除。",
            })
        ann_id = create_resp.json()["data"]["id"]

        with patch("app.api.announcements.delete_documents_for_announcement"):
            resp = client.delete(f"/api/admin/announcements/{ann_id}", headers=admin_headers)
        data = resp.json()
        assert data["success"] is True

        # 确认已删除
        list_resp = client.get("/api/announcements")
        assert len(list_resp.json()["data"]) == 0

    def test_delete_nonexistent_announcement(self, client, admin_headers):
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/api/admin/announcements/{fake_id}", headers=admin_headers)
        assert resp.status_code == 404
