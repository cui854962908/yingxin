/** 认识牧院 · 学院介绍配置 */

import {
  INTRO_SIE_FACULTY_FALLBACK,
  INTRO_SIE_OVERVIEW_FALLBACK,
} from './intro-sie-fallbacks'
export { INTRO_WIKI_FALLBACK, INTRO_WIKI_HIGHLIGHTS } from './intro-wiki-fallbacks'

export const INTRO_SCHOOL = '河南牧业经济学院'

/** 牧院大百科 · 学校级介绍 */
export const INTRO_WIKI_TAGLINE = '尚严崇实 · 善知敏行'
export const INTRO_WIKI_CATEGORY = 'intro_campus_wiki'
export const INTRO_WIKI_HERO_IMAGE = '/campus-official/hero-longzi-gate.webp'
export const INTRO_WIKI_OFFICIAL_URL = 'https://www.hnuahe.edu.cn'

/** 首页亮点数据 */
export const INTRO_WIKI_STATS = [
  { label: '办学渊源', value: '1957年' },
  { label: '本科专业', value: '53个' },
  { label: '全日制在校生', value: '3万余' },
] as const

export const INTRO_WIKI_CAMPUSES = [
  {
    id: 'longzi',
    name: '龙子湖校区',
    tag: '郑东新区',
    address: '郑州市郑东新区龙子湖北路6号',
    image: '/campus-official/campus-longzi-library.webp',
  },
  {
    id: 'yingcai',
    name: '英才校区',
    tag: '惠济区',
    address: '郑州市惠济区英才街146号',
    image: '/campus-official/campus-yingcai-gate.webp',
  },
  {
    id: 'beilin',
    name: '北林校区',
    tag: '金水区',
    address: '郑州市金水区北林路16号',
    image: '/campus-official/campus-beilin-aerial.webp',
  },
] as const

export type IntroCampusId = (typeof INTRO_WIKI_CAMPUSES)[number]['id']

export interface IntroCampusConfig {
  id: IntroCampusId
  name: string
  tag: string
  address: string
  heroImage: string
  cardImage: string
  tagline: string
  summary: string
  stats: { label: string; value: string }[]
  overview: string
  features: string[]
  facilities: string[]
  transport: string
  gallery: { src: string; caption: string }[]
}

export const INTRO_CAMPUSES: IntroCampusConfig[] = [
  {
    id: 'longzi',
    name: '龙子湖校区',
    tag: '郑东新区',
    address: '郑州市郑东新区龙子湖北路6号',
    heroImage: '/campus-official/hero-longzi-gate.webp',
    cardImage: '/campus-official/campus-longzi-library.webp',
    tagline: '行政中心 · 教学主阵地',
    summary:
      '龙子湖校区是学校主校区，承担大部分本科教学与行政管理，图书馆、实验实训与文体设施集中，是新生认识牧院的第一站。',
    stats: [
      { label: '所在区域', value: '郑东新区' },
      { label: '校区定位', value: '主校区' },
      { label: '毗邻', value: '龙子湖' },
    ],
    overview:
      '龙子湖校区位于郑州市郑东新区龙子湖北路6号，为河南牧业经济学院主校区。2013年两校合并组建本科院校后，学校行政、教务与大部分本科专业的日常教学、科研与管理工作在此集中开展。' +
      '校区规划现代开阔，与龙子湖高校园区、龙子湖湿地公园相邻，周边高校与商业配套成熟，学习、实习与生活条件便利。' +
      '新生报到、学籍注册、大型校级活动多在此校区进行，是了解牧院整体面貌的首选入口。',
    features: [
      '学校行政与综合教学功能最集中的校区，校级职能部门与主要教学单位多在此办公',
      '图书馆、综合实验楼、体育场馆、学生公寓与双餐厅（醒园、随园）等核心资源配套齐全',
      '龙子湖高校园区地铁、公交覆盖较好，毗邻龙子湖湿地与高校聚集区，课余生活选择丰富',
      '承担多数经管、牧工、文法等专业的理论课程与公共课教学，跨校区选课需留意课表地点',
      '开学季校门口与周边道路车流较大，建议提前规划路线并预留步行入校时间',
    ],
    facilities: [
      '醒园（第一餐厅）',
      '随园（第二餐厅）',
      '图书馆与自习空间',
      '综合实验楼',
      '体育馆与运动场地',
      '学生公寓与生活服务点',
      '洗浴中心与校园超市',
      '校医院与健康服务',
    ],
    transport:
      '可乘郑州地铁、公交至龙子湖高校园区，再步行或骑行至龙子湖北路6号。郑东新区道路较宽，高峰时段仍可能拥堵。' +
      '报到季建议使用地图 App 搜索「河南牧业经济学院龙子湖校区」，结合实时路况选择地铁或公交；大件行李较多时可考虑出租车/网约车直达校门。',
    gallery: [
      { src: '/campus-official/hero-longzi-gate.webp', caption: '校区校门' },
      { src: '/campus-official/campus-longzi-library.webp', caption: '图书馆' },
      { src: '/campus-official/campus-longzi-scenery.webp', caption: '校园风光' },
    ],
  },
  {
    id: 'yingcai',
    name: '英才校区',
    tag: '惠济区',
    address: '郑州市惠济区英才街146号',
    heroImage: '/campus-official/campus-yingcai-gate.webp',
    cardImage: '/campus-official/campus-yingcai-gate.webp',
    tagline: '商科底蕴 · 应用型培养',
    summary:
      '英才校区延续原河南商业高等专科学校办学积淀，商科与应用型人才培养特色鲜明；信息工程学院日常教学与实验实训主要在此，学子广场与风景湖是标志性景观。',
    stats: [
      { label: '所在区域', value: '惠济区' },
      { label: '前身渊源', value: '商专' },
      { label: '标志景观', value: '风景湖' },
    ],
    overview:
      '英才校区位于郑州市惠济区英才街146号，保留了原河南商业高等专科学校（1960年建校）的教学与生活传统，在商贸、经管等学科方向积淀深厚。' +
      '校区与龙子湖、北林校区共同构成学校「一校三区」布局。信息工程学院及多数信工类新生的课程、实验、竞赛与社团活动主要在此校区完成。' +
      '学子广场、风景湖、教学楼群与实验楼共同构成日常学习动线，周边高校聚集，餐饮、购物与公交出行较为方便。',
    features: [
      '商科与应用型人才培养的重要基地，经管类学科在此有长期办学传统',
      '信息工程学院日常教学、60 余个实验实训室及华为 ICT 学院等产教平台主要在此',
      '学子广场是集会、社团活动与课余交流的核心场所，风景湖为校园标志性水景',
      'A/B 栋教学楼、综合实验楼与图书馆支撑日常上课、上机与自习需求',
      '惠济区英才街沿线高校与生活配套丰富，适合新生快速熟悉校园周边',
      '部分公共课或跨校区课程可能安排在龙子湖、北林，选课前请核对教室所在校区',
    ],
    facilities: [
      '学子广场',
      'A/B 栋教学楼',
      '综合实验楼与上机机房',
      '信息工程学院实验实训室群',
      '图书馆与电子阅览室',
      '学生公寓与食堂',
      '办公楼与校园服务中心',
      '运动场与篮球场',
      '校园超市与快递点',
    ],
    transport:
      '可乘公交至「英才街」「河南牧业经济学院英才校区」等附近站点，下车后按校内指示牌步行入校。' +
      '惠济区高校开学季人流与车流集中，建议预留 10–15 分钟步行时间；夜间返程请优先选择照明良好、人流较多的主路。',
    gallery: [
      { src: '/campus-official/campus-yingcai-gate.webp', caption: '校区校门' },
      { src: '/campus-official/campus-yingcai-lake.webp', caption: '风景湖' },
    ],
  },
  {
    id: 'beilin',
    name: '北林校区',
    tag: '金水区',
    address: '郑州市金水区北林路16号',
    heroImage: '/campus-official/campus-beilin-aerial.webp',
    cardImage: '/campus-official/campus-beilin-aerial.webp',
    tagline: '牧科传统 · 学科深耕',
    summary:
      '北林校区承继原郑州牧业工程高等专科学校牧科传统，动物科学、食品等学科在此深耕多年，校史馆记录学校数十年沿革，是感受牧院历史底蕴的重要窗口。',
    stats: [
      { label: '所在区域', value: '金水区' },
      { label: '前身渊源', value: '牧专' },
      { label: '特色', value: '牧科' },
    ],
    overview:
      '北林校区位于郑州市金水区北林路16号，是学校历史最悠久的校区之一，延续1957年郑州畜牧兽医学校的办学基因。' +
      '校区布局紧凑实用，综合教学楼、校史馆、图书馆与运动场地齐全，动物科学、食品科学与工程等方向的重要课程、实验与科研活动长期在此开展。' +
      '身处金水区城区，实习、社会实践与城市生活资源便利，适合需要频繁往返市区各点的同学。',
    features: [
      '牧业、动物科学、食品等传统优势学科的重要承载地，专业实验与实训氛围浓厚',
      '校史馆系统展示从牧专、商专到本科院校合并组建的发展历程，值得新生参观',
      '综合教学楼、图书馆与餐厅满足日常教学与生活，篮球场、排球场服务课余锻炼',
      '金水区公交与地铁接驳便利，但城区高峰易拥堵，跨校区通勤请预留时间',
      '部分专业实验课、牧业相关实践平台设在本校区，具体以学院教学安排为准',
    ],
    facilities: [
      '综合教学楼',
      '校史馆',
      '图书馆与资料室',
      '专业实验室与实训场地',
      '学生餐厅',
      '学生公寓',
      '篮球场与排球场',
      '校园医务与后勤服务点',
    ],
    transport:
      '可乘地铁或公交至金水区「北林路」沿线，按导航前往北林路16号。城区道路高峰可能拥堵，建议错峰出行。' +
      '首次到访可搜索「河南牧业经济学院北林校区」，注意与郑州市其他「北林」地名区分；报到当日跟随志愿者指引效率更高。',
    gallery: [
      { src: '/campus-official/campus-beilin-aerial.webp', caption: '校区鸟瞰' },
      { src: '/campus-official/campus-beilin-aerial.webp', caption: '教学区概览' },
    ],
  },
]

export function getIntroCampus(id: string): IntroCampusConfig | undefined {
  return INTRO_CAMPUSES.find((c) => c.id === id)
}

export interface IntroClubFilter {
  clubIds?: string[]
  categories?: string[]
}

export interface IntroClubGroup {
  id: string
  label: string
  subtitle: string
  kind?: 'category' | 'club'
}

export const INTRO_CLUB_GROUP_META: Record<string, { subtitle: string }> = {
  信工团学会: { subtitle: '学院团学组织与各科室、社团' },
  校级组织: { subtitle: '全校性学生组织' },
  兴趣社团: { subtitle: '跨学院兴趣类社团' },
}

export function resolveIntroClubGroups(filter: IntroClubFilter): IntroClubGroup[] {
  if (filter.categories?.length) {
    return filter.categories.map((id) => ({
      id,
      label: id,
      subtitle: INTRO_CLUB_GROUP_META[id]?.subtitle ?? '点击查看下属社团',
      kind: 'category' as const,
    }))
  }
  if (filter.clubIds?.length) {
    return [{ id: '__college__', label: '本院社团', subtitle: '点击查看相关社团', kind: 'category' as const }]
  }
  return []
}

/** 社团介绍 Tab 顶层的组织卡片：信工团学会 + 各校级组织 + 兴趣社团 */
export function resolveIntroTabGroups(
  clubs: { id: string; name: string; category: string; intro?: string }[],
): IntroClubGroup[] {
  const groups: IntroClubGroup[] = [
    {
      id: '信工团学会',
      label: '信工团学会',
      subtitle: INTRO_CLUB_GROUP_META['信工团学会'].subtitle,
      kind: 'category',
    },
  ]

  const schoolOrgs = clubs
    .filter((club) => club.category === '校级组织')
    .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))

  for (const club of schoolOrgs) {
    const intro = club.intro?.trim() ?? ''
    groups.push({
      id: `club:${club.id}`,
      label: club.name,
      subtitle: intro
        ? (intro.length > 40 ? `${intro.slice(0, 40)}…` : intro)
        : INTRO_CLUB_GROUP_META['校级组织'].subtitle,
      kind: 'club',
    })
  }

  groups.push({
    id: '兴趣社团',
    label: '兴趣社团',
    subtitle: INTRO_CLUB_GROUP_META['兴趣社团'].subtitle,
    kind: 'category',
  })

  return groups
}

export interface IntroCollegeConfig {
  id: string
  college: string
  shortName: string
  tagline: string
  summary: string
  coverImage?: string
  officialUrl?: string
  stats: { label: string; value: string }[]
  overviewCategory: string
  facultyCategory: string
  overviewFallback: { title: string; content: string }[]
  facultyFallback: { title: string; content: string }[]
  clubFilter: IntroClubFilter
}

export const INTRO_COLLEGES: IntroCollegeConfig[] = [
  {
    id: 'sie',
    college: '信息工程学院',
    shortName: '信工',
    tagline: '河南省特色化示范性软件学院',
    summary:
      '位于英才校区，开设软件工程、物联网工程、数据科学与大数据技术、数字媒体技术 4 个本科专业，建有 60 余个实验实训室，与华为共建 ICT 学院，注重项目驱动教学与学科竞赛，培养能落地、能协作的信息技术应用型人才。',
    coverImage: '/campus-official/campus-yingcai-lake.webp',
    officialUrl: 'https://xxdz.hnuahe.edu.cn',
    stats: [
      { label: '本科专业', value: '4个' },
      { label: '实验实训室', value: '60余个' },
      { label: '产教融合', value: '华为ICT学院' },
    ],
    overviewCategory: 'intro_sie_overview',
    facultyCategory: 'intro_sie_faculty',
    overviewFallback: [...INTRO_SIE_OVERVIEW_FALLBACK],
    facultyFallback: [...INTRO_SIE_FACULTY_FALLBACK],
    clubFilter: { categories: ['信工团学会'] },
  },
]

export function getIntroCollege(id: string): IntroCollegeConfig | undefined {
  return INTRO_COLLEGES.find((c) => c.id === id)
}

/** 仅配置一个学院时，Tab 直达该学院详情；多个学院时进入列表 */
export function getIntroCollegeTabPath(): string {
  return INTRO_COLLEGES.length === 1
    ? `/intro/${INTRO_COLLEGES[0].id}`
    : '/intro/colleges'
}

export function filterClubsForCollege<T extends { id: string; category: string }>(
  all: T[],
  filter: IntroClubFilter,
): T[] {
  if (filter.clubIds?.length) {
    const ids = new Set(filter.clubIds)
    return all.filter((c) => ids.has(c.id))
  }
  if (filter.categories?.length) {
    const cats = new Set(filter.categories)
    return all.filter((c) => cats.has(c.category))
  }
  return []
}

export function filterClubsByIntroGroupId<T extends { id: string; category: string }>(
  all: T[],
  groupId: string,
  filter?: IntroClubFilter,
): T[] {
  if (groupId.startsWith('club:')) {
    const clubId = groupId.slice(5)
    return all.filter((club) => club.id === clubId)
  }
  const scoped = filter ? filterClubsForCollege(all, filter) : all
  if (groupId === '__college__') return scoped
  return scoped.filter((club) => club.category === groupId)
}

export const INTRO_TABS = [
  { id: 'wiki', label: '牧院大百科', shortLabel: '大百科', path: '/intro/wiki' },
  { id: 'colleges', label: '学院介绍', shortLabel: '学院', path: '/intro/colleges' },
  { id: 'clubs', label: '社团介绍', shortLabel: '社团', path: '/intro/clubs' },
] as const
