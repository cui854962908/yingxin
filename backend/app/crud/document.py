"""FAQ + 公告 + 社团向量化入库与余弦检索（对齐 HOUDAUN(3).md §3.3）。"""

from __future__ import annotations

import json
import logging
import math
import os
import uuid
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.llm import embed
from app.models.announcement import Announcement
from app.models.club import Club
from app.models.document import (
    DOCUMENT_SOURCE_ANNOUNCEMENT,
    DOCUMENT_SOURCE_CLUB,
    DOCUMENT_SOURCE_STUDENT_FAQ,
    Document,
)
from app.models.faq import FAQ

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _build_club_blob(row: Club) -> str:
    """将社团字段拼接为可用于向量检索的文本块。"""
    parts: list[str] = []
    if row.name:
        parts.append(row.name)
    if row.category:
        parts.append(f"类别：{row.category}")
    if row.intro:
        parts.append(f"简介：{row.intro}")
    if row.description:
        parts.append(row.description)
    if row.honor:
        parts.append(f"荣誉：{row.honor}")
    return "\n".join(parts)


def rebuild_documents_best_effort() -> None:
    """供 ``BackgroundTasks`` / 初始化使用：新开 Session；失败仅打日志。"""
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        build_documents(db, progress=False)
    except Exception:
        logger.warning("documents 向量重建未完成（DeepSeek API 不可用或迁移未执行）", exc_info=True)
    finally:
        db.close()


def build_documents(db: Session, *, progress: bool = False) -> dict[str, Any]:
    """全量重写 ``documents``：删表内全部记录后从 ``faq``、``announcements``、``clubs`` 入库；单行失败跳过。"""
    n_deleted = db.execute(delete(Document)).rowcount or 0
    if progress:
        print(f"[build_documents] 已删除原有 documents 行数: {n_deleted}", flush=True)

    texts: list[tuple[str, str, str, str]] = []

    for row in db.query(FAQ).all():
        uid = str(row.id)
        title = (row.question or "").strip()
        blob = title + "\n" + (row.answer or "").strip()
        texts.append((DOCUMENT_SOURCE_STUDENT_FAQ, uid, title, blob))

    for ann in db.query(Announcement).order_by(Announcement.created_at.asc()).all():
        uid = str(ann.id)
        title = (ann.title or "").strip()
        blob = title + "\n" + (ann.content or "").strip()
        texts.append((DOCUMENT_SOURCE_ANNOUNCEMENT, uid, title, blob))

    for club in db.query(Club).order_by(Club.created_at.asc()).all():
        uid = str(club.id)
        title = (club.name or "").strip()
        blob = _build_club_blob(club)
        texts.append((DOCUMENT_SOURCE_CLUB, uid, title, blob))

    count_ok = count_skip = 0
    verbose = os.getenv("EMBED_VERBOSE", "").lower() in {"1", "true", "yes"}
    total = len(texts)

    for i, (source_kind, source_id_str, title, content) in enumerate(texts, 1):
        if progress:
            print(f"  [{i}/{total}] {source_kind} id={source_id_str} …", flush=True)
        try:
            vec = embed(content)
        except Exception:
            count_skip += 1
            if verbose:
                logger.warning("[build_documents] embed 失败跳过: %s %s", source_kind, source_id_str, exc_info=True)
            continue

        ej = json.dumps(vec)
        title_trim = title[:512]

        doc = Document(
            source_kind=source_kind,
            title=title_trim,
            content=content,
            embedding_json=ej,
            source_student_faq_id=uuid.UUID(source_id_str) if source_kind == DOCUMENT_SOURCE_STUDENT_FAQ else None,
            source_announcement_id=uuid.UUID(source_id_str) if source_kind == DOCUMENT_SOURCE_ANNOUNCEMENT else None,
            source_club_id=uuid.UUID(source_id_str) if source_kind == DOCUMENT_SOURCE_CLUB else None,
            is_enabled=True,
        )
        db.add(doc)
        count_ok += 1

    db.commit()
    return {
        "written": count_ok,
        "skipped_embed_errors": count_skip,
        "deleted_previous": int(n_deleted or 0),
    }


def incremental_embed_student_faq(db: Session, faq_row: FAQ) -> None:
    """管理员新增/更新单行 FAQ 后：删同源 rows 再写一条 ``documents``。"""
    db.execute(delete(Document).where(Document.source_student_faq_id == faq_row.id))
    title = (faq_row.question or "").strip()
    content = title + "\n" + (faq_row.answer or "").strip()
    title_trim = title[:512]
    try:
        vec = embed(content)
    except Exception:
        logger.warning("[incremental_embed_student_faq] embed 跳过 faq_id=%s", faq_row.id, exc_info=True)
        db.commit()
        return
    doc = Document(
        source_kind=DOCUMENT_SOURCE_STUDENT_FAQ,
        title=title_trim,
        content=content,
        embedding_json=json.dumps(vec),
        source_student_faq_id=faq_row.id,
        source_announcement_id=None,
        source_club_id=None,
        is_enabled=True,
    )
    db.add(doc)
    db.commit()


def incremental_embed_announcement(db: Session, row: Announcement) -> None:
    """发布公告后写入对应 ``documents`` 行。"""
    db.execute(delete(Document).where(Document.source_announcement_id == row.id))
    title = (row.title or "").strip()
    content = title + "\n" + (row.content or "").strip()
    title_trim = title[:512]
    try:
        vec = embed(content)
    except Exception:
        logger.warning(
            "[incremental_embed_announcement] embed 跳过 announcement_id=%s",
            row.id,
            exc_info=True,
        )
        db.commit()
        return
    doc = Document(
        source_kind=DOCUMENT_SOURCE_ANNOUNCEMENT,
        title=title_trim,
        content=content,
        embedding_json=json.dumps(vec),
        source_student_faq_id=None,
        source_announcement_id=row.id,
        source_club_id=None,
        is_enabled=True,
    )
    db.add(doc)
    db.commit()


def incremental_embed_club(db: Session, row: Club) -> None:
    """社团新增/更新后写入对应 ``documents`` 行。"""
    db.execute(delete(Document).where(Document.source_club_id == row.id))
    title = (row.name or "").strip()
    content = _build_club_blob(row)
    title_trim = title[:512]
    try:
        vec = embed(content)
    except Exception:
        logger.warning(
            "[incremental_embed_club] embed 跳过 club_id=%s",
            row.id,
            exc_info=True,
        )
        db.commit()
        return
    doc = Document(
        source_kind=DOCUMENT_SOURCE_CLUB,
        title=title_trim,
        content=content,
        embedding_json=json.dumps(vec),
        source_student_faq_id=None,
        source_announcement_id=None,
        source_club_id=row.id,
        is_enabled=True,
    )
    db.add(doc)
    db.commit()


def delete_documents_for_student_faq(db: Session, faq_id: uuid.UUID) -> None:
    db.execute(delete(Document).where(Document.source_student_faq_id == faq_id))
    db.commit()


def delete_documents_for_announcement(db: Session, ann_id: uuid.UUID) -> None:
    db.execute(delete(Document).where(Document.source_announcement_id == ann_id))
    db.commit()


def delete_documents_for_club(db: Session, club_id: uuid.UUID) -> None:
    db.execute(delete(Document).where(Document.source_club_id == club_id))
    db.commit()


def search_similar(db: Session, query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """
    embed(query) → 加载全部 Document → Python 余弦 → 返回 [{"title","content","score"}, ...]
    """
    docs = db.query(Document).filter(Document.embedding_json.is_not(None)).all()
    if not docs:
        return []

    try:
        q_vec = embed(query.strip())
    except Exception:
        return []

    scored: list[dict[str, Any]] = []
    for doc in docs:
        raw = doc.embedding_json
        if not raw:
            continue
        try:
            d_vec = json.loads(raw)
            if not isinstance(d_vec, list):
                continue
            dvf = [float(x) for x in d_vec]
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        if len(dvf) != len(q_vec):
            continue
        score = _cosine_similarity(q_vec, dvf)
        scored.append({"title": doc.title, "content": doc.content, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
