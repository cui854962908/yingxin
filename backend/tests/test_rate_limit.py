"""测试 IP + 用户限流中间件（精确路径 & 公开 GET 前缀限流）。"""

from __future__ import annotations

import time
from collections import deque

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import (
    _READ_PREFIX_RULES,
    _RATE_RULES,
    _store,
    _too_many,
    RateLimitMiddleware,
)


# ── 单元测试：_too_many ──────────────────────────────


class TestTooMany:
    def test_under_limit_allows_requests(self):
        """未达阈值时放行，store 记录时间戳。"""
        key = "test:under"
        _store.clear()
        assert not _too_many(key, limit=3, window=60)
        assert not _too_many(key, limit=3, window=60)
        assert not _too_many(key, limit=3, window=60)
        assert len(_store[key]) == 3

    def test_exceed_limit_returns_true(self):
        """超过阈值后返回 True，不再追加时间戳。"""
        key = "test:over"
        _store.clear()
        for _ in range(5):
            _too_many(key, limit=5, window=60)
        assert _too_many(key, limit=5, window=60) is True
        # 超过限流后不再追加
        assert len(_store[key]) == 5

    def test_window_expiry_clears_old_entries(self):
        """窗口外的旧时间戳被清理，请求重新放行。"""
        key = "test:expire"
        _store.clear()
        # 伪造一个 120 秒前的时间戳
        _store[key] = deque([time.time() - 120])
        assert not _too_many(key, limit=1, window=60)
        assert len(_store[key]) == 1  # 旧记录已清除

    def test_different_keys_independent(self):
        """不同 key 之间计数独立。"""
        _store.clear()
        for _ in range(10):
            _too_many("key_a", limit=10, window=60)
        assert not _too_many("key_b", limit=10, window=60)

    def teardown_method(self):
        _store.clear()


# ── 集成测试：通过 TestClient 触发限流 ────────────────


@pytest.fixture
def client_with_low_limits(monkeypatch):
    """替换限流规则为极低阈值（2 次/60s），方便测试。"""
    from app.main import app

    monkeypatch.setitem(_RATE_RULES, ("POST", "/api/verify"), (2, 60))
    monkeypatch.setattr(
        "app.core.rate_limit._READ_PREFIX_RULES",
        {"/api/faq": (2, 60), "/api/announcements": (2, 60), "/api/clubs": (2, 60)},
    )
    _store.clear()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    _store.clear()


class TestRateLimitIntegration:
    def test_public_get_under_limit(self, client_with_low_limits):
        """公开 GET 在阈值内正常返回。"""
        r1 = client_with_low_limits.get("/api/faq?page=1&page_size=2")
        r2 = client_with_low_limits.get("/api/announcements")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_public_get_over_limit_returns_429(self, client_with_low_limits):
        """超过公开 GET 限流后返回 429。"""
        for _ in range(2):
            r = client_with_low_limits.get("/api/faq?page=1&page_size=2")
            assert r.status_code == 200
        r = client_with_low_limits.get("/api/faq?page=1&page_size=2")
        assert r.status_code == 429
        body = r.json()
        assert body["success"] is False
        assert "频繁" in body["message"]

    def test_public_get_clubs_prefix_match(self, client_with_low_limits):
        """/api/clubs/{id} 也匹配前缀，受同一限流桶约束。"""
        for _ in range(2):
            r = client_with_low_limits.get("/api/clubs")
            assert r.status_code == 200
        # 第三次请求 /api/clubs（即使是详情）也命中前缀限流
        r = client_with_low_limits.get("/api/clubs/nonexistent-id")
        assert r.status_code == 429

    def test_post_verify_rate_limit(self, client_with_low_limits):
        """登录接口限流生效。"""
        body = {"name": "test", "student_id": "2024001", "password": ""}
        for _ in range(2):
            r = client_with_low_limits.post("/api/verify", json=body)
            # 可能是 401（凭据错）但不能是 429
            assert r.status_code != 429
        r = client_with_low_limits.post("/api/verify", json=body)
        assert r.status_code == 429

    def test_429_response_format(self, client_with_low_limits):
        """429 响应体符合项目统一格式 {success, message, data}。"""
        for _ in range(3):
            client_with_low_limits.get("/api/faq?page=1&page_size=2")
        r = client_with_low_limits.get("/api/faq?page=1&page_size=2")
        body = r.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert body["success"] is False

    def test_different_prefixes_independent(self, client_with_low_limits):
        """FAQ 限流不影响公告。"""
        for _ in range(2):
            client_with_low_limits.get("/api/faq?page=1&page_size=2")
        # FAQ 已耗尽，但公告仍可访问
        r = client_with_low_limits.get("/api/announcements")
        assert r.status_code == 200

    def test_unlimited_path_not_affected(self, client_with_low_limits):
        """未配置限流的路径不受影响。"""
        for _ in range(5):
            r = client_with_low_limits.get("/api/auth/me")
            # 无 token，预期 401 而非 429
            assert r.status_code == 401
