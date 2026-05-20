"""FAQ 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.crud.faq import list_faq, create_faq, delete_faq
from app.schemas.faq import FaqCreate, FaqOut

router = APIRouter()


@router.get("/faq")
def get_faq(db: Session = Depends(get_db)):
    items = list_faq(db)
    return {"success": True, "data": [FaqOut.model_validate(f).model_dump() for f in items]}


@router.post("/admin/faq")
def admin_add_faq(data: FaqCreate, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    item = create_faq(db, data)
    return {"success": True, "data": FaqOut.model_validate(item).model_dump()}


@router.delete("/admin/faq/{faq_id}")
def admin_delete_faq(faq_id: str, db: Session = Depends(get_db), _admin: dict = Depends(require_admin)):
    ok = delete_faq(db, faq_id)
    if not ok:
        raise HTTPException(404, "问题不存在")
    return {"success": True, "message": "已删除"}
