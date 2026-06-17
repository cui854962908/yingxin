"""统一校园关键词表，供 agent 路由与 llm 模块共用。"""

SCHOOL_KEYWORDS = (
    "迎新",
    "新生",
    "报到",
    "签到",
    "入学",
    "学校",
    "校园",
    "系统",
    "宿舍",
    "寝室",
    "缴费",
    "学费",
    "住宿费",
    "教材",
    "教材费",
    "校园卡",
    "军训",
    "通知",
    "公告",
    "辅导员",
    "志愿者",
    "网上",
    "线上",
    "现场",
    "材料",
    "档案",
    "密码",
    "登录",
    "账号",
    "钥匙",
    "物资",
    "领取",
    "个人信息",
    "填错",
    "修改",
    "地点",
    "流程",
    "常见问题",
    "faq",
    "FAQ",
    "图书馆",
    "借书",
    "借书证",
    "开学",
    "快递",
    "选课",
    "课程",
    "专业",
    "学院",
    "报道",
    "毕业",
    "考试",
    "成绩",
    "奖学金",
    "助学",
    "贷款",
    "校",
    "老师",
    "学生",
    "上课",
    "放假",
    "安排",
    "体检",
    "服装",
    "行政",
    "食堂",
    "教室",
    "班主任",
    "代班",
    "班助",
)


def is_domain_related(message: str) -> bool:
    """返回 True 表示消息与迎新/校园相关。"""
    m = message.strip()
    if not m:
        return False
    return any(t.lower() in m.lower() if t.isascii() else t in m for t in SCHOOL_KEYWORDS)


def has_school_keyword(question: str) -> bool:
    """返回 True 表示问题包含学校相关关键词（供 LLM prompt 构造使用）。"""
    return any(kw in question for kw in SCHOOL_KEYWORDS)
