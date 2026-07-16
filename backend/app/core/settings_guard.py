"""启动时检查弱密钥；生产环境 REQUIRE_SECURE_SETTINGS=true 时拒绝启动。"""

from __future__ import annotations

import logging
import os

from app.core.config import Settings

_WEAK_JWT_MARKERS = ("change-me", "replace-with", "your-secret", "please-change")


def validate_settings(settings: Settings) -> None:
    issues: list[str] = []
    strict = os.getenv("REQUIRE_SECURE_SETTINGS", "").lower() in ("1", "true", "yes")
    jwt = settings.JWT_SECRET_KEY
    if len(jwt) < 32 or any(m in jwt.lower() for m in _WEAK_JWT_MARKERS):
        issues.append("JWT_SECRET_KEY 过短或为示例占位符")

    if not issues:
        return

    msg = "；".join(issues)
    if strict:
        raise RuntimeError(f"安全配置未就绪：{msg}")
    logging.getLogger("app.startup").warning("安全配置提醒：%s", msg)
