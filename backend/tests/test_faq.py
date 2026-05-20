"""FAQ 端点测试"""


class TestListFaq:
    def test_list_public(self, client, db):
        from app.models.faq import Faq
        db.add_all([
            Faq(question="问题1", answer="答案1"),
            Faq(question="问题2", answer="答案2"),
        ])
        db.commit()

        resp = client.get("/api/faq")
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_list_empty(self, client):
        resp = client.get("/api/faq")
        data = resp.json()
        assert data["success"] is True
        assert data["data"] == []


class TestCreateFaq:
    def test_create_as_admin(self, client, auth_headers):
        resp = client.post("/api/admin/faq", headers=auth_headers, json={
            "question": "测试问题？", "answer": "测试答案。",
        })
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["question"] == "测试问题？"
        assert "id" in data["data"]

    def test_create_as_student_denied(self, client, student_headers):
        resp = client.post("/api/admin/faq", headers=student_headers, json={
            "question": "?", "answer": "!",
        })
        assert resp.status_code == 403

    def test_create_empty_question(self, client, auth_headers):
        resp = client.post("/api/admin/faq", headers=auth_headers, json={
            "question": "", "answer": "答案",
        })
        assert resp.status_code == 422


class TestDeleteFaq:
    def test_delete_as_admin(self, client, db, auth_headers):
        from app.models.faq import Faq
        faq = Faq(question="待删", answer="删除答案")
        db.add(faq)
        db.commit()
        faq_id = str(faq.id)

        resp = client.delete(f"/api/admin/faq/{faq_id}", headers=auth_headers)
        assert resp.json()["success"] is True

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/api/admin/faq/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_as_student_denied(self, client, student_headers):
        resp = client.delete("/api/admin/faq/some-id", headers=student_headers)
        assert resp.status_code == 403
