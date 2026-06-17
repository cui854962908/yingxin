import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.response import ok_envelope
from app.core.security import require_admin
from app.crud.document import (
    delete_documents_for_student_faq,
    incremental_embed_student_faq,
)
from app.db.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQItem, FAQUpdate
from app.services.faq_service import clear_faq_cache

router_public = APIRouter(tags=["faq"])
router_admin = APIRouter(prefix="/admin", tags=["admin-faq"])


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@router_public.get("/faq")
def list_faq(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """列表为迎新公开内容，允许未登录浏览（发帖/删除仍须管理员 JWT）。"""
    offset = (page - 1) * page_size
    total = db.query(FAQ).count()
    rows = db.scalars(
        select(FAQ).order_by(FAQ.sort_order.asc(), FAQ.created_at.asc()).offset(offset).limit(page_size)
    ).all()
    data = [FAQItem.model_validate(r).model_dump(mode="json") for r in rows]
    return ok_envelope(message="操作成功", data={
        "items": data,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router_admin.post("/faq")
def create_faq(
    body: FAQCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    item = FAQ(
        question=body.question.strip(),
        answer=body.answer.strip(),
        keywords=(body.keywords.strip() if body.keywords else None),
        category=(body.category.strip() if body.category else None),
        sort_order=body.sort_order,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    incremental_embed_student_faq(db, item)
    clear_faq_cache()
    return ok_envelope(
        message="创建成功",
        data=FAQItem.model_validate(item).model_dump(mode="json"),
    )


@router_admin.patch("/faq/{faq_id}")
def update_faq(
    faq_id: uuid.UUID,
    body: FAQUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.get(FAQ, faq_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="常见问题不存在")
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"keywords", "category"}:
            setattr(row, field, _clean_optional_text(value))
        else:
            setattr(row, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(row)
    # 内容变更后重新向量化并清缓存
    if "question" in update_data or "answer" in update_data:
        incremental_embed_student_faq(db, row)
    clear_faq_cache()
    return ok_envelope(message="更新成功", data=FAQItem.model_validate(row).model_dump(mode="json"))


@router_admin.delete("/faq/{faq_id}")
def delete_faq(
    faq_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    row = db.get(FAQ, faq_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="常见问题不存在")
    delete_documents_for_student_faq(db, faq_id)
    db.delete(row)
    db.commit()
    clear_faq_cache()
    return ok_envelope(message="删除成功", data=None)


class FAQReorderItem(BaseModel):
    id: uuid.UUID
    sort_order: int


class FAQReorderBody(BaseModel):
    items: list[FAQReorderItem]


@router_admin.patch("/faq/reorder")
def reorder_faq(
    body: FAQReorderBody,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """批量更新 FAQ 排序权重（拖拽排序后调用）。"""
    for item in body.items:
        db.execute(
            update(FAQ).where(FAQ.id == item.id).values(sort_order=item.sort_order)
        )
    db.commit()
    clear_faq_cache()
    return ok_envelope(message="排序已更新", data=None)
