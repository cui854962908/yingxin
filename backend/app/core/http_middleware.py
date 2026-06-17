"""HTTP 安全头 + 上传 Content-Length 上限。"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

MAX_BODY_BYTES = 5 * 1024 * 1024
_UPLOAD_PATHS = ("/api/admin/clubs/upload-image",)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


class UploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST" and request.url.path in _UPLOAD_PATHS:
            raw = request.headers.get("content-length")
            if raw and int(raw) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"success": False, "message": "上传文件过大（上限 5MB）", "data": None},
                )
        return await call_next(request)
