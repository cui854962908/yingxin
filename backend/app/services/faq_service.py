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
    "快递站在哪里？怎么取快递？": (
        "快递", "快递站", "取快递", "寄快递", "快递点", "驿站",
        "包裹", "取件", "收快递", "快递在哪", "取件码",
    ),
    "校园网和校园卡怎么办理？": (
        "校园网", "WiFi", "wifi", "网络", "上网", "校园卡", "办卡",
        "营业厅", "套餐", "推销", "一卡通",
    ),
    "学校有哪些餐厅？": (
        "食堂", "餐厅", "去哪吃", "伙食", "吃饭", "梅园", "桃园", "兰园", "菊园",
    ),
    "宿舍有哪些管理规定？": (
        "宿舍", "门禁", "熄灯", "几点关门", "进出", "通电", "水电",
        "晚归", "22:30", "十点半", "宿舍几点熄灯",
    ),
    "学费和住宿费怎么交？缴费截止到什么时候？": (
        "学费", "住宿费", "缴费", "支付", "交费", "交钱", "助学贷款", "缓交",
        "在哪缴费", "怎么缴费", "缴清了没有",
    ),
    "图书馆在哪里？开放时间是几点？": (
        "图书馆", "自习", "借书", "阅览", "看书", "图书馆在哪", "闭馆", "学生证",
    ),
    "军训什么时候开始？军训服装怎么领取？": (
        "军训时间", "军训安排", "什么时候军训", "军训多久",
        "军训服装", "军训要带什么", "迷彩服",
    ),
    "新生报到需要带什么材料？报到流程是什么？": (
        "报到流程", "怎么走流程", "报到步骤", "入学流程",
        "要带什么", "带啥", "准备什么", "入学材料", "报到材料", "携带材料",
    ),
    "选课怎么选？什么时候开始？": (
        "选课", "喜鹊儿", "抢课", "选修课", "必修课", "公选课", "体育课", "怎么选课",
    ),
    "缺课多少不能参加期末考试？": (
        "缺课", "旷课", "缺考", "不能考试", "期末考核",
    ),
    "转专业需要满足什么条件？": (
        "转专业", "换专业", "转系", "专业调整",
    ),
    "什么情况下可以申请休学？复学怎么办理？": (
        "休学", "复学", "停课", "康复证明",
    ),
    "毕业、结业和提前毕业有什么区别？": (
        "毕业", "结业", "提前毕业", "学分", "学士学位",
    ),
    "学校有哪些学生奖励项目？": (
        "奖励", "评优", "三好学生", "优秀干部", "标兵",
    ),
    "违纪处分有哪些种类？可以申诉吗？": (
        "处分", "违纪", "警告", "记过", "开除学籍", "申诉",
    ),
    "什么情况下可以申请转学？": (
        "转学", "转校", "换学校",
    ),
    "校园内有哪些纪律红线需要注意？": (
        "纪律", "校规", "宗教", "网络", "红线",
    ),
    "学校三个校区地址分别在哪里？": (
        "校区", "地址", "龙子湖", "英才", "北林", "在哪里", "怎么去",
    ),
    "学校的校训和校庆日是哪天？": (
        "校训", "校庆", "尚严崇实", "善知敏行", "校史", "9月19",
    ),
    # ===== 资助政策（运营种子）=====
    "国家助学金的资助标准是多少？": (
        "助学金", "助学金多少", "贫困补助", "困难补助", "4400", "3700", "3000",
    ),
    "国家励志奖学金的奖励标准是多少？": (
        "励志奖学金", "国家励志", "1000", "3000",
    ),
    "国家助学贷款每年最多能贷多少钱？": (
        "助学贷款", "贷款多少", "能贷多少", "20000", "贷款上限",
    ),
    "国家助学贷款有哪几种？如何申请？": (
        "怎么贷款", "贷款申请", "生源地", "高校贷款", "资助中心",
    ),
    "临时困难补助的资助标准是多少？": (
        "临时困难", "困难补助", "500", "3000",
    ),
    "学校有哪些勤工助学机会？": (
        "勤工助学", "勤工", "打工", "兼职",
    ),
    "学校的资助体系覆盖范围有多大？": (
        "资助体系", "奖贷助补", "覆盖面",
    ),
    # ===== 入学报到（运营种子）=====
    "新生报到需要带什么材料？": (
        "要带什么", "带啥", "报到材料", "身份证", "档案", "照片",
    ),
    "不能按时报到怎么办？": (
        "不能报到", "延期报到", "请假", "晚到", "逾期",
    ),
    "学校在哪些地方设有新生接待站？": (
        "接站", "接待站", "火车站", "郑州东站", "西广场",
    ),
    "新生需要办理户口迁移吗？": (
        "户口迁移", "迁户口", "户籍",
    ),
    "学校有几个校区？": (
        "几个校区", "校区数量", "龙子湖", "英才", "北林",
    ),
    # ===== 后勤医疗（运营种子）=====
    "学校提供公寓用品吗？": (
        "被子", "被褥", "床上用品", "公寓用品", "要带被子吗",
    ),
    "大学生医疗保险如何缴纳？": (
        "医保", "医疗保险", "参保", "怎么交医保",
    ),
    "新生入学体检费用是多少？": (
        "体检", "体检费", "30元", "入学体检",
    ),
    # ===== 学校概况（运营种子）=====
    "河南牧业经济学院是什么性质的学校？": (
        "什么性质", "公办", "本科", "省属",
    ),
    "学校的校训是什么？": (
        "校训", "尚学崇实", "善知敏行",
    ),
    "河南牧业经济学院的建校历史是什么？": (
        "建校历史", "校史", "1957", "2013",
    ),
    "学校占地面积有多大？": (
        "占地面积", "面积", "191.3",
    ),
    "学校有多少教职工？": (
        "教职工", "教师人数", "师资",
    ),
    "学校有哪些国家级、省级教学名师？": (
        "教学名师", "国家级", "优秀教师",
    ),
    "学校有多少个本科专业？": (
        "本科专业", "53", "专业数量",
    ),
    "学校的重点学科和特色专业有哪些？": (
        "重点学科", "特色专业", "一流专业",
    ),
    "学校获得过哪些重要教学成果？": (
        "教学成果", "国家级", "省级",
    ),
    "学校有哪些科研平台？": (
        "科研平台", "省级平台", "创新团队",
    ),
    "学校有哪些科研成果？": (
        "科研成果", "国家基金", "专利",
    ),
    "学校的社会服务模式是什么？": (
        "社会服务", "三三一", "校地融合",
    ),
    "学校与哪些企业有合作？": (
        "企业合作", "华为", "牧原", "双汇", "产业学院",
    ),
    "学校有国际合作吗？": (
        "国际合作", "中外合作", "爱尔兰", "留学",
    ),
    "学校获得过哪些荣誉称号？": (
        "荣誉称号", "文明校园", "平安校园", "就业",
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
