# 迎新系统（YingXin）代码审查 & 工程质量报告

> 审查日期：2026-06-28 | 审查范围：后端 / 前端 / 数据库 / 脚本 / 配置

---

## 一、安全漏洞

### 1.1 XSS 风险：v-html 未使用 DOMPurify 净化（中危）

多个组件对来自 API 的 HTML 内容直接使用 `v-html` 渲染，但未用 DOMPurify 净化。这些内容来自管理员后台公告（可信任用户），但缺少纵深防御。

| 文件 | 行号 | 说明 |
|------|------|------|
| `frontend/src/components/IntroSchoolWiki.vue` | 104, 160, 174 | `v-html` 直接渲染公告 HTML 内容（overviewBody / cultureBlock.body / strengthBody） |
| `frontend/src/components/IntroCollegeModule.vue` | 96, 115 | `v-html` 直接渲染学院介绍 HTML |

对比 ClubDetail.vue（第 425、485 行）已正确使用 `DOMPurify.sanitize()`。

**风险影响**：若公告管理账号被盗，可通过公告正文注入 XSS payload。

**建议**：所有 `v-html` 统一使用 DOMPurify.sanitize()。

---

### 1.2 localStorage 明文存储 token 和完整学生信息（低中危）

`frontend/src/App.vue`（第 75-76 行）将 JWT token 和完整学生信息（姓名、学号、班级、辅导员电话）以明文存入 localStorage。

**风险影响**：XSS 攻击可窃取 token 和学生个人信息；浏览器扩展也可能读取。

**建议**：这是校内系统且规模较小，短期可接受。长远可用 sessionStorage 减少持久化风险。按项目「按比例工程」原则，暂不建议引入 cookie/httpOnly 方案（需要后端刷新中间件）。

---

### 1.3 高德地图 JS 安全密钥写入 .env（已解决）

`AMAP_SECURITY_JS_CODE=f3efc5b44e8c8923177d05895598dfe0` 已正确存放在 `backend/.env`，通过安全代理转发，不暴露到前端。设计正确。但 `.env` 文件本身已被 `.gitignore` 忽略，确认安全。

---

## 二、代码坏味道

### 2.1 v-html 未净化（见 §1.1）

---

### 2.2 `any` 类型过度使用（低）

地图相关模块（AMap 无官方 TypeScript 类型）有大量 `any`，属于合理豁免。以下为非地图模块的 `any`：

| 文件 | 行号 | 说明 |
|------|------|------|
| `frontend/src/App.vue` | 50, 71, 81 | `buildStudent`/`applyLoginSession`/`onLoginSuccess` 参数 `Record<string, any>` |
| `frontend/src/composables/usePreload.ts` | 11 | `ref<any[]>([])` |
| `frontend/src/components/ClubDetail.vue` | 198 | `(editForm as any)[field]` |

CONRA.md 允许 `Record<string, any>` 表达"未校验的 JSON"，这几处符合该精神，建议保留。

---

### 2.3 backend print() 调试输出（已合规）

`backend/app/crud/document.py` 第 71、99 行使用了 `print(…, flush=True)`，但这是 CLI 进度输出（受 `progress: bool` 开关控制）。符合 CLAUDE.md 中「CLI 进度输出（flush=True + progress 开关）不在此列」的豁免规则。**无需修改。**

---

### 2.4 forum_posts.answer_count 与 forum_answers 行数不一致（逻辑隐患）

我们通过脚本插入问牧墙帖子时，硬编码了 `answer_count=2`。后端 `forum_service.py` 在 `create_answer`（第 309 行）和删除回答（第 342 行）时动态维护 `answer_count`。但若绕过服务层直接操作数据库，该计数就会和实际回答数不一致。

**建议**：低优先级。服务器正常运行时不会出现偏差。作为防御性改进，可在后台管理页增加「重新计数」按钮。

---

### 2.5 未被使用的 routes/导入（极低）

`IntrocampusDetail.vue` 中定义了 `scrollTo` 函数和锚点导航（第 31-33 行，template 第 67-70 行），功能正常。未发现死代码。

---

## 三、配置问题

### 3.1 .env.example 端口与实际不一致

| 项 | .env.example | 实际（Docker Compose） |
|----|-------------|----------------------|
| DATABASE_URL | `127.0.0.1:5432` | Docker 映射到宿主机 `5434` |

`.env.example` 第 5 行写 `5432`，注释说"本机 dev 用 127.0.0.1:5432"，但 docker-compose.yml 映射 `5434:5432`。如果开发者直接复制 example 到 .env 启动，就会报连接失败（我们之前遇到了）。

**建议**：将 `.env.example` 里的 5432 改为 5434，或加一行注释说明 Docker 环境要用 5434。

---

### 3.2 JWT_SECRET_KEY 仍为占位符（安全）

`backend/.env` 第 9 行 `JWT_SECRET_KEY=replace-with-long-random-secret-key-change-me`，45 个字符，长度符合要求（≥32），但明显是占位值。`REQUIRE_SECURE_SETTINGS=true` 未启用（第 20 行被注释）。

**风险影响**：生产部署时若不变更此密钥，JWT 可被伪造。

**建议**：至少生成一个随机值替换占位符。

---

### 3.3 DEEPSEEK_API_KEY 仍为占位符

`backend/.env` 第 31 行 `DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx`。小信对话功能当前不可用，但不影响地图和社团模块。**开发阶段可接受。**

---

## 四、临时脚本残留

本次开发过程中在 `scripts/` 目录下创建了 5 个一次性测试脚本：

| 文件 | 用途 | 建议 |
|------|------|------|
| `scripts/insert_shenghuobu.py` | 插入生活部 | **删除** |
| `scripts/insert_jijianbu.py` | 插入纪检部 | **删除** |
| `scripts/insert_forum.py` | 插入问牧墙帖子 | **删除** |
| `scripts/clean_clubs.py` | 清理重复社团 | **删除** |
| `scripts/check_students.py` | 查看学生账号 | **删除** |

这些脚本是一次性工具，不是项目正式资产。`.gitignore` 需要确认这些不会被意外提交。

---

## 五、数据库数据质量

### 5.1 测试数据残留

| 表 | 测试数据 | 风险 |
|----|---------|------|
| `clubs` | 生活部、纪检部 | `owner_student_id` 为 NULL，属于无主社团，管理功能对其无效 |
| `forum_posts` | 张三的食堂提问 | `author_id=3`，回复 `author_id=4,2`，外键有效 |
| `students` | 张三(20260901001)、李思雨(20260902001) 等 | 测试账号，正式上线前需清洗 |

**建议**：正式发布前执行数据清洗脚本，清除所有测试数据（或导出为 seed 脚本供后续开发用）。

### 5.2 forum_posts.answer_count 准确性

当前 `answer_count` 与实际 `forum_answers` 行数一致（我们插入时手工对齐了），后续若通过 API 正常操作，后端自动维护此字段。**无问题。**

---

## 六、工程质量总结

### A. 做得好的地方

- SQL 全部使用参数化查询，无字符串拼接——**安全**
- 后端无空 `except:` 块，异常处理得当
- 前端 Props/Emits 全部使用 TypeScript 接口声明（除地图相关 AMap any 外）——**规范**
- 高德地图 key 通过后端动态下发 + 安全代理，不暴露到前端——**设计正确**
- 公告/FAQ/社团的 HTML 内容分离存储，部分已使用 DOMPurify
- `.env` 文件已被 `.gitignore` 忽略
- 后端无调试 `print()`（仅 CLI 进度输出且受开关控制）

### B. 需改进的地方（按优先级）

| 优先级 | 问题 | 影响 |
|--------|------|------|
| **高** | IntroSchoolWiki / IntroCollegeModule 的 v-html 缺少 DOMPurify | XSS 风险（后台被盗时） |
| **中** | `.env.example` 端口 5432 vs 实际 5434 | 新开发者踩坑 |
| **中** | JWT_SECRET_KEY 是占位符 | 生产部署后 JWT 可伪造 |
| **中** | scripts/ 下有 5 个一次性脚本 | 代码库不干净 |
| **低** | forum_posts.answer_count 无一致性校验 | 极端情况可产生偏差 |
| **低** | localStorage 明文存储 token | 低风险（校内系统） |

---

## 七、建议修复顺序

1. **先修安全**：给 `IntroSchoolWiki.vue` 和 `IntroCollegeModule.vue` 的 `v-html` 加 DOMPurify.sanitize()
2. **修配置**：`.env.example` 端口改为 5434
3. **清理**：删除 `scripts/` 下的 `insert_*.py`、`clean_clubs.py`、`check_students.py`
4. **加固**：生成一个随机 JWT_SECRET_KEY 替换占位符
