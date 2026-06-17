import json
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


MAX_ACTIVITY_PHOTOS = 10


def _validate_photos_len(v: str | None) -> str | None:
    if v is None:
        return v
    try:
        photos = json.loads(v)
    except (json.JSONDecodeError, TypeError):
        return v
    if isinstance(photos, list) and len(photos) > MAX_ACTIVITY_PHOTOS:
        raise ValueError(f"最多上传 {MAX_ACTIVITY_PHOTOS} 张照片")
    return v


class ClubItem(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    cover_image: str | None = None
    hero_image: str | None = None
    intro: str
    status: str
    recruit_start: date | None = None
    recruit_end: date | None = None
    recruit_target: str | None = None
    recruit_count: int | None = Field(default=None, ge=0)
    recruit_require: str | None = None
    founded_year: int | None = None
    member_count: int | None = None
    advisor_name: str | None = None
    description: str | None = None
    honor: str | None = None
    activity_photos: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    leaders: str | None = None
    qq_group: str | None = None
    wechat_qr: str | None = None
    owner_student_id: int | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    intro: str = Field(..., min_length=1)
    cover_image: str | None = None
    hero_image: str | None = None
    status: str = "招新中"
    recruit_start: date | None = None
    recruit_end: date | None = None
    recruit_target: str | None = None
    recruit_count: int | None = Field(default=None, ge=0)
    recruit_require: str | None = None
    founded_year: int | None = None
    member_count: int | None = None
    advisor_name: str | None = None
    description: str | None = None
    honor: str | None = None
    activity_photos: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    leaders: str | None = None
    qq_group: str | None = None
    wechat_qr: str | None = None

    @field_validator("activity_photos")
    @classmethod
    def check_photos_len(cls, v: str | None) -> str | None:
        return _validate_photos_len(v)


class ClubUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    intro: str | None = None
    cover_image: str | None = None
    hero_image: str | None = None
    status: str | None = None
    recruit_start: date | None = None
    recruit_end: date | None = None
    recruit_target: str | None = None
    recruit_count: int | None = Field(default=None, ge=0)
    recruit_require: str | None = None
    founded_year: int | None = None
    member_count: int | None = None
    advisor_name: str | None = None
    description: str | None = None
    honor: str | None = None
    activity_photos: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    leaders: str | None = None
    qq_group: str | None = None
    wechat_qr: str | None = None

    @field_validator("activity_photos")
    @classmethod
    def check_photos_len(cls, v: str | None) -> str | None:
        return _validate_photos_len(v)
