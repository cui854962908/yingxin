from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel, Field, field_validator


def _clean_category(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class AnnouncementItem(BaseModel):
    id: uuid.UUID
    date: datetime.date | None = None
    title: str
    content: str
    category: str | None = None

    @field_validator("category", mode="before")
    @classmethod
    def default_category(cls, value: str | None) -> str:
        return _clean_category(value) or "campus"

    model_config = {"from_attributes": True}


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    date: datetime.date | None = None
    category: str | None = Field(default=None, max_length=50)

    @field_validator("category", mode="before")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return _clean_category(value)


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    content: str | None = Field(default=None, min_length=1)
    date: datetime.date | None = None
    category: str | None = Field(default=None, max_length=50)

    @field_validator("category", mode="before")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        return _clean_category(value)


