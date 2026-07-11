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


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, description="refresh token 原文")


class LogoutRequest(BaseModel):
    refresh_token: str = Field(default="", min_length=0, description="refresh token 原文，为空则仅提示前端清除本地状态")
