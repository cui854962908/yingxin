from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_payload
from app.core.response import fail_envelope, ok_envelope
from app.db.database import get_db
from app.schemas.agent import AgentChatEnvelopeData, AgentChatRequest
from app.services.agent_service import route_chat_async

router = APIRouter(tags=["agent"])


@router.post("/agent/chat")
async def agent_chat(
    request: Request,
    payload: AgentChatRequest,
    db: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_current_payload),
):
    """智能迎新助手（须登录）。个人敏感信息依赖 JWT `sub`（学号）。知识生成走小信（DeepSeek + documents）。"""
    msg = payload.message.strip()
    jwt = jwt_payload
    current_student_id = str(jwt.get("sub", "")).strip() or None
    role = str(jwt.get("role", "student")).strip().lower() or "student"
    t_body = time.perf_counter()

    result = await route_chat_async(
        db=db,
        message=msg,
        is_authenticated=True,
        current_student_id=current_student_id,
        role=role,
        request=request,
    )

    perf = getattr(request.state, "agent_perf", None)
    if perf is not None:
        perf["route_body"] = round(time.perf_counter() - t_body, 4)

    if result.get("source") == "fallback":
        logging.getLogger("app.agent.fallback").info(
            "message=%r", msg[:300]
        )

    data = AgentChatEnvelopeData(**result).model_dump()

    # 领域外拒答 → 返回失败信封，让前端降级到自己的兜底逻辑（FAQ/公告本地匹配）
    if result.get("source") == "irrelevant":
        return fail_envelope(message=result.get("reply", ""), data=data)

    return ok_envelope(message="success", data=data)
