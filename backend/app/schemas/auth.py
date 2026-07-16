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
    password: str = Field(
        ...,
        min_length=1,
        description="登录密码",
        validation_alias=AliasChoices("password", "pwd"),
    )


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=64, description="新密码")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, description="refresh token 原文")


class LogoutRequest(BaseModel):
    refresh_token: str = Field(default="", min_length=0, description="refresh token 原文，为空则仅提示前端清除本地状态")
