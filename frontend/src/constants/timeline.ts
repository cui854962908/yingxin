// 迎新时间轴 & 功能入口 — 占位数据，后续可替换为 /api/timeline 接口
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

// ===== 特殊事件节点 =====
export const MILESTONES: Milestone[] = [
  { id: 'admit',     date: '2026-07-20', title: '录取结果',    icon: 'letter' },
  { id: 'fee',       date: '2026-08-20', title: '学费缴纳',    icon: 'card' },
  { id: 'dorm',      date: '2026-08-28', title: '宿舍选择',    icon: 'home' },
  { id: 'health',    date: '2026-09-01', title: '入学体检',    icon: 'heart' },
  { id: 'uniform',   date: '2026-09-04', title: '军训服领取',  icon: 'shirt' },
  { id: 'ceremony',  date: '2026-09-06', title: '开学典礼',    icon: 'star' },
  { id: 'military',  date: '2026-09-08', title: '军训开始',    icon: 'flag' },
  { id: 'parade',    date: '2026-09-20', title: '军训汇演',    icon: 'check' },
  { id: 'class',     date: '2026-09-22', title: '正式上课',    icon: 'book' },
]

export const REGISTER_DATE = '2026-09-06'

// ===== 功能入口 =====
export const SERVICE_CARDS: ServiceCard[] = [
  { id: 'notice',  icon: 'notice',  title: '报到须知',   desc: '报到流程、所需材料及注意事项' },
  { id: 'dorm',    icon: 'dorm',    title: '宿舍选择',   desc: '在线选择宿舍楼栋及床位', link: 'http://51.weihouqin.cn:51806/ybd/' },
  { id: 'fee',     icon: 'fee',     title: '新生缴费',   desc: '统一支付平台缴纳学杂费', link: 'http://cwcpt.hnuahe.edu.cn/xysf/aAppPage/index.aspx?mac=5E4A28FDB3CE185F0ED09BF017CC1CEB#/loginTemp/loginIng' },
  { id: 'course',  icon: 'course',  title: '选课系统',   desc: '教务管理系统选课与课表', link: 'http://jiaowu.hnuahe.edu.cn/' },
  { id: 'map',     icon: 'map',     title: '校园导览',   desc: '教学楼、食堂、宿舍位置' },
  { id: 'web',     icon: 'web',     title: '学校官网',   desc: '河南牧业经济学院网上服务大厅', link: 'http://ehall.hnuahe.edu.cn/' },
  { id: 'tips',    icon: 'tips',    title: '新生攻略',   desc: '校园生活指南、快递地址、食堂分布' },
  { id: 'ai',      icon: 'ai',      title: 'AI迎新助手', desc: '基于迎新知识库的智能问答，答不上可去问牧墙' },
]
