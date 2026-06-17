import uuid

from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    keywords: str | None = None
    category: str | None = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class FAQCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    keywords: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=128)
    sort_order: int = Field(default=0, ge=0)


class FAQUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1)
    answer: str | None = Field(default=None, min_length=1)
    keywords: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=128)
    sort_order: int | None = Field(default=None, ge=0)
