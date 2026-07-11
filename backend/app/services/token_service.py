"""refresh token 服务：签发 / 轮换 / 撤销 / 批量撤销。"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


def issue_refresh_token(db: Session, *, student_id: int) -> tuple[str, RefreshToken]:
    """签发一个新的 refresh token，返回（原文, 持久化模型）。

    原文仅在此返回，之后不再以明文形式存储。
    """
    raw = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    record = RefreshToken(
        student_id=student_id,
        token_hash=hash_refresh_token(raw),
        expires_at=now + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
    )
    db.add(record)
    db.flush()
    return raw, record


def rotate_refresh_token(db: Session, *, raw_token: str) -> tuple[str, RefreshToken] | None:
    """验证并轮换 refresh token。

    成功：撤销旧 token、签发新 token，返回（新原文, 新记录）。
    失败（不存在、过期、已撤销）：返回 None。
    """
    token_hash = hash_refresh_token(raw_token)
    record = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked.is_(False),
    ).first()

    if not record:
        return None

    now = datetime.now(timezone.utc)
    if record.expires_at.replace(tzinfo=timezone.utc) < now:
        # 过期标记撤销
        record.revoked = True
        record.revoked_at = now
        db.flush()
        return None

    # 轮换：撤销旧的，签发新的
    new_raw = str(uuid.uuid4())
    new_record = RefreshToken(
        student_id=record.student_id,
        token_hash=hash_refresh_token(new_raw),
        expires_at=now + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS),
    )
    db.add(new_record)
    db.flush()

    record.revoked = True
    record.revoked_at = now
    record.replaced_by = new_record.id
    db.flush()

    return new_raw, new_record


def revoke_refresh_token(db: Session, *, raw_token: str) -> bool:
    """撤销单个 refresh token（用户主动登出）。返回是否找到了有效 token。"""
    token_hash = hash_refresh_token(raw_token)
    record = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked.is_(False),
    ).first()
    if not record:
        return False
    record.revoked = True
    record.revoked_at = datetime.now(timezone.utc)
    db.flush()
    return True


def revoke_all_for_student(db: Session, *, student_id: int) -> int:
    """撤销某学生的所有有效 refresh token（用于安全事件：检测到重用）。"""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(RefreshToken)
        .where(
            and_(
                RefreshToken.student_id == student_id,
                RefreshToken.revoked.is_(False),
            )
        )
        .values(revoked=True, revoked_at=now)
    )
    return result.rowcount or 0
