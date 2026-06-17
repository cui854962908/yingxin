import uuid
from datetime import datetime

from datetime import date
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hero_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    intro: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="招新中"
    )
    recruit_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    recruit_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    recruit_target: Mapped[str | None] = mapped_column(String(200), nullable=True)
    recruit_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recruit_require: Mapped[str | None] = mapped_column(Text, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    member_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    advisor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    honor: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_photos: Mapped[str | None] = mapped_column(Text, nullable=True)
    leader_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    leader_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    leaders: Mapped[str | None] = mapped_column(Text, nullable=True)
    qq_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    wechat_qr: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner_student_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("students.id"), nullable=True
    )
    owner: Mapped["Student | None"] = relationship(  # noqa: F821
        "Student", back_populates="owned_clubs", foreign_keys=[owner_student_id]
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
