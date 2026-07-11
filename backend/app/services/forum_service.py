"""牧院新生说业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.forum import (
    FORUM_CATEGORIES,
    ForumAnswer,
    ForumAnswerLike,
    ForumPost,
    ForumPostLike,
)
from app.models.student import Student
from app.schemas.forum import (
    ForumAnswerItem,
    ForumPostBrief,
    ForumPostDetail,
)
from app.services.forum_author_service import author_brief_for_viewer

EDIT_WINDOW = timedelta(hours=24)
MAX_POSTS_PER_DAY = 5
MAX_ANSWERS_PER_DAY = 30
PREVIEW_LEN = 96


def resolve_author_id(db: Session, payload: dict[str, Any]) -> int:
    sid = str(payload.get("sub", "")).strip()
    if not sid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    row = db.scalars(select(Student.id).where(Student.student_id == sid)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return row


def _preview(text: str) -> str:
    t = text.strip().replace("\n", " ")
    return t if len(t) <= PREVIEW_LEN else t[:PREVIEW_LEN] + "…"


def _ensure_category(category: str) -> str:
    if category not in FORUM_CATEGORIES:
        raise HTTPException(status_code=422, detail="无效分类")
    return category


def _get_visible_post(db: Session, post_id: uuid.UUID) -> ForumPost:
    post = db.get(ForumPost, post_id)
    if not post or post.is_hidden:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post


def _assert_edit_window(post_or_answer: ForumPost | ForumAnswer) -> None:
    created = post_or_answer.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created > EDIT_WINDOW:
        raise HTTPException(status_code=403, detail="已超过 24 小时，无法编辑")


def _count_today_posts(db: Session, author_id: int) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return db.scalar(
        select(func.count()).select_from(ForumPost).where(
            ForumPost.author_id == author_id,
            ForumPost.created_at >= start,
        )
    ) or 0


def _count_today_answers(db: Session, author_id: int) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return db.scalar(
        select(func.count()).select_from(ForumAnswer).where(
            ForumAnswer.author_id == author_id,
            ForumAnswer.created_at >= start,
        )
    ) or 0


def _liked_post_ids(db: Session, viewer_id: int | None, post_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    if viewer_id is None or not post_ids:
        return set()
    rows = db.scalars(
        select(ForumPostLike.post_id).where(
            ForumPostLike.user_id == viewer_id,
            ForumPostLike.post_id.in_(post_ids),
        )
    ).all()
    return set(rows)


def _liked_answer_ids(db: Session, viewer_id: int | None, answer_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    if viewer_id is None or not answer_ids:
        return set()
    rows = db.scalars(
        select(ForumAnswerLike.answer_id).where(
            ForumAnswerLike.user_id == viewer_id,
            ForumAnswerLike.answer_id.in_(answer_ids),
        )
    ).all()
    return set(rows)


def list_posts(
    db: Session,
    *,
    page: int,
    page_size: int,
    sort: str,
    category: str | None,
    q: str | None,
    mine: bool,
    viewer_id: int | None,
) -> dict[str, Any]:
    stmt = (
        select(ForumPost)
        .join(Student, ForumPost.author_id == Student.id)
        .where(ForumPost.is_hidden.is_(False))
    )
    if mine:
        if viewer_id is None:
            raise HTTPException(status_code=401, detail="查看我的提问需登录")
        stmt = stmt.where(ForumPost.author_id == viewer_id)
    if category:
        stmt = stmt.where(ForumPost.category == _ensure_category(category))
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(ForumPost.title.ilike(pattern), ForumPost.content.ilike(pattern)))
    if sort == "hot":
        order = (
            ForumPost.is_pinned.desc(),
            ForumPost.like_count.desc(),
            ForumPost.answer_count.desc(),
            ForumPost.created_at.desc(),
        )
    elif sort == "open":
        stmt = stmt.where(ForumPost.has_accepted.is_(False), ForumPost.is_closed.is_(False))
        order = (ForumPost.is_pinned.desc(), ForumPost.created_at.desc())
    else:
        order = (ForumPost.is_pinned.desc(), ForumPost.created_at.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.order_by(*order).offset((page - 1) * page_size).limit(page_size)).all()
    author_map = {
        s.id: s
        for s in db.scalars(select(Student).where(Student.id.in_([r.author_id for r in rows]))).all()
    }
    liked_posts = _liked_post_ids(db, viewer_id, [r.id for r in rows])
    items = []
    for row in rows:
        author = author_map.get(row.author_id)
        if not author:
            continue
        items.append(
            ForumPostBrief(
                id=row.id,
                title=row.title,
                content_preview=_preview(row.content),
                category=row.category,
                author=author_brief_for_viewer(author, viewer_id),
                answer_count=row.answer_count,
                has_accepted=row.has_accepted,
                is_closed=row.is_closed,
                is_pinned=row.is_pinned,
                like_count=row.like_count,
                view_count=row.view_count,
                liked_by_me=row.id in liked_posts,
                created_at=row.created_at,
                is_mine=viewer_id == row.author_id if viewer_id else False,
            ).model_dump(mode="json")
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_post_detail(db: Session, post_id: uuid.UUID, viewer_id: int | None) -> dict[str, Any]:
    post = db.scalar(
        select(ForumPost)
        .options(joinedload(ForumPost.answers))
        .where(ForumPost.id == post_id, ForumPost.is_hidden.is_(False))
    )
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    author = db.get(Student, post.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="帖子不存在")
    answer_authors = {
        s.id: s
        for s in db.scalars(
            select(Student).where(Student.id.in_([a.author_id for a in post.answers]))
        ).all()
    }
    visible_answers = [a for a in post.answers if not a.is_hidden]
    visible_answers.sort(key=lambda a: (not a.is_accepted, -a.like_count, a.created_at))
    liked_answers = _liked_answer_ids(db, viewer_id, [a.id for a in visible_answers])
    answer_items = [
        ForumAnswerItem(
            id=a.id,
            content=a.content,
            author=author_brief_for_viewer(answer_authors[a.author_id], viewer_id),
            is_accepted=a.is_accepted,
            like_count=a.like_count,
            liked_by_me=a.id in liked_answers,
            created_at=a.created_at,
            is_mine=viewer_id == a.author_id if viewer_id else False,
        )
        for a in visible_answers
        if a.author_id in answer_authors
    ]
    liked_posts = _liked_post_ids(db, viewer_id, [post.id])
    detail = ForumPostDetail(
        id=post.id,
        title=post.title,
        content=post.content,
        category=post.category,
        author=author_brief_for_viewer(author, viewer_id),
        author_id=post.author_id if viewer_id is not None else None,
        answer_count=post.answer_count,
        has_accepted=post.has_accepted,
        is_closed=post.is_closed,
        is_pinned=post.is_pinned,
        like_count=post.like_count,
        view_count=post.view_count,
        liked_by_me=post.id in liked_posts,
        created_at=post.created_at,
        is_mine=viewer_id == post.author_id if viewer_id else False,
        answers=answer_items,
    )
    return detail.model_dump(mode="json")


def view_post_detail(db: Session, post_id: uuid.UUID, viewer_id: int | None) -> dict[str, Any]:
    """Increase the counter only for an actual detail-page request."""
    result = db.execute(
        update(ForumPost)
        .where(ForumPost.id == post_id, ForumPost.is_hidden.is_(False))
        .values(view_count=ForumPost.view_count + 1)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="帖子不存在")
    db.commit()
    return get_post_detail(db, post_id, viewer_id)


def create_post(db: Session, payload: dict[str, Any], *, title: str, content: str, category: str) -> dict:
    author_id = resolve_author_id(db, payload)
    if _count_today_posts(db, author_id) >= MAX_POSTS_PER_DAY:
        raise HTTPException(status_code=429, detail="今日发帖已达上限（5 条）")
    post = ForumPost(
        author_id=author_id,
        title=title.strip(),
        content=content.strip(),
        category=_ensure_category(category),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return get_post_detail(db, post.id, author_id)


def update_post(
    db: Session, payload: dict[str, Any], post_id: uuid.UUID, fields: dict[str, str]
) -> dict:
    author_id = resolve_author_id(db, payload)
    post = _get_visible_post(db, post_id)
    is_admin = payload.get("role") == "admin"
    if not is_admin and post.author_id != author_id:
        raise HTTPException(status_code=403, detail="无权编辑")
    if not is_admin:
        _assert_edit_window(post)
    if "title" in fields:
        post.title = fields["title"].strip()
    if "content" in fields:
        post.content = fields["content"].strip()
    if "category" in fields:
        post.category = _ensure_category(fields["category"])
    db.commit()
    return get_post_detail(db, post_id, author_id)


def delete_post(db: Session, payload: dict[str, Any], post_id: uuid.UUID) -> None:
    author_id = resolve_author_id(db, payload)
    post = _get_visible_post(db, post_id)
    is_admin = payload.get("role") == "admin"
    if not is_admin and post.author_id != author_id:
        raise HTTPException(status_code=403, detail="无权删除")
    db.delete(post)
    db.commit()


def close_post(db: Session, payload: dict[str, Any], post_id: uuid.UUID) -> dict:
    author_id = resolve_author_id(db, payload)
    post = _get_visible_post(db, post_id)
    if payload.get("role") != "admin" and post.author_id != author_id:
        raise HTTPException(status_code=403, detail="无权关闭")
    post.is_closed = True
    db.commit()
    return get_post_detail(db, post_id, author_id)


def create_answer(db: Session, payload: dict[str, Any], post_id: uuid.UUID, content: str) -> dict:
    author_id = resolve_author_id(db, payload)
    post = _get_visible_post(db, post_id)
    if post.is_closed:
        raise HTTPException(status_code=403, detail="帖子已关闭")
    if _count_today_answers(db, author_id) >= MAX_ANSWERS_PER_DAY:
        raise HTTPException(status_code=429, detail="今日回答已达上限（30 条）")
    answer = ForumAnswer(post_id=post.id, author_id=author_id, content=content.strip())
    db.add(answer)
    post.answer_count += 1
    db.commit()
    return get_post_detail(db, post_id, author_id)


def update_answer(db: Session, payload: dict[str, Any], answer_id: uuid.UUID, content: str) -> dict:
    author_id = resolve_author_id(db, payload)
    answer = db.get(ForumAnswer, answer_id)
    if not answer or answer.is_hidden:
        raise HTTPException(status_code=404, detail="回答不存在")
    is_admin = payload.get("role") == "admin"
    if not is_admin and answer.author_id != author_id:
        raise HTTPException(status_code=403, detail="无权编辑")
    if not is_admin:
        _assert_edit_window(answer)
    answer.content = content.strip()
    db.commit()
    return get_post_detail(db, answer.post_id, author_id)


def delete_answer(db: Session, payload: dict[str, Any], answer_id: uuid.UUID) -> dict:
    author_id = resolve_author_id(db, payload)
    answer = db.get(ForumAnswer, answer_id)
    if not answer or answer.is_hidden:
        raise HTTPException(status_code=404, detail="回答不存在")
    post_id = answer.post_id
    is_admin = payload.get("role") == "admin"
    if not is_admin and answer.author_id != author_id:
        raise HTTPException(status_code=403, detail="无权删除")
    post = db.get(ForumPost, post_id)
    if post and answer.is_accepted:
        post.has_accepted = False
    if post:
        post.answer_count = max(0, post.answer_count - 1)
    db.delete(answer)
    db.commit()
    return get_post_detail(db, post_id, author_id)


def accept_answer(db: Session, payload: dict[str, Any], answer_id: uuid.UUID) -> dict:
    author_id = resolve_author_id(db, payload)
    answer = db.get(ForumAnswer, answer_id)
    if not answer or answer.is_hidden:
        raise HTTPException(status_code=404, detail="回答不存在")
    post = _get_visible_post(db, answer.post_id)
    if payload.get("role") != "admin" and post.author_id != author_id:
        raise HTTPException(status_code=403, detail="仅楼主可采纳")
    for a in post.answers:
        a.is_accepted = a.id == answer.id
    post.has_accepted = True
    db.commit()
    return get_post_detail(db, post.id, author_id)


def admin_pin_post(db: Session, post_id: uuid.UUID, pinned: bool) -> None:
    post = _get_visible_post(db, post_id)
    post.is_pinned = pinned
    db.commit()


def admin_hide_post(db: Session, post_id: uuid.UUID) -> None:
    post = db.get(ForumPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    post.is_hidden = True
    db.commit()


def toggle_post_like(db: Session, payload: dict[str, Any], post_id: uuid.UUID) -> dict[str, Any]:
    user_id = resolve_author_id(db, payload)
    post = _get_visible_post(db, post_id)
    key = {"user_id": user_id, "post_id": post.id}
    existing = db.get(ForumPostLike, key)
    if existing:
        db.delete(existing)
        post.like_count = max(0, post.like_count - 1)
        liked = False
    else:
        db.add(ForumPostLike(user_id=user_id, post_id=post.id))
        post.like_count += 1
        liked = True
    db.commit()
    return {"like_count": post.like_count, "liked_by_me": liked}


def toggle_answer_like(db: Session, payload: dict[str, Any], answer_id: uuid.UUID) -> dict[str, Any]:
    user_id = resolve_author_id(db, payload)
    answer = db.get(ForumAnswer, answer_id)
    if not answer or answer.is_hidden:
        raise HTTPException(status_code=404, detail="回答不存在")
    _get_visible_post(db, answer.post_id)
    key = {"user_id": user_id, "answer_id": answer.id}
    existing = db.get(ForumAnswerLike, key)
    if existing:
        db.delete(existing)
        answer.like_count = max(0, answer.like_count - 1)
        liked = False
    else:
        db.add(ForumAnswerLike(user_id=user_id, answer_id=answer.id))
        answer.like_count += 1
        liked = True
    db.commit()
    return {"like_count": answer.like_count, "liked_by_me": liked}
