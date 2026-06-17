"""日志写入前脱敏：身份证号、手机号。"""

from __future__ import annotations

import re

_ID18 = re.compile(r"\d{17}[\dXx]")
_PHONE = re.compile(r"(?<!\d)1\d{10}(?!\d)")


def redact_pii(text: str) -> str:
    text = _ID18.sub("[ID]", text)
    return _PHONE.sub("[PHONE]", text)
