"""
登录错误次数限制：同一学号连续 N 次验证失败 → 锁定 T 秒。

纯内存实现（单进程 uvicorn），无需 Redis/数据库。
"""

import time
from dataclasses import dataclass
from typing import Dict

MAX_FAILURES = 5
LOCK_SECONDS = 300  # 5 分钟

# 全局内存表：{student_id: _Entry}
_store: Dict[str, "_Entry"] = {}


@dataclass
class _Entry:
    fail_count: int = 0
    locked_until: float = 0.0


def check_locked(student_id: str) -> int:
    """
    检查学号是否在锁定期。
    返回 0 表示未锁定；>0 表示剩余锁定秒数。
    """
    entry = _store.get(student_id)
    if not entry or entry.locked_until == 0:
        return 0
    remaining = entry.locked_until - time.time()
    if remaining <= 0:
        # 锁定期已过，重置
        del _store[student_id]
        return 0
    return int(remaining) + 1  # 向上取整，至少 1 秒


def record_failure(student_id: str) -> int:
    """
    记录一次验证失败。
    返回剩余尝试次数（0 表示刚触发锁定）。
    """
    entry = _store.get(student_id)
    if not entry:
        entry = _Entry()
        _store[student_id] = entry

    # 如果旧锁已过期，重置计数
    if entry.locked_until and entry.locked_until < time.time():
        entry.fail_count = 0
        entry.locked_until = 0.0

    entry.fail_count += 1

    if entry.fail_count >= MAX_FAILURES:
        entry.locked_until = time.time() + LOCK_SECONDS
        return 0  # 表示刚锁定

    return MAX_FAILURES - entry.fail_count  # 剩余次数


def clear_record(student_id: str) -> None:
    """验证成功后清除该学号的所有记录。"""
    _store.pop(student_id, None)
