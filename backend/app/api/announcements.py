import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.core.response import ok_envelope
from app.core.security import require_admin
from app.crud.document import (
    delete_documents_for_announcement,
    incremental_embed_announcement,
)
from app.db.database import get_db
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementItem, AnnouncementUpdate

router_public = APIRouter(tags=["announcements"])
router_admin = APIRouter(prefix="/admin", tags=["admin-announcements"])


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@router_public.get("/announcements")
def list_announcements(
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """列表为迎新公开内容，允许未登录浏览。可选 category 筛选（如 guide=报到须知）。"""
    stmt = select(Announcement).order_by(
        desc(Announcement.date).nulls_last(),
        desc(Announcement.created_at),
    )
    if category == "campus":
        stmt = stmt.where(or_(Announcement.category == "campus", Announcement.category == None, Announcement.category == ""))  # noqa: E711
    elif category is not None:
        stmt = stmt.where(Announcement.category == category)
    rows = db.scalars(stmt).all()
    data = [AnnouncementItem.model_validate(r).model_dump(mode="json") for r in rows]
    return ok_envelope(message="操作成功", data=data)


@router_admin.post("/announcements")
def create_announcement(
    body: AnnouncementCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    adate = body.date
    if adate is None:
        adate = datetime.now().date()
    item = Announcement(
        title=body.title.strip(), content=body.content.strip(), date=adate,
        category=body.category,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    out = AnnouncementItem.model_validate(item).model_dump(mode="json")
    incremental_embed_announcement(db, item)
    return ok_envelope(message="发布成功", data=out)


@router_admin.patch("/announcements/{ann_id}")
def update_announcement(
    ann_id: uuid.UUID,
    body: AnnouncementUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.get(Announcement, ann_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")
    # 仅更新传入的字段，未传则保留原值
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "category":
            setattr(row, field, _clean_optional_text(value))
        else:
            setattr(row, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(row)
    # 内容变更后重新向量化
    if "content" in update_data or "title" in update_data:
        incremental_embed_announcement(db, row)
    return ok_envelope(message="更新成功", data=AnnouncementItem.model_validate(row).model_dump(mode="json"))


@router_admin.delete("/announcements/{ann_id}")
def delete_announcement(
    ann_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.get(Announcement, ann_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")
    delete_documents_for_announcement(db, ann_id)
    db.delete(row)
    db.commit()
    return ok_envelope(message="删除成功", data=None)
