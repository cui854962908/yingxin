"""
智能助手身份依赖：仅信任服务端签发的 JWT，不信任前端传入的 student_id。

返回 (is_authenticated, current_student_id, role)。
- 无 Bearer：未登录。
- 非法 / 过期 Bearer：公开可读接口按未登录（None）；须登录接口仍 401。
"""

from __future__ import annotations

from typing import Optional, Tuple

from fastapi import Depends

from app.core.security import get_optional_payload

JWTClaim = dict

AgentIdentity = Tuple[bool, Optional[str], str]


async def get_agent_identity(
    payload: Optional[JWTClaim] = Depends(get_optional_payload),
) -> AgentIdentity:
    if not payload:
        return False, None, "anonymous"
    sub = str(payload.get("sub", "")).strip()
    role = str(payload.get("role", "student")).strip().lower() or "student"
    return True, sub or None, role
