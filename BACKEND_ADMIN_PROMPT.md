# 修改管理员登录逻辑 · 前端对接要求

## 现状

后端文档中管理员登录是单独的 `POST /api/admin/login`，用 `username + password`。但前端目前没有管理员独立登录页面，管理员和学生走同一套登录流程。

## 要求

**去掉 `POST /api/admin/login`**，管理员也通过 `POST /api/verify` 登录。

## 改动点

### 1. 数据库中给管理员账号加三个字段

管理员账号和学生一样，需要有：

| 字段 | 示例值 |
|------|--------|
| name | 崔志远 |
| student_id | 2502160306002 |
| id_number | 411103200712010177 |
| role | admin |

### 2. `POST /api/verify` 逻辑

验证三要素匹配后，生成 JWT，payload 中的 `role` 字段直接取自数据库：

```
学生张三 → role: "student"
管理员崔志远 → role: "admin"
```

### 3. JWT payload 格式

```json
{
  "sub": "学号",
  "name": "姓名",
  "role": "student 或 admin",
  "exp": "过期时间"
}
```

### 4. 鉴权中间件

所有 `/api/admin/*` 接口校验 `role === "admin"`，不通过返回 403。这个你们文档已经有了，不需要改。

## 总结

就一句话：**去掉 `/api/admin/login`，在 `/api/verify` 的数据库里加一条 `role: admin` 的管理员记录即可。**
