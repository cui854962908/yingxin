"""公告端点测试"""

from datetime import date


class TestListAnnouncements:
    def test_list_public_sorted_by_date(self, client, db):
        from app.models.announcement import Announcement
        db.add_all([
            Announcement(date=date(2026, 8, 10), title="旧公告", content="旧内容"),
            Announcement(date=date(2026, 9, 1), title="新公告", content="新内容"),
        ])
        db.commit()

        resp = client.get("/api/announcements")
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["date"] >= data["data"][1]["date"]

    def test_list_empty(self, client):
        resp = client.get("/api/announcements")
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []


class TestCreateAnnouncement:
    def test_create_as_admin(self, client, auth_headers):
        resp = client.post("/api/admin/announcements", headers=auth_headers, json={
            "title": "测试公告", "content": "测试内容",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["title"] == "测试公告"
        assert "id" in data["data"]

    def test_create_with_explicit_date(self, client, auth_headers):
        resp = client.post("/api/admin/announcements", headers=auth_headers, json={
            "title": "指定日期公告", "content": "内容", "date": "2026-09-01",
        })
        data = resp.json()
        assert data["data"]["date"] == "2026-09-01"

    def test_create_defaults_to_today(self, client, auth_headers):
        resp = client.post("/api/admin/announcements", headers=auth_headers, json={
            "title": "今日公告", "content": "默认日期",
        })
        data = resp.json()
        assert data["data"]["date"] == str(date.today())

    def test_create_as_student_denied(self, client, student_headers):
        resp = client.post("/api/admin/announcements", headers=student_headers, json={
            "title": "越权公告", "content": "内容",
        })
        assert resp.status_code == 403

    def test_create_empty_title(self, client, auth_headers):
        resp = client.post("/api/admin/announcements", headers=auth_headers, json={
            "title": "", "content": "内容",
        })
        assert resp.status_code == 422


class TestDeleteAnnouncement:
    def test_delete_as_admin(self, client, db, auth_headers):
        from app.models.announcement import Announcement
        ann = Announcement(date=date.today(), title="待删", content="待删内容")
        db.add(ann)
        db.commit()
        ann_id = str(ann.id)

        resp = client.delete(f"/api/admin/announcements/{ann_id}", headers=auth_headers)
        assert resp.json()["success"] is True

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/api/admin/announcements/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_as_student_denied(self, client, student_headers):
        resp = client.delete("/api/admin/announcements/some-id", headers=student_headers)
        assert resp.status_code == 403
