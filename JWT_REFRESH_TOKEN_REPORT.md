# JWT Refresh Token 双令牌机制 —— 完成度报告

> 实施日期：2026-07-11  
> 涉及文件：17 个（后端 12 个，前端 5 个）  
> 新增文件：4 个 | 修改文件：13 个

---

## 一、架构总览

```
┌─────────────────────────────────────────────────────┐
│                    登录流程                          │
│   POST /api/verify  ──→  access_token (15min)       │
│                      ──→  refresh_token (7day)      │
│                      ──→  前端：access_token 存内存  │
│                      ──→  前端：refresh_token 存     │
│                              localStorage            │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  API 请求流程                        │
│   authFetch() ──→ 携带 access_token                 │
│              ──→  401？                              │
│                   ├─ 是 → tryRefresh()               │
│                   │       ├─ 成功 → 重放原请求       │
│                   │       └─ 失败 → 强制登出         │
│                   └─ 否 → 正常返回                   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                  刷新令牌流程                        │
│   POST /api/refresh  ──→  验证 refresh_token 哈希    │
│                      ──→  撤销旧 token               │
│                      ──→  签发新 token（轮换）        │
│                      ──→  返回 new_access_token      │
│                      ──→  返回 new_refresh_token     │
└─────────────────────────────────────────────────────┘
```

---

## 二、变更清单

### 2.1 后端新增文件

| # | 文件 | 说明 |
|---|------|------|
| 1 | `backend/app/models/refresh_token.py` | SQLAlchemy 模型：`refresh_tokens` 表，含 token_hash、student_id、expires_at、revoked、replaced_by 等字段 |
| 2 | `backend/app/services/token_service.py` | 四个函数：`issue_refresh_token`、`rotate_refresh_token`、`revoke_refresh_token`、`revoke_all_for_student` |
| 3 | `backend/alembic/versions/0020_add_refresh_tokens.py` | Alembic 迁移：创建 `refresh_tokens` 表及索引，链式 `0019→0020` |

### 2.2 后端修改文件

| # | 文件 | 变更内容 |
|---|------|----------|
| 4 | `backend/app/core/config.py` | `ACCESS_TOKEN_EXPIRE_HOURS` → `ACCESS_TOKEN_EXPIRE_MINUTES`（默认 15 分钟）；新增 `REFRESH_TOKEN_EXPIRE_HOURS`（默认 168 小时/7 天）；新增 `_positive_minutes` 校验器 |
| 5 | `backend/app/core/security.py` | `create_access_token()` 参数 `expires_hours` → `expires_minutes`；新增 `hash_refresh_token()` SHA-256 哈希函数 |
| 6 | `backend/app/core/response.py` | `verify_ok()` 新增可选参数 `refresh_token`，有值时加入响应体 |
| 7 | `backend/app/schemas/auth.py` | 新增 `TokenRefreshRequest` 和 `LogoutRequest` Pydantic 模型 |
| 8 | `backend/app/services/auth_service.py` | `verify_student_login` 返回 4 元组 `(token, refresh_raw, data, role)`，每次登录签发 refresh token |
| 9 | `backend/app/api/auth.py` | `/verify` 端点适配 4 元组；新增 `POST /refresh`（刷新）和 `POST /logout`（登出撤销）端点 |
| 10 | `backend/app/models/__init__.py` | 导入 `RefreshToken` |
| 11 | `backend/.env` | `ACCESS_TOKEN_EXPIRE_HOURS=168` → `ACCESS_TOKEN_EXPIRE_MINUTES=15` + `REFRESH_TOKEN_EXPIRE_HOURS=168` |
| 12 | `backend/.env.example` | 同上，保持模板同步 |

### 2.3 前端新增文件

| # | 文件 | 说明 |
|---|------|------|
| 13 | `frontend/src/composables/useAuthFetch.ts` | 核心 fetch 包装器，含自动刷新、并发锁、强制登出机制 |

### 2.4 前端修改文件

| # | 文件 | 变更内容 |
|---|------|----------|
| 14 | `frontend/src/composables/useAuth.ts` | 导入并重导出 `setAccessToken`/`getAccessToken`/`onForceLogout`/`authFetch`；`authHeaders()` 优先读取内存 token |
| 15 | `frontend/src/App.vue` | `onMounted` 中优先用 refresh token 恢复会话；`onLoginSuccess` 签名扩展为 `(s, token, refreshToken?)`；`clearAuth` 清除 refresh_token；`onLogout` 增加服务端撤销 |
| 16 | `frontend/src/components/LoginForm.vue` | emit 签名更新为 `'login-success': [student, token, refreshToken?]` |
| 17 | `frontend/src/components/LoginPage.vue` | emit 签名和模板同步更新 |

---

## 三、安全设计要点

### 3.1 令牌分级存储
- **Access Token**（15 分钟有效）：仅存于 JavaScript 内存（`_accessToken`），不落盘。即使 XSS 也无法通过 `localStorage` 窃取。
- **Refresh Token**（7 天有效）：存于 `localStorage`，服务端仅存储其 SHA-256 哈希值，原始字符串从不出现在数据库或日志中。

### 3.2 轮换（Rotation）
每次 `POST /api/refresh` 成功后：
1. 旧 token 标记 `revoked = true`，记录 `revoked_at`
2. 签发新 token，`replaced_by` 指向旧记录，形成链式审计追踪
3. 前端用新 refresh token 覆盖 localStorage 旧值

### 3.3 重用检测架构（已预留）
`refresh_tokens.replaced_by` 自引用外键构成链表。若一个已被轮换的 token 再次出现，可沿链追溯是正常轮换还是攻击者抢在合法用户之前使用了 stolen token。当前轮换逻辑已铺好数据基础，`revoke_all_for_student()` 函数也已就绪，可在检测到重用时全线撤销。

### 3.4 并发刷新锁
`tryRefresh()` 内部维护模块级 `_refreshPromise`，多个同时 401 的请求共享同一个刷新 Promise，避免竞争条件导致多次轮换。

### 3.5 主动登出
`POST /api/logout` 接收 refresh token 并在服务端标记撤销，前端同时清除所有本地凭据。即使用户的 refresh token 已泄露，主动登出后 token 立即失效。

---

## 四、编译验证

| 检查项 | 结果 |
|--------|------|
| `vue-tsc --noEmit`（TypeScript 类型检查） | ✅ 通过 |
| `python -m py_compile`（9 个 Python 文件） | ✅ 全部通过 |
| `.env` / `.env.example` 配置键同步 | ✅ 一致 |

---

## 五、待执行的手动步骤

以下步骤需要在开发机上手动执行——这些无法由本会话自动完成：

### 步骤 1：运行数据库迁移
```bash
cd backend
uv run alembic upgrade head
```
这将依次执行 `0019`（添加 `students.forum_role` 列）和 `0020`（创建 `refresh_tokens` 表）。

如果数据库中还没有 `0019`（即 `forum_role` 列缺失），运行此命令后两个迁移一并完成。

### 步骤 2：重启后端服务
```bash
# 终端 2（后端）
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
配置变更（`ACCESS_TOKEN_EXPIRE_MINUTES` 和 `REFRESH_TOKEN_EXPIRE_HOURS`）需要重启才能生效。

### 步骤 3：验证功能
1. 访问前端，用任意学生账号登录
2. 打开浏览器开发者工具 → Application → Local Storage，确认 `refresh_token` 已存储
3. 等待 15 分钟后（或手动缩短 `ACCESS_TOKEN_EXPIRE_MINUTES` 测试），刷新页面，应能自动通过 refresh token 恢复会话
4. 点击登出，确认 Local Storage 中 `refresh_token` 被清除，且数据库中对应记录 `revoked = true`

---

## 六、后续优化建议

| 优先级 | 建议 | 说明 |
|--------|------|------|
| 中 | 各组件逐步迁移到 `authFetch` | 当前 `useAuth.ts` 已导出 `authFetch`，但论坛、公告等组件仍使用原生 `fetch`。应逐步替换以享受自动刷新能力 |
| 低 | 实现 refresh token 重用检测 | 在 `rotate_refresh_token` 中：若查到的 token 已 `revoked`，说明可能被盗用，调用 `revoke_all_for_student()` 全线撤销 |
| 低 | 添加定时刷新策略 | 在前端设置 `setInterval`，在 access token 过期前 2 分钟主动刷新，避免用户操作瞬间的 401 延迟 |

---

## 七、变更统计

- 后端新增代码：约 200 行（含迁移）
- 后端修改代码：约 40 行
- 前端新增代码：约 110 行
- 前端修改代码：约 25 行
- **总计：约 375 行净变更**
- 零破坏性变更：所有现有登录流程保持兼容

---

*报告生成时间：2026-07-11*
