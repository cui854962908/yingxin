"""Edge-TTS 语音合成（HOUDAUN(3).md §3.5）"""

from __future__ import annotations

import io

import edge_tts
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.security import get_current_payload
from app.schemas.xiaoxin import XiaoxinTtsBody

router = APIRouter(tags=["tts"])


@router.post("/tts")
async def tts(req: XiaoxinTtsBody, _: dict = Depends(get_current_payload)):
    """须登录后使用（与小信配套）。"""
    communicate = edge_tts.Communicate(req.text.strip(), settings.EDGE_TTS_VOICE)
    buffer = io.BytesIO()

    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"TTS 失败：{exc}") from exc

    buffer.seek(0)
    payload = buffer.getvalue()
    if not payload:
        raise HTTPException(status_code=502, detail="TTS 无音频输出")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline"},
    )
