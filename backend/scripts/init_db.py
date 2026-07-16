"""迎新系统种子数据：管理员 + 示例学生 + FAQ + 公告。首次部署执行一次即可。"""

import logging
import os
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.announcement import Announcement
from app.models.faq import FAQ
from app.models.student import Student
from app.core.security import DEFAULT_INITIAL_PASSWORD, hash_password

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from faq_operational_seed import OPERATIONAL_FAQ  # noqa: E402
from faq_sort_order import sort_order_for  # noqa: E402
from guide_announcement_seed import GUIDE_ANNOUNCEMENTS, TIPS_ANNOUNCEMENTS  # noqa: E402

logger = logging.getLogger(__name__)

def _default_password_hash() -> str:
    return hash_password(DEFAULT_INITIAL_PASSWORD)


def _build_admin_seed() -> dict:
    name = os.getenv("ADMIN_SEED_NAME", "崔志远").strip() or "崔志远"
    student_id = os.getenv("ADMIN_SEED_STUDENT_ID", "admin").strip() or "admin"
    return {
        "name": name,
        "student_id": student_id,
        "password_hash": _default_password_hash(),
        "class_name": "系统管理",
        "role": "admin",
    }


# ── 管理员（首次 ensure 时写入；已存在则不会覆盖）──
DEMO_STUDENTS = [
    {
        "name": "张三",
        "student_id": "20260901001",
        "password_hash": _default_password_hash(),
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
        "password_hash": _default_password_hash(),
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
        "password_hash": _default_password_hash(),
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
        "password_hash": _default_password_hash(),
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
        "question": "快递站在哪里？怎么取快递？",
        "answer": (
            "英才校区快递站位于菊园餐厅西侧，紧邻商业街，日常取件很方便。\n\n"
            "取件步骤：收到短信后，凭淘宝或短信中的取件码，到对应货架找到包裹，扫码即可取走。"
        ),
        "keywords": "快递,取快递,快递站,菜鸟驿站,取件码,包裹,菊园,商业街",
        "category": "校园生活",
    },
    {
        "question": "校园网和校园卡怎么办理？",
        "answer": (
            "有上网需求的同学，可自行前往校内营业厅办理校园卡套餐，"
            "月租约 19—49 元，套餐内通常附赠校园网服务。\n\n"
            "温馨提示：请勿相信宿舍内上门推销办卡的人员，以免上当受骗；"
            "如有疑问，请直接到营业厅咨询。"
        ),
        "keywords": "校园网,WiFi,wifi,网络,上网,校园卡,办卡,营业厅,套餐,推销",
        "category": "校园生活",
    },
    {
        "question": "宿舍有哪些管理规定？",
        "answer": (
            "英才校区宿舍全天通电，水电费用由学校统一承担，同学们无需额外缴费。\n\n"
            "请注意：每晚 22:30 起，宿舍楼一般情况下禁止进出。"
            "如有晚归或临时外出需求，请提前规划行程，并与辅导员沟通。"
        ),
        "keywords": "宿舍,门禁,熄灯,进出,通电,水电,晚归,22:30,十点半",
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
            "英才校区图书馆位于南门进入校园后右手边，是日常借书、自习的主要场所。"
            "借书或入内自习时，请携带学生证。\n\n"
            "开放时间：平日 21:30 闭馆；"
            "每周四 14:30—17:30 闭馆维护，计划前往的同学请留意时段。"
        ),
        "keywords": "图书馆,图书,开放时间,借书,自习,阅览室,南门,学生证,闭馆,周四",
        "category": "学习资源",
    },
    {
        "question": "军训什么时候开始？军训服装怎么领取？",
        "answer": (
            "依据 2026~2027 学年校历：2026 级新生 9 月 12 日报到，"
            "9 月 14 日至 9 月 30 日为入学教育和军训，10 月 8 日正式上课。\n\n"
            "军训服装领取时间与地点以学院通知为准，请报到后关注班级群消息。"
        ),
        "keywords": "军训,军训时间,军训安排,入学教育,9月12,9月14,10月8,军训服装,迷彩服",
        "category": "新生军训",
    },
    {
        "question": "新生报到需要带什么材料？报到流程是什么？",
        "answer": (
            "报到时请携带：录取通知书、身份证原件及复印件、高考准考证、"
            "本人纸质档案（密封件）、一寸免冠照片若干（建议 5 张，以学院通知为准）；"
            "团员须带组织关系材料，党员另备介绍信。\n\n"
            "建议流程：学院报到处签到 → 提交材料登记 → 领取校园卡 → 宿舍入住 → 完成缴费。"
            "具体以录取通知书及学院现场指引为准。"
        ),
        "keywords": "报到,报到材料,报到流程,新生报到,入学材料,证件,录取通知书,档案",
        "category": "新生报到",
    },
    {
        "question": "学校有哪些餐厅？",
        "answer": (
            "英才校区共有四座学生餐厅：梅园、桃园、兰园、菊园，合称「梅兰桃菊」，"
            "日常三餐均可在各餐厅解决。\n\n"
            "位置提示：桃园、菊园在一楼；兰园、梅园在二楼。"
        ),
        "keywords": "食堂,餐厅,伙食,吃饭,梅园,桃园,兰园,菊园",
        "category": "校园生活",
    },
    {
        "question": "选课怎么选？什么时候开始？",
        "answer": (
            "选课时间与具体安排以辅导员通知为准，不同批次可能略有差异。\n\n"
            "请在「喜鹊儿」APP 完成选课，并及时关注班级群和学院通知。"
            "体育课、公选课等热门课程名额有限，建议开放后尽早选报，避免错过时间。"
        ),
        "keywords": "选课,喜鹊儿,教务,课程,选修,必修,公选课,体育课",
        "category": "教务学习",
    },
    {
        "question": "缺课多少不能参加期末考试？",
        "answer": (
            "根据学校课程考核规定：缺课达该门课程总课时三分之一以上，或平时考核不及格，"
            "不能参加期末课程考核，该门课程记为缺考。\n\n"
            "考查课由任课教师自行组织期末考核；考试课一般在本学期最后2周进行。"
            "体育课成绩综合考勤、课内教学和课外锻炼评定。"
        ),
        "keywords": "缺课,考试,期末,考核,缺考,旷课,体育课,绩点",
        "category": "学籍管理",
    },
    {
        "question": "转专业需要满足什么条件？",
        "answer": (
            "全日制在校本科一、二、三年级学生，专科一、二年级（三年制）可申请转专业，须同时满足：\n"
            "① 思想品德优良，遵守法律法规和学校管理制度；\n"
            "② 对拟转入专业有一定兴趣和特长；\n"
            "③ 符合转出、转入学院公布的条件。\n\n"
            "以特殊招生形式录取、或录取前与学校有明确约定的学生，一般不得转专业。"
            "具体接收计划与流程以教务处和学院当年通知为准。"
        ),
        "keywords": "转专业,换专业,转系,专业调整,转入,转出",
        "category": "学籍管理",
    },
    {
        "question": "什么情况下可以申请休学？复学怎么办理？",
        "answer": (
            "可申请休学的情形包括：\n"
            "① 因病经指定医院诊断需停课治疗、休养，时间占一学期总学时三分之一以上；\n"
            "② 一学期请假累计超过总学时三分之一以上；\n"
            "③ 因特殊原因本人申请或学校认为应当休学。\n\n"
            "休学期满后，应在复学学期开学2周内提出复学申请；因病休学者须提交二级甲等以上医院康复证明。"
            "复学后编入相同学制相应专业学习。休学期满未按时办理复学手续的，按退学处理。"
        ),
        "keywords": "休学,复学,请假,停课,康复证明,保留学籍",
        "category": "学籍管理",
    },
    {
        "question": "毕业、结业和提前毕业有什么区别？",
        "answer": (
            "毕业：修完人才培养方案规定的全部课程并达到毕业要求，发给毕业证书；"
            "本科毕业生符合条件者授予学士学位。\n\n"
            "结业：未达到毕业要求，但在校学习一年以上且取得最低毕业总学分25%以上，发给结业证书。\n\n"
            "提前毕业：修完规定教学计划并达到弹性毕业年限要求，可申请提前毕业。"
            "具体学分与审核标准以所在年级培养方案为准。"
        ),
        "keywords": "毕业,结业,提前毕业,学分,学士学位,毕业证书",
        "category": "学籍管理",
    },
    {
        "question": "学校有哪些学生奖励项目？",
        "answer": (
            "学校设有多层次奖励，包括：三好学生、优秀学生干部、优秀毕业生，"
            "以及考研奖励、参军入伍奖励、西部计划奖励、三支一扶奖励等。\n\n"
            "专项荣誉还包括十大优秀学生标兵之星、十大优秀学生干部标兵之星，"
            "以及技能之星、道德之星、诚信自强之星、阅读之星、百名学业之星等。"
            "奖助学金与评优具体条件、时间以学生处和学院当年通知为准。"
        ),
        "keywords": "奖励,评优,三好学生,优秀干部,标兵,考研奖励,西部计划",
        "category": "学籍管理",
    },
    {
        "question": "违纪处分有哪些种类？可以申诉吗？",
        "answer": (
            "纪律处分种类包括：警告、严重警告、记过、留校察看、开除学籍。"
            "处分一般设6至12个月期限，到期后可按程序申请解除。\n\n"
            "学生对处分决定有异议的，可向学校学生申诉处理委员会提出申诉。"
            "请珍惜在校学习机会，遵守校纪校规与法律法规。"
        ),
        "keywords": "处分,违纪,警告,记过,开除学籍,申诉,校纪",
        "category": "学籍管理",
    },
    {
        "question": "学校三个校区地址分别在哪里？",
        "answer": (
            "河南牧业经济学院现有三个校区：\n"
            "① 龙子湖校区：郑州市郑东新区龙子湖北路6号（学校主校区，紧邻地铁1号线文苑北路站）；\n"
            "② 英才校区：郑州市惠济区英才街146号（信息工程学院等在此办学）；\n"
            "③ 北林校区：郑州市金水区北林路16号。\n\n"
            "报到与日常上课地点以录取通知书和学院通知为准，出行前建议用地图 App 确认具体门牌与入校路线。"
        ),
        "keywords": "校区,地址,龙子湖,英才,北林,在哪里,怎么去",
        "category": "认识牧院",
    },
    {
        "question": "学校的校训和校庆日是哪天？",
        "answer": (
            "校训：尚严崇实，善知敏行。\n\n"
            "校庆日：9月19日。\n\n"
            "学校由原郑州牧业工程高等专科学校（1957年建校）与河南商业高等专科学校（1960年建校）于2013年合并组建，"
            "秉承「区域性、行业性、开放型、应用型」办学定位。"
            "2021年通过教育部本科教学工作合格评估；2024年获批河南省硕士学位立项建设单位。"
        ),
        "keywords": "校训,校庆,尚严崇实,善知敏行,9月19,校史",
        "category": "认识牧院",
    },
    {
        "question": "什么情况下可以申请转学？",
        "answer": (
            "可申请转学的一般情形：\n"
            "① 因患病或有特殊困难、无法继续在本校学习，且经学校认可；\n"
            "② 因学校培养条件改变等非本人原因需要转学。\n\n"
            "下列情形不得转学：入学未满一学期或毕业前一年；"
            "高考成绩低于拟转入学校同一年同专业录取成绩；由低学历层次转为高学历层次；"
            "未通过普通高考统一考试录取（含保送、专升本等）；应予退学；无正当理由等。"
            "具体以当年教育部与学校学籍管理规定为准。"
        ),
        "keywords": "转学,转校,学籍,换学校",
        "category": "学籍管理",
    },
    {
        "question": "校园内有哪些纪律红线需要注意？",
        "answer": (
            "请遵守以下校园秩序要求：\n"
            "① 学生社团活动须在学校管理范围内进行；\n"
            "② 不得从事或参与有损大学生形象、有悖公序良俗的活动；\n"
            "③ 任何组织和个人不得在校园内进行宗教活动；\n"
            "④ 遵守网络使用规定，不得传播非法信息、编造虚假信息或攻击他人网络系统；\n"
            "⑤ 遵守学校住宿管理制度。\n\n"
            "违纪将受到警告直至开除学籍等处分，对处分决定可按规定申诉。"
        ),
        "keywords": "纪律,校规,宗教,网络,宿舍,社团,红线,处分",
        "category": "学籍管理",
    },
]

_OBSOLETE_FAQ_QUESTIONS = (
    "新生报到需要带什么材料？",
)

_OBSOLETE_TIPS_TITLES = (
    "App 一览",
    "教务与学籍",
    "课堂与网课",
    "校园服务与生活",
    "活动、体育与第二课堂",
    "其它常用工具",
)

# ── 校园公告 ──
_OBSOLETE_ANNOUNCEMENT_TITLES = (
    "2026级新生入学教育安排通知",
    "关于2026级新生体检的通知",
    "关于新生军训服装领取的通知",
)

DEMO_ANNOUNCEMENTS = [
    {
        "title": "2026级新生入学教育与军训安排",
        "category": "campus",
        "content": (
            "依据校历，2026 级新生 9 月 12 日报到，"
            "9 月 14 日至 9 月 30 日为入学教育和军训，10 月 8 日正式上课。"
            "请按时到校，具体日程以学院通知为准。"
        ),
        "date": date(2026, 8, 20),
    },
    {
        "title": "2026级新生报到提醒",
        "category": "campus",
        "content": (
            "2026 级新生报到日期为 9 月 12 日（星期六）。"
            "请携带录取通知书、身份证等材料，按学院指引完成报到。"
            "老生 9 月 5 日至 6 日返校报到，9 月 7 日上课，请勿混淆。"
        ),
        "date": date(2026, 8, 25),
    },
    {
        "title": "2026级新生体检安排",
        "category": "campus",
        "content": (
            "新生体检时间与批次由学院统一安排，报到后请关注班级群与学院通知。"
            "体检一般需携带身份证，部分项目需空腹，请提前做好准备。"
        ),
        "date": date(2026, 8, 26),
    },
    {
        "title": "2026年秋季学期选课通知",
        "category": "campus",
        "content": (
            "2026年秋季学期选课时间与安排以辅导员通知为准。"
            "请在「喜鹊儿」APP 完成选课，并及时关注班级群与学院通知。"
            "体育课、公选课等热门课程名额有限，建议开放后尽早选报。"
        ),
        "date": date(2026, 8, 22),
    },
]

_ALL_ANNOUNCEMENT_SEEDS = (
    [*DEMO_ANNOUNCEMENTS, *GUIDE_ANNOUNCEMENTS, *TIPS_ANNOUNCEMENTS]
)


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
    existing = db.scalars(select(Student).where(Student.role == "admin")).first()
    if existing:
        logger.info(
            "已有管理员账号 %s（student_id=%s），跳过 admin 种子",
            existing.name,
            existing.student_id,
        )
        return
    _ensure_rows(db, Student, "student_id", [_build_admin_seed()])


def ensure_students(db: Session) -> None:
    _ensure_rows(db, Student, "student_id", DEMO_STUDENTS)


def ensure_faq(db: Session) -> None:
    """种子 FAQ：仅新增或更新，不删除库内已有条目（废弃问法除外）。"""
    for q in _OBSOLETE_FAQ_QUESTIONS:
        row = db.scalars(select(FAQ).where(FAQ.question == q)).first()
        if row:
            db.delete(row)
    for d in [*DEMO_FAQ, *OPERATIONAL_FAQ]:
        payload = dict(d)
        q = payload["question"]
        payload["sort_order"] = sort_order_for(q)
        row = db.scalars(select(FAQ).where(FAQ.question == q)).first()
        if row:
            row.answer = payload["answer"]
            row.keywords = payload.get("keywords")
            row.category = payload.get("category")
            row.sort_order = payload["sort_order"]
        else:
            db.add(FAQ(**payload))


def ensure_announcements(db: Session) -> None:
    """种子公告：按标题新增或更新正文，并清理已废弃的演示标题。"""
    for title in (*_OBSOLETE_ANNOUNCEMENT_TITLES, *_OBSOLETE_TIPS_TITLES):
        row = db.scalars(select(Announcement).where(Announcement.title == title)).first()
        if row:
            db.delete(row)
    for d in _ALL_ANNOUNCEMENT_SEEDS:
        row = db.scalars(select(Announcement).where(Announcement.title == d["title"])).first()
        if row:
            row.content = d["content"]
            row.date = d["date"]
            row.category = d.get("category")
        else:
            db.add(Announcement(**d))


def main() -> None:
    db = SessionLocal()
    try:
        ensure_admin(db)
        ensure_students(db)
        ensure_faq(db)
        ensure_announcements(db)
        db.commit()
        faq_total = len(db.scalars(select(FAQ)).all())
        print("初始化完成。")
        admin_row = _build_admin_seed()
        print(f"  管理员：student_id={admin_row['student_id']}（{admin_row['name']}）")
        print(f"  学生：{len(DEMO_STUDENTS)} 人")
        print(f"  FAQ：种子 {len(DEMO_FAQ) + len(OPERATIONAL_FAQ)} 条，库内合计 {faq_total} 条")
        print(f"  公告：种子 {len(_ALL_ANNOUNCEMENT_SEEDS)} 条（报到须知 {len(GUIDE_ANNOUNCEMENTS)}、新生攻略 {len(TIPS_ANNOUNCEMENTS)}）")

        try:
            from app.crud.document import rebuild_documents_best_effort
            rebuild_documents_best_effort()
            print("  向量库：已构建")
        except Exception:
            logger.warning(
                "向量库构建未完成（嵌入 API 不可用），启动后可手动执行 rebuild_documents_best_effort",
                exc_info=True,
            )

    except Exception:
        db.rollback()
        logger.exception("初始化失败")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
