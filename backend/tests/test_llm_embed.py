"""测试嵌入函数：远端 API（OpenAI 兼容格式）。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from httpx import HTTPStatusError, Request, Response

from app.core.llm import embed


def _mock_response(status: int, json_data: dict) -> MagicMock:
    resp = MagicMock(spec=Response)
    resp.status_code = status
    resp.json.return_value = json_data
    if status >= 400:
        resp.raise_for_status.side_effect = HTTPStatusError(
            "error", request=MagicMock(spec=Request), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


class TestEmbed:
    def test_returns_embedding_from_openai_compatible_response(self, monkeypatch):
        """解析 OpenAI 兼容格式 {data: [{embedding: [...]}]}。"""
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_KEY", "sk-test")
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_BASE_URL", "https://api.example.com/v1")
        monkeypatch.setattr("app.core.llm.settings.EMBED_MODEL", "test-model")
        monkeypatch.setattr("app.core.llm.settings.EMBED_TIMEOUT_SECONDS", 10.0)

        mock_resp = _mock_response(200, {"data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}]})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            result = embed("测试文本")

        assert result == [0.1, 0.2, 0.3]
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "test-model"
        assert call_args[1]["json"]["input"] == "测试文本"
        assert "Authorization" in call_args[1]["headers"]

    def test_raises_on_unexpected_response(self, monkeypatch):
        """响应格式异常时抛出 ValueError。"""
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_KEY", "sk-test")
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_BASE_URL", "https://api.example.com/v1")
        monkeypatch.setattr("app.core.llm.settings.EMBED_MODEL", "test-model")
        monkeypatch.setattr("app.core.llm.settings.EMBED_TIMEOUT_SECONDS", 10.0)

        mock_resp = _mock_response(200, {"unexpected": "format"})
        with patch("httpx.post", return_value=mock_resp):
            with pytest.raises(ValueError):
                embed("test")

    def test_raises_on_http_error(self, monkeypatch):
        """HTTP 错误直接传播。"""
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_KEY", "sk-test")
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_BASE_URL", "https://api.example.com/v1")
        monkeypatch.setattr("app.core.llm.settings.EMBED_MODEL", "test-model")
        monkeypatch.setattr("app.core.llm.settings.EMBED_TIMEOUT_SECONDS", 10.0)

        mock_resp = _mock_response(401, {"error": "unauthorized"})
        with patch("httpx.post", return_value=mock_resp):
            with pytest.raises(HTTPStatusError):
                embed("test")

    def test_url_construction(self, monkeypatch):
        """验证 API 地址拼接正确。"""
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_KEY", "sk-test")
        monkeypatch.setattr("app.core.llm.settings.EMBED_API_BASE_URL", "https://api.siliconflow.cn/v1")
        monkeypatch.setattr("app.core.llm.settings.EMBED_MODEL", "BAAI/bge-m3")
        monkeypatch.setattr("app.core.llm.settings.EMBED_TIMEOUT_SECONDS", 30.0)

        mock_resp = _mock_response(200, {"data": [{"embedding": [1.0], "index": 0}]})
        with patch("httpx.post", return_value=mock_resp) as mock_post:
            embed("hello")

        url = mock_post.call_args[0][0]
        assert url == "https://api.siliconflow.cn/v1/embeddings"
        assert mock_post.call_args[1]["json"]["model"] == "BAAI/bge-m3"
