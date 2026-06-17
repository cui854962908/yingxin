"""Agent 核心链路测试：domain → privacy → FAQ → fallback（不依赖 LLM）。"""
import pytest
from sqlalchemy.orm import Session

from app.services.agent_service import route_chat_async
from app.services.student_agent_service import (
    student_gate_response,
    is_personal_status_question,
    mentions_other_person,
)
from app.services.faq_service import find_best_faq, normalize_text, FaqMatch
from app.core.keywords import is_domain_related
from app.models.faq import FAQ


# ── 域检测 ──

@pytest.mark.parametrize("text,expected", [
    ("宿舍在哪里", True),
    ("怎么报到", True),
    ("校园卡怎么领", True),
    ("今天天气怎么样", False),
    ("你好", False),
    ("", False),
])
def test_is_domain_related(text: str, expected: bool):
    assert is_domain_related(text) is expected


# ── 隐私闸 / 个人状态 ──

@pytest.mark.parametrize("text,expected", [
    ("同学的宿舍在哪", True),
    ("李明的电话多少", True),
    ("别人的缴费状态", True),
    ("我的宿舍在哪", False),
    ("怎么报到", False),
])
def test_mentions_other_person(text: str, expected: bool):
    assert mentions_other_person(text) is expected


@pytest.mark.parametrize("text,expected", [
    ("我的宿舍在哪", True),
    ("我缴费了吗", True),
    ("我的报到进度", True),
    ("怎么报到", False),
    ("快递站在哪", False),
])
def test_is_personal_status_question(text: str, expected: bool):
    assert is_personal_status_question(text) is expected


def test_student_gate_privacy_other():
    reply, intent, source = student_gate_response(
        message="同学的宿舍在哪",
        is_authenticated=True,
        current_student_id="20260901001",
        role="student",
    )
    assert reply is not None and "隐私" in reply
    assert intent == "privacy"


def test_student_gate_unauthenticated_personal():
    reply, intent, source = student_gate_response(
        message="我的宿舍在哪",
        is_authenticated=False,
        current_student_id=None,
        role="anonymous",
    )
    assert reply is not None and "登录" in reply
    assert intent == "dorm"


def test_student_gate_admin_personal():
    reply, intent, source = student_gate_response(
        message="我的宿舍在哪",
        is_authenticated=True,
        current_student_id="admin",
        role="admin",
    )
    assert reply is not None and "管理员" in reply


def test_student_gate_pass_through():
    reply, intent, source = student_gate_response(
        message="我的宿舍在哪",
        is_authenticated=True,
        current_student_id="20260901001",
        role="student",
    )
    assert reply is None


# ── FAQ 匹配 ──

def test_normalize_text():
    assert normalize_text("  Hello   World！？  ") == "helloworld"


def test_find_best_faq_hit(db: Session):
    faq = FAQ(question="宿舍在哪里查询？", answer="登录后点击'个人档案'查看。")
    db.add(faq)
    db.commit()

    result = find_best_faq(db, "我的宿舍在哪查")
    assert result is not None
    assert result.faq.question == "宿舍在哪里查询？"
    assert result.score > 0


def test_find_best_faq_miss(db: Session):
    faq = FAQ(question="如何取快递？", answer="北苑菜鸟驿站。")
    db.add(faq)
    db.commit()

    result = find_best_faq(db, "宇宙有多大")
    assert result is None


# ── Agent 编排（不含 RAG / DeepSeek 路径）──

@pytest.mark.asyncio
async def test_route_chat_empty(db: Session):
    out = await route_chat_async(db=db, message="")
    assert out["source"] == "validation"
    assert "请输入" in out["reply"]


@pytest.mark.asyncio
async def test_route_chat_greeting(db: Session):
    for g in ("你好", "在吗", "早上好"):
        out = await route_chat_async(db=db, message=g)
        assert out["source"] == "greeting", f"greeting={g!r} → {out}"


@pytest.mark.asyncio
async def test_route_chat_irrelevant(db: Session):
    out = await route_chat_async(db=db, message="今天天气怎么样")
    assert out["source"] == "irrelevant"


@pytest.mark.asyncio
async def test_route_chat_faq_hit(db: Session):
    faq = FAQ(question="宿舍在哪里查询？", answer="登录后点击'个人档案'查看。")
    db.add(faq)
    db.commit()

    out = await route_chat_async(
        db=db,
        message="宿舍在哪查",
        is_authenticated=True,
        current_student_id="20260901001",
        role="student",
    )
    assert out["source"] == "faq"
    assert "个人档案" in out["reply"]


@pytest.mark.asyncio
async def test_route_chat_privacy_block(db: Session):
    out = await route_chat_async(
        db=db,
        message="同学的宿舍在哪",
        is_authenticated=True,
        current_student_id="20260901001",
        role="student",
    )
    assert out["source"] == "privacy" or out["source"] == "student_agent"
    assert "隐私" in out["reply"]


@pytest.mark.asyncio
async def test_route_chat_faq_before_rag(db: Session):
    """FAQ 命中时不应走到 RAG 路径。"""
    faq = FAQ(question="快递站在哪里？", answer="北苑菜鸟驿站，南苑京东快递柜。")
    db.add(faq)
    db.commit()

    out = await route_chat_async(db=db, message="快递站在哪")
    assert out["source"] == "faq"
    assert "菜鸟" in out["reply"]
