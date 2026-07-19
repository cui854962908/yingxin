# 小信 SSE（`POST /api/chat`）与 TTS

与 `POST /api/agent/chat`（域检测 / 隐私闸 / FAQ 后再走同款 `documents` + 嵌入 API）并存；本节描述 SSE 形态的 `POST /api/chat`。

鉴权：游客不可用小信。前端仅在登录后挂载悬浮窗；`POST /api/chat`、`POST /api/tts` 均须 `Authorization: Bearer <JWT>`（学生或管理员）。登录用户另有账号级限流（chat 25/min、tts 20/min，见 `app/core/rate_limit.py`）。

---

## 1. 环境与 `.env`

| 变量 | 说明 |
|------|------|
| `XIAOXIN_CHAT_ENABLED` | 默认 `true`；`false` 时 `POST /api/chat` 返回 503 |
| `EMBED_API_KEY` | 远端嵌入 API Key（如 SiliconFlow）|
| `EMBED_API_BASE_URL` | 默认 `https://api.siliconflow.cn/v1` |
| `EMBED_MODEL` | 默认 `BAAI/bge-m3` |
| `DEEPSEEK_CHAT_MODEL` | 默认 `deepseek-v4-flash` |
| `DOCUMENT_COSINE_THRESHOLD` | 默认 `0.6` |
| `DEEPSEEK_CHAT_TIMEOUT_SECONDS` | 默认 `120` |
| `EDGE_TTS_VOICE` | 默认 `zh-CN-XiaoyiNeural` |

完整列表见 `app/core/config.py`。

---

## 2. 嵌入模型

小信 RAG 通过远端 API 生成向量嵌入，配置见上表。无需本地模型部署。

---

## 3. 迁移与向量构建

Alembic 需至少到最新 head（含 `documents` 表与 `source_kind` 字段）。

`app/crud/document.py` 的 `build_documents` 会聚合同步三类来源：

- `faq`（学生端 CRUD 常见问题）→ `source_kind=student_faq`
- `announcements` → `source_kind=announcement`
- `clubs` → `source_kind=club`

均写入 `documents.embedding_json`（远端嵌入 API，见 `app/core/llm.py`）。

在 `backend` 目录：

```powershell
uv run alembic upgrade head
uv run python scripts/init_db.py
```

`init_db.py` 会在种子数据写入后调用 `rebuild_documents_best_effort()`。

管理员在 FAQ / 公告 / 社团增删改成功后，后台会通过 `incremental_embed_*` 异步更新向量；若嵌入 API 当时未就绪，可再跑全量重建命令或 `rebuild_documents_best_effort()`（详见 `docs/ADMIN_GUIDE.md` 第 4 节）。

小信 `done` 事件中的 `links` 在未命中知识库时可含牧院新生说（`/wall`）引导。

若 embedding 失败，检查 `EMBED_API_KEY` 是否有效、嵌入 API 服务是否可达。

---

## 4. SSE 事件

`Content-Type: text/event-stream`，每帧：`data: {JSON}\n\n`。

| `event` | 说明 |
|---------|------|
| `delta` | 字段 `content` 为正文片段 |
| `done` | 结束；含 `reply_mode`：`knowledge_base` / `no_hit_in_domain` / `chitchat` / `privacy` |
| `error` | `detail` 说明原因 |

编排见 `app/services/xiaoxin_chat_service.py`。

---

## 5. TTS

`POST /api/tts`，body `{ "text": "..." }`，响应 `audio/mpeg`。须登录（同上 Bearer JWT）。

---

## 6. 源码索引

| 文件 |
|------|
| `app/api/v1/chat.py`、`app/api/v1/tts.py` |
| `app/core/llm.py`、`app/services/xiaoxin_chat_service.py` |
| `app/models/document.py`、`app/schemas/xiaoxin.py` |
| `app/crud/document.py`、`scripts/init_db.py` |

前端字段级说明见 `docs/FRONTEND_API.md` 第 6 节。
