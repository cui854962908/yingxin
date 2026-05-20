# 迎新系统 API 接口文档

> 河南牧业经济学院 2026 迎新 | 校训：尚严崇实 善知敏行
>
> 前端 Vue 3，需后端提供 FastAPI + PostgreSQL 接口。

---

## 通用约定

- 所有接口 `/api/` 前缀
- 请求/响应格式：JSON
- 响应统一信封：`{ "success": bool, "message": "string（可选）", "data": ... }`
- 需开启 CORS，允许 `localhost:5173`（生产环境改实际域名）
- JWT 认证：登录后返回 token，前端存 localStorage，每次请求带 `Authorization: Bearer <token>`
- token 有效期 24h，payload 为 `{ "sub": "学号", "name": "姓名", "role": "student|admin", "exp": ... }`
- 所有 `/api/admin/*` 接口需 `role: "admin"`，否则返回 403

---

## 接口列表

### 1. POST /api/verify — 登录验证

```
Request  { "name": "张三", "student_id": "20260901001", "id_number": "410105200509010011" }

Response {
  "success": true,
  "message": "欢迎你，张三同学！",
  "token": "eyJhbG...",
  "data": {
    "name": "张三",
    "student_id": "20260901001",
    "photo": "",
    "class_name": "计算机科学与技术 2026-1班",
    "dormitory": "北苑 3号楼 412室",
    "advisor":       { "name": "李明辉", "phone": "138-0000-1111" },
    "class_teacher": { "name": "赵文博", "phone": "137-0000-7777" },
    "assistants": [
      { "name": "王浩", "phone": "139-0000-2222", "class_name": "计算机科学 2025-1班" }
    ],
    "role": "student"
  }
}
```

### 2. GET /api/auth/me — 校验 token（自动登录用）

```
Headers  Authorization: Bearer <token>
Response { "success": true, "data": { "sub": "学号", "name": "姓名", "role": "admin" } }
```

### 3. GET /api/admin/students — 按班级分组列表

```
Headers  Authorization: Bearer <token>  （需要 admin）
Response {
  "success": true,
  "data": {
    "计算机科学与技术 2026-1班": [ { "name":"张三", "student_id":"...", ... } ],
    "软件工程 2026-2班": [ ... ]
  }
}
```

### 4. GET /api/admin/students/search?q=学号 — 按学号搜索

```
Headers  Authorization: Bearer <token>  （需要 admin）
Response 同 verify 的 data 结构
```

### 5. POST /api/admin/students — 新增学生

```
Headers  Authorization: Bearer <token>  （需要 admin）
Request  同 verify 的 data 结构，去掉 role 字段
```

### 6. PUT /api/admin/students/{student_id} — 更新学生

```
Headers  Authorization: Bearer <token>  （需要 admin）
Request  部分字段即可，如 { "dormitory": "新宿舍" }
```

### 7. DELETE /api/admin/students/{student_id} — 删除学生

```
Headers  Authorization: Bearer <token>  （需要 admin）
```

### 8. POST /api/admin/students/import — Excel 批量导入

```
Headers  Authorization: Bearer <token>  （需要 admin）
Content-Type  multipart/form-data，字段名 "file"
Excel 表头  姓名 | 学号 | 身份证号 | 班级 | 宿舍 | 辅导员 | 辅导员电话 | 班主任 | 班主任电话 | 代班 | 代班电话 | 代班班级
Response    { "success": true, "message": "导入完成：成功 100 人，跳过 3 人", "data": { "imported": 100, "skipped": 3 } }
```

### 9. GET /api/faq — 常见问题列表

```
Response { "success": true, "data": [ { "id":"abc", "question":"如何取快递？", "answer":"..." } ] }
```

### 10. POST /api/admin/faq — 新增问题

```
Headers  Authorization: Bearer <token>  （需要 admin）
Request  { "question": "问题", "answer": "答案" }
```

### 11. DELETE /api/admin/faq/{id} — 删除问题

```
Headers  Authorization: Bearer <token>  （需要 admin）
```

### 12. GET /api/announcements — 公告列表

```
Response { "success": true, "data": [ { "id":"abc", "date":"2026-08-10", "title":"...", "content":"..." } ] }
```

### 13. POST /api/admin/announcements — 发布公告

```
Headers  Authorization: Bearer <token>  （需要 admin）
Request  { "title": "标题", "content": "正文", "date": "2026-08-10（可选，默认当天）" }
```

### 14. DELETE /api/admin/announcements/{id} — 删除公告

```
Headers  Authorization: Bearer <token>  （需要 admin）
```

---

## 数据库表建议

### students 表
| 字段 | 类型 | 说明 |
|------|------|------|
| name | varchar | 姓名 |
| student_id | varchar | 学号（唯一） |
| id_number | varchar | 身份证号 |
| photo | varchar | 照片 URL |
| class_name | varchar | 班级，如「计算机科学与技术 2026-1班」 |
| dormitory | varchar | 宿舍，如「北苑 3号楼 412室」 |
| role | varchar | student \| admin |

### advisors / class_teachers / assistants 表
| 字段 | 类型 |
|------|------|
| name | varchar |
| phone | varchar |
| class_name | varchar（仅 assistants） |

### announcements 表
| 字段 | 类型 |
|------|------|
| id | uuid |
| date | date |
| title | varchar |
| content | text |

### faq 表
| 字段 | 类型 |
|------|------|
| id | uuid |
| question | varchar |
| answer | text |
