"""公告 Pydantic Schemas"""

from datetime import date as date_type

from pydantic import BaseModel, Field, field_validator


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    date: str = ""


class AnnouncementOut(BaseModel):
    id: str
    date: str
    title: str
    content: str

    model_config = {"from_attributes": True}

    @field_validator("id", "date", mode="before")
    @classmethod
    def coerce_str(cls, v: object) -> str:
        if hasattr(v, "isoformat"):
            return v.isoformat()  # type: ignore[union-attr]
        return str(v) if v is not None else ""
