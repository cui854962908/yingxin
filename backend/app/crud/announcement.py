"""公告 CRUD"""

from datetime import date as date_type

from sqlalchemy.orm import Session

from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate


def list_announcements(db: Session) -> list[Announcement]:
    return db.query(Announcement).order_by(Announcement.date.desc()).all()


def create_announcement(db: Session, data: AnnouncementCreate) -> Announcement:
    ann_date = date_type.fromisoformat(data.date) if data.date else date_type.today()
    announcement = Announcement(title=data.title, content=data.content, date=ann_date)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


def delete_announcement(db: Session, aid: str) -> bool:
    announcement = db.query(Announcement).filter(Announcement.id == aid).first()
    if announcement is None:
        return False
    db.delete(announcement)
    db.commit()
    return True
