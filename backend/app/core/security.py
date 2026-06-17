import hashlib
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings


def hash_id_number(id_number: str) -> str:
    """对身份证号做 SHA-256 加盐哈希，不可逆。"""
    raw = id_number.strip()
    salt = settings.ID_NUMBER_SALT.encode("utf-8")
    return hashlib.sha256(raw.encode("utf-8") + salt).hexdigest()

http_bearer = HTTPBearer(auto_error=False)
optional_http_bearer = HTTPBearer(auto_error=False)


def create_access_token(
    *,
    subject: str,
    name: str,
    role: str,
    expires_hours: Optional[int] = None,
) -> str:
    hours = expires_hours if expires_hours is not None else settings.ACCESS_TOKEN_EXPIRE_HOURS
    expire = datetime.now(timezone.utc) + timedelta(hours=hours)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "name": name,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


async def get_token_string(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌，请在 Header 中携带 Authorization: Bearer <token>",
        )
    return credentials.credentials


async def get_current_payload(
    token: str = Depends(get_token_string),
) -> Dict[str, Any]:
    try:
        payload = decode_token(token)
        if "sub" not in payload or "role" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌内容无效",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
        ) from None


async def get_optional_payload(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_http_bearer),
) -> Optional[Dict[str, Any]]:
    """无 Authorization 时返回 None；显式提供但非法的 token 仍 401。"""
    t0 = time.perf_counter()
    try:
        if credentials is None or not credentials.credentials:
            return None
        try:
            payload = decode_token(credentials.credentials)
            if "sub" not in payload or "role" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌内容无效",
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效或已过期",
            ) from None
    finally:
        perf = getattr(request.state, "agent_perf", None)
        if perf is not None:
            perf["jwt"] = round(time.perf_counter() - t0, 4)


async def require_admin(
    payload: Dict[str, Any] = Depends(get_current_payload),
) -> Dict[str, Any]:
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return payload


async def require_any_admin(
    payload: Dict[str, Any] = Depends(get_current_payload),
) -> Dict[str, Any]:
    """允许 admin 或 club_admin 角色访问。"""
    role = payload.get("role", "")
    if role not in ("admin", "club_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return payload


def get_student_id_from_payload(payload: Dict[str, Any]) -> int | None:
    """从 JWT payload 的 sub（student_id 字符串）反查 Student.id。"""
    from app.db.database import SessionLocal
    from app.models.student import Student
    from sqlalchemy import select

    sid = str(payload.get("sub", ""))
    if not sid:
        return None
    db = SessionLocal()
    try:
        row = db.scalars(select(Student.id).where(Student.student_id == sid)).first()
        return row
    finally:
        db.close()
