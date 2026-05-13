# 迎新系统 (YingXin)

> 学校 2026 年 9 月招新迎新网页系统

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite
- **后端**: FastAPI + Python 3.12+
- **数据库**: PostgreSQL 18
- **工具链**: uv + Git + Docker

## 项目结构

```
yingxin/
├── backend/           # FastAPI 后端
│   ├── app/           # 应用代码
│   │   ├── api/       # API 路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据库模型
│   │   └── schemas/   # Pydantic 模型
│   ├── tests/         # 测试
│   └── pyproject.toml # Python 项目配置
├── frontend/          # Vue 3 前端
│   └── src/           # 源代码
└── docker/            # Docker 配置
```

## 快速启动

```bash
# 后端
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev

# 浏览器访问 http://localhost:5173
```
