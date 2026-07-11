import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.response import ok_envelope
from app.core.security import get_current_payload, get_optional_payload, require_admin
from app.db.database import get_db
from app.schemas.forum import ForumAnswerCreate, ForumAnswerUpdate, ForumPostCreate, ForumPostUpdate
from app.services import forum_service as svc

router_public = APIRouter(tags=["forum"])
router_admin = APIRouter(prefix="/admin", tags=["admin-forum"])


def _viewer_id(db: Session, payload: dict[str, Any] | None) -> int | None:
    if not payload:
        return None
    try:
        return svc.resolve_author_id(db, payload)
    except HTTPException:
        return None


@router_public.get("/forum/posts")
def list_forum_posts(
    page: int = 1,
    page_size: int = 15,
    sort: str = "latest",
    category: str | None = None,
    q: str | None = None,
    mine: bool = False,
    db: Session = Depends(get_db),
    payload: dict | None = Depends(get_optional_payload),
):
    if sort not in ("latest", "hot", "open"):
        sort = "latest"
    page = max(1, page)
    page_size = min(max(1, page_size), 50)
    data = svc.list_posts(
        db,
        page=page,
        page_size=page_size,
        sort=sort,
        category=category,
        q=q,
        mine=mine,
        viewer_id=_viewer_id(db, payload),
    )
    return ok_envelope(message="操作成功", data=data)


@router_public.get("/forum/posts/{post_id}")
def get_forum_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict | None = Depends(get_optional_payload),
):
    data = svc.view_post_detail(db, post_id, _viewer_id(db, payload))
    return ok_envelope(message="操作成功", data=data)


@router_public.post("/forum/posts")
def create_forum_post(
    body: ForumPostCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.create_post(
        db, payload, title=body.title, content=body.content, category=body.category
    )
    return ok_envelope(message="发布成功", data=data)


@router_public.patch("/forum/posts/{post_id}")
def update_forum_post(
    post_id: uuid.UUID,
    body: ForumPostUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=422, detail="无更新字段")
    data = svc.update_post(db, payload, post_id, fields)
    return ok_envelope(message="已更新", data=data)


@router_public.delete("/forum/posts/{post_id}")
def delete_forum_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    svc.delete_post(db, payload, post_id)
    return ok_envelope(message="已删除", data=None)


@router_public.post("/forum/posts/{post_id}/close")
def close_forum_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.close_post(db, payload, post_id)
    return ok_envelope(message="已关闭", data=data)


@router_public.post("/forum/posts/{post_id}/like")
def toggle_forum_post_like(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.toggle_post_like(db, payload, post_id)
    return ok_envelope(message="操作成功", data=data)


@router_public.post("/forum/posts/{post_id}/answers")
def create_forum_answer(
    post_id: uuid.UUID,
    body: ForumAnswerCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.create_answer(db, payload, post_id, body.content)
    return ok_envelope(message="回答成功", data=data)


@router_public.patch("/forum/answers/{answer_id}")
def update_forum_answer(
    answer_id: uuid.UUID,
    body: ForumAnswerUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.update_answer(db, payload, answer_id, body.content)
    return ok_envelope(message="已更新", data=data)


@router_public.delete("/forum/answers/{answer_id}")
def delete_forum_answer(
    answer_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.delete_answer(db, payload, answer_id)
    return ok_envelope(message="已删除", data=data)


@router_public.post("/forum/answers/{answer_id}/accept")
def accept_forum_answer(
    answer_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.accept_answer(db, payload, answer_id)
    return ok_envelope(message="已采纳", data=data)


@router_public.post("/forum/answers/{answer_id}/like")
def toggle_forum_answer_like(
    answer_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_payload),
):
    data = svc.toggle_answer_like(db, payload, answer_id)
    return ok_envelope(message="操作成功", data=data)


@router_admin.post("/forum/posts/{post_id}/pin")
def pin_forum_post(
    post_id: uuid.UUID,
    pinned: bool = True,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    svc.admin_pin_post(db, post_id, pinned)
    return ok_envelope(message="操作成功", data={"pinned": pinned})


@router_admin.post("/forum/posts/{post_id}/hide")
def hide_forum_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    svc.admin_hide_post(db, post_id)
    return ok_envelope(message="已隐藏", data=None)
