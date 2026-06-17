"""单进程内存限流（登录 / 小信 / TTS）。多 worker 部署时每进程独立计数。"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# (method, path) -> (max_calls, window_seconds)
_RATE_RULES: dict[tuple[str, str], tuple[int, int]] = {
    ("POST", "/api/verify"): (30, 60),
    ("POST", "/api/agent/chat"): (40, 60),
    ("POST", "/api/tts"): (30, 60),
}

_store: Dict[str, Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _too_many(key: str, limit: int, window: int) -> bool:
    now = time.time()
    q = _store[key]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rule = _RATE_RULES.get((request.method, request.url.path))
        if rule:
            limit, window = rule
            ip = _client_ip(request)
            key = f"{request.method}:{request.url.path}:{ip}"
            if _too_many(key, limit, window):
                return JSONResponse(
                    status_code=429,
                    content={"success": False, "message": "请求过于频繁，请稍后再试", "data": None},
                )
        return await call_next(request)
