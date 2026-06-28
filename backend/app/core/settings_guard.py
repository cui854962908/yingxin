"""启动时检查弱密钥；生产环境 REQUIRE_SECURE_SETTINGS=true 时拒绝启动。"""

from __future__ import annotations

import logging
import os

from app.core.config import Settings

_DEFAULT_SALT = "yingxin-default-salt-change-in-production"
_DEFAULT_ADMIN_ID = "000000000000000000"
_WEAK_JWT_MARKERS = ("change-me", "replace-with", "your-secret", "please-change")


def validate_settings(settings: Settings) -> None:
    issues: list[str] = []
    strict = os.getenv("REQUIRE_SECURE_SETTINGS", "").lower() in ("1", "true", "yes")
    if settings.ID_NUMBER_SALT == _DEFAULT_SALT:
        issues.append("ID_NUMBER_SALT 仍为默认值")
    jwt = settings.JWT_SECRET_KEY
    if len(jwt) < 32 or any(m in jwt.lower() for m in _WEAK_JWT_MARKERS):
        issues.append("JWT_SECRET_KEY 过短或为示例占位符")
    admin_id = os.getenv("ADMIN_SEED_ID_NUMBER", "").strip()
    if strict and (not admin_id or admin_id == _DEFAULT_ADMIN_ID):
        issues.append("生产环境请设置 ADMIN_SEED_ID_NUMBER（勿用默认管理员身份证）")

    if not issues:
        return

    msg = "；".join(issues)
    if strict:
        raise RuntimeError(f"安全配置未就绪：{msg}")
    logging.getLogger("app.startup").warning("安全配置提醒：%s", msg)
