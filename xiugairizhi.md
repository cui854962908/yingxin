# 项目修改日志

---

## 2026-05-23 — 代码清理 + 组件拆分 + 关键词统一

### 提交 `223633f`：删除死代码，文件归位

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/core/security.py` | 删除 | `verify_password`、`get_password_hash`、`import bcrypt`（项目使用 JWT，从未调用） |
| `backend/app/core/config.py` | 删除 | 5 个 `OPENAI_*` 配置项（项目使用 Ollama，从未引用） |
| `backend/app/db/init_db.py` → `backend/scripts/init_db.py` | 移动 | 种子数据脚本移出应用代码目录 |
| `yunwei.md` | 修改 | 更新 init_db.py 路径引用 |

### 提交 `c9282fe`：提取共享组件 + 统一关键词表

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/components/XinAvatar.vue` | 新建 | 封装 SVG 机器人头像组件（Props：size、animated），消除 3 处重复 |
| `frontend/src/types/student.ts` | 新建 | 提取 `Student` 接口，App.vue + HomePage.vue 共享 |
| `backend/app/core/keywords.py` | 新建 | 合并 `agent_domain.py`（49 词）+ `llm.py`（32 词）为统一 75 词词表，导出 `is_domain_related()` 和 `has_school_keyword()` |
| `backend/app/services/agent_domain.py` | 修改 | 删除内联词表，改为 import 统一模块 |
| `backend/app/core/llm.py` | 修改 | `school_keywords_question()` 改为 import 统一模块 |
| `backend/app/services/xiaoxin_chat_service.py` | 修改 | `_schoolish()` 改用统一关键词 |
| `frontend/src/App.vue` | 修改 | 内联 `interface Student` → `import type { Student }` |
| `frontend/src/components/HomePage.vue` | 修改 | 同上 |

### 提交 `45e86b4`：拆分小信助手子模块

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/composables/useDrag.ts` | 新建 | 悬浮角色 PointerEvent 拖拽逻辑（51 行） |
| `frontend/src/composables/useTTS.ts` | 新建 | Edge-TTS 语音合成 + 自动播报开关（39 行） |
| `frontend/src/components/XinQuickTags.vue` | 新建 | 快捷问题标签栏（38 行） |
| `frontend/src/components/XinChatBubble.vue` | 新建 | 单条消息气泡 + 朗读按钮 + 跳转链接（107 行） |
| `frontend/src/components/XiaoXinAssistant.vue` | 修改 | 移除内联拖拽/TTS/消息渲染，改为 import 子模块 |

### 提交 `d775e38`：提取聊天状态机

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/composables/useXinChat.ts` | 新建 | Agent → SSE → 本地 fallback 三级降级 + 打字机效果 + 消息生命周期管理（298 行） |
| `frontend/src/components/XiaoXinAssistant.vue` | 修改 | 848 行 → 379 行（减少 55%），聊天逻辑全部委托给 useXinChat |
| `frontend/src/composables/useTTS.ts` | 修复 | `welcomeSpoken` 对外暴露导致的 const 赋值问题 |

---

## 2026-05-24 凌晨 — 登录安全 + XSS 修复 + 基础测试

### 提交 `c31a5ee`

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/services/login_guard.py` | 新建 | 登录暴力防护：5 次失败锁定 5 分钟，内存字典存储，超时自动清理 |
| `backend/app/api/auth.py` | 修改 | `/verify`：登录前 `check_locked` → 失败 `record_failure`（返回剩余次数）→ 成功 `clear_record`；`/auth/me`：查不到学生时兜底返回完整结构，防止前端模板字段缺失崩溃 |
| `frontend/src/components/XinChatBubble.vue` | 修改 | `v-html` → `v-text` + CSS `white-space: pre-line`（XSS 修复） |
| `backend/app/api/students.py` | 修改 | 导入异常分类：`ValueError` → 友好提示，意外异常 → 日志 + 通用提示 |
| `backend/app/core/llm.py` | 修改 | `embed()` 添加 3 次重试机制（1s 间隔），网络抖动不崩请求 |
| `backend/tests/__init__.py` | 新建 | 包初始化 |
| `backend/tests/conftest.py` | 修改 | TestClient + 种子学生 fixture |
| `backend/tests/test_login_guard.py` | 新建 | 6 个单元测试：计数、锁定触发、剩余秒数、过期、清除、学号隔离 |
| `backend/tests/test_auth.py` | 修改 | 5 个集成测试：正确登录、错误返回次数、第 5 次锁定、锁定后拦截、/auth/me |
| `frontend/src/components/AdminPanel.vue` | 修改 | 7 处 toast 提示（增删改查成功+失败），空 catch 全部替换为 toast |
| `frontend/tsconfig.json` | 修改 | 添加 `"types": ["vitest/globals"]`，使测试文件识别 describe/it/vi |

---

## 2026-05-24 — 四轮改进（本次会话，未提交）

### 第一轮：补测试

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/tests/conftest.py` | 重写 | SQLite 文件库替代 `:memory:`（解决 FastAPI 线程池连接隔离）；`Base.metadata.create_all` 一次性创建所有表；新增 `seed_admin`、`admin_token`、`admin_headers` fixture |
| `backend/app/models/faq.py` | 修改 | PostgreSQL `UUID(as_uuid=True)` → SQLAlchemy 2.0 通用 `Uuid`，兼容 SQLite |
| `backend/app/models/announcement.py` | 修改 | 同上 |
| `backend/app/models/document.py` | 修改 | 同上，外键引用同步 |
| `backend/tests/test_students.py` | 新建 | 16 个测试：列表分组、搜索、新增/重复/保留字校验、编辑、删除、Excel 导入 mock |
| `backend/tests/test_faq.py` | 新建 | 7 个测试：公开列表、管理员新增（mock embedding）、删除（mock document 清理） |
| `backend/tests/test_announcements.py` | 新建 | 7 个测试：公开列表、管理员新增（mock embedding）、删除（mock document 清理） |

### 第二轮：修静默吞错 + 消除关键词重复

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/components/AnnouncementPanel.vue` | 修改 | 2 处空 catch → `console.warn` |
| `frontend/src/components/FaqPanel.vue` | 修改 | 2 处空 catch → `console.warn` |
| `frontend/src/components/AnnAddForm.vue` | 修改 | 1 处空 catch → `console.warn` |
| `frontend/src/components/FaqAddForm.vue` | 修改 | 1 处空 catch → `console.warn` |
| `frontend/src/App.vue` | 修改 | 1 处空 catch → `console.warn` |
| `frontend/src/composables/useXinChat.ts` | 修改 | 删除 8 条硬编码中文关键词词典（快递、宿舍等），改为完全走后端 FAQ/公告匹配 |
| `backend/scripts/seed_faq.sql` | 新建 | 8 条 FAQ 种子数据，对应前端删除的关键词（快递、宿舍、食堂、军训、学费、图书馆、选课、校园卡） |

### 第三轮：身份证号加盐哈希

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/core/config.py` | 修改 | 新增 `ID_NUMBER_SALT` 配置项 |
| `backend/app/core/security.py` | 修改 | 新增 `hash_id_number()` — SHA-256 + 盐值单向哈希 |
| `backend/app/models/student.py` | 修改 | `id_number` 列 → `id_number_hash`（String 64） |
| `backend/app/services/auth_service.py` | 修改 | 登录时输入值哈希后再与数据库比对 |
| `backend/app/services/student_service.py` | 修改 | 管理端详情 `id_number` 返回空字符串（不可逆） |
| `backend/app/services/import_service.py` | 修改 | Excel 导入时对身份证号哈希后存储 |
| `backend/app/api/students.py` | 修改 | 新增/编辑时 `id_number` 映射为 `id_number_hash` 并调用哈希 |
| `backend/tests/conftest.py` | 修改 | seed 数据改用 `id_number_hash=hash_id_number(...)` |
| `backend/migrations/002_hash_id_number.sql` | 新建 | 迁移 SQL 骨架（添加列 → 回填 → 删旧列） |
| `backend/scripts/hash_existing_id_numbers.py` | 新建 | 一次性脚本，读取旧 `id_number` 计算哈希回写 |

### 第四轮：前端 composable 测试 + E2E 测试

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/composables/__tests__/useTTS.spec.ts` | 新建 | 9 个测试：autoSpeak、speak 成功/HTTP错误/网络异常、stopSpeak、toggleSpeak |
| `frontend/src/composables/__tests__/useDrag.spec.ts` | 新建 | 8 个测试：初始位置、isMobile、resize、拖拽生命周期、边界限制、点击 vs 拖拽 |
| `frontend/src/composables/__tests__/useXinChat.spec.ts` | 新建 | 15 个测试：ensureWelcome、send 拦截、closeChat/navigateTo、onKeydown、agent/fallback 流程 |
| `frontend/src/components/__tests__/XinAvatar.spec.ts` | 新建 | 4 个测试：大/小尺寸 SVG、动画开/关 |
| `frontend/src/components/__tests__/XinQuickTags.spec.ts` | 新建 | 3 个测试：渲染、点击 emit、空列表 |
| `frontend/src/components/__tests__/XinChatBubble.spec.ts` | 新建 | 9 个测试：小信/用户消息渲染、打字光标、链接显隐、emit 事件 |
| `frontend/vitest.config.ts` | 新建 | Vitest 配置：jsdom + Vue 插件 + globals |
| `frontend/playwright.config.ts` | 新建 | Playwright 配置：Chromium headless |
| `frontend/e2e/student-flow.spec.ts` | 新建 | 3 个 E2E：登录→聊天→AI 回复；未登录小信隐藏；Escape 关闭面板（API 全部 mock） |
| `frontend/package.json` | 修改 | 新增 devDependencies：`vitest`、`@vue/test-utils`、`jsdom`、`@playwright/test` |

---

## 核实说明

对你列表的核实结果：

| 你的描述 | 核实结论 |
|----------|----------|
| auth.py /verify 集成锁定 + /auth/me 兜底 | 正确，已在 5/24 凌晨提交 `c31a5ee` |
| login_guard.py 5 次锁定 5 分钟 | 正确，同上 |
| test_login_guard.py 6 单测 + test_auth.py 5 集成测 | 正确，同上 |
| XinChatBubble.vue v-html → v-text（XSS 修复） | 正确，同上 |
| llm.py embed() 3 次重试 | 正确，同上，未单独列出 commit 但在 `c31a5ee` 中 |
| AdminPanel.vue 7 处 toast | 正确，同上 |
| tsconfig.json vitest/globals | 正确，同上 |
| keywords.py 合并 49+32=75 词词表 | 正确，在 5/23 提交 `c9282fe` |
| security.py 删 bcrypt 死代码 | 正确，在 5/23 提交 `223633f` |
| config.py 删 OpenAI 死配置 | 正确，同上 |
| init_db.py → scripts/ | 正确，同上 |
| XinAvatar / useDrag / useTTS / XinQuickTags / XinChatBubble 提取 | 正确，在 5/23 提交 `45e86b4` |
| useXinChat 聊天状态机 | 正确，在 5/23 提交 `d775e38` |
| ~~HomePage.vue inject()! → 运行时检查~~ | **不准确**：代码使用的是 `inject<Ref<Student>>('student')`，无 `!` 断言，无运行时检查 |
| ~~XiaoXinAssistant.vue AgentResponse 类型接口~~ | **不准确**：`AgentResponse` 定义在 `useXinChat.ts` 中，非 `XiaoXinAssistant.vue` |
| students.py 导入异常分类 | 正确，在 `c31a5ee` 中 |
| students.py id_number 哈希处理 | 正确，本次会话第三轮改动 |
| 空 catch 修复 | 正确，本次会话第二轮改动 |
| 关键词去重 + seed_faq.sql | 正确，本次会话第二轮改动 |
| 身份证号加盐哈希全链路 | 正确，本次会话第三轮改动 |
| 测试补全（44 后端 + 48 前端 + 3 E2E） | 正确，本次会话第一、四轮改动 |
| CLAUDE.md / ~/.claude/rules/ / skills / MCP | 属于个人开发环境配置，不计入项目修改日志 |

**重复项（你列表里多次出现的内容，已合并）：**
- login_guard / test_login_guard / test_auth 在你列表中出现 2 次
- keywords.py 词表统一出现 2 次
- security.py bcrypt 删除出现 2 次
- config.py OpenAI 删除出现 2 次
- XinAvatar/useDrag/useTTS 组件拆分出现 2 次

---

## 测试统计总览

| 层级 | 文件数 | 用例数 | 框架 |
|------|--------|--------|------|
| 后端 API 集成测试 | 6 | 44 | pytest + TestClient |
| 前端组件测试 | 3 | 16 | vitest + @vue/test-utils |
| 前端 Composable 测试 | 3 | 32 | vitest |
| E2E 端到端测试 | 1 | 3 | Playwright |
| **合计** | **13** | **95** | — |

全部 95 个测试本地运行约 20 秒（后端 2s + 前端 1s + E2E 15s）。
