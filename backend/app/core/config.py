from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    #: SQLAlchemy → psycopg 的 connect_timeout（秒）。Docker 刚就绪或宿主机较慢时可调大（环境变量 DATABASE_CONNECT_TIMEOUT）
    DATABASE_CONNECT_TIMEOUT: int = 60
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    # 若为 false（默认）：不挂载 /docs、/redoc、/openapi.json，避免匿名浏览完整 API 定义
    EXPOSE_API_DOCS: bool = False
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    # 可选：正则匹配 Origin（如局域网 IP 访问前端时 `http://192.168.1.5:5173`）。留空则只用 BACKEND_CORS_ORIGINS。
    BACKEND_CORS_ORIGIN_REGEX: Optional[str] = None

    # --- 智能助手（Agent）---
    EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_PROVIDER: str = "none"
    VECTOR_DISTANCE_THRESHOLD: float = 0.55
    FAQ_MATCH_MIN_SCORE: float = 8.0
    #: 为 true 时在请求结束后打印 [agent_perf]（仅 POST /api/agent/chat）
    AGENT_PERF_LOG: bool = False

    # --- 小信 SSE：`POST /api/chat`（Ollama + documents 余弦检索）---
    #: 若为 false，`POST /api/chat` 返回 503（便于未安装 Ollama 的环境）
    XIAOXIN_CHAT_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_EMBED_MODEL: str = "bge-m3:latest"
    OLLAMA_CHAT_MODEL: str = "qwen2.5:1.5b-instruct-q4_K_M"
    #: 余弦相似度阈值（embedding 归一化后点积）；与计划中「最高分 > 0.6」一致
    DOCUMENT_COSINE_THRESHOLD: float = 0.6
    #: Ollama HTTP 超时（生成可能较慢）
    OLLAMA_CHAT_TIMEOUT_SECONDS: float = 120.0
    #: Edge-TTS 普通话晓伊音色
    EDGE_TTS_VOICE: str = "zh-CN-XiaoyiNeural"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @field_validator("BACKEND_CORS_ORIGIN_REGEX", mode="before")
    @classmethod
    def _cors_regex_strip(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return str(v)

    @field_validator("ACCESS_TOKEN_EXPIRE_HOURS")
    @classmethod
    def _positive_hours(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_HOURS must be positive")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
