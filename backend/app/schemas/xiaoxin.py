from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class XiaoxinChatBody(BaseModel):
    """对齐《小信》计划：POST /api/chat 使用 question。"""

    question: str = Field(..., min_length=1, max_length=500, description="用户问题")

    @field_validator("question")
    @classmethod
    def strip_nonempty(cls, value: str) -> str:
        s = value.strip()
        if not s:
            raise ValueError("问题不能为空")
        return s


class XiaoxinTtsBody(BaseModel):
    """POST /api/tts：合成语音"""

    text: str = Field(..., min_length=1, max_length=500, description="待朗读正文")

    @field_validator("text")
    @classmethod
    def strip_nonempty(cls, value: str) -> str:
        s = value.strip()
        if not s:
            raise ValueError("文本不能为空")
        return s
