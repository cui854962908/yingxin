"""
学生专属问答：依赖 JWT（sub=学号）；禁止信任前端传来的 student_id。
主库仅有 students 表内宿舍等字段，隐私闸与个人问题识别仍在此处集中处理。
"""

from __future__ import annotations

import re

_PRIVACY_OTHER = (
    "为保护学生隐私，我只能查询当前登录账号本人的迎新信息。"
    "其他同学的信息请通过本人账号查看，或联系学院老师确认。"
)

_ADMIN_PERSONAL = (
    "管理员账号无法通过迎新助手查询个人宿舍、缴费等信息，请使用管理后台学生管理功能。"
)

_LOGIN_HINT = (
    "请先登录迎新系统后再查询个人宿舍、缴费、报到进度或物资领取信息。"
)

_PERSONAL_MARKERS = ("我", "我的", "本人", "自己")

_DORM_TERMS = ("宿舍", "寝室", "住哪", "住宿", "床位", "房间", "宿舍楼")
_PAY_TERMS = ("缴费", "学费", "住宿费", "教材费", "费用", "交钱", "支付", "缴了吗", "交了没")
_CHECKIN_TERMS = ("报到", "签到", "完成了吗", "还差", "进度", "流程")
_MATERIAL_TERMS = ("校园卡", "军训服", "钥匙", "资料袋", "领取", "物资")

_OTHER_PEOPLE_MARKERS = (
    "同学",
    "别人",
    "他的",
    "她的",
    "他们",
    "室友",
    "某某",
    "学号",
    "手机号",
    "电话",
    "身份证",
)


def mentions_other_person(message: str) -> bool:
    m = message.strip()
    if not m:
        return False

    if re.search(r"(?:同学|室友|别人|他|她|他们).*(?:宿舍|缴费|手机|电话|身份证)", m):
        return True

    if re.search(r"[\u4e00-\u9fa5]{2,4}的(?:宿舍|寝室|缴费|手机号|电话|身份证)", m):
        return True

    if any(k in m for k in _OTHER_PEOPLE_MARKERS) and any(
        k in m for k in (*_DORM_TERMS, *_PAY_TERMS, "手机", "电话", "身份证")
    ):
        return True

    return False


def is_personal_status_question(message: str) -> bool:
    msg = message.strip()
    if not msg:
        return False

    personal = any(k in msg for k in _PERSONAL_MARKERS) or any(
        phrase in msg for phrase in ("完成了吗", "缴了吗", "在哪", "还差")
    )

    dorm_hit = any(k in msg for k in _DORM_TERMS)
    pay_hit = any(k in msg for k in _PAY_TERMS) or ("缴" in msg and ("吗" in msg or "没" in msg))
    checkin_hit = any(k in msg for k in _CHECKIN_TERMS)
    material_hit = any(k in msg for k in _MATERIAL_TERMS)

    if personal and (dorm_hit or pay_hit or checkin_hit or material_hit):
        return True

    if personal and ("报到" in msg or "签到" in msg) and ("吗" in msg or "没" in msg or "完成" in msg):
        return True

    return False


def classify_personal_intent(message: str) -> str:
    m = message
    if any(k in m for k in _DORM_TERMS):
        return "dorm"
    if any(k in m for k in _PAY_TERMS):
        return "payment"
    if any(k in m for k in _MATERIAL_TERMS):
        return "material"
    if any(k in m for k in _CHECKIN_TERMS):
        return "checkin"
    return "unknown"


def student_gate_response(
    *,
    message: str,
    is_authenticated: bool,
    current_student_id: str | None,
    role: str,
) -> tuple[str | None, str | None, str | None]:
    """
    返回 (reply, intent, source)；无需拦截则 (None, None, None)。

    current_student_id:
      JWT sub（学号）；管理员为 admin 等。
    """
    if mentions_other_person(message):
        return _PRIVACY_OTHER, "privacy", "privacy"

    if not is_authenticated and is_personal_status_question(message):
        intent = classify_personal_intent(message)
        return _LOGIN_HINT, intent, "student_agent"

    if is_authenticated and role == "admin" and is_personal_status_question(message):
        return _ADMIN_PERSONAL, classify_personal_intent(message), "student_agent"

    _ = current_student_id
    return None, None, None
