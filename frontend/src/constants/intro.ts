/** 认识牧院 · 学院介绍配置 */

export const INTRO_SCHOOL = '河南牧业经济学院'

/** 牧院大百科 · 学校级介绍（事实来源：学校官网 hnuahe.edu.cn / 学校章程） */
export const INTRO_WIKI_TAGLINE = '尚严崇实 · 善知敏行'
export const INTRO_WIKI_CATEGORY = 'intro_campus_wiki'
export const INTRO_WIKI_HERO_IMAGE = '/campus-official/hero-longzi-gate.webp'
export const INTRO_WIKI_OFFICIAL_URL = 'https://www.hnuahe.edu.cn'

/** 首页亮点数据（官网学校概况，占地等为约数展示） */
export const INTRO_WIKI_STATS = [
  { label: '办学渊源', value: '1957年' },
  { label: '校区', value: '3个' },
  { label: '占地', value: '约191万㎡' },
] as const

export const INTRO_WIKI_CAMPUSES = [
  {
    id: 'longzi',
    name: '龙子湖校区',
    tag: '主校区',
    address: '郑州市郑东新区龙子湖北路6号',
    image: '/campus-official/campus-longzi-library.webp',
  },
  {
    id: 'yingcai',
    name: '英才校区',
    tag: '惠济',
    address: '郑州市惠济区英才街2号',
    image: '/campus-official/campus-yingcai-gate.webp',
  },
  {
    id: 'beilin',
    name: '北林校区',
    tag: '金水',
    address: '郑州市金水区北林路16号',
    image: '/campus-official/campus-beilin-aerial.webp',
  },
] as const

export const INTRO_WIKI_FALLBACK = [
  {
    title: '学校简介',
    content:
      '<p>河南牧业经济学院位于河南省郑州市，由原郑州牧业工程高等专科学校（1957年建校）与原河南商业高等专科学校（1960年建校）于2013年合并组建，是河南省人民政府举办的省属公办全日制普通本科院校。</p>' +
      '<p>学校坚持「区域性、行业性、开放型、应用型」办学定位，立足河南、面向行业，为现代农牧业、食品加工业、商贸物流业等培养应用型人才。官网：<a href="https://www.hnuahe.edu.cn" target="_blank" rel="noopener">www.hnuahe.edu.cn</a></p>' +
      '<p><img src="/campus-official/campus-longzi-scenery.webp" alt="龙子湖校区校园风光" /></p>',
  },
  {
    title: '校训与校风',
    content:
      '<p><strong>校训：尚严崇实，善知敏行。</strong></p>' +
      '<p>「尚严」强调严密严谨的治学与管理；「崇实」倡导求真务实；「善知敏行」鼓励求知与实践并重。以上表述摘自学校章程与官网公开信息。</p>',
  },
  {
    title: '办学实力',
    content:
      '<p>据学校官网公开数据：总占地面积约191.3万平方米，教学科研仪器设备总值约2.77亿元，馆藏纸质图书约299.7万册；建有龙子湖、英才、北林三个校区及多个实训与科研平台。</p>' +
      '<p><img src="/campus-official/campus-yingcai-lake.webp" alt="英才校区风景湖" /></p>',
  },
]

/** 学院详情页内嵌社团的筛选规则（稍后按学院配置 clubIds） */
export interface IntroClubFilter {
  /** 精确指定社团 ID，非空时优先生效 */
  clubIds?: string[]
  /** 按社团 category 临时筛选，clubIds 配齐后可留空 */
  categories?: string[]
}

export interface IntroCollegeConfig {
  id: string
  college: string
  shortName: string
  tagline: string
  /** 列表卡片摘要 */
  summary: string
  coverImage?: string
  /** 详情页亮点数据（静态配置，后续可接 API） */
  stats: { label: string; value: string }[]
  overviewCategory: string
  facultyCategory: string
  overviewFallback: { title: string; content: string }[]
  facultyFallback: { title: string; content: string }[]
  /** 详情页「社团招新」区块展示哪些社团 */
  clubFilter: IntroClubFilter
}

export const INTRO_COLLEGES: IntroCollegeConfig[] = [
  {
    id: 'sie',
    college: '信息工程学院',
    shortName: '信工',
    tagline: '尚严崇实 · 善知敏行',
    summary: '涵盖计算机、软件工程、物联网等方向，注重工程实践与创新能力。',
    coverImage: '/campus-official/campus-longzi-scenery.webp',
    stats: [
      { label: '本科专业', value: '6+' },
      { label: '在校生', value: '3000+' },
      { label: '实践基地', value: '10+' },
    ],
    overviewCategory: 'intro_sie_overview',
    facultyCategory: 'intro_sie_faculty',
    overviewFallback: [
      {
        title: '学院简介',
        content:
          '<p>信息工程学院是河南牧业经济学院重点建设的工科学院，面向信息技术与数字经济培养应用型人才。</p>' +
          '<p>学院坚持「尚严崇实、善知敏行」院训，重视课程与实践相结合。</p>',
      },
      {
        title: '培养特色',
        content:
          '<ul><li>项目驱动教学，强化动手能力</li><li>校企协同，提供实习与竞赛平台</li><li>关注就业与升学双线发展</li></ul>',
      },
    ],
    facultyFallback: [
      {
        title: '示例教师',
        content: '在 intro_sie_faculty 分类下维护师资：标题为姓名，正文为简介，可插图。',
      },
    ],
    // 待提供各社团隶属学院后，改为 clubIds: ['uuid-1', ...]
    clubFilter: { categories: ['信工团学会'] },
  },
]

export function getIntroCollege(id: string): IntroCollegeConfig | undefined {
  return INTRO_COLLEGES.find((c) => c.id === id)
}

/** 按学院配置筛出应展示的社团 */
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

/** 顶栏 Tab */
export const INTRO_TABS = [
  { id: 'wiki', label: '牧院大百科', path: '/intro/wiki' },
  { id: 'colleges', label: '学院概况', path: '/intro/colleges' },
  { id: 'clubs', label: '社团招新', path: '/intro/clubs' },
] as const

/** @deprecated */
export const INTRO_COLLEGE = INTRO_COLLEGES[0]
export const INTRO_CATEGORY_OVERVIEW = INTRO_COLLEGE.overviewCategory
export const INTRO_CATEGORY_FACULTY = INTRO_COLLEGE.facultyCategory
export const INTRO_FALLBACK_OVERVIEW = INTRO_COLLEGE.overviewFallback
export const INTRO_FALLBACK_FACULTY = INTRO_COLLEGE.facultyFallback
