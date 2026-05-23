# 迎新系统 — 运维部署指南

> **给运维人员**：本文档涵盖后端部署、环境配置、数据库初始化、依赖安装。代码修改相关请参阅同目录下的 `xiugai.md`，系统排查请参阅 `wenti.md`。

---

## 一、环境清理（拿到代码后第一件事）

以下文件/目录是开发过程留下的，部署前应删除：

```
删除  .venv/                                               (开发机虚拟环境，部署环境需重建)
删除  main_backup_before_agent.sql                          (开发期数据库备份)
删除  main_backup_before_pgvector_20260518_222808.sql        (开发期数据库备份)
删除  docs/                                                 (14个AI开发过程文档，运行时不需要)
删除  welcome_backend.egg-info/                             (构建产物)
```

---

## 二、环境准备

### 2.1 依赖安装

```bash
cd backend
uv sync
```

### 2.2 .env 配置文件

在 `backend/` 目录下创建 `.env` 文件：

```env
# ── 必填 ──
DATABASE_URL=postgresql://postgres:你的密码@localhost:5432/yingxin
JWT_SECRET_KEY=替换为一串随机字符串至少32位

# ── 可选（有默认值）──
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Ollama（默认连接本机 11434 端口）
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_EMBED_MODEL=bge-m3:latest
OLLAMA_CHAT_MODEL=qwen2.5:1.5b-instruct-q4_K_M

# 小信 SSE 开关（默认开启）
XIAOXIN_CHAT_ENABLED=true

# 文档向量检索阈值（0~1，默认 0.6）
DOCUMENT_COSINE_THRESHOLD=0.6

# FAQ 快车匹配阈值（默认 8.0）
FAQ_MATCH_MIN_SCORE=8.0

# CORS 允许的前端地址
BACKEND_CORS_ORIGINS=http://localhost:5173

# 是否暴露 /docs API 文档（生产环境建议 false）
EXPOSE_API_DOCS=false

# Edge-TTS 语音
EDGE_TTS_VOICE=zh-CN-XiaoyiNeural
```

### 2.3 PostgreSQL

确保 PostgreSQL 运行中，并创建数据库：

```sql
CREATE DATABASE yingxin;
```

### 2.4 Ollama

```bash
# 安装 Ollama（如未安装）
# 参考 https://ollama.com/download

# 拉取必需模型
ollama pull bge-m3:latest
ollama pull qwen2.5:1.5b-instruct-q4_K_M

# 验证
curl http://localhost:11434/api/tags
```

---

## 三、首次启动

### 3.1 创建数据库表 + 种子数据

```bash
cd backend

# 建表
uv run python -c "
from app.db.database import engine, Base
from app.models import Student, Announcement, FAQ, Document
Base.metadata.create_all(bind=engine)
print('所有表已创建')
"

# 导入种子数据（管理员 + 示例学生 + FAQ + 公告 + 向量库）
uv run python scripts/init_db.py
```

### 3.2 导入 Agent FAQ 数据（快车数据源）

```bash
# 如果 agent_data_only.sql 存在且包含 faqs 表数据：
psql -U postgres -d yingxin -f agent_data_only.sql
```

### 3.3 构建文档向量库

```bash
uv run python -c "
from app.crud.document import rebuild_documents_best_effort
rebuild_documents_best_effort()
print('向量库构建完成')
"
```

### 3.4 启动服务

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

建议使用进程管理工具（如 Windows Service、systemd 或 Docker）：

```bash
# Docker 方式
docker-compose up -d
```

---

## 四、防火墙

```bash
# Windows（管理员终端）
netsh advfirewall firewall add rule name="Yingxin Backend" dir=in action=allow protocol=tcp localport=8000

# Linux
sudo ufw allow 8000
```

---

## 五、日常运维

### 5.1 新增/修改 FAQ 后刷新快车缓存

Agent 的快车路径使用 `faqs` 表且走进程缓存。管理员通过前端新增 FAQ 后，调用以下接口刷新：

```bash
curl -X POST http://localhost:8000/api/admin/agent/faq-cache/invalidate \
  -H "Authorization: Bearer <管理员Token>"
```

### 5.2 同步 `faq` 表到 `faqs` 表

当前 FAQ 管理 API 写入 `faq` 表，如需同步到 Agent 快车使用的 `faqs` 表，需手动执行 SQL 或等待 `xiugai.md` 中的同步代码修改生效。

### 5.3 重建向量库（新增 FAQ/公告后）

```bash
uv run python -c "
from app.crud.document import rebuild_documents_best_effort
rebuild_documents_best_effort()
"
```

### 5.4 健康检查

```bash
curl http://localhost:8000/health -H "Authorization: Bearer <Token>"
```

### 5.5 日志

FastAPI 默认输出到 stdout。建议配置日志收集工具（如 Docker logs、journalctl）。

---

## 六、资源参考（8GB 服务器）

| 进程 | 预计内存 |
|------|----------|
| PostgreSQL | ~500MB |
| Ollama (bge-m3) | ~2GB |
| Ollama (qwen2.5:1.5b) | ~2GB |
| FastAPI (uvicorn) | ~200MB |
| **合计** | **~4.7GB** |

8GB 服务器可运行但偏紧，建议设置 swap 或限制 Ollama 模型并发数。

---

## 七、故障排查

详见同目录下的 `wenti.md`，覆盖网络、数据库、Ollama、向量库、前后端对接的全部排查步骤。
