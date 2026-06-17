# 社团 & 公告模块 API 文档

> 统一响应格式：`{ success: boolean, message: string, data: T | null }`

---

## 一、社团模块 (Clubs)

### 公开接口（无需登录）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/clubs` | 获取社团列表（按拼音首字母排序） |
| GET | `/api/clubs/{club_id}` | 获取单个社团详情 |

### 管理员接口

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| POST | `/api/admin/clubs` | admin / club_admin | 创建社团 |
| PUT | `/api/admin/clubs/{club_id}` | admin / club_admin | 更新社团（club_admin 只能改自己的） |
| DELETE | `/api/admin/clubs/{club_id}` | admin | 删除社团（仅超管） |
| PATCH | `/api/admin/clubs/{club_id}/status` | admin / club_admin | 修改招募状态 |
| POST | `/api/admin/clubs/upload-image` | admin / club_admin | 上传社团图片 |

### 社团字段 (ClubItem)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 社团名称 |
| category | string | 分类（信工团学会 / 校级组织 / 兴趣社团） |
| intro | string | 一句话简介 |
| description | string? | 详细介绍（支持 HTML） |
| status | string | 招新中 / 已结束（根据招募时段自动计算） |
| cover_image | string? | 团徽 URL |
| hero_image | string? | 封面大图 URL |
| activity_photos | string? | 风采照片 JSON 数组（最多 10 张） |
| honor | string? | 荣誉描述 |
| founded_year | int? | 成立年份 |
| member_count | int? | 成员数 |
| advisor_name | string? | 指导老师 |
| leader_name | string? | 社长 |
| leaders | string? | 社长数组 JSON `[{name, phone}]` |
| qq_group | string? | QQ 群号 |
| wechat_qr | string? | QQ 群二维码 URL |
| recruit_start | date? | 招新开始日期 |
| recruit_end | date? | 招新结束日期 |
| owner_student_id | int? | 社团管理员 student id |
| updated_at | datetime? | 更新时间 |

### 创建 / 更新社团

```
POST /api/admin/clubs
PUT  /api/admin/clubs/{club_id}
Content-Type: application/json

{
  name: string (必填)
  category: string (必填)
  intro: string (必填)
  status?: string           // 默认 "招新中"
  cover_image?: string
  hero_image?: string
  description?: string
  activity_photos?: string  // JSON 数组字符串，≤ 10 张
  honor?: string
  founded_year?: int
  member_count?: int
  advisor_name?: string
  leader_name?: string
  qq_group?: string
  wechat_qr?: string
  recruit_start?: date
  recruit_end?: date
}
```

### 修改状态

```
PATCH /api/admin/clubs/{club_id}/status
Content-Type: application/json

{ "status": "招新中" | "已结束" }
```

### 上传图片

```
POST /api/admin/clubs/upload-image
Content-Type: multipart/form-data
Body: file (支持 .png / .jpg / .jpeg / .gif / .webp / .svg)

Response: { success: true, data: { url: "/static/uploads/clubs/xxx.png" } }
```

---

## 二、公告模块 (Announcements)

### 公开接口（无需登录）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/announcements` | 获取公告列表（按日期降序），可选 `?category=` 筛选 |

### 管理员接口（需 admin）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/announcements` | 发布公告 |
| PATCH | `/api/admin/announcements/{ann_id}` | 更新公告（仅更新传入字段） |
| DELETE | `/api/admin/announcements/{ann_id}` | 删除公告 |

### 公告字段 (AnnouncementItem)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | string | 标题 |
| content | string | 正文 |
| date | date? | 公告日期 |
| category | string? | 分类（guide=报到须知 / tips=新生攻略 / 留空=普通公告） |

### 创建公告

```
POST /api/admin/announcements
Content-Type: application/json

{
  title: string (必填)
  content: string (必填)
  date?: date        // 不传则默认当天
  category?: string  // guide | tips | 其他
}
```

### 更新公告

```
PATCH /api/admin/announcements/{ann_id}
Content-Type: application/json

{
  title?: string
  content?: string
  date?: date
  category?: string
}
// 仅更新传入字段，未传字段保留原值
```

---

## 三、两个模块对比

| | 社团 (Clubs) | 公告 (Announcements) |
|------|------|------|
| 公开列表 | GET /api/clubs | GET /api/announcements?category= |
| 公开详情 | GET /api/clubs/{id} | — |
| 创建 | POST /api/admin/clubs | POST /api/admin/announcements |
| 更新 | PUT /api/admin/clubs/{id} | PATCH /api/admin/announcements/{id} |
| 删除 | DELETE /api/admin/clubs/{id} | DELETE /api/admin/announcements/{id} |
| 额外接口 | 状态修改 / 图片上传 | — |
| 鉴权差异 | admin + club_admin | 仅 admin |
