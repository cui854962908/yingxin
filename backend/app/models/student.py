from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.club import Club


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    id_number_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    class_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dormitory: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    advisor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    advisor_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    class_teacher_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    class_teacher_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    assistant_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assistant_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    assistant_class_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default="student")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owned_clubs: Mapped[list["Club"]] = relationship(
        "Club", back_populates="owner", foreign_keys="Club.owner_student_id"
    )
