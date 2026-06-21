import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import agent, announcements, auth, clubs, faq, forum

# ── Agent fallback 日志：记录小信未回答上来的问题，供运维补充知识库 ──
_log_dir = Path("logs")
_log_dir.mkdir(exist_ok=True)
_fallback_handler = RotatingFileHandler(
    _log_dir / "agent_fallback.log",
    maxBytes=10 * 1024 * 1024,  # 单文件 10MB
    backupCount=3,
    encoding="utf-8",
)
_fallback_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
_fallback_logger = logging.getLogger("app.agent.fallback")
_fallback_logger.setLevel(logging.INFO)
_fallback_logger.addHandler(_fallback_handler)
_fallback_logger.propagate = False  # 不重复输出到控制台

from app.api.v1.router import api_router as v1_api_router
from app.core.config import settings
from app.core.http_middleware import SecurityHeadersMiddleware, UploadSizeMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.core.settings_guard import validate_settings
from app.core.security import get_current_payload

_docs_url = "/docs" if settings.EXPOSE_API_DOCS else None
_redoc_url = "/redoc" if settings.EXPOSE_API_DOCS else None
_openapi_url = "/openapi.json" if settings.EXPOSE_API_DOCS else None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    validate_settings(settings)
    yield


app = FastAPI(
    title="河南牧业经济学院迎新门户",
    version="0.1.0",
    description="迎新系统后端（FastAPI + PostgreSQL），业务接口统一以 `/api` 为前缀。",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
    lifespan=lifespan,
)

# Starlette 后注册的先执行。请求顺序：CORS → RateLimit → UploadSize → SecurityHeaders
# CORS 保持最外层，429/413 等提前返回的响应仍经 CORSMiddleware 带上跨域头
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(UploadSizeMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def agent_perf_logging_middleware(request: Request, call_next):
    if (
        settings.AGENT_PERF_LOG
        and request.url.path == "/api/agent/chat"
        and request.method == "POST"
    ):
        request.state.agent_perf = {}
    response = await call_next(request)
    perf = getattr(request.state, "agent_perf", None)
    if perf and settings.AGENT_PERF_LOG:
        keys = (
            "jwt",
            "domain",
            "privacy_gate",
            "student_agent",
            "faq_db_or_cache",
            "faq_match",
            "xiaoxin_rag",
            "embedding",
            "vector_search",
            "route_body",
        )
        msg = " ".join(f"{k}={perf.get(k, 0)}s" for k in keys)
        logging.getLogger("app.agent").info("[agent_perf] %s", msg)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    message = detail if isinstance(detail, str) else "请求失败"
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": message, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数校验失败",
            "data": exc.errors(),
        },
    )


app.include_router(v1_api_router)
app.include_router(agent.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(faq.router_public, prefix="/api")
app.include_router(faq.router_admin, prefix="/api")
app.include_router(announcements.router_public, prefix="/api")
app.include_router(announcements.router_admin, prefix="/api")
app.include_router(clubs.router_public, prefix="/api")
app.include_router(clubs.router_admin, prefix="/api")
app.include_router(forum.router_public, prefix="/api")
app.include_router(forum.router_admin, prefix="/api")

# 静态文件 — 上传的社团图片等
_static_dir = Path("static")
_static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


@app.get("/health")
def health(_: dict = Depends(get_current_payload)):
    """存活探测；需与业务接口相同方式携带 JWT，避免匿名推断服务状态。"""
    return {"status": "ok"}


_root = APIRouter()


@_root.get("/", include_in_schema=False)
def root_no_info():
    """根路径不返回业务数据；匿名访问仅得 404。"""
    raise HTTPException(status_code=404, detail="Not Found")


app.include_router(_root)
