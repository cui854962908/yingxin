"""小信引导链接（问牧墙联动）单元测试。"""

from app.services.xiaoxin_chat_service import _links_for_fallback, _links_for_kb


def test_links_for_fallback_prioritizes_wall():
    links = _links_for_fallback()
    assert len(links) == 3
    assert links[0]["to"] == "/wall"
    assert "问牧墙" in links[0]["label"]


def test_links_for_kb_unchanged():
    links = _links_for_kb()
    assert len(links) == 2
    assert all(l["to"] in ("/faq", "/announcements") for l in links)
