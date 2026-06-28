/**
 * 产品定位 · 全站文案单一来源
 * 与 CONTEXT.md「产品定位」章节保持一致
 */

export const PRODUCT_NAME = '2026 迎新门户'

/** 一句话定位（登录页、侧栏、认识牧院顶栏） */
export const PRODUCT_TAGLINE = '认识牧院 · 指导报到 · 智能答疑'

/** 新生互助论坛（路由 /wall） */
export const FORUM_MODULE_NAME = '牧院新生说'

/** 面向谁、解决什么 */
export const PRODUCT_POSITIONING =
  '面向 2026 级新生与家长：帮助了解学校与学院、准备报到入学，并通过 FAQ、小信 AI 与牧院新生说获取答疑与互助。'

/** 明确边界，避免被当成学籍系统 */
export const PRODUCT_BOUNDARY =
  '本系统不是学籍/名册管理平台。学生名单由运维脚本导入，网页端仅做身份校验与个人报到信息展示；内容在 FAQ、公告与认识牧院模块维护。'

/** 三大能力柱（对应首页入口与模块划分） */
export const PRODUCT_PILLARS = [
  { id: 'intro', title: '认识牧院', desc: '学校大百科、学院介绍、社团文化' },
  { id: 'guide', title: '报到指导', desc: '报到须知、新生攻略、校园导览' },
  { id: 'qa', title: '答疑互助', desc: 'FAQ 知识库、小信 AI、牧院新生说' },
] as const

export const GUEST_ENTRY_LABEL = '游客浏览 · 先看学校与学院介绍'

export const GUEST_ROLE_LABEL = '访客 · 迎新门户'

/** 游客身份卡片状态文案 */
export const GUEST_PROFILE_STATUS = '正在游客浏览中'
export const GUEST_PROFILE_HINT = '登录后可查看学号、宿舍与联系人信息'

/** 3D 校园漫游标注试用版；2D / 3D 由用户在导览入口自行选择 */
export const CAMPUS_3D_TRIAL_LABEL = '试用版'
export const CAMPUS_3D_TRIAL_NOTE =
  '功能持续完善中，建议在 Wi‑Fi 与较新浏览器下体验'
