from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class StudentVerifyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, description="姓名")
    student_id: str = Field(
        ...,
        min_length=1,
        description="学号",
        validation_alias=AliasChoices("student_id", "studentId"),
    )
    id_number: str = Field(
        default="",
        min_length=0,
        description="身份证号",
        validation_alias=AliasChoices("id_number", "idNumber"),
    )
