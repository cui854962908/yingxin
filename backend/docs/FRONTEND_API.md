# 河南牧业经济学院迎新系统 · 后端接口说明（供前端对接）

**配套文档：** `docs/XIAOXIN_SSE.md`（小信 SSE / TTS 专项）、**`docs/ADMIN_GUIDE.md`**（管理员维护）

**版本：** 与当前仓库后端一致（FastAPI），含智能助手 Agent。  
**交给前端建议一并提供：** 本文件；机器可读契约可在 `.env` 设 **`EXPOSE_API_DOCS=true`** 后访问 **`/openapi.json`**。

**联调基址（开发）：**

- 本机：`http://localhost:8000` 或 `http://127.0.0.1:8000`
- **局域网（手机 / 同事电脑访问你这台机器）：** `http://<你电脑的局域网IP>:8000`  
  例如：`http://192.168.1.100:8000`（在 Windows 终端执行 `ipconfig` 查看 **IPv4 地址**）

**生产：** 由运维/部署替换为实际域名，例如 `https://api.example.com`

**在线文档（Swagger）：** 仅当服务端 `.env` 中 **`EXPOSE_API_DOCS=true`** 时挂载 **`/docs`**、`/openapi.json`；默认关闭，避免匿名浏览完整 API 定义。

---

## 1. 通用约定

### 1.0 哪些接口要不要带 Token？

| 接口 | Bearer | 说明 |
|------|--------|------|
| **`POST /api/verify`** | 不需要 | 三要素换 JWT |
| **`POST /api/agent/chat`** | **需要** | 须 **学生/管理员** JWT（与小信一致，游客不可用） |
| **`POST /api/chat`**（SSE，小信） | **需要** | 须 **学生/管理员** JWT；游客不可用 |
| **`POST /api/tts`** | **需要** | 须登录（小信语音播报） |
| **`GET /api/faq`**、**`GET /api/announcements`** | **不需要** | 迎新公开展示列表；可按需仍可带 Bearer（不传亦 **200**） |
| **`GET /api/forum/posts`**、**`GET /api/forum/posts/{id}`** | **不需要** | 牧院新生说列表/详情；带 Bearer 时可识别「我的」、点赞态 |
| **`POST /api/forum/*`**（发帖、回答、点赞等） | **需要** | 须 **学生** JWT（游客不可用） |
| **`GET /api/auth/me`** | **需要** | 解析当前用户 |
| **`GET /health`** | **需要** | 学生或管理员 |
| 所有 **`/api/admin/*`** | **需要** | 须 **管理员** JWT（部分非 admin 为 403） |

匿名访问根路径 **`/`** 为 **404**，无业务数据。

### 1.1 路径前缀

业务接口统一前缀：**`/api`**。健康检查为 **`GET /health`**（无 `/api` 前缀，但同样需 Bearer）。

### 1.2 请求 / 响应格式

- `Content-Type`：`application/json`（文件上传接口除外）
- 字符编码：UTF-8
- 时间、ID：FAQ/公告的 `id` 为 UUID，JSON 中多为字符串；日期为 ISO 字符串（如 `2026-08-10`）

### 1.3 CORS（开发环境）

后端通过 `.env` 放行前端页面所在 **Origin**（协议 + 主机 + 端口）：

| 变量 | 含义 |
|------|------|
| `BACKEND_CORS_ORIGINS` | 逗号分隔的完整来源列表，默认含 `http://localhost:5173`、`http://127.0.0.1:5173` |
| `BACKEND_CORS_ORIGIN_REGEX` | **可选**。正则匹配来源；当前仓库默认用于放行常见 **局域网 IP**（`192.168.*`、`10.*`、`172.16–31.*`）下 **任意端口**，便于用 `http://192.168.x.x:5173` 打开前端 |

**前端 axios / fetch 的基址示例：** 若网页从 `http://192.168.1.5:5173` 打开，则 API 基址应设为 `http://192.168.1.5:8000`（与后端所在机器 IP 一致，端口为 **8000**）。

**Vue / Vite：** 若需局域网访问开发服务器，请在 `vite.config` 中配置 `server.host: true`（或启动命令加 `--host`），否则外机无法打开 `http://IP:5173`。

**生产环境：** 建议删除 `BACKEND_CORS_ORIGIN_REGEX`，仅在 `BACKEND_CORS_ORIGINS` 中写死前端正式域名。

### 1.4 统一响应信封

**常规成功：**

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

`data` 可为对象、数组或 `null`，以各接口说明为准。

**常规失败（业务层返回或 HTTP 异常处理）：**

```json
{
  "success": false,
  "message": "错误原因说明",
  "data": null
}
```

**参数校验失败（HTTP 422）：**

```json
{
  "success": false,
  "message": "请求参数校验失败",
  "data": [ ... ]
}
```

`data` 为 FastAPI/Pydantic 校验错误列表（便于联调定位字段）。

**学生验证成功 / 管理员登录成功：** 在信封基础上，**顶层额外字段 `token`**（JWT），与 `data` 同级：

```json
{
  "success": true,
  "message": "...",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....",
  "data": { }
}
```

**GET `/api/auth/me` 成功：** 当前实现为 **`success` + `data`**，**不一定**包含 `message`：

```json
{
  "success": true,
  "data": {
    "sub": "20260901001",
    "name": "张三",
    "role": "student"
  }
}
```

---

## 2. 认证说明

### 2.1 JWT 存放与携带

- **`POST /api/verify` 返回的 `token`**（**学生与管理员共用此接口**：库中 `students.role` 为 `admin` 时同样走三要素校验，返回 `role: admin` 的 JWT）

需要鉴权的接口在请求头增加：

```http
Authorization: Bearer <token>
```

**注意：** `Bearer` 与 token 之间有一个空格。

### 2.2 令牌载荷（解码后字段约定）

学生典型载荷：

- `sub`：学号  
- `name`：姓名  
- `role`：`"student"`  
- `exp`：过期时间  

管理员典型载荷：

- `sub`：**学号字段**（默认管理员为 `admin`，与 `students.student_id` 一致）  
- `name`：显示名称  
- `role`：`"admin"`  
- `exp`：过期时间  

> **说明：** 管理员账号保存在 **`students`** 表中，`role = admin`，**不再提供** `/api/admin/login`。

默认有效期：**24 小时**（服务端可配置）。

### 2.3 管理员接口权限

所有 **`/api/admin/*`** 下需登录的接口必须携带 **`role` 为 `admin` 的 JWT**（通过 **`POST /api/verify`** 获得）。

| HTTP 状态 | 含义 |
|-----------|------|
| 401 | 未携带 token 或 token 无效/过期 |
| 403 | token 有效但 `role` 不是 `admin` |

---

## 3. 健康检查（无 `/api` 前缀）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 存活探测。须 **`Authorization: Bearer <token>`**（学生或管理员均可）；无/无效 token：**401**。成功响应：`{"status":"ok"}`（**非**统一信封） |

---

## 4. 认证与学生

### 4.1 三要素登录（学生 + 管理员）

**POST** `/api/verify`

学生与管理员 **同一接口**：后端根据匹配到的 `students` 记录上的 **`role`** 区分（`student` / `admin` / `club_admin`）。

**Body：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| student_id | string | 是 | 学号（管理员默认账号见下） |
| password | string | 是 | 登录密码 |

亦支持 **camelCase**：`studentId`（password 字段名不变）。

**学生请求示例：**

```json
{
  "name": "张三",
  "student_id": "20260901001",
  "password": "01234567"
}
```

**默认管理员（`init_db` 初始化后，可按库中实际数据修改）：**

```json
{
  "name": "崔志远",
  "student_id": "admin",
  "password": "01234567"
}
```

**成功（HTTP 200）：** 顶层含 `success`、`message`、`token`（access token）、`refresh_token`、`data`。

- **学生：** `message` 为「欢迎你，{姓名}同学！」；`data` 含完整迎新嵌套结构（见下表「学生字段」）。
- **管理员：** `message` 为「管理员登录成功」；`data` 为：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 姓名 |
| student_id | string | 学号（与请求一致） |
| role | string | 固定 `admin` |

**学生 `data` 其它字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| photo | string | 照片 URL，可为 `""` |
| class_name | string | 班级 |
| dormitory | string | 宿舍 |
| advisor | object | `name`、`phone`（可为 null） |
| class_teacher | object | `name`、`phone` |
| assistants | array | 代班列表，每项含 `name`、`phone`、`class_name` |
| role | string | `student` |

**失败（HTTP 200）：** `success: false`，姓名/学号/密码不匹配等。

### 4.2 刷新 Access Token

**POST** `/api/refresh`

**Body：** `{ "refresh_token": "<refresh_token>" }`

**成功：** `data.access_token`、`data.refresh_token`（轮换，旧 refresh 立即失效）。

### 4.3 主动登出

**POST** `/api/logout`

**Body：** `{ "refresh_token": "<refresh_token>" }`

### 4.4 修改密码

**POST** `/api/auth/change-password`

**Headers：** `Authorization: Bearer <access_token>`

**Body：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| current_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码（≥8 位，不能与当前相同） |

**成功：** `success: true`；服务端撤销该账号全部 refresh token，其他设备需重新登录。

### 4.5 校验 Token（学生 / 管理员通用）

**GET** `/api/auth/me`

**Headers：** `Authorization: Bearer <token>`

**成功：** 见 1.4， `data.sub` / `data.name` / `data.role`。

**失败：** 401，`success: false`。

---

## 5. 智能助手（Agent）

与迎新业务 **同一数据库**。通用问答可**不带** Bearer；涉及**本人宿舍等个人数据**时必须带学生 JWT（`sub` 为学号）。**勿**在请求体传 `student_id`；身份**只认**服务端签发的 JWT。

### 5.0 对接要点（给前端）

1. **URL：** `POST {API_BASE}/api/agent/chat`，`Content-Type: application/json`。  
2. **Body 仅允许：** `{ "message": string }`，`message` 去首尾空格后不能为空，否则 **422**。  
3. **个人向：** 用户问「我的宿舍」等时，把学生登录拿到的 token 放进 **`Authorization: Bearer <token>`**；未登录则仍返回 **200**，`data.source` 为 `student_agent`，`reply` 为登录提示。  
4. **展示逻辑建议：** 以 **`data.source`** 为主区分业务类型（见下表）；**`data.intent`** 为辅助（隐私场景：`source` 与 `intent` 均为 **`privacy`**）。  
5. **错误：** 仅当请求携带了 **非法/过期** JWT 时返回 **401**；其它业务分支（无关、隐私、兜底等）均为 **200** + `success: true`。  
6. **知识生成：** FAQ 未命中时的回答与 **`POST /api/chat` SSE**（小信）同源——**远端嵌入 API + 表 `documents` 的余弦检索**；不再使用 OpenAI/pgvector **`knowledge_chunks`** 链路回答本接口。

**`source` 常见取值（与 `intent` 典型组合）**

| `data.source` | 含义 | `intent` 常见值 | 前端可怎么做 |
|----------------|------|-----------------|--------------|
| `faq` | Agent 表 `faqs` 命中 | `faq` | 展示 `reply`，可显示 `matched_title` |
| `xiaoxin_kb` | 小信知识库：`documents` 向量命中后经远端 API 生成 | `knowledge` | 展示 `reply` / `matched_title`（常为命中的文档标题） |
| `chitchat` | 用户问题偏离迎新主题，走闲聊模型 | `irrelevant` | 可当普通对话气泡展示 |
| `student_agent` | 登录提示 / 宿舍等本人业务 / 管理员个人向引导 | `dorm` / `payment` / … | 未登录可跳转登录；已登录展示宿舍等 |
| `privacy` | 问询他人敏感信息被拒 | `privacy` | 展示隐私话术即可 |
| `irrelevant` | **域外**：与迎新关键词无关而被拒答 | `irrelevant` | 提示换领域提问 |
| `fallback` | 迎新域内未命中文档，或服务暂时不可用时的引导 | `unknown` | 引导去通知公告 / 联系老师 |
| `validation` | 空消息（校验失败时） | `unknown` | 提示输入问题 |

**成功响应形状（所有业务分支一致）：**

```json
{
  "success": true,
  "message": "success",
  "data": {
    "reply": "字符串，助手自然语言回复",
    "intent": "faq | knowledge | dorm | privacy | irrelevant | ... | null",
    "source": "faq | xiaoxin_kb | chitchat | student_agent | privacy | irrelevant | fallback | ...",
    "matched_title": "命中时的标题，可为 null"
  }
}
```

**fetch 示例（个人向：有 token 则带上）：**

```ts
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

export async function agentChat(message: string, token?: string | null) {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/api/agent/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message }),
  });
  const body = await res.json();
  if (res.status === 401) {
    throw new Error(body?.message ?? "未授权");
  }
  if (!body?.success) {
    throw new Error(body?.message ?? "请求失败");
  }
  return body.data as {
    reply: string;
    intent: string | null;
    source: string | null;
    matched_title: string | null;
  };
}
```

**HTTP 状态（本接口）：**

| HTTP | 说明 |
|------|------|
| 200 | 正常业务响应（含兜底、隐私、无关等），读 `success` 与 `data` |
| 401 | 未登录或 Bearer 无效/过期 |
| 422 | 参数错误（如 `message` 为空） |

### 5.1 对话

**POST** `/api/agent/chat`

**Headers：** `Authorization: Bearer <token>`（**必须**）

**Body：** 仅支持下列字段（**不要**传 `student_id`）：

```json
{ "message": "报到需要带什么材料？" }
```

**成功：** 统一信封，`data` 含：

| 字段 | 类型 | 说明 |
|------|------|------|
| reply | string | 助手回复正文 |
| intent | string \| null | 细分意图，如 `faq`、`privacy`、`knowledge`、`irrelevant`；部分场景为 `unknown` |
| source | string \| null | **建议前端以此区分链路**：`faq`、`xiaoxin_kb`、`chitchat`、`student_agent`、`privacy`、`irrelevant`、`fallback` 等 |
| matched_title | string \| null | 命中 FAQ 或小信检索到的文档标题等 |

### 5.2 FAQ 缓存与兜底观测（无独立管理路由）

后台 **POST/DELETE `/api/admin/faq`** 成功后服务端会清空进程内 **`faq`** 快车缓存，无需单独的缓存失效接口。  
历史接口 **`GET /api/agent/logs/fallbacks`**、**`POST /api/admin/agent/faq-cache/invalidate`** 已移除。兜底问题可开后端 **`AGENT_PERF_LOG`**，并检索 **`source=fallback`** 时 **`app.agent`** 日志打点。

### 5.3 性能调试（可选）

服务端 `.env` 设置 **`AGENT_PERF_LOG=true`** 后，对 `POST /api/agent/chat` 会在日志中输出 **`[agent_perf]`** 各阶段耗时（jwt、domain、faq、`xiaoxin_rag`、route_body 等；历史向量字段则可能为 0 或未计入）。

### 5.4 小信 SSE：`POST /api/chat`（嵌入 API + `documents` 表）

面向「小信」聊天窗：**流式 SSE**。**与 JSON 信封 `POST /api/agent/chat`** 在编排上略有不同（SSE 独立入口先做隐私闸，再直奔向量分支；Agent JSON 会先尝试 **`faq`** 快车）。两者在 **知识检索（`documents` + 嵌入 API）** 上一致。

**Body：**

```json
{ "question": "报到需要带什么？" }
```

**Headers：** `Content-Type: application/json`；（计划中未强制 Bearer，可自行扩展）。

**响应：** `Content-Type: text/event-stream`。每行为 **`data:` + JSON 对象**，形如：

```text
data: {"event":"delta","content":"片段"}
data: {"event":"done","reply_mode":"knowledge_base","top_similarity":0.72}
```

- **`reply_mode`** 可能：`knowledge_base` | `no_hit_in_domain` | `chitchat` | `privacy`。
- **`event`=`error`** 时含 **`detail`** 字符串。
- **`XIAOXIN_CHAT_ENABLED=false`** 时：**HTTP 503**（信封同全局异常：`success:false`）。
- **`documents.embedding_json`** 需在库中就绪；由 **`app/crud/document.py`** 的 **`build_documents`** / **`incremental_embed_*`**（远端嵌入 API）写入；全量重建见 **`scripts/init_db.py`**。

**依赖：** `EMBED_API_KEY` 已配置且嵌入 API 可达。

**前端建议：** `fetch` 读 **`response.body`** 的 ReadableStream，`EventSource` 标准不支持 POST，一般用 fetch 解析 `data:` 行。

详见 **`backend/docs/XIAOXIN_SSE.md`**。

### 5.5 小信朗读：`POST /api/tts`

**Body：** `{ "text": "要合成的文字" }`  

**响应：** `Content-Type: audio/mpeg`，二进制音频流。**502** 时走统一信封（由全局 `HTTPException` 处理）。

**依赖：** Python 环境可访问微软 Edge TTS 服务（依赖包 **edge-tts**）。

---

## 6. FAQ

### 6.1 获取 FAQ 列表（匿名可读）

**GET** `/api/faq`

**Headers：** 不要求 `Authorization`。未登录访客也可拉列表；若附带合法 Bearer，同样 **200**。

**成功 `data`：** 数组，每项：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string (UUID) | |
| question | string | |
| answer | string | |

---

### 6.2 新增 FAQ（管理员）

**POST** `/api/admin/faq`

需管理员 JWT。

**Body：**

```json
{
  "question": "如何取快递？",
  "answer": "请前往菜鸟驿站凭取件码领取。"
}
```

**成功：** `data` 为新建项（含 `id` 等）。

---

### 6.3 删除 FAQ（管理员）

**DELETE** `/api/admin/faq/{id}`

`id` 为 UUID。

**成功：** `message` 如「删除成功」，`data` 为 `null`。

**不存在：** 404。

---

## 7. 社团

### 7.1 社团列表（匿名可读）

**GET** `/api/clubs`

**成功 `data`：** 数组，按名称拼音排序。主要字段：`id`、`name`、`category`、`cover_image`、`hero_image`、`intro`、`status`（含招募期自动计算「招新中/已结束」）、`recruit_start`、`recruit_end`、`member_count`、`qq_group`、`wechat_qr` 等。

### 7.2 社团详情（匿名可读）

**GET** `/api/clubs/{club_id}`

`club_id` 为 UUID。**404** 表示不存在。

### 7.3 管理端 CRUD

需管理员或社团管理员 JWT（`require_any_admin`）。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/clubs` | 创建；社团管理员仅能创建一个 |
| PUT | `/api/admin/clubs/{club_id}` | 更新；社团管理员仅能改自己的 |
| DELETE | `/api/admin/clubs/{club_id}` | 删除（需系统管理员） |
| PATCH | `/api/admin/clubs/{club_id}/status` | 手动设「招新中/已结束」 |
| POST | `/api/admin/clubs/upload-image` | 上传风采图，返回 `{ url }` |

增删改成功后异步更新 **`documents`** 向量（`incremental_embed_club`）。

---

## 8. 公告

### 8.1 获取公告列表（匿名可读）

**GET** `/api/announcements`

**Headers：** 不要求 `Authorization`。未登录访客也可拉列表；若附带合法 Bearer，同样 **200**。

**排序：** 按 `date` 降序（无日期的靠后），再按创建时间降序。

**成功 `data`：** 数组，每项：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string (UUID) | |
| date | string \| null | 如 `2026-08-10` |
| title | string | |
| content | string | |

---

### 8.2 发布公告（管理员）

**POST** `/api/admin/announcements`

需管理员 JWT。

**Body：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 标题 |
| content | string | 是 | 正文 |
| date | string (YYYY-MM-DD) | 否 | 不传则默认**服务端当前日期** |

**成功：** `data` 为新建公告对象（JSON 中 `date` 一般为字符串）。

---

### 8.3 删除公告（管理员）

**DELETE** `/api/admin/announcements/{id}`

`id` 为 UUID。

**成功：** `message` 如「删除成功」，`data` 为 `null`。

**不存在：** 404。

---

## 9. 牧院新生说（Forum）

前端模块名 **牧院新生说**，路由 **`/wall`**。详细维护说明见 **`docs/ADMIN_GUIDE.md`** §3。

### 9.1 帖子列表（匿名可读）

**GET** `/api/forum/posts`

**Query：**

| 参数 | 默认 | 说明 |
|------|------|------|
| page | 1 | 页码 |
| page_size | 15 | 最大 50 |
| sort | `latest` | `latest` \| `hot` \| `open`（待解答） |
| category | — | `报到` \| `学习` \| `生活` \| `社团` \| `其他` |
| q | — | 标题/正文模糊搜索 |
| mine | false | `true` 时仅看本人帖子（**须 Bearer**） |

**成功 `data`：** `{ items: ForumPostBrief[], total, page, page_size }`

### 9.2 帖子详情

**GET** `/api/forum/posts/{post_id}`

含 `answers` 数组。隐藏帖（`is_hidden`）对公众不可见。游客响应中 **`author_id` 为 `null`**（防关联同一作者）；登录用户可见。

### 9.3 发帖 / 改帖 / 删帖 / 关帖

| 方法 | 路径 | 鉴权 |
|------|------|------|
| POST | `/api/forum/posts` | 学生 JWT |
| PATCH | `/api/forum/posts/{id}` | 楼主，24h 内 |
| DELETE | `/api/forum/posts/{id}` | 楼主或 **admin** |
| POST | `/api/forum/posts/{id}/close` | 楼主 |
| POST | `/api/forum/posts/{id}/like` | 学生 JWT |

**发帖 Body：** `{ title, content, category? }`（`category` 默认 `其他`）

### 9.4 回答

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/forum/posts/{id}/answers` | 创建回答 |
| PATCH | `/api/forum/answers/{id}` | 作者 24h 内编辑 |
| DELETE | `/api/forum/answers/{id}` | 作者或 admin |
| POST | `/api/forum/answers/{id}/accept` | 楼主采纳 |
| POST | `/api/forum/answers/{id}/like` | 点赞 |

### 9.5 管理员

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/forum/posts/{id}/pin?pinned=true` | 置顶 / 取消 |
| POST | `/api/admin/forum/posts/{id}/hide` | 隐藏（列表不可见） |

Web 详情页已实现 **隐藏**；置顶目前仅 API。

---

## 10. 前端联调清单（建议）

1. 使用 Vite 默认 `http://localhost:5173` 调试，避免 CORS 问题；局域网调试见 **§1.3**。  
2. **环境变量：** 配置 `VITE_API_BASE`（或项目约定名）指向后端，例如 `http://127.0.0.1:8000`，与后端 **`BACKEND_CORS_ORIGINS`** 中的前端 Origin 一致。  
3. **管理端：** 使用 **`POST /api/verify`**，请求体为管理员的姓名 / 学号 / 身份证号（与 `students` 表中一致），成功后存 `token`，并判断 `data.role === 'admin'`。  
4. **学生端：** 同样 **`POST /api/verify`**，存 `token`，`GET /api/auth/me` 做自动登录恢复。  
5. **`GET /api/faq`、`GET /api/announcements`：** **可不带头**。**`GET /api/auth/me`、`GET /health`、全部 `/api/admin/*`：** 按 **§1.0** 携带 `Authorization: Bearer ${token}`。  
6. **`POST /api/agent/chat`：** 须登录（Bearer）；FAQ 快车读 **`faq` 表**，未命中再走小信。
7. **小信（SSE）：** `POST /api/chat` + **`question`**，`fetch` 读流解析 `text/event-stream`；需 **`EMBED_API_KEY` + `documents` 向量**；未命中时可引导 **牧院新生说**（`/wall`）；可选 **`POST /api/tts` 朗读。**  
8. **牧院新生说：** 列表/详情可匿名 **`GET /api/forum/posts*`**；发帖/回答须学生 JWT。  
9. 以 **`success` 字段** 区分业务成功与否；HTTP 状态码同时参考 401/403/404/422/503。  
10. **交接物：** 提供 **`docs/FRONTEND_API.md`**、**`docs/ADMIN_GUIDE.md`**、`docs/XIAOXIN_SSE.md`（做小信 SSE 时）；约定后端 commit/tag；接口变更后同步前端。

---

## 11. 接口路径速查

| 方法 | 路径 | 鉴权 |
|------|------|------|
| GET | `/health` | Bearer（学生或管理员） |
| POST | `/api/verify` | 无 |
| GET | `/api/auth/me` | Bearer |
| POST | `/api/chat` | 无强制（可按需加 Bearer） |
| POST | `/api/tts` | 无 |
| POST | `/api/agent/chat` | Bearer（必须） |
| GET | `/api/faq` | **无强制** Bearer |
| POST | `/api/admin/faq` | 管理员 |
| DELETE | `/api/admin/faq/{id}` | 管理员 |
| GET | `/api/clubs` | **无强制** Bearer |
| GET | `/api/clubs/{club_id}` | **无强制** Bearer |
| POST | `/api/admin/clubs` | 管理员 / 社团管理员 |
| PUT | `/api/admin/clubs/{club_id}` | 管理员 / 社团管理员 |
| DELETE | `/api/admin/clubs/{club_id}` | 管理员 |
| POST | `/api/admin/clubs/upload-image` | 管理员 / 社团管理员 |
| GET | `/api/announcements` | **无强制** Bearer |
| POST | `/api/admin/announcements` | 管理员 |
| DELETE | `/api/admin/announcements/{id}` | 管理员 |
| GET | `/api/forum/posts` | **无强制** Bearer |
| GET | `/api/forum/posts/{post_id}` | **无强制** Bearer |
| POST | `/api/forum/posts` | 学生 |
| DELETE | `/api/forum/posts/{post_id}` | 楼主 / admin |
| POST | `/api/admin/forum/posts/{id}/pin` | 管理员 |
| POST | `/api/admin/forum/posts/{id}/hide` | 管理员 |

---

**文档路径（仓库内）：** `backend/docs/FRONTEND_API.md`  
**OpenAPI：** 服务端 **`EXPOSE_API_DOCS=true`** 时访问 **`/openapi.json`**

若后端基址或 CORS 变更，请同步修改本文件「联调基址」与第一节说明；接口签名变更请重新导出 OpenAPI 并知会前端。
