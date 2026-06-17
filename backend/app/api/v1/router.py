"""小信相关 API 聚合（HOUDAUN(3).md §4.1 子集）：仅挂载 chat / tts。"""

from fastapi import APIRouter

from app.api.v1 import chat as chat_router
from app.api.v1 import tts as tts_router

api_router = APIRouter(prefix="/api")
api_router.include_router(chat_router.router, tags=["chat"])
api_router.include_router(tts_router.router, tags=["tts"])
