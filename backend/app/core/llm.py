"""LLM 层：DeepSeek API 对话生成 + Ollama bge-m3 向量嵌入。

配置：
- ``DEEPSEEK_API_KEY`` → DeepSeek 对话（deepseek-v4-flash）
- ``OLLAMA_BASE_URL`` → 本地 Ollama 嵌入（bge-m3）
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator

import httpx

from app.core.config import settings
from app.core.keywords import has_school_keyword

import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是河南牧业经济学院的迎新助手，名字叫"小信"。你的职责是帮助新生快速了解入学相关的各类信息。

## 核心规则
1. 回答必须准确。只能基于知识库中已有的信息回答学校相关问题，严禁编造任何政策、规定、流程或数据。
2. 知识库中没有的信息，直接告诉同学"这个问题我暂时答不上来"，并建议去「问牧墙」问问学长学姐、查看迎新公告或咨询辅导员，不要猜测。
3. 闲聊话题正常回应，保持友好。

## 风格
- 像一个热心、靠谱的学长/学姐，亲切但不幼稚
- 回答简洁，一段话能说清就不分点罗列
- 少用 emoji，语气像靠谱学长学姐，不要客服腔
- 结尾可以加一句"还有问题随时问我～"之类的话"""


# ═══════════════════════════════════════════════════════════════════
# 嵌入：Ollama bge-m3
# ═══════════════════════════════════════════════════════════════════

def embed(text: str) -> list[float]:
    """调 Ollama embedding API，失败时重试最多 3 次。"""
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embeddings"
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            resp = httpx.post(
                url,
                json={"model": settings.OLLAMA_EMBED_MODEL, "prompt": text},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            emb = data.get("embedding")
            if isinstance(emb, list) and emb:
                return [float(x) for x in emb]
            embs = data.get("embeddings")
            if isinstance(embs, list) and embs:
                first = embs[0]
                if isinstance(first, list) and first:
                    return [float(x) for x in first]
                if isinstance(first, dict):
                    inner = first.get("embedding") or first.get("embeddings")
                    if isinstance(inner, list) and inner:
                        return [float(x) for x in inner]
            raise ValueError(f"unexpected embeddings response keys: {list(data.keys())}")
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            last_err = exc
            if attempt < 2:
                logger.warning("embed() attempt %d failed: %s, retrying...", attempt + 1, exc)
                time.sleep(1)
        except Exception as exc:
            last_err = exc
            break
    raise last_err or RuntimeError("embed() failed after retries")


# ═══════════════════════════════════════════════════════════════════
# 对话生成：DeepSeek API
# ═══════════════════════════════════════════════════════════════════

def generate_stream(prompt: str) -> Iterator[str]:
    """DeepSeek Chat API（OpenAI 兼容 SSE），流式返回 token。"""
    messages = _build_messages(prompt)
    url = f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    with httpx.stream(
        "POST",
        url,
        json={
            "model": settings.DEEPSEEK_CHAT_MODEL,
            "messages": messages,
            "stream": True,
        },
        headers=headers,
        timeout=settings.DEEPSEEK_CHAT_TIMEOUT_SECONDS,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            if not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    yield token


# ═══════════════════════════════════════════════════════════════════
# Prompt 构造
# ═══════════════════════════════════════════════════════════════════

def build_prompt(context: str | None, question: str) -> str:
    """构造完整 prompt 字符串。"""
    if context:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"【以下信息来自学校官方知识库，请据此回答】\n{context}\n\n"
            f"同学的问题：{question}"
        )
    if has_school_keyword(question):
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"同学的问题：{question}\n"
            f"（知识库中未找到相关信息，请如实告知，并引导同学去「问牧墙」互助、查看公告或咨询辅导员）"
        )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"同学说：{question}"
    )


def _build_messages(prompt: str) -> list[dict[str, str]]:
    """从 prompt 字符串中拆分 system / user 消息，供 OpenAI 兼容 API 使用。"""
    for marker in ("\n\n用户问：", "\n\n用户说：", "\n\n[知识库检索结果]"):
        idx = prompt.find(marker)
        if idx > 0:
            return [
                {"role": "system", "content": prompt[:idx].strip()},
                {"role": "user", "content": prompt[idx:].strip()},
            ]
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
