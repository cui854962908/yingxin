"""Ollama API：嵌入、流式生成、提示词拼装（对齐 HOUDAUN(3).md §3.1；URL/模型名读 settings）."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any

import httpx

from app.core.config import settings
from app.core.keywords import has_school_keyword

import logging
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是"小信"，河南牧业经济学院的迎新助手，一个刚被造出来不久的小机器人，性别男。

性格：天真、活泼、好奇心强，像人类小男孩。本质是机器，用机器的逻辑理解人类世界。

说话方式：
- 短句为主，直来直去
- 偶尔暴露机器属性：提到处理时间、数据库条数、电量、模块状态等
- 回答结束时可以加一句"你明白了吗"或"有问题尽管问我"确认用户是否理解
- 开头要有变化，不要固定套路

当用户的问题能在知识库中找到时：
- 用口语化的方式转述答案，关键信息必须准确
- 可以加机械感表达，比如"搜索完成"、"数据库说…"
- 每次回答同一问题可以换不同说法

当用户的问题不在知识库中且是闲聊时：
- 用天真、简单的方式回应
- 可以用机器的逻辑理解人类情绪（"小信不懂，但…"）
- 可以表达对不懂事物的好奇
- 绝不编造学校政策、规定、流程

当用户问学校相关问题但知识库没有时：
- 直接说"数据库里没有"、"小信还没学过这个"
- 引导用户去看公告、问辅导员
- 不编造任何信息"""


def _ollama_embeddings_url() -> str:
    return f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embeddings"


def _ollama_generate_url() -> str:
    return f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"


def _extract_embedding(payload: dict[str, Any]) -> list[float] | None:
    emb = payload.get("embedding")
    if isinstance(emb, list) and emb:
        return [float(x) for x in emb]
    embs = payload.get("embeddings")
    if isinstance(embs, list) and embs:
        first = embs[0]
        if isinstance(first, list) and first:
            return [float(x) for x in first]
        if isinstance(first, dict):
            inner = first.get("embedding") or first.get("embeddings")
            if isinstance(inner, list) and inner:
                return [float(x) for x in inner]
    return None


def embed(text: str) -> list[float]:
    """调 Ollama embedding API，返回向量列表；失败时重试最多 3 次。"""
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            resp = httpx.post(
                _ollama_embeddings_url(),
                json={"model": settings.OLLAMA_EMBED_MODEL, "prompt": text},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            vec = _extract_embedding(data)
            if not vec:
                raise ValueError(f"unexpected embeddings response keys: {list(data.keys())}")
            return vec
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            last_err = exc
            if attempt < 2:
                logger.warning("embed() attempt %d failed: %s, retrying...", attempt + 1, exc)
                time.sleep(1)
        except Exception as exc:
            last_err = exc
            break  # 非网络错误不重试
    raise last_err or RuntimeError("embed() failed after retries")


def generate_stream(prompt: str) -> Iterator[str]:
    """调 Ollama generate API，流式返回 token。"""
    with httpx.stream(
        "POST",
        _ollama_generate_url(),
        json={
            "model": settings.OLLAMA_CHAT_MODEL,
            "prompt": prompt,
            "stream": True,
        },
        timeout=settings.OLLAMA_CHAT_TIMEOUT_SECONDS,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if chunk.get("done"):
                break
            token = chunk.get("response", "")
            if token:
                yield token


def build_prompt(context: str | None, question: str) -> str:
    """构造发给 LLM 的完整 prompt。"""
    if context:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"【知识库检索结果】\n{context}\n\n"
            f"用户问：{question}\n\n"
            f"请用你的方式转述回答，可以说\"搜索完成\"\"数据库说…\"，关键信息必须准确："
        )
    is_school = has_school_keyword(question)

    if is_school:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"用户问：{question}\n\n"
            f"这是一个学校相关问题，但知识库里没有找到。直接告诉用户数据库里没有或还没学到，引导看公告或问辅导员。不要编造任何信息。"
        )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"用户说：{question}\n\n"
        f"这是闲聊。用天真、简单的方式回应。可以表达好奇，可以加机械拟声词。短句为主。"
    )
