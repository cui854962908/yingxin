# 迎新系统 (YingXin)

河南牧业经济学院 **2026 级新生迎新门户**。

## 产品定位

**认识牧院 · 指导报到 · 智能答疑**

面向 2026 级新生与家长：帮助了解学校与学院、准备报到入学，并通过 FAQ、小信 AI 与问牧墙获取答疑与互助。

| 能力 | 说明 |
|------|------|
| 认识牧院 | 牧院大百科、学院介绍、社团文化（游客可浏览） |
| 报到指导 | 报到须知、新生攻略、校园导览 |
| 答疑互助 | FAQ、小信 AI、问牧墙 |

**边界：** 不是学籍/名册管理系统。学生名单由运维脚本导入；Web 端做身份校验、个人报到信息展示与内容维护。

完整说明见 [CONTEXT.md](CONTEXT.md) §1.1。

## 快速启动

```bash
docker compose up -d
```

## 项目画像

详见 [CONTEXT.md](CONTEXT.md) — 规模参数、技术栈、模块说明、工程原则。

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
