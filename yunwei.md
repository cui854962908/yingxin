# 迎新系统 — 运维部署指南

> 给运维人员：环境配置、数据库初始化、日常维护。接口契约见 `backend/docs/FRONTEND_API.md`；项目画像见根目录 `CONTEXT.md`。

---

## 一、部署前清理（可选）

开发机遗留物不必带上生产服务器：

```
删除  backend/.venv/          （部署环境需 uv sync 重建）
删除  backend/*backup*.sql    （开发期数据库备份，已在 .gitignore）
删除  backend/welcome_backend.egg-info/  （构建产物）
```

**保留** `backend/docs/` — 含 API 文档，运维/前端联调需要。

---

## 二、环境准备

### 2.1 依赖

```bash
cd backend
uv sync
```

前端生产构建：`cd frontend && npm ci && npm run build`

### 2.2 `.env` 配置

复制 `backend/.env.example` 为 `backend/.env`，至少填写：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接串（须含 pgvector） |
| `JWT_SECRET_KEY` | 生产环境替换为 ≥32 位随机串 |
| `DEEPSEEK_API_KEY` | 小信对话必填 |

**本机开发**（仅 DB 容器）：

```env
DATABASE_URL=postgresql+psycopg://welcome:welcome@127.0.0.1:5434/welcome_db
```

**Docker 全栈**（backend 容器内连 db 服务）：

```env
DATABASE_URL=postgresql+psycopg://welcome:welcome@db:5432/welcome_db
```

完整变量说明见 `backend/.env.example` 与 `backend/app/core/config.py`。

### 2.3 PostgreSQL + pgvector

**方式 A — 仅数据库（本机 dev）：**

```bash
cd backend
docker compose up -d
```

映射端口 `5434`，镜像 `pgvector/pgvector:pg16`。

**方式 B — 全栈：**

```bash
# 项目根目录
docker compose up -d
```

根 `docker-compose.yml` 已使用 pgvector 镜像，凭据与 `.env.example` 一致。

### 2.4 Ollama（向量嵌入）

小信 RAG 需要本地 Ollama 嵌入模型：

```bash
ollama pull bge-m3:latest
curl http://127.0.0.1:11434/api/tags   # 验证
```

对话生成走 **DeepSeek API**（`.env` 中 `DEEPSEEK_API_KEY`），**不需要**本地对话模型。

---

## 三、首次启动

```bash
cd backend

# 1. 数据库迁移
uv run alembic upgrade head

# 2. 种子数据（管理员 + 示例 FAQ/公告/社团 + 向量库重建）
uv run python scripts/init_db.py
```

若向量构建因 Ollama 未就绪而跳过，Ollama 启动后手动重建：

```bash
uv run python -c "from app.crud.document import rebuild_documents_best_effort; rebuild_documents_best_effort()"
```

**启动后端：**

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# 或 Windows 开发：.\scripts\start_backend.ps1
```

---

## 四、防火墙

```powershell
# Windows（管理员）
netsh advfirewall firewall add rule name="Yingxin Backend" dir=in action=allow protocol=tcp localport=8000
```

```bash
# Linux
sudo ufw allow 8000
```

---

## 五、日常运维

### 5.1 FAQ / 公告 / 社团变更

- **FAQ 快车**：管理员增删改 FAQ 后，服务端自动清进程内缓存，**无需**手动刷缓存接口。
- **向量库**：FAQ / 公告 / 社团变更后会异步 `incremental_embed_*`；若 Ollama 当时不可用，执行 §三 中的 `rebuild_documents_best_effort()`。

### 5.2 批量导入学生

Web 端与 API 均已移除学生名册管理。首次部署或本地演示请执行 `scripts/init_db.py` 写入管理员与示例学生；生产环境新生名单由运维在数据库侧维护（不经过本 Web）。

### 5.3 健康检查

```bash
curl http://localhost:8000/health
```

需 Bearer 时：`curl -H "Authorization: Bearer <token>" http://localhost:8000/health`

### 5.4 日志

FastAPI 默认 stdout；Docker 部署用 `docker compose logs -f backend`。

---

## 六、资源参考（8GB 服务器）

| 进程 | 预计内存 |
|------|----------|
| PostgreSQL | ~500MB |
| Ollama (bge-m3) | ~2GB |
| FastAPI | ~200MB |
| **合计** | **~2.7GB** |

DeepSeek 对话在云端，不占本地 GPU/大模型内存。8GB 服务器足够；建议预留 swap。

---

## 七、故障排查速查

| 现象 | 检查 |
|------|------|
| 迁移失败 `vector` 扩展 | DB 镜像是否为 pgvector；`alembic upgrade head` |
| 小信 503 | `XIAOXIN_CHAT_ENABLED`、`DEEPSEEK_API_KEY` |
| 向量检索无结果 | Ollama 是否运行；`rebuild_documents_best_effort()` |
| 前端连不上 API | `BACKEND_CORS_ORIGINS`、反向代理端口 |
| Docker backend 连不上 DB | `.env` 中 `DATABASE_URL` 主机名是否为 `db`（非 127.0.0.1） |

修改历史见同目录 `xiugairizhi-backend.md` / `xiugairizhi-frontend.md`。
