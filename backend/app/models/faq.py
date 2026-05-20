"""Faq ORM 模型"""

import uuid

from sqlalchemy import Column, String, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Faq(Base):
    __tablename__ = "faq"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(String(1000), nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(Date, server_default=func.current_date())
