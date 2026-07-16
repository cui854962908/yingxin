// 迎新时间轴 — 依据 2026~2027 学年校历
export interface Milestone {
  id: string
  date: string
  title: string
  icon: string
}

export interface ServiceCard {
  id: string; icon: string; title: string; desc: string
  link?: string  // 可选外部跳转链接，有则新标签页打开
}

/** 2026 级新生报到日（校历备注第 2 条） */
export const REGISTER_DATE = '2026-09-12'

// ===== 迎新关键节点（2026 级新生） =====
export const MILESTONES: Milestone[] = [
  { id: 'fee',        date: '2026-08-25', title: '学费缴纳',      icon: 'card' },
  { id: 'dorm',       date: '2026-09-01', title: '宿舍准备',      icon: 'home' },
  { id: 'register',   date: '2026-09-12', title: '新生报到',      icon: 'letter' },
  { id: 'orient',     date: '2026-09-14', title: '入学教育·军训', icon: 'flag' },
  { id: 'orient-end', date: '2026-09-30', title: '军训结束',      icon: 'medal' },
  { id: 'class',      date: '2026-10-08', title: '正式上课',      icon: 'book' },
]

// ===== 功能入口 =====
export const SERVICE_CARDS: ServiceCard[] = [
  { id: 'notice',  icon: 'notice',  title: '报到须知',   desc: '报到流程、所需材料及注意事项' },
  { id: 'dorm',    icon: 'dorm',    title: '宿舍选择',   desc: '在线选择宿舍楼栋及床位', link: 'http://51.weihouqin.cn:51806/ybd/' },
  { id: 'fee',     icon: 'fee',     title: '新生缴费',   desc: '统一支付平台缴纳学杂费', link: 'http://cwcpt.hnuahe.edu.cn/xysf/aAppPage/index.aspx?mac=5E4A28FDB3CE185F0ED09BF017CC1CEB#/loginTemp/loginIng' },
  { id: 'course',  icon: 'course',  title: '选课系统',   desc: '教务管理系统选课与课表', link: 'http://jiaowu.hnuahe.edu.cn/' },
  { id: 'map',     icon: 'map',     title: '校园导览',   desc: '教学楼、食堂、宿舍位置' },
  { id: 'web',     icon: 'web',     title: '学校官网',   desc: '河南牧业经济学院网上服务大厅', link: 'http://ehall.hnuahe.edu.cn/' },
  { id: 'tips',    icon: 'tips',    title: '新生攻略',   desc: '在校常用 App 图标一览' },
  { id: 'ai',      icon: 'ai',      title: 'AI迎新助手', desc: '基于迎新知识库的智能问答，答不上可去牧院新生说' },
]
