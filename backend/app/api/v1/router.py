"""API v1 路由聚合"""

from fastapi import APIRouter

from app.api.v1 import auth, students, faq, announcements

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(students.router, tags=["students"])
api_router.include_router(faq.router, tags=["faq"])
api_router.include_router(announcements.router, tags=["announcements"])
