"""迎新系统种子数据：管理员 + 示例学生 + FAQ + 公告。首次部署执行一次即可。"""

import logging
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.announcement import Announcement
from app.models.faq import FAQ
from app.models.student import Student
from app.core.security import hash_id_number

logger = logging.getLogger(__name__)

# ── 管理员 ──
ADMIN = {
    "name": "崔志远",
    "student_id": "admin",
    "id_number_hash": hash_id_number("000000000000000000"),
    "class_name": "系统管理",
    "role": "admin",
}

# ── 示例学生 ──
DEMO_STUDENTS = [
    {
        "name": "张三",
        "student_id": "20260901001",
        "id_number_hash": hash_id_number("410105200509010011"),
        "class_name": "计算机科学与技术2026-1班",
        "dormitory": "北苑3号楼412室",
        "advisor_name": "李明辉",
        "advisor_phone": "138-0000-1111",
        "class_teacher_name": "赵文博",
        "class_teacher_phone": "137-0000-7777",
        "assistant_name": "王浩",
        "assistant_phone": "139-0000-2222",
        "assistant_class_name": "计算机科学2025-1班",
        "role": "student",
    },
    {
        "name": "李思雨",
        "student_id": "20260902001",
        "id_number_hash": hash_id_number("410105200510150022"),
        "class_name": "软件工程2026-2班",
        "dormitory": "南苑5号楼608室",
        "advisor_name": "陈雅婷",
        "advisor_phone": "138-0000-3333",
        "class_teacher_name": "刘志强",
        "class_teacher_phone": "137-0000-8888",
        "assistant_name": "马宁",
        "assistant_phone": "139-0000-4444",
        "assistant_class_name": "软件工程2025-2班",
        "role": "student",
    },
    {
        "name": "王浩然",
        "student_id": "20260903001",
        "id_number_hash": hash_id_number("410105200508200033"),
        "class_name": "数据科学与大数据2026-1班",
        "dormitory": "西苑2号楼315室",
        "advisor_name": "张丽",
        "advisor_phone": "138-0000-5555",
        "class_teacher_name": "周敏",
        "class_teacher_phone": "137-0000-9999",
        "assistant_name": "赵雪",
        "assistant_phone": "139-0000-6666",
        "assistant_class_name": "大数据2025-1班",
        "role": "student",
    },
    {
        "name": "刘子涵",
        "student_id": "20260904001",
        "id_number_hash": hash_id_number("410105200509050044"),
        "class_name": "物联网工程2026-6班",
        "dormitory": "北苑12号楼419室",
        "advisor_name": "王子钰",
        "advisor_phone": "138-0000-0000",
        "class_teacher_name": "张红红",
        "class_teacher_phone": "137-0000-0000",
        "assistant_name": "袁振康",
        "assistant_phone": "139-0000-0000",
        "assistant_class_name": "物联网工程2025-5班",
        "role": "student",
    },
]

# ── 常见问题（keywords 供快车精准匹配，注意：admin 新增 FAQ 时 keywords 字段会同步到快车缓存）──
DEMO_FAQ = [
    {
        "question": "学校快递站在哪里？取快递的流程是什么？",
        "answer": (
            "快递站位于北苑食堂西侧，凭取件码和校园卡取件。\n\n"
            "流程：① 收到取件短信后查看取件码 → ② 前往快递站按货架号找到包裹 → "
            "③ 出示校园卡或取件码给工作人员核验 → ④ 核验通过取走包裹"
        ),
        "keywords": "快递,取快递,快递站,菜鸟驿站,取件码,包裹",
        "category": "校园生活",
    },
    {
        "question": "如何办理校园卡？校园卡丢失了怎么办？",
        "answer": (
            "校园卡在入学报道时统一发放，免费领取。\n\n"
            "补办流程：① 前往行政楼一楼卡务中心 → ② 携带身份证和学生证 → "
            "③ 缴纳20元工本费 → ④ 现场制卡，立等可取"
        ),
        "keywords": "校园卡,一卡通,办卡,补办,卡务中心,学生卡",
        "category": "校园生活",
    },
    {
        "question": "宿舍几点熄灯？有门禁吗？",
        "answer": (
            "宿舍熄灯时间：周日到周四23:00熄灯，周五周六23:30熄灯。\n\n"
            "门禁：每晚22:30后只进不出，23:00准时锁门。晚归需提前向辅导员报备。"
        ),
        "keywords": "宿舍,熄灯,门禁,熄灯时间,锁门,晚归",
        "category": "宿舍管理",
    },
    {
        "question": "学费和住宿费怎么交？缴费截止到什么时候？",
        "answer": (
            "通过学校统一支付平台缴费：\n\n"
            "① 登录学校官网 → 财务处 → 学生缴费 → "
            "② 支持微信、支付宝、银联在线支付 → "
            "③ 学费与住宿费需在每学期开学后两周内缴清 → "
            "④ 如有经济困难可申请助学贷款或缓交，具体联系辅导员"
        ),
        "keywords": "学费,住宿费,缴费,支付,交费,交钱,助学贷款,缓交",
        "category": "财务缴费",
    },
    {
        "question": "图书馆在哪里？开放时间是几点？",
        "answer": (
            "图书馆位于校园中心广场东侧，凭校园卡入馆。\n\n"
            "开放时间：每天7:00—22:00，期末复习周延长至23:00。\n"
            "借阅：本科生可借10册，借期30天，可续借一次。"
        ),
        "keywords": "图书馆,开放时间,借书,自习,阅览室",
        "category": "学习资源",
    },
    {
        "question": "军训什么时候开始？军训服装怎么领取？",
        "answer": (
            "军训为期两周，9月初正式开始。具体日期以学校通知为准。\n\n"
            "军训服装领取：8月28日至8月30日在体育馆一楼发放，"
            "需携带录取通知书或校园卡。含迷彩服一套、帽子一顶、腰带一条、解放鞋一双。"
        ),
        "keywords": "军训,军训时间,军训服装,军训服,迷彩服,体育馆,领取服装",
        "category": "新生军训",
    },
    {
        "question": "新生报到需要带什么材料？报到流程是什么？",
        "answer": (
            "报到必备材料：\n"
            "① 录取通知书原件 → ② 身份证原件及复印件2份 → "
            "③ 高考准考证 → ④ 近期一寸免冠照片4张（蓝底）→ "
            "⑤ 学生档案（部分省份由招办统一邮寄）→ ⑥ 团员档案/党员组织关系介绍信\n\n"
            "报到流程：校门口签到 → 学院报到点登记 → 领取校园卡 → 宿舍入住 → 缴纳费用"
        ),
        "keywords": "报到,报到材料,报到流程,新生报到,入学材料,证件,录取通知书",
        "category": "新生报到",
    },
    {
        "question": "学校食堂在哪里？伙食怎么样？",
        "answer": (
            "学校共有三个食堂：北苑食堂（靠近北区宿舍）、南苑食堂（靠近南区宿舍）、"
            "西区美食广场（教学楼附近）。\n\n"
            "均支持校园卡和手机支付（微信/支付宝），菜品涵盖中餐、面食、小吃、清真窗口，"
            "早餐约3-8元，午晚餐约8-15元。"
        ),
        "keywords": "食堂,餐厅,伙食,吃饭,美食广场,清真",
        "category": "校园生活",
    },
    {
        "question": "学校校园网怎么开通？宿舍有没有WiFi？",
        "answer": (
            "校园网开通：报到后携带校园卡前往信息化办公室（行政楼二楼）办理。\n\n"
            "资费：基础套餐免费（访问校内资源），高速套餐20元/月（不限流量，访问外网）。"
            "宿舍区均有WiFi覆盖（SSID：HUA-YUAN-WiFi），使用学号+统一认证密码登录。"
        ),
        "keywords": "校园网,WiFi,wifi,网络,上网,信息化办公室,网费",
        "category": "校园生活",
    },
    {
        "question": "选课怎么选？什么时候开始选课？",
        "answer": (
            "选课通过教务管理系统进行（学校官网→教务处→教务系统）。\n\n"
            "选课时间：开学前一周开放预选，开学第一周为补退选阶段。"
            "热门课程（体育、公选课）名额有限，建议尽早登录选课。"
        ),
        "keywords": "选课,教务系统,课程,选修,必修,公选课,体育课",
        "category": "教务学习",
    },
    {
        "question": "学校有奖学金和助学金吗？怎么申请？",
        "answer": (
            "我校设有多种奖助学金：\n"
            "① 国家奖学金（8000元/年）→ ② 国家励志奖学金（5000元/年）→ "
            "③ 校级奖学金（一等3000/二等2000/三等1000）→ "
            "④ 国家助学金（平均3300元/年）→ ⑤ 勤工助学岗位\n\n"
            "申请时间：每学年开学后一个月内，向辅导员提交申请材料，学院初审后报学生处审批。"
        ),
        "keywords": "奖学金,助学金,国家奖学金,励志奖学金,勤工助学,助学金申请",
        "category": "奖助学金",
    },
    {
        "question": "学校附近有什么银行？怎么存取钱？",
        "answer": (
            "校内：北苑食堂一楼设有建设银行ATM、工商银行ATM。\n"
            "校外步行范围：建设银行营业厅（出南门左转200米）、中国银行（学校东门对面）。\n\n"
            "建议办理建设银行卡（学校合作银行），奖学金、助学金均通过建行卡发放。"
        ),
        "keywords": "银行,ATM,取钱,存钱,建设银行,工商银行,银行卡",
        "category": "校园生活",
    },
]

# ── 校园公告 ──
DEMO_ANNOUNCEMENTS = [
    {
        "title": "2026级新生入学教育安排通知",
        "content": (
            "2026级新生入学教育将于9月1日至9月5日在校礼堂举行，请全体新生按时参加。"
            "内容包括：校史校情介绍、安全教育、心理健康教育、专业导论等。"
            "具体日程安排请关注各学院通知公告栏。"
        ),
        "date": date(2026, 8, 20),
    },
    {
        "title": "关于2026级新生体检的通知",
        "content": (
            "新生体检定于9月6日至9月8日，地点为校医院。请携带身份证和校园卡，"
            "空腹参加抽血项目。各学院分批次前往，具体时间安排见学院通知。"
        ),
        "date": date(2026, 8, 25),
    },
    {
        "title": "关于新生军训服装领取的通知",
        "content": (
            "军训服装将于8月28日至8月30日在体育馆一楼发放。请携带录取通知书或校园卡，"
            "按学院分批领取。服装含迷彩服一套、帽子一顶、腰带一条、解放鞋一双。"
            "如有尺码不合适可在8月31日统一调换。"
        ),
        "date": date(2026, 8, 26),
    },
    {
        "title": "2026年秋季学期选课通知",
        "content": (
            "2026年秋季学期选课系统将于8月25日上午9:00开放。请登录教务管理系统进行选课。"
            "预选阶段：8月25日—8月30日。补退选阶段：9月1日—9月7日。"
            "体育课和公共选修课名额有限，请尽早选择。"
        ),
        "date": date(2026, 8, 22),
    },
]


def _ensure_rows(
    db: Session,
    model,
    key_field: str,
    rows: list[dict],
) -> None:
    for row in rows:
        existing = db.scalars(
            select(model).where(getattr(model, key_field) == row[key_field])
        ).first()
        if existing:
            continue
        db.add(model(**row))


def ensure_admin(db: Session) -> None:
    _ensure_rows(db, Student, "student_id", [ADMIN])


def ensure_students(db: Session) -> None:
    _ensure_rows(db, Student, "student_id", DEMO_STUDENTS)


def ensure_faq(db: Session) -> None:
    rows = [dict(d, question=d["question"]) for d in DEMO_FAQ]
    _ensure_rows(db, FAQ, "question", rows)


def ensure_announcements(db: Session) -> None:
    _ensure_rows(db, Announcement, "title", DEMO_ANNOUNCEMENTS)


def main() -> None:
    db = SessionLocal()
    try:
        ensure_admin(db)
        ensure_students(db)
        ensure_faq(db)
        ensure_announcements(db)
        db.commit()
        print("初始化完成。")
        print(f"  管理员：student_id=admin（{ADMIN['name']}）")
        print(f"  学生：{len(DEMO_STUDENTS)} 人")
        print(f"  FAQ：{len(DEMO_FAQ)} 条")
        print(f"  公告：{len(DEMO_ANNOUNCEMENTS)} 条")

        try:
            from app.crud.document import rebuild_documents_best_effort
            rebuild_documents_best_effort()
            print("  向量库：已构建")
        except Exception:
            logger.warning(
                "向量库构建未完成（DeepSeek API 不可用），启动后可手动执行 rebuild_documents_best_effort",
                exc_info=