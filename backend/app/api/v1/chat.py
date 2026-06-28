"""SSE 流式聊天（HOUDAUN(3).md §3.4）"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.security import get_current_payload
from app.schemas.xiaoxin import XiaoxinChatBody
from app.services import xiaoxin_chat_service

router = APIRouter(tags=["xiaoxin-chat"])


def _sse(data: dict) -> str:
    public: dict = dict(data)
    if public.get("done") is True:
        public = {"done": True, "links": public.get("links") or []}
    elif "token" in public:
        public = {"token": public["token"]}
    elif "error" in public:
        public = {"error": public["error"]}
    return f"data: {json.dumps(public, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(req: XiaoxinChatBody, _: dict = Depends(get_current_payload)):
    """小信 SSE：须登录（游客不可用）。"""
    if not settings.XIAOXIN_CHAT_ENABLED:
        raise HTTPException(status_code=503, detail="小信 SSE 已在服务端关闭（XIAOXIN_CHAT_ENABLED=false）")

    async def event_stream():
        async for item in xiaoxin_chat_service.stream_xiaoxin_events(req.question):
            yield _sse(item)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
