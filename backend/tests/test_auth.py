"""auth 路由集成测试：登录验证 + 锁定逻辑 + /auth/me。"""

import pytest
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.services import login_guard


class TestVerifyStudent:
    """POST /api/verify 登录验证。"""

    def test_valid_credentials_return_token(self, client, seed_student):
        """正确凭证返回 token。"""
        resp = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        })
        data = resp.json()
        assert data["success"] is True
        assert "token" in data
        assert "refresh_token" in data
        assert data["data"]["name"] == "张三"

    def test_login_persists_refresh_token(self, client, db, seed_student):
        """登录签发的 refresh token 会持久化，后续才能刷新会话。"""
        resp = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        })
        data = resp.json()

        record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == hash_refresh_token(data["refresh_token"]),
            RefreshToken.revoked.is_(False),
        ).first()

        assert data["success"] is True
        assert record is not None
        assert record.student_id == seed_student.id

    def test_wrong_credentials_return_remaining(self, client, seed_student):
        """错误凭证返回剩余次数。"""
        resp = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "wrong",
        })
        data = resp.json()
        assert data["success"] is False
        assert "还剩" in data["message"]
        assert data["data"]["remaining_attempts"] == 4

    def test_lock_after_5_failures(self, client, seed_student):
        """连续 5 次错误后返回锁定消息。"""
        payload = {
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "wrong",
        }
        # 前 4 次
        for _ in range(4):
            client.post("/api/verify", json=payload)
        # 第 5 次
        resp = client.post("/api/verify", json=payload)
        data = resp.json()
        assert data["success"] is False
        assert "锁定" in data["message"]

    def test_locked_account_cannot_login(self, client, seed_student):
        """锁定后即使正确凭证也无法登录。"""
        # 先锁定
        payload_wrong = {
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "wrong",
        }
        for _ in range(5):
            client.post("/api/verify", json=payload_wrong)

        # 正确凭证登录
        resp = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        })
        data = resp.json()
        assert data["success"] is False
        assert "锁定" in data["message"]

    def test_auth_me_returns_profile(self, client, seed_student):
        """已认证用户 GET /auth/me 返回个人信息。"""
        # 先登录获取 token
        resp = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        })
        token = resp.json()["token"]

        # 用 token 访问 /auth/me
        resp2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        data = resp2.json()
        assert data["success"] is True
        assert data["data"]["name"] == "张三"
        assert data["data"]["student_id"] == "20260901001"
        assert isinstance(data["data"]["id"], int)

    def test_refresh_rotates_token_and_rejects_old_token(self, client, db, seed_student):
        """刷新接口会轮换 refresh token，并让旧 refresh token 失效。"""
        login = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        }).json()
        old_refresh = login["refresh_token"]

        refreshed = client.post("/api/refresh", json={"refresh_token": old_refresh}).json()
        old_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == hash_refresh_token(old_refresh),
        ).first()

        assert refreshed["success"] is True
        assert refreshed["data"]["access_token"]
        assert refreshed["data"]["refresh_token"] != old_refresh
        assert old_record is not None
        assert old_record.revoked is True

        reused = client.post("/api/refresh", json={"refresh_token": old_refresh}).json()
        assert reused["success"] is False

    def test_logout_revokes_refresh_token(self, client, db, seed_student):
        """主动退出会撤销当前 refresh token。"""
        login = client.post("/api/verify", json={
            "name": "张三",
            "student_id": "20260901001",
            "id_number": "410105200509010011",
        }).json()
        refresh_token = login["refresh_token"]

        logout = client.post("/api/logout", json={"refresh_token": refresh_token}).json()
        record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == hash_refresh_token(refresh_token),
        ).first()

        assert logout["success"] is True
        assert record is not None
        assert record.revoked is True
