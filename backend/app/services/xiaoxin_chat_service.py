"""
小信 SSE 与 Agent 单行回复：`documents`（HOUDAUN §3）余弦检索 + ``app.core.llm`` 拼装与流式生成。

Wire：服务层字典含 ``token`` / ``error`` / ``done``（含 ``matched_title``、``reply_mode`` 供 Agent）；
路由层 ``app.api.v1.chat`` 仅在 SSE 上对 ``done`` 收敛为 HOUDAUN 的 ``{"done", "links"}``。
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import AsyncIterator

from app.core.config import settings
from app.core.llm import build_prompt, generate_stream
from app.crud.document import search_similar
from app.services.student_agent_service import mentions_other_person

_PRIVACY_REPLY = (
    "为保护同学隐私，我只能回答与当前会话相关的公开迎新信息。"
    "请不要在对话中打探他人身份证号、手机号、宿舍等个人信息。"
)

_SERVICE_DISABLED_REPLY = (
    "智能迎新助手暂未开放（服务端已关闭对话功能）。"
    "请通过迎新系统中的通知公告或常见问题查看最新信息。"
)

_EMBED_OR_GEN_FAIL = "生成失败，请稍后重试"

_SEM = threading.Semaphore(2)


def _links_for_kb() -> list[dict[str, str]]:
    return [
        {"label": "查看问题答疑", "to": "/faq"},
        {"label": "查看校园公告", "to": "/announcements"},
    ]


def _links_for_fallback() -> list[dict[str, str]]:
    """知识库未命中时的引导链接（牧院新生说优先）。"""
    return [
        {"label": "🌾 去牧院新生说", "to": "/wall"},
        {"label": "查看问题答疑", "to": "/faq"},
        {"label": "查看校园公告", "to": "/announcements"},
    ]


def _retrieve_in_thread(question: str) -> tuple[list[dict], float, str | None, str, str]:
    """在线程独立 Session 中做向量检索，避免跨线程共用 ORM Session。"""
    from app.db.database import SessionLocal

    th = settings.DOCUMENT_COSINE_THRESHOLD
    db = SessionLocal()
    try:
        hits = search_similar(db, question, 3)
        top_score = float(hits[0]["score"]) if hits else 0.0
        matched_title = (hits[0]["title"].strip() if hits else "") or None
        if top_score > th and hits:
            context_parts = [f"【{h['title']}】{h['content']}" for h in hits]
            context = "\n\n".join(context_parts)
            reply_mode = "knowledge_base"
        else:
            matched_title = None
            reply_mode = "no_hit_school" if _schoolish(question) else "chitchat"
            context = ""

        return hits, top_score, matched_title, context, reply_mode
    finally:
        db.close()


async def stream_xiaoxin_events(question: str) -> AsyncIterator[dict]:
    """SSE 与 Agent 共用；yield ``dict``。"""
    req = (question or "").strip()
    if not req:
        yield {"error": "问题不能为空"}
        yield {"done": True, "links": [], "matched_title": None, "reply_mode": "validation"}
        return

    if mentions_other_person(req):
        yield {"token": _PRIVACY_REPLY.strip()}
        yield {"done": True, "links": [], "matched_title": None, "reply_mode": "privacy"}
        return

    if not settings.XIAOXIN_CHAT_ENABLED:
        yield {"error": "小信 SSE 功能已在服务端关闭（XIAOXIN_CHAT_ENABLED=false）"}
        yield {"done": True, "links": [], "matched_title": None, "reply_mode": "disabled"}
        return

    if not _SEM.acquire(blocking=False):
        yield {"error": "服务器繁忙，请稍后再试"}
        yield {"done": True, "links": [], "matched_title": None, "reply_mode": "busy"}
        return

    try:
        _hits, _top_score, matched_title, context_str, reply_mode = await asyncio.to_thread(
            _retrieve_in_thread, req
        )
        context: str | None = context_str or None

        prompt = build_prompt(context, req)

        try:
            queue: asyncio.Queue[str | None] = asyncio.Queue()
            loop = asyncio.get_running_loop()

            def _pump_tokens() -> None:
                try:
                    for tok in generate_stream(prompt):
                        loop.call_soon_threadsafe(queue.put_nowait, tok)
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None)

            await loop.run_in_executor(None, _pump_tokens)

            while True:
                token = await queue.get()
                if token is None:
                    break
                yield {"token": token}
                # 微小延迟，让前端打字效果可见（DeepSeek 推理模型输出极快）
                await asyncio.sleep(0.03)

            if context:
                links = _links_for_kb()
            elif reply_mode == "no_hit_school":
                links = _links_for_fallback()
            else:
                links = []
            yield {
                "done": True,
                "links": links,
                "matched_title": matched_title,
                "reply_mode": reply_mode,
            }

        except Exception:
            yield {"error": _EMBED_OR_GEN_FAIL}
            yield {"done": True, "links": [], "matched_title": None, "reply_mode": "error"}

    finally:
        _SEM.release()


def _schoolish(question: str) -> bool:
    from app.core.keywords import has_school_keyword

    return has_school_keyword(question)


def _finalize_matched_title(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    t = raw.strip()
    return t or None


async def complete_xiaoxin_turn(question: str) -> dict:
    """与 ``POST /api/chat`` / HOUDAUN 同源。"""
    text = (question or "").strip()

    reply_parts: list[str] = []
    done_ev: dict | None = None
    err_txt: str | None = None
    async for ev in stream_xiaoxin_events(text):
        if "token" in ev:
            reply_parts.append(str(ev.get("token") or ""))
        elif ev.get("done"):
            done_ev = ev
        elif "error" in ev:
            err_txt = str(ev.get("error") or "").strip()

    reply = "".join(reply_parts).strip()
    mt = _finalize_matched_title((done_ev or {}).get("matched_title"))
    mode = (done_ev or {}).get("reply_mode")

    if mode == "privacy":
        return {
            "reply": reply or _PRIVACY_REPLY.strip(),
            "intent": "privacy",
            "source": "privacy",
            "matched_title": mt,
        }
    if mode == "knowledge_base":
        return {
            "reply": reply or "模型生成暂时失败，请稍后再试或查看迎新通知公告获取信息。",
            "intent": "knowledge",
            "source": "xiaoxin_kb",
            "matched_title": mt,
        }
    if mode == "no_hit_school":
        return {"reply": reply, "intent": "unknown", "source": "fallback", "matched_title": None}
    if mode == "chitchat":
        return {
            "reply": reply or "模型生成暂时失败，请稍后再试。",
            "intent": "irrelevant",
            "source": "chitchat",
            "matched_title": None,
        }
    if mode in {"busy", "disabled"}:
        r = reply or (_SERVICE_DISABLED_REPLY if mode == "disabled" else "服务器繁忙，请稍后再试。")
        return {"reply": r, "intent": "unknown", "source": "fallback", "matched_title": None}
    if mode == "validation":
        return {
            "reply": reply or "请输入你要咨询的问题内容。",
            "intent": "unknown",
            "source": "validation",
            "matched_title": None,
        }

    if err_txt:
        reply_f = err_txt
        if "XIAOXIN_CHAT_ENABLED" in err_txt or "服务端关闭" in err_txt:
            reply_f = _SERVICE_DISABLED_REPLY
        if len(reply_f) > 800:
            reply_f = reply_f[:800] + "…"
        return {"reply": reply_f, "intent": "unknown", "source": "fallback", "matched_title": None}

    return {
        "reply": reply or "模型生成暂时失败，请稍后再试或查看迎新通知公告获取信息。",
        "intent": "unknown",
        "source": "fallback",
        "matched_title": None,
    }
