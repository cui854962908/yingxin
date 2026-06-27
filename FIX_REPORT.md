# 代码审查修复报告

> 修复日期：2026-06-28 | 基于 CODE_REVIEW.md 的发现逐一修复

---

## 修复清单

### 1. 数据库端口统一为 5432

| 文件 | 改动 |
|------|------|
| `backend/.env` | `DATABASE_URL` 端口从 5434 改回 5432 |
| `docker-compose.yml` | DB 端口映射从 `5434:5432` 改为 `5432:5432` |

`.env.example` 原本就是 5432，无需修改。`backend/docker-compose.yml` 原本就是 5432:5432，无需修改。现在全项目统一用 5432。

---

### 2. XSS 防护：v-html 统一使用 DOMPurify 净化

| 文件 | 改动 |
|------|------|
| `frontend/src/components/IntroSchoolWiki.vue` | 新增 `import DOMPurify from 'dompurify'`；新增 3 个 sanitized computed（`overviewBodySafe`、`cultureBodySafe`、`strengthBodySafe`）；3 处 `v-html` 绑定从原始值改为 sanitized 值 |
| `frontend/src/components/IntroCollegeModule.vue` | 新增 `import DOMPurify from 'dompurify'`；新增 2 个 sanitized computed（`safeBlocks`、`safeFacultyProse`）；v-for 循环从 `blocks`/`facultyProse` 改为 `safeBlocks`/`safeFacultyProse` |

ClubDetail.vue 此前已正确使用 DOMPurify.sanitize()，无需修改。

---

### 3. 临时脚本清理

删除 `scripts/` 下 5 个一次性测试脚本：

- `insert_shenghuobu.py`
- `insert_jijianbu.py`
- `insert_forum.py`
- `clean_clubs.py`
- `check_students.py`

保留 `scripts/verify.sh`（项目验证脚本）。

---

### 4. JWT 密钥替换占位符

`backend/.env` 中 `JWT_SECRET_KEY` 从占位符 `replace-with-long-random-secret-key-change-me` 替换为 64 字符随机十六进制字符串。

> ⚠ 更换 JWT 密钥后，所有已签发的 token 立即失效。需重新登录。

---

## 验证结果

```
========== 文件行数 ==========
[Vue SFC ≤ 300 行]     ✓ 全部通过
[Python/TS ≤ 450 行]   ✓ 全部通过
[SQL/YAML/JSON ≤ 200 行] ✓ 全部通过

========== 调试语句 ==========
[前端 console.log/debug] ✓ 0 处
[后端 print() 调试]      ✓ 0 处

========== 函数行数 ==========
[Python 函数 ≤ 50 行]   ✓ 全部通过

========================================
  全部硬性规则检查通过 ✓
========================================
```

---

## 未修复的已知项（低优先级，按比例工程暂缓）

| 项 | 原因 |
|----|------|
| localStorage 明文存 token | 校内系统、小规模，cookie/httpOnly 方案过度 |
| forum_posts.answer_count 无一致性校验 | 正常 API 操作自动维护，脚本插入时才需手动对齐 |
| AMap 相关 `any` 类型 | 无官方 TS 类型，合理豁免 |
| DEEPSEEK_API_KEY 占位符 | 不影响社团/地图/问牧墙功能，上线前再配 |
