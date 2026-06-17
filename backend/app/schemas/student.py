from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator


def _coerce_str(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    if isinstance(v, str):
        return v.strip()
    return v


def _flatten_nested_contact_fields(data: dict[str, Any]) -> dict[str, Any]:
    """把前端常见的嵌套结构展平为扁平字段（与 GET 返回结构对称）。"""
    d = dict(data)

    adv = d.pop("advisor", None)
    if isinstance(adv, dict):
        if adv.get("name") is not None and "advisor_name" not in d and "advisorName" not in d:
            d["advisor_name"] = adv.get("name")
        if adv.get("phone") is not None and "advisor_phone" not in d and "advisorPhone" not in d:
            d["advisor_phone"] = adv.get("phone")

    ct = d.pop("classTeacher", None)
    if ct is None:
        ct = d.pop("class_teacher", None)
    if isinstance(ct, dict):
        if ct.get("name") is not None and "class_teacher_name" not in d and "classTeacherName" not in d:
            d["class_teacher_name"] = ct.get("name")
        if ct.get("phone") is not None and "class_teacher_phone" not in d and "classTeacherPhone" not in d:
            d["class_teacher_phone"] = ct.get("phone")

    asst = d.pop("assistants", None)
    if asst is None:
        asst = d.pop("assistant", None)
    first: dict[str, Any] | None = None
    if isinstance(asst, list) and len(asst) > 0 and isinstance(asst[0], dict):
        first = asst[0]
    elif isinstance(asst, dict):
        first = asst
    if first is not None:
        if first.get("name") is not None and d.get("assistant_name") is None and d.get("assistantName") is None:
            d["assistant_name"] = first.get("name")
        if first.get("phone") is not None and d.get("assistant_phone") is None and d.get("assistantPhone") is None:
            d["assistant_phone"] = first.get("phone")
        cn = first.get("class_name", first.get("className"))
        if cn is not None and d.get("assistant_class_name") is None and d.get("assistantClassName") is None:
            d["assistant_class_name"] = cn

    if "student" in d and isinstance(d["student"], dict) and len(d) == 1:
        return _flatten_nested_contact_fields(d["student"])

    return d


class StudentCreate(BaseModel):
    """新增学生：snake_case / camelCase + 嵌套 advisor 等与列表接口对齐。"""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1, validation_alias=AliasChoices("student_id", "studentId"))
    id_number: str = Field(..., min_length=1, validation_alias=AliasChoices("id_number", "idNumber"))
    photo: str | None = Field("", validation_alias=AliasChoices("photo"))
    class_name: str = Field(..., min_length=1, validation_alias=AliasChoices("class_name", "className"))
    dormitory: str | None = Field("", validation_alias=AliasChoices("dormitory"))
    advisor_name: str | None = Field(None, validation_alias=AliasChoices("advisor_name", "advisorName"))
    advisor_phone: str | None = Field(None, validation_alias=AliasChoices("advisor_phone", "advisorPhone"))
    class_teacher_name: str | None = Field(
        None, validation_alias=AliasChoices("class_teacher_name", "classTeacherName")
    )
    class_teacher_phone: str | None = Field(
        None, validation_alias=AliasChoices("class_teacher_phone", "classTeacherPhone")
    )
    assistant_name: str | None = Field(None, validation_alias=AliasChoices("assistant_name", "assistantName"))
    assistant_phone: str | None = Field(
        None, validation_alias=AliasChoices("assistant_phone", "assistantPhone")
    )
    assistant_class_name: str | None = Field(
        None, validation_alias=AliasChoices("assistant_class_name", "assistantClassName")
    )

    @model_validator(mode="before")
    @classmethod
    def _before_create(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        flat = _flatten_nested_contact_fields(data)
        for key in (
            "name",
            "student_id",
            "studentId",
            "id_number",
            "idNumber",
            "class_name",
            "className",
            "photo",
            "dormitory",
            "advisor_name",
            "advisorName",
            "advisor_phone",
            "advisorPhone",
            "class_teacher_name",
            "classTeacherName",
            "class_teacher_phone",
            "classTeacherPhone",
            "assistant_name",
            "assistantName",
            "assistant_phone",
            "assistantPhone",
            "assistant_class_name",
            "assistantClassName",
        ):
            if key in flat:
                flat[key] = _coerce_str(flat[key])
        return flat


class StudentUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, validation_alias=AliasChoices("name"))
    id_number: str | None = Field(None, validation_alias=AliasChoices("id_number", "idNumber"))
    photo: str | None = Field(None, validation_alias=AliasChoices("photo"))
    class_name: str | None = Field(None, validation_alias=AliasChoices("class_name", "className"))
    dormitory: str | None = Field(None, validation_alias=AliasChoices("dormitory"))
    advisor_name: str | None = Field(None, validation_alias=AliasChoices("advisor_name", "advisorName"))
    advisor_phone: str | None = Field(None, validation_alias=AliasChoices("advisor_phone", "advisorPhone"))
    class_teacher_name: str | None = Field(
        None, validation_alias=AliasChoices("class_teacher_name", "classTeacherName")
    )
    class_teacher_phone: str | None = Field(
        None, validation_alias=AliasChoices("class_teacher_phone", "classTeacherPhone")
    )
    assistant_name: str | None = Field(None, validation_alias=AliasChoices("assistant_name", "assistantName"))
    assistant_phone: str | None = Field(
        None, validation_alias=AliasChoices("assistant_phone", "assistantPhone")
    )
    assistant_class_name: str | None = Field(
        None, validation_alias=AliasChoices("assistant_class_name", "assistantClassName")
    )

    @model_validator(mode="before")
    @classmethod
    def _before_update(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        flat = _flatten_nested_contact_fields(data)
        for key in list(flat.keys()):
            if key in flat and flat[key] is not None:
                if isinstance(flat[key], str) or isinstance(flat[key], (int, float)):
                    flat[key] = _coerce_str(flat[key])
        return flat
