"""FAQ Pydantic Schemas"""

from pydantic import BaseModel, Field, field_validator


class FaqCreate(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1)


class FaqOut(BaseModel):
    id: str
    question: str
    answer: str

    model_config = {"from_attributes": True}

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v: object) -> str:
        return str(v) if v is not None else ""
