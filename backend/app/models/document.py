"""小信向量表 ``documents``：HOUDAUN(3).md §3.2（字段名保持与现行迁移兼容：向量列 ``embedding_json``）。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

DOCUMENT_SOURCE_STUDENT_FAQ = "student_faq"
DOCUMENT_SOURCE_ANNOUNCEMENT = "announcement"
DOCUMENT_SOURCE_CLUB = "club"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_kind: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="student_faq",
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    source_student_faq_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("faq.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source_announcement_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source_club_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
