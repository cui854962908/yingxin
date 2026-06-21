from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ForumCategory = Literal["报到", "生活", "学习", "社团", "其他"]
ForumSort = Literal["latest", "hot", "open"]


class ForumPostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=5, max_length=2000)
    category: ForumCategory = "其他"


class ForumPostUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=120)
    content: str | None = Field(None, min_length=5, max_length=2000)
    category: ForumCategory | None = None


class ForumAnswerCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class ForumAnswerUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class ForumAuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    class_name: str


class ForumPostBrief(BaseModel):
    id: UUID
    title: str
    content_preview: str
    category: str
    author: ForumAuthorBrief
    answer_count: int
    has_accepted: bool
    is_closed: bool
    is_pinned: bool
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    is_mine: bool = False


class ForumAnswerItem(BaseModel):
    id: UUID
    content: str
    author: ForumAuthorBrief
    is_accepted: bool
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    is_mine: bool = False


class ForumPostDetail(BaseModel):
    id: UUID
    title: str
    content: str
    category: str
    author: ForumAuthorBrief
    author_id: int
    answer_count: int
    has_accepted: bool
    is_closed: bool
    is_pinned: bool
    like_count: int = 0
    liked_by_me: bool = False
    created_at: datetime
    is_mine: bool = False
    answers: list[ForumAnswerItem]
