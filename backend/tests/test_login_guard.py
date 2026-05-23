"""login_guard 单元测试：计数、锁定、清除。"""

import time
import pytest
from app.services.login_guard import (
    check_locked,
    record_failure,
    clear_record,
    MAX_FAILURES,
    LOCK_SECONDS,
)


class TestRecordFailure:
    """验证 record_failure 的计数与锁定逻辑。"""

    def test_first_4_failures_return_remaining(self):
        """前 4 次失败返回剩余尝试次数。"""
        sid = "test_001"
        clear_record(sid)
        assert record_failure(sid) == 4  # 剩 4 次
        assert record_failure(sid) == 3  # 剩 3 次
        assert record_failure(sid) == 2  # 剩 2 次
        assert record_failure(sid) == 1  # 剩 1 次

    def test_5th_failure_triggers_lock(self):
        """第 5 次失败触发锁定，返回 0。"""
        sid = "test_002"
        clear_record(sid)
        for _ in range(4):
            record_failure(sid)
        assert record_failure(sid) == 0  # 第 5 次，锁定

    def test_check_locked_returns_remaining_seconds(self):
        """锁定期间 check_locked 返回 >0。"""
        sid = "test_003"
        clear_record(sid)
        for _ in range(MAX_FAILURES):
            record_failure(sid)
        remaining = check_locked(sid)
        assert remaining > 0
        assert remaining <= LOCK_SECONDS + 1

    def test_lock_expires_after_time(self):
        """锁定期过后 check_locked 返回 0。"""
        sid = "test_004"
        clear_record(sid)
        # 伪造一个已过期的锁
        from app.services.login_guard import _store, _Entry
        _store[sid] = _Entry(fail_count=5, locked_until=time.time() - 10)
        assert check_locked(sid) == 0

    def test_clear_after_success(self):
        """成功登录后 clear_record 清除计数。"""
        sid = "test_005"
        clear_record(sid)
        record_failure(sid)
        record_failure(sid)
        clear_record(sid)
        assert check_locked(sid) == 0
        # 重新开始计数
        assert record_failure(sid) == 4

    def test_different_ids_independent(self):
        """不同学号独立计数。"""
        clear_record("A")
        clear_record("B")
        for _ in range(MAX_FAILURES):
            record_failure("A")
        assert check_locked("A") > 0
        assert check_locked("B") == 0
