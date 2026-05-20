"""SQLAlchemy 数据库引擎、会话、基类 & 种子数据"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_demo_data():
    """首次启动时填充示例数据（仅在表为空时执行）。"""
    from datetime import date

    from app.models.student import Student, Assistant
    from app.models.announcement import Announcement
    from app.models.faq import Faq

    db = SessionLocal()
    try:
        if db.query(Student).count() > 0:
            return

        # ── 示例学生 ──
        demo_students = [
            Student(
                name="张三",
                student_id="20260901001",
                id_number="410105200509010011",
                class_name="计算机科学与技术 2026-1班",
                dormitory="北苑 3号楼 412室",
                advisor_name="李明辉",
                advisor_phone="138-0000-1111",
                class_teacher_name="赵文博",
                class_teacher_phone="137-0000-7777",
                role="student",
            ),
            Student(
                name="李四",
                student_id="20260901002",
                id_number="410105200510150022",
                class_name="软件工程 2026-2班",
                dormitory="北苑 5号楼 208室",
                advisor_name="张丽华",
                advisor_phone="138-0000-3333",
                class_teacher_name="孙建国",
                class_teacher_phone="137-0000-8888",
                role="student",
            ),
            Student(
                name="王五",
                student_id="20260901003",
                id_number="410105200508200033",
                class_name="数据科学与大数据 2026-1班",
                dormitory="南苑 2号楼 515室",
                advisor_name="陈刚",
                advisor_phone="138-0000-5555",
                class_teacher_name="周敏",
                class_teacher_phone="137-0000-9999",
                role="student",
            ),
            Student(
                name="崔志远",
                student_id="2502160306002",
                id_number="411103200712010177",
                class_name="25级物联网工程06班",
                dormitory="12号楼419",
                advisor_name="王子钰",
                advisor_phone="—",
                class_teacher_name="张红红",
                class_teacher_phone="—",
                role="admin",
            ),
        ]
        db.add_all(demo_students)
        db.flush()  # 获取 student.id 用于 assistants

        # ── 代班 ──
        demo_assistants = [
            Assistant(student_id="20260901001", name="王浩", phone="139-0000-2222", class_name="计算机科学 2025-1班"),
            Assistant(student_id="20260901002", name="刘洋", phone="139-0000-4444", class_name="软件工程 2025-2班"),
            Assistant(student_id="20260901003", name="赵雪", phone="139-0000-6666", class_name="大数据 2025-1班"),
            Assistant(student_id="2502160306002", name="袁振康", phone="—", class_name="24级物联网工程05班"),
            Assistant(student_id="2502160306002", name="周沫言", phone="—", class_name="24级软件工程11班"),
        ]
        db.add_all(demo_assistants)

        # ── 示例 FAQ ──
        demo_faq = [
            Faq(
                question="学校快递站在哪里？取快递的流程是什么？",
                answer="快递站位于北苑食堂西侧，凭取件码和校园卡取件。\n\n1. 收到短信后查看取件码\n2. 前往快递站按货架号找到包裹\n3. 出示校园卡或取件码给工作人员核验\n4. 核验通过后即可取走",
            ),
            Faq(
                question="如何办理校园卡？",
                answer="校园卡在入学报道时统一发放。如需补办：\n\n1. 前往行政楼一楼卡务中心\n2. 携带身份证和学生证\n3. 缴纳 20 元工本费\n4. 现场制卡，立等可取",
            ),
            Faq(
                question="宿舍几点熄灯？有门禁吗？",
                answer="宿舍周日到周四 23:00 熄灯，周五周六 23:30 熄灯。\n\n门禁时间：每晚 22:30 后只进不出，23:00 准时锁门。晚归需向辅导员报备。",
            ),
            Faq(
                question="学费和住宿费怎么交？",
                answer="通过学校统一支付平台缴费：\n\n1. 登录学校官网 → 财务处 → 学生缴费\n2. 支持微信、支付宝、银联\n3. 学费与住宿费需在每学期开学后两周内缴清\n4. 如有困难可申请助学贷款或缓交",
            ),
        ]
        db.add_all(demo_faq)

        # ── 示例公告 ──
        demo_announcements = [
            Announcement(
                date=date(2026, 8, 10),
                title="新生入学教育安排通知",
                content="2026 级新生入学教育将于 9 月 1 日至 9 月 5 日在校礼堂举行，请全体新生按时参加。具体日程安排请关注各学院通知。",
            ),
            Announcement(
                date=date(2026, 8, 11),
                title="关于 2026 级新生体检的通知",
                content="新生体检定于 9 月 6 日至 9 月 8 日，地点为校医院。请携带身份证和校园卡，按学院分批前往。",
            ),
            Announcement(
                date=date(2026, 8, 12),
                title="关于新生军训服装领取的通知",
                content="军训服装将于 8 月 28 日至 8 月 30 日在体育馆一楼发放，请携带录取通知书或校园卡领取。",
            ),
        ]
        db.add_all(demo_announcements)

        db.commit()
    finally:
        db.close()
