"""测试 HTTP 安全响应头中间件。"""

from fastapi.testclient import TestClient

from app.core.http_middleware import MAX_BODY_BYTES

HEADER_CHECKS = [
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
]

CSP_MUST_HAVE = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    "frame-src 'self'",
    "media-src 'self' blob:",
]


def _client():
    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


class TestSecurityHeaders:
    def test_all_security_headers_present_on_public_route(self):
        """公开路由（/api/faq）应带齐所有安全头。"""
        r = _client().get("/api/faq?page=1&page_size=1")
        assert r.status_code == 200
        for name, expected in HEADER_CHECKS:
            assert r.headers.get(name) == expected, f"{name} 缺失或值不符"

    def test_security_headers_on_error_response(self):
        """404 响应也应带安全头（响应应经中间件处理）。"""
        r = _client().get("/api/not-exist")
        for name, expected in HEADER_CHECKS:
            assert r.headers.get(name) == expected, f"{name} 缺失或值不符"

    def test_security_headers_on_post(self):
        """POST 响应也应带安全头。"""
        r = _client().post("/api/verify", json={"name": "", "student_id": "", "id_number": ""})
        for name, expected in HEADER_CHECKS:
            assert r.headers.get(name) == expected, f"{name} 缺失或值不符"


class TestCSPHeader:
    def test_csp_header_present(self):
        """Content-Security-Policy 头存在且非空。"""
        r = _client().get("/api/faq?page=1&page_size=1")
        csp = r.headers.get("Content-Security-Policy")
        assert csp, "CSP header missing"

    def test_csp_contains_required_directives(self):
        """CSP 包含所有必需的指令。"""
        r = _client().get("/api/faq?page=1&page_size=1")
        csp = r.headers["Content-Security-Policy"]
        for directive in CSP_MUST_HAVE:
            assert directive in csp, f"缺少指令: {directive}"


class TestUploadSizeLimit:
    def test_upload_within_limit_passes(self):
        """上传内容在 5MB 以内，中间件放行。"""
        r = _client().post(
            "/api/admin/clubs/upload-image",
            headers={"Content-Length": str(MAX_BODY_BYTES)},
            data=b"x" * 100,
        )
        # 预期 403（无 token）或 401，而非 413
        assert r.status_code != 413

    def test_upload_exceeds_limit_returns_413(self):
        """上传内容超过 5MB 上限，返回 413。"""
        r = _client().post(
            "/api/admin/clubs/upload-image",
            headers={"Content-Length": str(MAX_BODY_BYTES + 1)},
            data=b"x" * 100,
        )
        assert r.status_code == 413
        body = r.json()
        assert body["success"] is False
        assert "5MB" in body["message"]

    def test_non_upload_path_not_limited(self):
        """非上传路径不受 Content-Length 检查影响。"""
        r = _client().post(
            "/api/verify",
            headers={"Content-Length": str(MAX_BODY_BYTES + 1)},
            json={"name": "", "student_id": "", "id_number": ""},
        )
        # 不应该是 413
        assert r.status_code != 413
