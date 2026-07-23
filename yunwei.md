# 迎新系统 · 运维部署指南

面向运维：环境配置、数据库初始化、公网部署与日常维护。Nginx 配置示例见 `deploy/nginx-yingxin.conf.example`；管理员内容维护见 `backend/docs/ADMIN_GUIDE.md`；接口说明见 `backend/docs/FRONTEND_API.md`；产品背景见 `CONTEXT.md`。

---

## 一、部署前清理（可选）

开发机上的这些内容不必拷到生产服务器：

```
删除  backend/.venv/          （到服务器后执行 uv sync 重建）
删除  backend/*backup*.sql    （开发期数据库备份，已在 .gitignore）
删除  backend/welcome_backend.egg-info/
```

保留 `backend/docs/`，联调和管理员查阅时会用到。

---

## 二、环境准备

### 2.1 依赖

```bash
cd backend
uv sync
```

前端生产构建在**开发机**执行：`cd frontend && npm ci && npm run build`。  
内存小于 2GB 的服务器不要在上面跑 `npm run build`，容易 OOM。

### 2.2 `.env` 配置

复制 `backend/.env.example` 为 `backend/.env`，至少填写：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接串（须含 pgvector） |
| `JWT_SECRET_KEY` | 生产环境替换为 ≥32 位随机串 |
| `REQUIRE_SECURE_SETTINGS` | 生产建议 `true`：弱 JWT 或默认 SALT 时拒绝启动 |
| `DEEPSEEK_API_KEY` | 小信对话必填 |

本机开发（仅 DB 容器）：

```env
DATABASE_URL=postgresql+psycopg://welcome:welcome@127.0.0.1:5434/welcome_db
```

Docker 全栈（backend 容器内连 db 服务）：

```env
DATABASE_URL=postgresql+psycopg://welcome:welcome@db:5432/welcome_db
```

完整变量说明见 `backend/.env.example` 与 `backend/app/core/config.py`。

生产环境还建议：

- 设置 `REQUIRE_SECURE_SETTINGS=true`
- `BACKEND_CORS_ORIGINS` 只填正式前端域名；`BACKEND_CORS_ORIGIN_REGEX` 留空或收窄
- 密钥走环境变量或 secrets，不要把含真密钥的 `.env` 打进镜像

### 2.3 PostgreSQL + pgvector

方式 A — 仅数据库（本机开发）：

```bash
cd backend
docker compose up -d
```

映射端口 `5434`，镜像 `pgvector/pgvector:pg16`。

方式 B — 全栈 Docker：

```bash
# 项目根目录
docker compose up -d
```

根目录 `docker-compose.yml` 已使用 pgvector 镜像，凭据与 `.env.example` 一致。

### 2.4 嵌入 API

小信 RAG 使用远端嵌入 API（`.env` 中 `EMBED_API_KEY`，默认 SiliconFlow BAAI/bge-m3）。对话生成走 DeepSeek API（`DEEPSEEK_API_KEY`）。

---

## 三、首次启动

```bash
cd backend

# 1. 数据库迁移
uv run alembic upgrade head

# 2. 种子数据（管理员 + 示例 FAQ/公告/社团 + 向量库重建）
uv run python scripts/init_db.py
```

若向量构建因嵌入 API 不可用而跳过，API 就绪后手动重建：

```bash
uv run python -c "from app.crud.document import rebuild_documents_best_effort; rebuild_documents_best_effort()"
```

启动后端：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Windows 开发：.\scripts\start_backend.ps1
```

生产环境建议后端只监听 `127.0.0.1:8000`，由 Nginx 反代 `/api/`，不对外直接暴露 8000。

---

## 四、公网生产部署（Nginx + 静态前端）

当前推荐的线上形态：

| 组件 | 方式 |
|------|------|
| 前端 | 开发机构建 `frontend/dist`，Nginx 托管静态文件 |
| 后端 | systemd 守护 `yingxin-backend`，Nginx 反代 `/api/`、`/static/` |
| 数据库 | Docker 跑 `welcome-postgres`，或本机 PostgreSQL |

**关键原则（踩坑总结）：**

| 要做 | 不要做 |
|------|--------|
| 本机 `npm run build`，上传 `dist` 压缩包 | 在 ≤2GB 服务器上 `npm run build`（易 OOM 卡死） |
| 解压到 Nginx 的 `dist/` 目录 | 在服务器 `git pull` 指望前端自动更新（`dist/` 在 `.gitignore`，Git 不管打包产物） |
| `systemctl restart yingxin-backend` | SSH 里裸跑 `uv run`（非交互 shell 常找不到 `uv`） |
| 更新后用无痕窗口验证 | 普通刷新（浏览器会缓存旧 JS） |

### 4.0 生产路径与 systemd（阿里云示例）

以当前公网机为例（路径因安装而异，以实际为准）：

| 项目 | 路径 / 命令 |
|------|-------------|
| 项目源码 | `/var/www/yingxin` |
| Nginx 静态根 | `/var/www/yingxin/frontend/dist` |
| 后端工作目录 | `/var/www/yingxin/backend` |
| systemd 单元 | `yingxin-backend.service` |
| 启动命令 | `/root/.local/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` |

查看服务配置：

```bash
systemctl cat yingxin-backend.service
systemctl status yingxin-backend --no-pager
journalctl -u yingxin-backend -n 50 --no-pager
```

### 4.1 Nginx 要点

示例配置见 `deploy/nginx-yingxin.conf.example`。常见路径：

```nginx
root /var/www/yingxin/frontend/dist;

location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

确认实际路径：

```bash
sudo nginx -T 2>/dev/null | grep -E '^\s*root '
```

### 4.2 更新前端（只改界面时）

Nginx 只读 **`frontend/dist/`**，不读 `frontend/src/`。因此必须在本机构建后再上传。

**开发机（Windows PowerShell）：**

```powershell
cd C:\path\to\yingxin
git pull origin master
git log -1 --oneline

cd frontend
npm run build
tar -czf dist.tar.gz -C dist .
scp dist.tar.gz root@服务器IP:/tmp/dist.tar.gz
```

`-C dist .` 表示打包 **dist 目录内的内容**（`index.html`、`assets/` 等），不是把整个 `dist` 文件夹再套一层。

也可用 Termius SFTP：本机选 `dist.tar.gz`，拖到服务器 `/tmp/`。

**不要用 7z 压整个 `dist` 文件夹**——解压后易出现 `dist/dist/index.html`，Nginx 读不到正确入口。若必须用 7z，请进入 `dist` **内部**全选文件再压缩。

**服务器：**

```bash
ls -lh /tmp/dist.tar.gz
sudo rm -rf /var/www/yingxin/frontend/dist/*
sudo tar -xzf /tmp/dist.tar.gz -C /var/www/yingxin/frontend/dist/
rm -f /tmp/dist.tar.gz

# 确认 index.html 直接在 dist 根下（不应有 dist/dist/）
ls /var/www/yingxin/frontend/dist/index.html
find /var/www/yingxin/frontend/dist -name index.html
```

仅前端变更时**不必**重启后端。更新后用无痕窗口验证，避免浏览器缓存旧资源。

### 4.3 更新后端

**推荐：systemd 重启（不要用 SSH 里裸跑 `uv run`）**

```bash
cd /var/www/yingxin
git pull origin master
cd backend && uv sync
sudo systemctl restart yingxin-backend
sleep 2
systemctl status yingxin-backend --no-pager
```

验证（论坛公开列表 + 无效 token 应 200，见 security 修复）：

```bash
curl -s -o /dev/null -w "forum: HTTP %{http_code}\n" \
  "http://127.0.0.1:8000/api/forum/posts?page=1&page_size=4" \
  -H "Authorization: Bearer invalid"
```

若涉及数据库结构变更，先执行 `uv run alembic upgrade head`。

**服务器 `git pull` / `git fetch` 卡住时（国内 ECS 连 GitHub 常见）**

不要在卡住的终端里等。可改用本机 scp 传改动的 `.py` 文件，再 restart：

```powershell
scp C:\path\to\yingxin\backend\app\core\security.py root@服务器IP:/var/www/yingxin/backend/app/core/security.py
```

```bash
sudo systemctl restart yingxin-backend
```

或换镜像后再 pull（用完可改回官方地址）：

```bash
cd /var/www/yingxin
git remote set-url origin https://mirror.ghproxy.com/https://github.com/cui854962908/yingxin.git
git fetch origin && git reset --hard origin/master
cd backend && uv sync
sudo systemctl restart yingxin-backend
```

### 4.4 完整发布（前后端都有改动）

```powershell
# === 本机 ===
cd C:\path\to\yingxin
git pull origin master
cd frontend && npm run build && tar -czf dist.tar.gz -C dist .
scp dist.tar.gz root@服务器IP:/tmp/dist.tar.gz
```

```bash
# === 服务器 ===
sudo rm -rf /var/www/yingxin/frontend/dist/*
sudo tar -xzf /tmp/dist.tar.gz -C /var/www/yingxin/frontend/dist/
rm -f /tmp/dist.tar.gz

cd /var/www/yingxin && git pull origin master
cd backend && uv sync
sudo systemctl restart yingxin-backend

curl -s -o /dev/null -w "forum: HTTP %{http_code}\n" \
  "http://127.0.0.1:8000/api/forum/posts?page=1&page_size=4" \
  -H "Authorization: Bearer invalid"
```

浏览器无痕打开站点，重新登录验证。

---

## 五、防火墙与安全

```bash
# Linux：放行 HTTP
sudo ufw allow 80
# 若使用 HTTPS
sudo ufw allow 443
```

PostgreSQL 端口（5432）只应对本机或内网开放，不要对公网 `0.0.0.0` 暴露。  
内存 ≤2GB 且无 Swap 的机器，建议加 512MB Swap 作兜底。

---

## 六、日常运维

### 6.1 FAQ / 公告 / 社团变更

- 管理员增删改 FAQ 后，服务端自动清进程内缓存，无需手动刷缓存。
- FAQ / 公告 / 社团变更后会异步更新向量；若嵌入 API 当时不可用，见下文「向量库手动重建」。

### 6.2 牧院新生说

- 前端模块「牧院新生说」（`/wall`），无独立后台。
- 系统管理员可在帖子详情页隐藏或删除；置顶见 `backend/docs/ADMIN_GUIDE.md`。

### 6.3 学生名单

Web 端不提供名册管理。首次部署或演示环境执行 `init_db.py`；生产环境新生名单由运维写库或通过脚本导入。

### 6.4 健康检查

`GET /health` 须携带有效 Bearer（见 `backend/docs/FRONTEND_API.md`），无 token 会 401。可用论坛公开接口侧面验证后端存活：

```bash
curl -s -o /dev/null -w "forum: HTTP %{http_code}\n" \
  "http://127.0.0.1:8000/api/forum/posts?page=1&page_size=1"
```

### 6.5 日志

FastAPI 默认输出到 stdout；Docker 部署用 `docker compose logs -f backend`。

### 6.6 开发用脚本（不随 init 执行）

| 脚本 | 用途 |
|------|------|
| `backend/scripts/manage_student_account.py` | 重置密码、管理账号 |
| `backend/scripts/seed_forum_posts.py` | 手动插入论坛测试帖 |

---

## 七、管理员与内容维护

完整说明见 `backend/docs/ADMIN_GUIDE.md`。

### 7.1 向量库手动重建

嵌入 API 就绪后：

```powershell
cd backend
uv run python -c "from app.crud.document import rebuild_documents_best_effort; rebuild_documents_best_effort()"
```

带进度：

```powershell
uv run python -c "from app.db.database import SessionLocal; from app.crud.document import build_documents; db=SessionLocal(); print(build_documents(db, progress=True)); db.close()"
```

---

## 八、服务器配置参考

只跑迎新一套（Nginx 静态前端 + uvicorn + PostgreSQL）时：

| 进程 | 预计内存 |
|------|----------|
| PostgreSQL | ~300–500MB |
| FastAPI（单 worker） | ~150–250MB |
| Nginx | ~30MB |
| 合计 | ~0.8–1.1GB |

DeepSeek 对话与嵌入在云端，不占本地 GPU 或大模型内存。

| 配置 | 说明 |
|------|------|
| 2GB 内存、独享、只跑迎新 | 够用，推荐生产最低配置 |
| 4GB 内存 | 宽裕 |
| 1.6GB 且与其他 Docker 项目共用 | 能跑但不稳，高峰可能卡顿 |

---

## 九、故障排查

| 现象 | 检查 |
|------|------|
| 迁移失败 `vector` 扩展 | DB 镜像是否为 pgvector；`alembic upgrade head` |
| 小信 503 | `XIAOXIN_CHAT_ENABLED`、`DEEPSEEK_API_KEY` |
| 小信答不上 / 无 RAG | `EMBED_API_KEY`、`documents` 是否为空；跑向量重建；可引导至牧院新生说 |
| 前端连不上 API | `BACKEND_CORS_ORIGINS`、Nginx 反代是否指向 `127.0.0.1:8000` |
| 页面仍是旧版 | 无痕窗口；确认 `dist/index.html` 时间为刚上传；**不是**只做了 `git pull` |
| `git fetch` 卡住 / 终端假死 | 国内 ECS 连 GitHub 慢；`Ctrl+C` 中断；改用 scp 传文件或 ghproxy 镜像 |
| 手动 `uv run` 报 Exit 127 | 非交互 shell 无 `uv` PATH；用 `systemctl restart yingxin-backend` |
| 改了后端代码不生效 | 确认改在 `/var/www/yingxin/backend`；restart systemd，不要另起 `nohup uvicorn` |
| 上传后样式乱 / 白屏 | 压缩包目录多一层（7z 压了整个 `dist` 文件夹）；见 4.2 解压检查 |
| 本地正常、线上登录后 401 多 | 后端未更新或未 restart；论坛列表应对无效 token 返回 200 |
| Docker backend 连不上 DB | `.env` 中 `DATABASE_URL` 主机名是否为 `db`（非 127.0.0.1） |
