"""Author presentation and privacy rules for forum responses."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.models.student import Student
from app.schemas.forum import ForumAuthorBrief


def _guest_author_label(student: Student, *, now: datetime | None = None) -> str:
    sid = (student.student_id or "").strip()
    match = re.match(r"^(\d{4})", sid)
    if not match:
        return "牧院学子"
    year = int(match.group(1))
    if year < 2000 or year > 2100:
        return "牧院学子"
    reference = now or datetime.now(timezone.utc)
    enrollment_year = reference.year if reference.month >= 6 else reference.year - 1
    return f"{year} 级新生" if year == enrollment_year else f"{year} 级"


def author_brief_for_viewer(student: Student, viewer_id: int | None) -> ForumAuthorBrief:
    if viewer_id is None:
        return ForumAuthorBrief(
            name=_guest_author_label(student),
            class_name="—",
            forum_role=None,
        )
    return ForumAuthorBrief(
        name=student.name,
        class_name=student.class_name or "—",
        forum_role=student.forum_role,
    )
