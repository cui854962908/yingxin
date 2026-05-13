"""JWT 认证工具"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("JWT_SECRET", "yingxin-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

bearer_scheme = HTTPBearer(auto_error=False)


def create_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(401, "未提供认证令牌")
    payload = decode_token(creds.credentials)
    if payload is None:
        raise HTTPException(401, "令牌无效或已过期")
    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(403, "需要管理员权限")
    return user
