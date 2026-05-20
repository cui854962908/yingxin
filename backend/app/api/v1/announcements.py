"""公告路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.crud.announcement import list_announcements, create_announcement, delete_announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementOut

router = APIRouter()


@router.get("/announcements")
def get_announcements(db: Session = Depends(get_db)):
    items = list_announcements(db)
    return {"success": True, "data": [AnnouncementOut.model_validate(a).model_dump() for a in items]}


@router.post("/admin/announcements")
def admin_add_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    item = create_announcement(db, data)
    return {"success": True, "data": AnnouncementOut.model_validate(item).model_dump()}


@router.delete("/admin/announcements/{aid}")
def admin_delete_announcement(aid: str, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    ok = delete_announcement(db, aid)
    if not ok:
        raise HTTPException(404, "公告不存在")
    return {"success": True, "message": "已删除"}
