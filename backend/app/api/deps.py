"""FastAPI 共享依赖"""

from fastapi import Depends, HTTPException

from app.core.auth import get_current_user
from app.core.database import get_db


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(403, "需要管理员权限")
    return user
