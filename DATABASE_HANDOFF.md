# 数据库交付说明

本压缩包包含一份 PostgreSQL 数据导出文件：

```text
database_dump.sql
```

## 数据来源

导出来源为本机 Docker 容器：

```text
yingxin-db-1
```

数据库：

```text
welcome_db
```

## 当前导出数据量

```text
alembic_version: 1
announcements: 4
clubs: 1
documents: 0
faq: 12
students: 5
```

## 恢复方式

如果使用 Docker Compose 启动 PostgreSQL，并且数据库用户名、库名保持默认：

```bash
psql -U welcome -d welcome_db -f database_dump.sql
```

如果在 Docker 容器中恢复，可以使用：

```bash
docker exec -i <postgres_container_name> psql -U welcome -d welcome_db < database_dump.sql
```

例如：

```bash
docker exec -i yingxin-db-1 psql -U welcome -d welcome_db < database_dump.sql
```

## 注意事项

- `database_dump.sql` 包含表结构和当前业务数据。
- 交付包不包含真实 `.env`，请复制 `backend/.env.example` 后按本地环境创建 `backend/.env`。
- 默认本地 PostgreSQL 映射端口为 `5432`，对应 `DATABASE_URL` 中的 `localhost:5432`。
- 如果你临时改过 Docker 端口映射，需要同步修改 `DATABASE_URL`。
