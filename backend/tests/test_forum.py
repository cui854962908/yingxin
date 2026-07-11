"""牧院新生说 API 集成测试。"""

import pytest
from sqlalchemy import select
from app.core.security import create_access_token
from app.models.student import Student


@pytest.fixture
def student_headers(seed_student):
    token = create_access_token(subject="20260901001", name="张三", role="student")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_student_headers(db, seed_student):
    from app.core.security import hash_id_number
    from app.models.student import Student

    s = Student(
        name="李四",
        student_id="20260901002",
        id_number_hash=hash_id_number("410105200509010022"),
        class_name="软件工程2026-1班",
        role="student",
    )
    db.add(s)
    db.commit()
    token = create_access_token(subject="20260901002", name="李四", role="student")
    return {"Authorization": f"Bearer {token}"}


def _create_post(client, headers, title="宿舍几点关门？"):
    return client.post(
        "/api/forum/posts",
        headers=headers,
        json={"title": title, "content": "想了解一下晚上回寝时间。", "category": "生活"},
    )


def _create_dorm_post(client, headers):
    return client.post(
        "/api/forum/posts",
        headers=headers,
        json={"title": "宿舍有独立卫浴吗？", "content": "想提前了解宿舍洗浴条件。", "category": "宿舍"},
    )


class TestForumPosts:
    def test_forum_role_is_visible_only_to_logged_in_forum_viewers(self, client, db, seed_student, student_headers):
        seed_student.forum_role = "teacher"
        db.commit()
        post_id = _create_post(client, student_headers).json()["data"]["id"]

        logged_in = client.get(f"/api/forum/posts/{post_id}", headers=student_headers)
        guest = client.get(f"/api/forum/posts/{post_id}")

        assert logged_in.json()["data"]["author"]["forum_role"] == "teacher"
        assert guest.json()["data"]["author"]["forum_role"] is None

    def test_forum_role_is_resolved_dynamically_for_existing_answers(self, client, db, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "这是第一条回答。"},
        )
        author = db.scalars(select(Student).where(Student.student_id == "20260901002")).one()
        author.forum_role = "assistant"
        db.commit()

        detail = client.get(f"/api/forum/posts/{post_id}", headers=student_headers).json()["data"]
        assert detail["answers"][0]["author"]["forum_role"] == "assistant"

    def test_dorm_category_can_be_created_and_filtered(self, client, student_headers):
        created = _create_dorm_post(client, student_headers)
        assert created.status_code == 200
        assert created.json()["data"]["category"] == "宿舍"

        listing = client.get("/api/forum/posts?category=宿舍")
        items = listing.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["category"] == "宿舍"

    def test_detail_view_count_increments_only_on_get(self, client, student_headers):
        created = _create_post(client, student_headers).json()["data"]
        post_id = created["id"]
        assert created["view_count"] == 0

        first = client.get(f"/api/forum/posts/{post_id}")
        second = client.get(f"/api/forum/posts/{post_id}")
        assert first.json()["data"]["view_count"] == 1
        assert second.json()["data"]["view_count"] == 2

        client.post(f"/api/forum/posts/{post_id}/close", headers=student_headers)
        listing = client.get("/api/forum/posts")
        assert listing.json()["data"]["items"][0]["view_count"] == 2

    def test_list_public_masks_author_by_grade(self, client, student_headers):
        _create_post(client, student_headers)
        resp = client.get("/api/forum/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["items"]
        assert data["data"]["items"][0]["author"]["name"] == "2026 级新生"

    def test_list_public_shows_other_grade_label(self, client, db):
        from app.core.security import hash_id_number, create_access_token
        from app.models.student import Student

        s = Student(
            name="王五",
            student_id="20250901001",
            id_number_hash=hash_id_number("410105200409010033"),
            class_name="动科2025-1班",
            role="student",
        )
        db.add(s)
        db.commit()
        token = create_access_token(subject="20250901001", name="王五", role="student")
        _create_post(client, {"Authorization": f"Bearer {token}"}, title="老生发帖")
        resp = client.get("/api/forum/posts")
        names = [it["author"]["name"] for it in resp.json()["data"]["items"]]
        assert "2025 级" in names
        assert "王五" not in names

    def test_detail_guest_hides_author_id(self, client, student_headers):
        create = _create_post(client, student_headers)
        post_id = create.json()["data"]["id"]
        resp = client.get(f"/api/forum/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["author_id"] is None

    def test_detail_logged_in_shows_author_id(self, client, student_headers):
        create = _create_post(client, student_headers)
        post_id = create.json()["data"]["id"]
        resp = client.get(f"/api/forum/posts/{post_id}", headers=student_headers)
        assert resp.json()["data"]["author_id"] is not None

    def test_list_shows_real_author_when_logged_in(self, client, student_headers):
        _create_post(client, student_headers)
        resp = client.get("/api/forum/posts", headers=student_headers)
        assert resp.json()["data"]["items"][0]["author"]["name"] == "张三"

    def test_create_and_detail(self, client, student_headers):
        resp = _create_post(client, student_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "宿舍几点关门？"
        assert data["author"]["name"] == "张三"

        post_id = data["id"]
        detail = client.get(f"/api/forum/posts/{post_id}")
        assert detail.json()["data"]["answer_count"] == 0

    def test_create_requires_auth(self, client):
        resp = client.post("/api/forum/posts", json={"title": "x", "content": "hello world", "category": "其他"})
        assert resp.status_code == 401

    def test_answer_and_accept(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        ans = client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "一般是 22:30。"},
        )
        assert ans.status_code == 200
        assert ans.json()["data"]["answer_count"] == 1

        accept = client.post(
            f"/api/forum/answers/{ans.json()['data']['answers'][0]['id']}/accept",
            headers=student_headers,
        )
        assert accept.status_code == 200
        assert accept.json()["data"]["has_accepted"] is True

    def test_non_author_cannot_accept(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        ans = client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "回答一条"},
        )
        answer_id = ans.json()["data"]["answers"][0]["id"]
        bad = client.post(f"/api/forum/answers/{answer_id}/accept", headers=other_student_headers)
        assert bad.status_code == 403

    def test_close_post(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        client.post(f"/api/forum/posts/{post_id}/close", headers=student_headers)
        blocked = client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "不能再答了"},
        )
        assert blocked.status_code == 403

    def test_mine_requires_auth(self, client, student_headers):
        assert client.get("/api/forum/posts?mine=true").status_code == 401
        resp = client.get("/api/forum/posts?mine=true", headers=student_headers)
        assert resp.status_code == 200

    def test_admin_hide(self, client, admin_headers, student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        hide = client.post(f"/api/admin/forum/posts/{post_id}/hide", headers=admin_headers)
        assert hide.status_code == 200
        assert client.get(f"/api/forum/posts/{post_id}").status_code == 404

    def test_author_delete_own_post(self, client, student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        resp = client.delete(f"/api/forum/posts/{post_id}", headers=student_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert client.get(f"/api/forum/posts/{post_id}").status_code == 404

    def test_author_delete_with_answers(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "一条回答"},
        )
        resp = client.delete(f"/api/forum/posts/{post_id}", headers=student_headers)
        assert resp.status_code == 200
        assert client.get(f"/api/forum/posts/{post_id}").status_code == 404

    def test_teacher_forum_role_cannot_delete_others_post(self, client, db, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        teacher = db.scalars(select(Student).where(Student.student_id == "20260901002")).one()
        teacher.forum_role = "teacher"
        db.commit()

        resp = client.delete(f"/api/forum/posts/{post_id}", headers=other_student_headers)
        assert resp.status_code == 403

    def test_admin_with_assistant_forum_role_can_delete_post(self, client, db, seed_admin, admin_headers, student_headers):
        seed_admin.forum_role = "assistant"
        db.commit()
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        resp = client.delete(f"/api/forum/posts/{post_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert client.get(f"/api/forum/posts/{post_id}").status_code == 404

    def test_toggle_post_like(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        like = client.post(f"/api/forum/posts/{post_id}/like", headers=other_student_headers)
        assert like.status_code == 200
        assert like.json()["data"]["like_count"] == 1
        assert like.json()["data"]["liked_by_me"] is True

        detail = client.get(f"/api/forum/posts/{post_id}", headers=other_student_headers)
        assert detail.json()["data"]["like_count"] == 1
        assert detail.json()["data"]["liked_by_me"] is True

        unlike = client.post(f"/api/forum/posts/{post_id}/like", headers=other_student_headers)
        assert unlike.json()["data"]["like_count"] == 0
        assert unlike.json()["data"]["liked_by_me"] is False

    def test_toggle_answer_like(self, client, student_headers, other_student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        ans = client.post(
            f"/api/forum/posts/{post_id}/answers",
            headers=other_student_headers,
            json={"content": "点赞测试回答"},
        )
        answer_id = ans.json()["data"]["answers"][0]["id"]
        like = client.post(f"/api/forum/answers/{answer_id}/like", headers=student_headers)
        assert like.status_code == 200
        assert like.json()["data"]["like_count"] == 1

    def test_like_requires_auth(self, client, student_headers):
        post_id = _create_post(client, student_headers).json()["data"]["id"]
        assert client.post(f"/api/forum/posts/{post_id}/like").status_code == 401
