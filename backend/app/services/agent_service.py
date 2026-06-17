"""
智能助手编排：空消息 → 无关拒答 → 学生专属/隐私 → FAQ 快路径 → 小信（documents + DeepSeek）。
"""

from __future__ import annotations

import time

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.services import faq_service, student_agent_service, xiaoxin_chat_service
from app.core.keywords import is_domain_related

_GREETINGS = {
    "你好", "您好", "嗨", "哈喽", "hello", "hi", "hey",
    "在吗", "在不在", "在不在线", "有人在吗",
    "早上好", "下午好", "晚上好", "早", "晚安",
    "你是谁", "你叫什么", "你是什么", "你是哪位",
    "你好呀", "嗨喽", "hello你好", "hi你好",
}
_GREETING_REPLY = (
    "你好！我是小信，河南牧业经济学院信息工程学院的智能迎新助手。"
    "你可以问我报到流程、宿舍查询、缴费状态、校园卡领取、快递站位置等问题，随时为你服务！"
)

_IRRELEVANT_REPLY = (
    "我主要负责解答校园迎新系统、新生报到和校园服务相关问题。"
    "你可以问我报到流程、宿舍查询、缴费状态、校园卡领取等问题。"
)


async def route_chat_async(
    *,
    db: Session,
    message: str,
    is_authenticated: bool = False,
    current_student_id: str | None = None,
    role: str = "anonymous",
    request: Request | None = None,
) -> dict:
    """统一 Agent 信封；FAQ 之后在本地走小信 RAG（与 ``/api/chat`` SSE 同源）。"""
    text = (message or "").strip()
    if not text:
        return {
            "reply": "请输入你要咨询的问题内容。",
            "intent": "unknown",
            "source": "validation",
            "matched_title": None,
        }

    t0 = time.perf_counter()

    # 简单问候/自我介绍 —— 返回友好欢迎语，不进入领域过滤
    if text.lower().rstrip("!！~～ ") in _GREETINGS or (
        len(text) <= 6 and any(g in text for g in ("你好", "您好", "hello", "hi", "嗨", "在吗"))
    ):
        return {
            "reply": _GREETING_REPLY,
            "intent": "greeting",
            "source": "greeting",
            "matched_title": None,
        }

    if not is_domain_related(text):
        if request is not None and getattr(request.state, "agent_perf", None) is not None:
            request.state.agent_perf["domain"] = round(time.perf_counter() - t0, 4)
        return {
            "reply": _IRRELEVANT_REPLY,
            "intent": "irrelevant",
            "source": "irrelevant",
            "matched_title": None,
        }
    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["domain"] = round(time.perf_counter() - t0, 4)

    t_g = time.perf_counter()
    r, intent, source = student_agent_service.student_gate_response(
        message=text,
        is_authenticated=is_authenticated,
        current_student_id=current_student_id,
        role=role,
    )
    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["privacy_gate"] = round(time.perf_counter() - t_g, 4)
    if r:
        return {"reply": r, "intent": intent or "unknown", "source": source or "student_agent", "matched_title": None}

    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["student_agent"] = 0.0

    faq_hit = faq_service.find_best_faq(db, text, request=request)
    if faq_hit:
        return {
            "reply": faq_hit.faq.answer.strip(),
            "intent": "faq",
            "source": "faq",
            "matched_title": faq_hit.faq.question.strip(),
        }

    t_x = time.perf_counter()
    out = await xiaoxin_chat_service.complete_xiaoxin_turn(text)
    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["xiaoxin_rag"] = round(time.perf_counter() - t_x, 4)

    return out
