"""单进程内存限流（IP + 登录用户 sub）。多 worker 时每进程独立计数。"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.security import decode_token

# (method, path) -> (max_calls, window_seconds) — 按 IP
_RATE_RULES: dict[tuple[str, str], tuple[int, int]] = {
    ("POST", "/api/verify"): (30, 60),
    ("POST", "/api/agent/chat"): (40, 60),
    ("POST", "/api/chat"): (40, 60),
    ("POST", "/api/tts"): (30, 60),
}

# 公开 GET 端点前缀限流（防脚本刷库，120次/分足够校园共享 IP 正常使用）
_READ_PREFIX_RULES: dict[str, tuple[int, int]] = {
    "/api/faq": (120, 60),
    "/api/announcements": (120, 60),
    "/api/clubs": (120, 60),
    "/api/forum": (60, 60),
}

# 登录用户（JWT sub）限流 — 小信 / TTS / Agent
_USER_RATE_RULES: dict[tuple[str, str], tuple[int, int]] = {
    ("POST", "/api/chat"): (25, 60),
    ("POST", "/api/tts"): (20, 60),
    ("POST", "/api/agent/chat"): (30, 60),
}

_store: Dict[str, Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _jwt_sub(request: Request) -> str | None:
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        payload = decode_token(token)
        sub = str(payload.get("sub", "")).strip()
        return sub or None
    except JWTError:
        return None


def _rate_limit_json(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"success": False, "message": message, "data": None},
    )


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
        path_key = (request.method, request.url.path)

        # 登录用户限流
        user_rule = _USER_RATE_RULES.get(path_key)
        if user_rule:
            sub = _jwt_sub(request)
            if sub:
                limit, window = user_rule
                user_key = f"user:{path_key[0]}:{path_key[1]}:{sub}"
                if _too_many(user_key, limit, window):
                    return _rate_limit_json("操作过于频繁，请稍后再试")

        # 精确路径 IP 限流
        rule = _RATE_RULES.get(path_key)
        if rule:
            limit, window = rule
            ip = _client_ip(request)
            ip_key = f"ip:{path_key[0]}:{path_key[1]}:{ip}"
            if _too_many(ip_key, limit, window):
                return _rate_limit_json("请求过于频繁，请稍后再试")

        # 公开 GET 前缀限流
        if request.method == "GET":
            for prefix, (limit, window) in _READ_PREFIX_RULES.items():
                if request.url.path.startswith(prefix):
                    ip = _client_ip(request)
                    prefix_key = f"ip:GET:{prefix}:{ip}"
                    if _too_many(prefix_key, limit, window):
                        return _rate_limit_json("请求过于频繁，请稍后再试")
                    break

        return await call_next(request)
