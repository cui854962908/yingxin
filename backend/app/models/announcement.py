"""Announcement ORM 模型"""

import uuid

from sqlalchemy import Column, String, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(Date, server_default=func.current_date())
