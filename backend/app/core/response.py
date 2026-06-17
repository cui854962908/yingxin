from typing import Any, Dict

JSONDict = Dict[str, Any]


def ok_envelope(
    *,
    message: str = "操作成功",
    data: Any = None,
) -> JSONDict:
    return {"success": True, "message": message, "data": data}


def fail_envelope(*, message: str, data: Any = None) -> JSONDict:
    return {"success": False, "message": message, "data": data}


def verify_ok(
    *,
    message: str,
    token: str,
    data: Any,
) -> JSONDict:
    """学生验证成功：token 与 data 同级。"""
    return {
        "success": True,
        "message": message,
        "token": token,
        "data": data,
    }


