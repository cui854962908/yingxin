# 迎新系统 · 管理员与内容维护指南

> 面向 **系统管理员**、**社团管理员** 与 **运维**。接口细节见 **`docs/FRONTEND_API.md`**；部署见根目录 **`yunwei.md`**；产品全貌见 **`CONTEXT.md`**。

---

## 1. 角色与登录

| 角色 | `students.role` | 登录方式 | 典型能力 |
|------|-----------------|----------|----------|
| 游客 | — | 无需登录 | 浏览认识牧院、FAQ、公告、**牧院新生说**列表（**不可用小信**） |
| 新生 | `student` | **`POST /api/verify`** 姓名+学号+密码 | 个人信息、小信、**牧院新生说**发帖/回答 |
| 系统管理员 | `admin` | 同上（库中 `student_id` 默认 **`admin`**） | FAQ / 公告 / 社团 / 论坛 moderation |
| 社团管理员 | `club_admin` | 同上 | 仅维护**名下社团** |

**无独立 `/api/admin/login`**：管理员与学生共用 **`POST /api/verify`**，JWT 内 `role` 区分权限。

默认管理员（`init_db.py` 种子；**生产务必用 `manage_student_account.py --reset-password` 修改初始密码**）：

```json
{ "name": "崔志远", "student_id": "admin", "role": "admin" }
```

初始密码默认为 `01234567`（与演示学生相同）。

---

## 2. Web 端维护入口（系统管理员）

登录后通过左侧导航进入各模块（文案常量 **`FORUM_MODULE_NAME`** = **牧院新生说**，路由 **`/wall`**）。

| 模块 | 路由 | 维护方式 |
|------|------|----------|
| 校园公告 | `/announcements` | 页内增删（含报到须知、新生攻略等 **category**） |
| 问题答疑 | `/faq` | 增删改、拖拽排序；**keywords** 影响小信 FAQ 快车 |
| 社团 | `/clubs` | 系统管理员管全部；社团管理员仅自己的社团 |
| 认识牧院 | `/intro/*` | 学院/百科正文多来自 **公告 category**（见 CONTEXT §4.3）；学院社团归属在 `frontend/src/constants/intro.ts` 配置 |
| **牧院新生说** | `/wall` | **无独立后台**；见 §3 |

---

## 3. 牧院新生说（新生互助论坛）

**产品名：** 牧院新生说（原「问牧墙」）  
**前端路由：** `/wall`（列表）、`/wall/new`（发帖）、`/wall/{id}`（详情）

### 3.1 用户侧

- **游客**：可浏览列表与详情，不可发帖/点赞。
- **登录新生**：发帖（分类：报到 / 学习 / 生活 / 社团 / 其他）、回答、点赞、采纳、24h 内编辑自己的帖/答；每日发帖 ≤5、回答 ≤30。
- **小信联动**：知识库未命中时，前端与 LLM 提示引导至 **牧院新生说**（可预填标题跳转 `/wall/new?title=…`）。

### 3.2 管理员侧（Web）

在帖子 **详情页**（`/wall/{id}`），管理员可见：

| 操作 | 说明 |
|------|------|
| **隐藏帖子** | 调用 `POST /api/admin/forum/posts/{id}/hide`，列表不再展示 |
| **删除帖子** | 与普通删帖相同接口；可删任意帖 |

**置顶**暂无 Web 按钮，需 API：`POST /api/admin/forum/posts/{id}/pin?pinned=true`（见 FRONTEND_API §9）。

### 3.3 侧栏说明（桌面）

列表页右侧：**提问说明**、**热门话题**（静态搜索快捷词，非实时热度）、**小信助手**。窄屏（≤1100px）侧栏隐藏。

---

## 4. 小信与向量库（运维）

小信 RAG 读取 **`documents`** 表，来源：**FAQ + 公告 + 社团**（**不含**认识牧院长文 wiki，除非写入 FAQ/公告）。

| 操作 | 何时做 |
|------|--------|
| FAQ / 公告 / 社团增删改 | 服务端自动 **`incremental_embed_*`** |
| 嵌入 API 未就绪导致嵌入失败 | 手动全量重建（见下） |
| 首次部署 / 大改内容后 | `init_db.py` 或全量重建 |

**前置：** `.env` 中 `EMBED_API_KEY` 已配置且嵌入 API 可达。

```powershell
cd backend
# 全量重建 documents（带进度）
uv run python -c "from app.db.database import SessionLocal; from app.crud.document import build_documents; db=SessionLocal(); print(build_documents(db, progress=True)); db.close()"

# 或静默重建（init_db / 后台任务同款）
uv run python -c "from app.crud.document import rebuild_documents_best_effort; rebuild_documents_best_effort()"
```

小信 **须登录** 使用；登录用户调用 **`POST /api/chat`** / **`POST /api/tts`** 有账号级限流（见 `rate_limit.py`）。

---

## 5. 生产环境检查（管理员协同运维）

| 项 | 建议 |
|----|------|
| `JWT_SECRET_KEY` | ≥32 位随机串 |
| `REQUIRE_SECURE_SETTINGS` | **`true`** |
| 管理员/新生初始密码 | 部署后批量通知改密，或用 `manage_student_account.py --reset-password` |
| `DEEPSEEK_API_KEY` | 有效，小信可用 |
| `BACKEND_CORS_ORIGINS` | 仅正式前端域名 |
| 新生名单 | 运维写库 / 脚本，**无 Web 导入** |
| 向量库 | 部署后跑一次重建并抽测小信 |

---

## 6. 相关文档

| 文档 | 内容 |
|------|------|
| `docs/FRONTEND_API.md` | 全部 REST 接口（含牧院新生说 §9） |
| `docs/XIAOXIN_SSE.md` | 小信 SSE、嵌入 API、向量构建 |
| `docs/AGENT_AND_XIAOXIN_DUAL_PATH.md` | Agent 与小信双链路 |
| `yunwei.md` | Docker、迁移、防火墙、排障 |
| `CONTEXT.md` | 产品定位与各模块说明 |

**文档路径（仓库内）：** `backend/docs/ADMIN_GUIDE.md`
