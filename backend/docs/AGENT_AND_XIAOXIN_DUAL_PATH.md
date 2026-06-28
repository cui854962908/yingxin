# 两条智能对话链路：`/api/agent/chat` 与「小信」`/api/chat`

> **说明**：后端**没有**两套互斥的「大模型 Agent 进程」。用户侧可以理解为 **两条产品入口**：一条是 **迎新智能助手（JSON 单行）**，一条是 **小信（SSE 流式）**。第二条在知识生成阶段复用 **`xiaoxin_chat_service`**，与第一条在走完 FAQ 快车等业务后的 **小信聚合**同源。  

---

## 一、术语对照（避免和后端文件名混淆）

| 口语 / 前端 | HTTP 接口 | 实现要点 |
|-------------|-----------|-----------|
| **迎新智能助手 / Agent** | `POST /api/agent/chat` | `app/api/agent.py` → `route_chat_async`：**编排**多层逻辑，最后一步可能调用 **`complete_xiaoxin_turn`**。 |
| **小信** | `POST /api/chat`（SSE） | `app/api/v1/chat.py` → **`stream_xiaoxin_events`**：**直接**走进向量 + 嵌入 API，无前面的域检测 / FAQ 快车等。 |

「另一个」常被说成第二个 Agent——**实际上是上述第一条链路的整条编排**，不是另一个独立常驻模型服务。

---

## 二、链路 A：迎新智能助手 `POST /api/agent/chat`

### 2.1 入口与鉴权

- **路由**：`app/api/agent.py` → **`agent_chat`**
- **Body**：`{ "message": "…" }`（`schemas/agent.AgentChatRequest`）
- **Authorization**：**必须**携带合法 Bearer；无效 / 过期 **401**。**个人向业务**依赖 JWT `sub`（学号），不信前端传来的 `student_id`。
- **响应**：统一信封，`data.reply` / `intent` / `source` / `matched_title`。

### 2.2 编排顺序（自上而下，命中即返回）

实现：**`app/services/agent_service.route_chat_async`**。

```
空消息 → validation（非 LLM）
  ↓
is_domain_related（迎新域关键词）→ 域外 irrelevant 固定话术
  ↓
student_gate_response（打探他人隐私 / 匿名问「我的…」登录提示 / admin 问个人信息的提示）
  ↓
faq_service.find_best_faq —— 读 **`faq`**（学生常见问题），进程内缓存，规则打分 vs FAQ_MATCH_MIN_SCORE → 命中则 source=faq
  ↓
complete_xiaoxin_turn(question) —— 与链路 B 同一套「小信内核」（见下文 3.x），聚合成单行 → source 多为 xiaoxin_kb / chitchat / fallback 等
```

### 2.3 链路 A 使用的数据源小结

| 阶段 | 读什么 |
|------|--------|
| 隐私 / 登录闸 | **`student_agent_service`** 规则（可查 **`students`** 仅用于闸门文案场景；无结构化寝室短路） |
| FAQ 快车 | **`faq`**（与学生端 CRUD 同源） |
| 小信步 | **`documents`**（由 **`faq` + `announcements` + `clubs`** 全量或增量写入，见 `build_documents` / `incremental_embed_*`） |

快车与小信向量 **同源**：运营在后台维护 **`faq`** 后，FAQ 快车立即反映；**`documents`** 随行增量嵌入（失败仅日志；可择机跑 `scripts/init_db.py` 或 `rebuild_documents_best_effort()` 兜底）。

### 2.4 收尾

- **兜底观测**：`/api/agent/chat` 在小信分支返回 **`source=fallback`** 时由 `app.agent` logger 打点（不再写 `agent_chat_logs`）。
- **可选打点**：`AGENT_PERF_LOG` 时对 `/api/agent/chat` 的中间件分段计时。

---

## 三、链路 B：小信 `POST /api/chat`（SSE）

### 3.1 入口

- **路由**：`app/api/v1/router.py` 挂载 → **`app/api/v1/chat.py`** → **`chat`**
- **Body**：`{ "question": "…" }`（`schemas/xiaoxin.XiaoxinChatBody`）
- **`XIAOXIN_CHAT_ENABLED=false`**：可先 **503**（路由层）。
- **响应**：`text/event-stream`；服务端事件经 `_sse` 过滤后主要为 **`{"token":"…"}`**，结束 **`{"done":true,"links":[…]}`**。

### 3.2 运行逻辑（`stream_xiaoxin_events`）

实现：**`app/services/xiaoxin_chat_service.stream_xiaoxin_events`**。

```
.strip 空 → error + done（validation）

mentions_other_person → privacy 话术 token + done（不走向量）

XIAOXIN_CHAT_ENABLED=false → error + disabled

threading.Semaphore(2)：繁忙则 error + busy

asyncio.to_thread(_retrieve_in_thread)：
  - 新开 SessionLocal
  - search_similar(question) → 【documents.embedding_json】全表余弦，Top3
  - 最高分 > DOCUMENT_COSINE_THRESHOLD → context 拼装；否则无 context（学校/闲聊分支在 build_prompt）
build_prompt(context, question) → generate_stream（远端 API）→ 逐个 token yield
done：有 context 则 links 指向 /faq、/announcements；未命中时可含 **牧院新生说** `/wall`；附带 matched_title、reply_mode（路由层收敛 done 时可只透出 links）
```

### 3.3 与链路 A「小信步」的关系

| 对照项 | **`complete_xiaoxin_turn`（链路 A 末尾）** | **`stream_xiaoxin_events`（链路 B）** |
|--------|--------------------------------------------|----------------------------------------|
| **内核** | 内部 **`async for` 消费同上 `stream_xiaoxin_events`**，拼成单行 `reply`。 | SSE 按需对外推 `token`。 |
| **阈值 / 向量 / Prompt** | 相同 `search_similar`、`build_prompt`、`generate_stream`。 | 相同。 |

---

## 四、环境与依赖（两条链路共用与小信专有）

| 配置 / 组件 | 作用 |
|-------------|------|
| `DOCUMENT_COSINE_THRESHOLD` | `documents` 是否当「命中知识库」。 |
| `EMBED_*` | 嵌入 API（OpenAI 兼容格式）。 |
| **`build_documents`** / **`rebuild_documents_best_effort`** | 维护 **`documents`**，源为 **`faq` + announcements + clubs**。 |
| Edge-TTS | 仅 **`POST /api/tts`**，与上文两条对话逻辑独立。 |

---

## 五、相关源文件一览

| 文件 | 作用 |
|------|------|
| `app/api/agent.py` | 链路 A 入口 |
| `app/services/agent_service.py` | 链路 A 编排 |
| `app/services/faq_service.py` | 链路 A 的 `faqs` 快车 |
| `app/api/v1/chat.py` | 链路 B SSE 外壳 |
| `app/services/xiaoxin_chat_service.py` | **小信共享内核**（流式 +聚合） |
| `app/crud/document.py` | **`search_similar`**、**`build_documents`** |
| `app/core/llm.py` | **embed / generate_stream（同步 HTTP） / build_prompt** |

更细的 Agent 分支与 `source` 含义见上文 §2.2～§2.3。

---

**文档路径：** `backend/docs/AGENT_AND_XIAOXIN_DUAL_PATH.md`
