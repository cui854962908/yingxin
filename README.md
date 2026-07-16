# 迎新系统 (YingXin)

河南牧业经济学院 **2026 级新生迎新门户**。

## 产品定位

**认识牧院 · 指导报到 · 智能答疑**

面向 2026 级新生与家长：帮助了解学校与学院、准备报到入学，并通过 FAQ、小信 AI 与牧院新生说获取答疑与互助。

| 能力 | 说明 |
|------|------|
| 认识牧院 | 牧院大百科、学院介绍、社团文化（游客可浏览） |
| 报到指导 | 报到须知、新生攻略、校园导览 |
| 答疑互助 | FAQ、小信 AI、牧院新生说 |

**边界：** 不是学籍/名册管理系统。学生名单由运维脚本导入；Web 端做身份校验、个人报到信息展示与内容维护。

完整说明见 [CONTEXT.md](CONTEXT.md) §1.1。

## 快速启动

```powershell
# 终端 1：启动数据库
cd backend
docker compose up -d postgres

# 终端 2：启动后端（FastAPI，端口 8000）
cd backend
.\scripts\start_backend.ps1

# 终端 3：启动前端（Vite，端口 5173）
cd frontend
npm run dev
```

启动后访问 `http://localhost:5173`，其他设备通过局域网 IP 访问（如 `http://192.168.43.6:5173`）。

首次启动后需执行种子数据初始化（仅一次）：

```powershell
cd backend
uv run python scripts/init_db.py
```

## 内置账号

系统通过**姓名 + 学号 + 密码**三项认证登录。初始密码为 `01234567`，登录后请尽快修改。连续错误 5 次锁定 5 分钟。

### 管理员

| 姓名 | 学号 | 初始密码 | 角色 |
|------|------|----------|------|
| 崔志远 | `admin` | `01234567` | admin |

可通过环境变量覆盖：`ADMIN_SEED_NAME`、`ADMIN_SEED_STUDENT_ID`。生产环境请用 `manage_student_account.py --reset-password` 修改管理员密码。

### 演示学生

| 姓名 | 学号 | 初始密码 | 班级 |
|------|------|----------|------|
| 张三 | `20260901001` | `01234567` | 计算机科学与技术2026-1班 |
| 李思雨 | `20260902001` | `01234567` | 软件工程2026-2班 |
| 王浩然 | `20260903001` | `01234567` | 数据科学与大数据2026-1班 |
| 刘子涵 | `20260904001` | `01234567` | 物联网工程2026-6班 |

### 数据库

| 地址 | 用户 | 密码 | 数据库 |
|------|------|------|--------|
| `127.0.0.1:5434` | `welcome` | `welcome` | `welcome_db` |

## 项目画像

详见 [CONTEXT.md](CONTEXT.md) — 规模参数、技术栈、模块说明、工程原则。

## 运维

- [yunwei.md](yunwei.md) — 部署、公网 VPS 与排障
- [deploy/nginx-yingxin.conf.example](deploy/nginx-yingxin.conf.example) — Nginx 反向代理示例
- [backend/docs/ADMIN_GUIDE.md](backend/docs/ADMIN_GUIDE.md) — **管理员与内容维护**
- [backend/docs/FRONTEND_API.md](backend/docs/FRONTEND_API.md) — 前后端接口
- [CONTEXT.md](CONTEXT.md) — 项目画像与模块说明

## 开发

```bash
# 后端测试
cd backend && uv run pytest

# 前端测试
cd frontend && npx vitest run

# 前端类型检查
cd frontend && npx vue-tsc --noEmit

# 前端生产构建
cd frontend && npm run build
```
