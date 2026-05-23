"""迎新助手域检测（供 Agent / 小信共用，关键词表统一在 app.core.keywords）。"""

from __future__ import annotations

from app.core.keywords import is_domain_related  # noqa: F401 — 保持原有 import 兼容
