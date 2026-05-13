# 迎新系统 (YingXin)

> 河南牧业经济学院 2026 迎新 | 校训：尚严崇实 善知敏行
>
> 我负责前端（Vue 3），后端队友负责 FastAPI + PostgreSQL。

## 技术栈

| 端 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite |
| 后端 | FastAPI + PostgreSQL（队友实现） |
| 本地 Mock | FastAPI + uvicorn（`backend/`，仅开发用） |

---

## 后端需要提供的接口

> 响应格式统一：`{ "success": bool, "message": "string（可选）", "data": ... }`
> 需开启 CORS，允许 `localhost:5173`

### 1. POST /api/verify — 登录验证

```
Request:  { "name": "张三", "student_id": "20260901001", "id_number": "410105200509010011" }

Response: {
  "success": true,
  "message": "欢迎你，张三同学！",
  "token": "eyJhbG...（JWT，有效期 24h，payload: sub/name/role）",
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
    "role": "student"   // "student" | "admin"
  }
}
```

### 2. GET /api/auth/me — 自动登录（需 Authorization: Bearer <token>）

```
Response: { "success": true, "data": { "sub": "学号", "name": "姓名", "role": "角色" } }
```

### 3. GET /api/admin/students — 按班级分组列表（需 admin token）

```
Response: {
  "success": true,
  "data": {
    "计算机科学与技术 2026-1班": [ { "name":"张三", "student_id":"...", ... }, ... ],
    "软件工程 2026-2班": [ ... ]
  }
}
```

### 4. GET /api/admin/students/search?q=学号 — 按学号搜索（需 admin token）

### 5. POST /api/admin/students — 新增学生（需 admin token）

```
Request: 同 verify 返回的 data 结构，去掉 role 字段
```

### 6. PUT /api/admin/students/{student_id} — 更新学生（需 admin token）

```
Request: 部分字段即可，{ "dormitory": "新宿舍", "advisor": { "name": "新导员", "phone": "..." } }
```

### 7. DELETE /api/admin/students/{student_id} — 删除学生（需 admin token）

### 8. POST /api/admin/students/import — Excel 批量导入（需 admin token）

```
multipart/form-data，字段名 "file"
Excel 表头：姓名/学号/身份证号/班级/宿舍/辅导员/辅导员电话/班主任/班主任电话/代班/代班电话/代班班级
Response: { "success": true, "message": "导入完成：成功 100 人，跳过 3 人", "data": { "imported": 100, "skipped": 3 } }
```

### 9. GET /api/faq — 常见问题列表

```
Response: {
  "success": true,
  "data": [
    { "id": "abc123", "question": "如何取快递？", "answer": "前往北苑食堂西侧..." }
  ]
}
```

### 10. POST /api/admin/faq — 新增问题（需 admin token）

### 11. DELETE /api/admin/faq/{id} — 删除问题（需 admin token）

---

## 关键约定

- **Token**：登录后返回 JWT，前端存 localStorage，每次请求带 `Authorization: Bearer <token>`
- **角色**：`role` 字段区分 `"student"` 和 `"admin"`，管理接口需 admin 权限
- **代班**：`assistants` 是数组，每班通常 2 个代班
- **班级分组**：前端按 `class_name` 做折叠展示，后端按此字段分组返回
- **接口前缀**：统一 `/api/`
- **前端代理**：Vite 把 `/api/*` 转发到后端，配置在 `frontend/vite.config.ts`

---

## 本地启动（前端 + Mock 后端）

```bash
# 前端
cd frontend && npm install && npm run dev     # → localhost:5173

# Mock 后端（临时，仅开发用）
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
```
