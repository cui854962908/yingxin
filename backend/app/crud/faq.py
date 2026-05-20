"""FAQ CRUD"""

from sqlalchemy.orm import Session

from app.models.faq import Faq
from app.schemas.faq import FaqCreate


def list_faq(db: Session) -> list[Faq]:
    return db.query(Faq).all()


def create_faq(db: Session, data: FaqCreate) -> Faq:
    faq = Faq(question=data.question, answer=data.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq_id: str) -> bool:
    faq = db.query(Faq).filter(Faq.id == faq_id).first()
    if faq is None:
        return False
    db.delete(faq)
    db.commit()
    return True
