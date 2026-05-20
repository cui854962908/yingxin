"""Student & Assistant ORM 模型"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    id_number = Column(String(30), nullable=False, default="")
    photo = Column(String(500), default="")
    class_name = Column(String(200), default="")
    dormitory = Column(String(200), default="")
    advisor_name = Column(String(100), default="")
    advisor_phone = Column(String(50), default="")
    class_teacher_name = Column(String(100), default="")
    class_teacher_phone = Column(String(50), default="")
    role = Column(String(20), default="student")

    assistants = relationship("Assistant", back_populates="student", cascade="all, delete-orphan")


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), default="")
    phone = Column(String(50), default="")
    class_name = Column(String(200), default="")

    student = relationship("Student", back_populates="assistants")
