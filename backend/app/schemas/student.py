"""学生 Pydantic Schemas — 平字段输入，嵌套对象输出"""

from pydantic import BaseModel, Field


# ── 输入 schemas：匹配前端发送的平字段格式 ──

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    student_id: str = Field(..., min_length=1, max_length=50)
    id_number: str = Field(default="", max_length=30)
    class_name: str = Field(default="", max_length=200)
    dormitory: str = Field(default="", max_length=200)
    advisor_name: str = Field(default="", max_length=100)
    advisor_phone: str = Field(default="", max_length=50)
    class_teacher_name: str = Field(default="", max_length=100)
    class_teacher_phone: str = Field(default="", max_length=50)
    assistant_name: str = Field(default="", max_length=100)
    assistant_phone: str = Field(default="", max_length=50)
    assistant_class_name: str = Field(default="", max_length=200)


class StudentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    student_id: str | None = Field(None, min_length=1, max_length=50)
    id_number: str | None = Field(None, max_length=30)
    class_name: str | None = Field(None, max_length=200)
    dormitory: str | None = Field(None, max_length=200)
    advisor_name: str | None = Field(None, max_length=100)
    advisor_phone: str | None = Field(None, max_length=50)
    class_teacher_name: str | None = Field(None, max_length=100)
    class_teacher_phone: str | None = Field(None, max_length=50)
    assistant_name: str | None = Field(None, max_length=100)
    assistant_phone: str | None = Field(None, max_length=50)
    assistant_class_name: str | None = Field(None, max_length=200)


# ── 输出子 schemas：嵌套格式匹配前端期望的响应 ──

class AdvisorOut(BaseModel):
    name: str
    phone: str


class ClassTeacherOut(BaseModel):
    name: str
    phone: str


class AssistantOut(BaseModel):
    name: str
    phone: str
    class_name: str


class StudentOut(BaseModel):
    name: str
    student_id: str
    photo: str = ""
    class_name: str
    dormitory: str
    advisor: AdvisorOut
    class_teacher: ClassTeacherOut
    assistants: list[AssistantOut] = []
    role: str = "student"
