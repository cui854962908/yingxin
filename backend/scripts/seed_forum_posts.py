"""
手动开发脚本：向 forum_posts 表插入测试帖子（不随 init_db 执行）。
用法：cd backend && uv run python scripts/seed_forum_posts.py
"""
import random
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import text
from app.db.database import SessionLocal
from app.models.forum import FORUM_CATEGORIES, ForumPost

POSTS_REAL = [
    # === 报到 ===
    {
        "author_student_id": "20260901001",
        "title": "报到当天需要带哪些证件？复印件要几份？",
        "content": "录取通知书上写要带身份证和准考证，但是没有说要几份复印件。有学长学姐知道身份证和户口本复印件各要几份吗？还需要带高中档案吗？",
        "category": "报到",
    },
    {
        "author_student_id": "20260901001",
        "title": "北苑3号楼的住宿条件怎么样？需要自备床垫吗？",
        "content": "我被分到了北苑3号楼412室，想了解一下宿舍有空调吗？床是多大的？需要自己带床垫和被子吗？还有其他什么建议带去的东西？",
        "category": "报到",
    },
    {
        "author_student_id": "20260902001",
        "title": "行李太多怎么办？快递到学校可以提前几天寄？",
        "content": "我家在省外，东西比较多，打算先把一些行李快递到学校。但不知道学校的快递点在哪里，可以提前几天寄过去？到了会有学长帮忙搬吗？",
        "category": "报到",
    },
    # === 宿舍 ===
    {
        "author_student_id": "20260902001",
        "title": "南苑5号楼洗澡是独立卫浴还是公共澡堂？",
        "content": "我是南苑5号楼608室的，想提前了解一下宿舍的卫浴情况。如果有独立卫生间的话热水是24小时供应吗？另外学校有洗衣机吗，怎么收费的？",
        "category": "宿舍",
    },
    {
        "author_student_id": "20260903001",
        "title": "西苑2号楼晚上断电断网吗？",
        "content": "想问一下住在西苑的学长们，宿舍晚上几点熄灯断电？周末也会断电吗？还有校园网的网速怎么样，需要自己办宽带吗？",
        "category": "宿舍",
    },
    # === 学习 ===
    {
        "author_student_id": "20260903001",
        "title": "数据科学与大数据专业大一有哪些必修课？",
        "content": "我是数据科学专业的新生，想知道大一的课表大概是什么样的。有没有特别难的课需要提前预习的？另外，英语分班考试大概什么时候考？",
        "category": "学习",
    },
    {
        "author_student_id": "20260901001",
        "title": "图书馆可以占座吗？自习室需要预约吗？",
        "content": "听说牧院图书馆很大，想问一下平时自习需要预约座位吗？可以隔夜占座吗？有没有通宵自习室？另外图书馆的计算机可以随便用吗？",
        "category": "学习",
    },
    {
        "author_student_id": "20260902001",
        "title": "计算机二级和英语四级大一下就要求过吗？",
        "content": "我们学校对计算机二级和英语四级有硬性要求吗？是不是大一就得开始准备？求过来的学长学姐分享一下备考经验和推荐资料～",
        "category": "学习",
    },
    # === 生活 ===
    {
        "author_student_id": "20260904001",
        "title": "学校有几个食堂？哪个食堂最好吃？",
        "content": "想提前了解一下学校的伙食！听说不同校区的食堂水平不一样，求各位学长学姐推荐北苑附近好吃的窗口。另外食堂支持微信/支付宝吗，还是必须用校园卡？",
        "category": "生活",
    },
    {
        "author_student_id": "20260904001",
        "title": "校园卡怎么充值？丢了怎么办？",
        "content": "刚拿到的校园卡上面有余额吗？怎么充值会比较方便，有没有线上充值的渠道？万一不小心丢了在哪里补办？",
        "category": "生活",
    },
    {
        "author_student_id": "20260901001",
        "title": "牧院周边有什么好玩的地方吗？",
        "content": "周末想出去逛逛，学校附近有没有好吃的街或者好玩的地方？去市区远不远，坐几路公交能到？听说龙子湖附近有很多学校，那边热闹吗？",
        "category": "生活",
    },
    # === 社团 ===
    {
        "author_student_id": "20260902001",
        "title": "新生什么时候可以加社团？有什么社团推荐？",
        "content": "想加入学生会或者一些兴趣社团，不知道什么时候开始招新。有经验的学长学姐能推荐一下牧院比较好的社团吗？我对摄影和编程比较感兴趣～",
        "category": "社团",
    },
    {
        "author_student_id": "20260903001",
        "title": "加入两个社团会不会太忙？时间怎么分配？",
        "content": "大一课程好像不算太少，如果同时加入两个社团的话能兼顾得来吗？社团活动一般都在什么时间段？影响晚自习吗？",
        "category": "社团",
    },
    # === 其他 ===
    {
        "author_student_id": "20260903001",
        "title": "军训一般多久？有什么要注意的？",
        "content": "听说我们学校军训挺严格的，一般军训几天？是大一开学就训还是等一段时间？需要自己准备防晒霜和厚鞋垫吗？求过来人给点建议！",
        "category": "其他",
    },
    {
        "author_student_id": "20260904001",
        "title": "校医院看病方便吗？在手机上预约可以吗？",
        "content": "想问一下校医院的位置在哪里，小感冒之类的去看方便吗？需要带什么证件？可以刷医保吗？另外学校周围有大一点的医院吗？",
        "category": "其他",
    },
]


def main():
    db = SessionLocal()
    try:
        # 查询所有可用学生
        rows = db.execute(
            text("SELECT id, student_id, name, class_name FROM students ORDER BY id")
        ).fetchall()
        student_map = {r[1]: {"id": r[0], "name": r[2], "class_name": r[3]} for r in rows}
        print(f"可用学生: {len(student_map)} 人")

        created = 0
        now = datetime.now(timezone.utc)

        for i, p in enumerate(POSTS_REAL):
            sid = p["author_student_id"]
            if sid not in student_map:
                print(f"  ⚠ 跳过: student_id={sid} 不在库中")
                continue

            student = student_map[sid]
            post = ForumPost(
                id=uuid4(),
                author_id=student["id"],
                title=p["title"],
                content=p["content"],
                category=p["category"],
                answer_count=0,
                has_accepted=False,
                is_closed=False,
                is_pinned=False,
                is_hidden=False,
                like_count=random.randint(0, 8),
                view_count=random.randint(10, 200),
                created_at=now - timedelta(minutes=random.randint(10, 60 * 24 * 3)),
            )
            db.add(post)
            created += 1
            print(f"  ✓ [{p['category']}] {p['title'][:30]}... — by {student['name']}")

        db.commit()
        print(f"\n✅ 成功插入 {created} 条论坛帖子")

        # 统计
        total = db.execute(text("SELECT count(*) FROM forum_posts")).scalar()
        print(f"📊 论坛帖子总数: {total}")
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}", file=sys.stderr)
    finally:
        db.close()


if __name__ == "__main__":
    main()
