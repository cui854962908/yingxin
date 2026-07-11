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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_HOURS: int = 168
    #: SHA-256 加盐哈希的盐值，用于存储身份证号哈希（三要素验证的第三个因子）
    ID_NUMBER_SALT: str = "yingxin-default-salt-change-in-production"
    # 若为 false（默认）：不挂载 /docs、/redoc、/openapi.json，避免匿名浏览完整 API 定义
    EXPOSE_API_DOCS: bool = False
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    # 可选：正则匹配 Origin（如局域网 IP 访问前端时 `http://192.168.1.5:5173`）。留空则只用 BACKEND_CORS_ORIGINS。
    BACKEND_CORS_ORIGIN_REGEX: Optional[str] = None
    AMAP_WEB_KEY: str = ""
    AMAP_SECURITY_JS_CODE: str = ""

    # --- 智能助手（Agent）---
    FAQ_MATCH_MIN_SCORE: float = 8.0
    #: 为 true 时在请求结束后打印 [agent_perf]（仅 POST /api/agent/chat）
    AGENT_PERF_LOG: bool = False

    # --- 小信 SSE：`POST /api/chat`（DeepSeek 对话 + 远端嵌入）---
    #: 若为 false，`POST /api/chat` 返回 503
    XIAOXIN_CHAT_ENABLED: bool = True

    # --- DeepSeek API（对话生成）---
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_CHAT_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_CHAT_TIMEOUT_SECONDS: float = 120.0

    # --- 嵌入模型（远端 API，OpenAI 兼容）---
    #: 远端嵌入 API Key（如 SiliconFlow）
    EMBED_API_KEY: str = ""
    #: 远端嵌入 API 地址（如 https://api.siliconflow.cn/v1）
    EMBED_API_BASE_URL: str = "https://api.siliconflow.cn/v1"
    #: 远端嵌入模型名（如 BAAI/bge-m3）
    EMBED_MODEL: str = "BAAI/bge-m3"
    #: 远端嵌入超时秒数
    EMBED_TIMEOUT_SECONDS: float = 30.0

    #: 余弦相似度阈值（embedding 归一化后点积）
    DOCUMENT_COSINE_THRESHOLD: float = 0.6
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

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def _positive_minutes(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
