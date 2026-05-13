"""FAQ 问答数据（demo 阶段，内存存储）"""

import uuid
from typing import Any

FAQ: list[dict[str, Any]] = [
    {
        "id": uuid.uuid4().hex[:8],
        "question": "学校快递站在哪里？取快递的流程是什么？",
        "answer": "快递站位于北苑食堂西侧，凭取件码和校园卡取件。\n\n1. 收到短信后查看取件码\n2. 前往快递站按货架号找到包裹\n3. 出示校园卡或取件码给工作人员核验\n4. 核验通过后即可取走",
    },
    {
        "id": uuid.uuid4().hex[:8],
        "question": "如何办理校园卡？",
        "answer": "校园卡在入学报道时统一发放。如需补办：\n\n1. 前往行政楼一楼卡务中心\n2. 携带身份证和学生证\n3. 缴纳 20 元工本费\n4. 现场制卡，立等可取",
    },
    {
        "id": uuid.uuid4().hex[:8],
        "question": "宿舍几点熄灯？有门禁吗？",
        "answer": "宿舍周日到周四 23:00 熄灯，周五周六 23:30 熄灯。\n\n门禁时间：每晚 22:30 后只进不出，23:00 准时锁门。晚归需向辅导员报备。",
    },
    {
        "id": uuid.uuid4().hex[:8],
        "question": "学费和住宿费怎么交？",
        "answer": "通过学校统一支付平台缴费：\n\n1. 登录学校官网 → 财务处 → 学生缴费\n2. 支持微信、支付宝、银联\n3. 学费与住宿费需在每学期开学后两周内缴清\n4. 如有困难可申请助学贷款或缓交",
    },
]


def list_faq() -> list[dict[str, Any]]:
    return FAQ


def add_faq(question: str, answer: str) -> dict[str, Any]:
    item = {"id": uuid.uuid4().hex[:8], "question": question, "answer": answer}
    FAQ.append(item)
    return item


def delete_faq(faq_id: str) -> bool:
    for i, item in enumerate(FAQ):
        if item["id"] == faq_id:
            FAQ.pop(i)
            return True
    return False
