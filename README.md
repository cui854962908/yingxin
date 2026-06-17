# 迎新系统 (YingXin)

河南牧业经济学院新生迎新 Web 应用。新生登录后查看公告、FAQ、社团信息、个人报到信息，内置「小信」AI 助手提供智能问答。

## 快速启动

```bash
docker compose up -d
```

## 项目画像

详见 [CONTEXT.md](CONTEXT.md) — 包含规模参数、技术栈、项目结构、核心功能、工程原则。

## 运维

部署和接口文档见 `rizhi/` 目录：
- `rizhi/yunwei.md` — 部署说明
- `rizhi/jieshao.md` — 文档索引（API 见 `backend/docs/FRONTEND_API.md`）
- `rizhi/xiugairizhi-*.md` — 修改日志

## 开发

```bash
# 后端
cd backend && uv run uvicorn app.main:app --reload

# 前端
cd frontend && npm run dev

# 测试
cd backend && uv run pytest
cd frontend && npx vitest run
```
