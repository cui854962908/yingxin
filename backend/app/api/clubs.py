import os
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pypinyin import lazy_pinyin
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.http_middleware import MAX_BODY_BYTES
from app.core.response import ok_envelope
from app.core.security import (
    get_student_id_from_payload,
    require_admin,
    require_any_admin,
)
from app.crud.document import (
    delete_documents_for_club,
    incremental_embed_club,
)
from app.db.database import get_db
from app.models.club import Club
from app.schemas.club import ClubCreate, ClubItem, ClubUpdate

router_public = APIRouter(tags=["clubs"])
router_admin = APIRouter(prefix="/admin", tags=["admin-clubs"])


def _effective_status(row: Club) -> str:
    """根据招募时间段自动计算状态；未设时间段则返回数据库值。"""
    if row.recruit_start and row.recruit_end:
        today = date.today()
        if row.recruit_start <= today <= row.recruit_end:
            return "招新中"
        else:
            return "已结束"
    return row.status


def _club_to_item(row: Club) -> dict:
    d = ClubItem.model_validate(row).model_dump(mode="json")
    d["status"] = _effective_status(row)
    return d


@router_public.get("/clubs")
def list_clubs(db: Session = Depends(get_db)):
    rows = db.scalars(select(Club)).all()
    rows = sorted(rows, key=lambda r: lazy_pinyin(r.name[0])[0].lower() if r.name else "z")
    data = [_club_to_item(r) for r in rows]
    return ok_envelope(message="操作成功", data=data)


@router_public.get("/clubs/{club_id}")
def get_club(club_id: uuid.UUID, db: Session = Depends(get_db)):
    row = db.get(Club, club_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="社团不存在")
    return ok_envelope(
        message="操作成功",
        data=_club_to_item(row),
    )


@router_admin.post("/clubs")
def create_club(
    body: ClubCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_any_admin),
):
    owner_id = None
    if payload.get("role") == "club_admin":
        owner_id = get_student_id_from_payload(db, payload)
        existing = db.scalars(
            select(Club).where(Club.owner_student_id == owner_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="社团管理员只能创建一个社团",
            )

    item = Club(**body.model_dump(), owner_student_id=owner_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    incremental_embed_club(db, item)
    return ok_envelope(
        message="创建成功",
        data=_club_to_item(item),
    )


@router_admin.put("/clubs/{club_id}")
def update_club(
    club_id: uuid.UUID,
    body: ClubUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_any_admin),
):
    row = db.get(Club, club_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="社团不存在")

    if payload.get("role") == "club_admin":
        owner_id = get_student_id_from_payload(db, payload)
        if row.owner_student_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能编辑自己管理的社团",
            )

    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(row, key, val)
    db.commit()
    db.refresh(row)
    incremental_embed_club(db, row)
    return ok_envelope(
        message="更新成功",
        data=_club_to_item(row),
    )


@router_admin.delete("/clubs/{club_id}")
def delete_club(
    club_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.get(Club, club_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="社团不存在")
    delete_documents_for_club(db, club_id)
    db.delete(row)
    db.commit()
    return ok_envelope(message="删除成功", data=None)


from pydantic import BaseModel

class StatusBody(BaseModel):
    status: str


@router_admin.patch("/clubs/{club_id}/status")
def set_club_status(
    club_id: uuid.UUID,
    body: StatusBody,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_any_admin),
):
    if body.status not in ("招新中", "已结束"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效状态")

    row = db.get(Club, club_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="社团不存在")

    if payload.get("role") == "club_admin":
        owner_id = get_student_id_from_payload(db, payload)
        if row.owner_student_id != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己管理的社团")

    row.status = body.status
    db.commit()
    return ok_envelope(message=f"状态已更新为「{row.status}」", data={"status": row.status})


_UPLOAD_DIR = Path("static/uploads/clubs")
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
_ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@router_admin.post("/clubs/upload-image")
async def upload_club_image(
    file: UploadFile = File(...),
    _: dict = Depends(require_any_admin),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持 {' / '.join(_ALLOWED_EXT)} 格式",
        )
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = _UPLOAD_DIR / filename
    content = await file.read()
    if len(content) > MAX_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="上传文件过大（上限 5MB）",
        )
    filepath.write_bytes(content)
    url = f"/static/uploads/clubs/{filename}"
    return ok_envelope(message="上传成功", data={"url": url})
