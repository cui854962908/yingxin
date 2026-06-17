from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.faq import FAQ

# --- MVP：进程内缓存 FAQ，修改后台数据后在路由里 clear_faq_cache 或重启 ---
_faq_cache: list["FaqEntry"] | None = None


@dataclass(frozen=True)
class FaqEntry:
    id: uuid.UUID
    question: str
    answer: str
    keywords: str | None


@dataclass
class FaqMatch:
    faq: FaqEntry
    score: float


def clear_faq_cache() -> None:
    global _faq_cache
    _faq_cache = None


def _row_to_entry(row: FAQ) -> FaqEntry:
    return FaqEntry(
        id=row.id,
        question=row.question,
        answer=row.answer,
        keywords=row.keywords,
    )


def load_enabled_faqs_from_db(db: Session) -> list[FaqEntry]:
    stmt = select(FAQ).order_by(FAQ.sort_order.asc(), FAQ.created_at.asc())
    rows = list(db.scalars(stmt).all())
    return [_row_to_entry(r) for r in rows]


def get_enabled_faq_entries(db: Session) -> list[FaqEntry]:
    global _faq_cache
    if _faq_cache is not None:
        return _faq_cache
    _faq_cache = load_enabled_faqs_from_db(db)
    return _faq_cache


def normalize_text(text: str) -> str:
    raw = text.strip().lower()
    raw = re.sub(r"[\s\u3000]+", "", raw)
    raw = re.sub(r"[^\w\u4e00-\u9fff]", "", raw)
    return raw


def _split_keywords(cell: str | None) -> list[str]:
    if not cell:
        return []
    parts: list[str] = []
    for raw in cell.replace("，", ",").split(","):
        t = raw.strip()
        if t:
            parts.append(t)
    return parts


FAQ_QUESTION_LINKED_PHRASES: dict[str, tuple[str, ...]] = {
    # ===== 入学报到 =====
    "新生报到流程是什么？": (
        "报到流程", "怎么走流程", "报到步骤", "入学流程", "需要什么手续",
    ),
    "报到需要带什么材料？": (
        "要带什么", "带啥", "准备什么", "要带啥", "入学要带",
        "开学要带", "入学材料", "报到材料", "携带材料", "证件材料",
    ),
    "报到地点在哪里查看？": (
        "报到地点", "报到点", "去哪报到",
    ),
    "现场签到怎么完成？": (
        "现场签到", "到校签到", "扫码签到", "怎么签到",
    ),
    "不能按时报到怎么办？": (
        "请假", "不能报到", "延期报到", "晚到报到", "迟到报到",
        "无法按时报到", "怎么请假",
    ),
    "学校在哪些地方设有新生接待站？": (
        "接站", "接新生", "火车站接", "在哪接", "免费接",
        "接待站", "郑州接站", "下车怎么走",
    ),
    # ===== 资助政策 =====
    "国家助学金的资助标准是多少？": (
        "助学金", "助学金多少", "贫困补助", "困难补助", "助学金标准",
        "怎么申请助学金", "助学金分几档", "贫困生资助",
    ),
    "国家助学贷款每年最多能贷多少钱？": (
        "助学贷款", "贷款多少", "能贷多少", "贷款上限", "贷款金额",
        "学费不够", "没钱交学费",
    ),
    "国家助学贷款有哪几种？如何申请？": (
        "怎么贷款", "贷款申请", "贷款流程", "贷款种类",
        "高校贷款", "生源地贷款", "在哪申请贷款",
    ),
    # ===== 宿舍 / 生活 =====
    "宿舍在哪里查询？": (
        "在哪里查", "在哪查", "宿舍在哪查", "在哪查宿舍",
        "寝室在哪看", "寝室分配", "住宿安排", "住在哪里",
        "住哪", "床位查询", "房间号", "宿舍楼",
    ),
    "宿舍钥匙在哪里领取？": (
        "宿舍钥匙", "钥匙在哪领", "领钥匙",
    ),
    "学校提供公寓用品吗？": (
        "被子", "被褥", "床上用品", "要带被子吗", "学校发被子",
        "宿舍用品", "公寓物品",
    ),
    "快递站在哪里？": (
        "快递", "快递站", "取快递", "寄快递", "快递点", "驿站",
        "包裹", "取件", "收快递",
    ),
    "学校有哪些食堂？": (
        "食堂", "餐厅", "去哪吃", "伙食", "吃饭",
    ),
    "宿舍几点熄灯？": (
        "熄灯", "几点关门", "门禁", "几点熄灯", "宿舍关门", "就寝时间",
    ),
    # ===== 校园卡 / 缴费 =====
    "校园卡在哪里领取？": (
        "校园卡怎么领", "一卡通", "领卡", "卡在哪领", "办卡",
    ),
    "校园卡怎么补办？": (
        "补办校园卡", "校园卡丢了", "卡丢了", "挂失", "补卡",
    ),
    "缴费状态在哪里查看？": (
        "缴费状态", "在哪缴费", "怎么缴费", "学费在哪交",
        "住宿费查询", "费用查询", "交了没有", "缴清了没有",
        "未缴费", "已缴费",
    ),
    # ===== 军训 =====
    "军训什么时候开始？": (
        "军训时间", "军训安排", "什么时候军训", "军训多久",
        "军训服装", "军训要带什么",
    ),
    # ===== 系统使用 =====
    "忘记密码怎么办？": (
        "密码忘了", "找回密码", "重置密码", "修改密码", "登录不了",
    ),
    "个人信息填错了怎么办？": (
        "信息填错", "资料填错", "改个人信息", "信息有误", "怎么改资料",
    ),
    "通知公告在哪里查看？": (
        "通知在哪看", "公告在哪", "最新通知",
    ),
    # ===== 教学 =====
    "怎么选课？": (
        "选课", "选课系统", "抢课", "选修课", "必修课",
    ),
    "图书馆在哪里？": (
        "图书馆", "自习", "借书", "阅览", "看书", "图书馆在哪",
    ),
    # ===== 医疗 / 体检 =====
    "大学生医疗保险如何缴纳？": (
        "医保", "医疗保险", "参保", "怎么交医保", "看病报销",
    ),
    "新生入学体检费用是多少？": (
        "体检", "体检费", "体检多少钱", "入学体检", "体检项目",
    ),
}


def _score_faq(message_norm: str, faq: FaqEntry) -> float:
    score = 0.0
    q_raw = faq.question.strip()
    q_norm = normalize_text(q_raw)

    if q_norm and q_norm in message_norm:
        score += 14.0
    if message_norm and len(message_norm) >= 4 and message_norm in q_norm:
        score += 10.0

    q_strip = normalize_text(q_raw.replace("？", "").replace("?", ""))
    if len(q_strip) >= 4:
        for win in range(min(len(q_strip), 12), 3, -1):
            for i in range(0, len(q_strip) - win + 1):
                sub = q_strip[i : i + win]
                if len(sub) >= 4 and sub in message_norm:
                    score += 5.0
                    break
            else:
                continue
            break

    for kw in _split_keywords(faq.keywords):
        kn = normalize_text(kw)
        if not kn:
            continue
        if kn in message_norm:
            score += 5.0 if len(kn) >= 4 else 3.0

    for phrase in FAQ_QUESTION_LINKED_PHRASES.get(q_raw, ()):
        pn = normalize_text(phrase)
        if pn and pn in message_norm:
            score += 7.0

    if q_norm:
        overlap = sum(1 for ch in q_norm if ch in message_norm)
        score += min(4.0, overlap / max(len(q_norm), 1) * 4.0)

    return score


def find_best_faq(
    db: Session,
    message: str,
    min_score: float | None = None,
    *,
    request: object | None = None,
) -> FaqMatch | None:
    threshold = settings.FAQ_MATCH_MIN_SCORE if min_score is None else min_score
    t0 = time.perf_counter()
    faqs = get_enabled_faq_entries(db)
    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["faq_db_or_cache"] = round(time.perf_counter() - t0, 4)
    if not faqs:
        return None

    message_norm = normalize_text(message)
    if not message_norm:
        return None

    t1 = time.perf_counter()
    best: FaqMatch | None = None
    for faq in faqs:
        s = _score_faq(message_norm, faq)
        if best is None or s > best.score:
            best = FaqMatch(faq=faq, score=s)

    if request is not None and getattr(request.state, "agent_perf", None) is not None:
        request.state.agent_perf["faq_match"] = round(time.perf_counter() - t1, 4)

    if best is None or best.score < threshold:
        return None

    return best
