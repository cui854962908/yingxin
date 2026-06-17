from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户问题")

    @field_validator("message")
    @classmethod
    def strip_nonempty(cls, value: str) -> str:
        s = value.strip()
        if not s:
            raise ValueError("消息不能为空")
        return s


class AgentChatEnvelopeData(BaseModel):
    reply: str
    intent: str | None = None
    source: str | None = None
    matched_title: str | None = None
