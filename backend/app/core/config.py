"""应用配置 — 环境变量集中管理"""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/yingxin",
)
JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "yingxin-dev-secret-key-change-in-production",
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
).split(",")
