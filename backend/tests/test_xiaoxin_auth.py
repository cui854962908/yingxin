"""小信 / TTS 登录门禁。"""

import pytest
from app.core.security import create_access_token


def test_chat_requires_auth(client):
    resp = client.post("/api/chat", json={"question": "校训是什么"})
    assert resp.status_code == 401


def test_chat_with_student_token(client):
    token = create_access_token(subject="20260901001", name="张三", role="student")
    resp = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "你好"},
    )
    # 503/502 表示 Ollama/DeepSeek 未就绪，但不应是 401
    assert resp.status_code != 401


def test_tts_requires_auth(client):
    resp = client.post("/api/tts", json={"text": "你好"})
    assert resp.status_code == 401


def test_agent_requires_auth(client):
    resp = client.post("/api/agent/chat", json={"message": "你好"})
    assert resp.status_code == 401
