/** 认识牧院 · 学院介绍配置 */

export const INTRO_SCHOOL = '河南牧业经济学院'

/** 牧院大百科 · 学校级介绍 */
export const INTRO_WIKI_TAGLINE = '尚严崇实 · 善知敏行'
export const INTRO_WIKI_CATEGORY = 'intro_campus_wiki'
export const INTRO_WIKI_HERO_IMAGE = '/campus-official/hero-longzi-gate.webp'
export const INTRO_WIKI_OFFICIAL_URL = 'https://www.hnuahe.edu.cn'

/** 首页亮点数据 */
export const INTRO_WIKI_STATS = [
  { label: '办学渊源', value: '1957年' },
  { label: '校区', value: '3个' },
  { label: '占地', value: '约191万㎡' },
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
    address: '郑州市惠济区英才街2号',
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
    address: '郑州市惠济区英才街2号',
    heroImage: '/campus-official/campus-yingcai-gate.webp',
    cardImage: '/campus-official/campus-yingcai-gate.webp',
    tagline: '商科底蕴 · 应用型培养',
    summary:
      '英才校区延续原河南商业高等专科学校办学积淀，商科与应用型人才培养特色鲜明；信息工程学院（软件学院）日常教学与实验实训主要在此，学子广场与风景湖是标志性景观。',
    stats: [
      { label: '所在区域', value: '惠济区' },
      { label: '前身渊源', value: '商专' },
      { label: '标志景观', value: '风景湖' },
    ],
    overview:
      '英才校区位于郑州市惠济区英才街2号，保留了原河南商业高等专科学校（1960年建校）的教学与生活传统，在商贸、经管等学科方向积淀深厚。' +
      '校区与龙子湖、北林校区共同构成学校「一校三区」布局。信息工程学院（软件学院）及多数信工类新生的课程、实验、竞赛与社团活动主要在此校区完成。' +
      '学子广场、风景湖、教学楼群与实验楼共同构成日常学习动线，周边高校聚集，餐饮、购物与公交出行较为方便。',
    features: [
      '商科与应用型人才培养的重要基地，经管类学科在此有长期办学传统',
      '信息工程学院（软件学院）日常教学、60 余个实验实训室及华为 ICT 学院等产教平台主要在此',
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

export const INTRO_WIKI_FALLBACK = [
  {
    title: '学校简介',
    content:
      '<p>河南牧业经济学院位于河南省郑州市，由原郑州牧业工程高等专科学校（1957年建校）与原河南商业高等专科学校（1960年建校）于2013年合并组建，是河南省人民政府举办的省属公办全日制普通本科院校。</p>' +
      '<p>学校坚持「区域性、行业性、开放型、应用型」办学定位，立足河南、面向行业，紧密对接现代农牧业、食品加工业、商贸物流业与数字经济发展需要，培养能在一线岗位快速上手、持续成长的应用型人才。</p>' +
      '<p>现设有龙子湖、英才、北林三个校区，总占地面积约191.3万平方米；学科专业覆盖农、经、管、工、文、法等多个门类，形成以牧业为特色、经管优势突出、多学科协调发展的办学格局。更多信息见官网：<a href="https://www.hnuahe.edu.cn" target="_blank" rel="noopener">www.hnuahe.edu.cn</a></p>' +
      '<p><img src="/campus-official/campus-longzi-scenery.webp" alt="龙子湖校区校园风光" /></p>',
  },
  {
    title: '校训与校风',
    content:
      '<p><strong>校训：尚严崇实，善知敏行。</strong></p>' +
      '<p>「尚严」强调严密严谨的治学态度与管理规范，引导师生在学业与工作中追求标准与质量；「崇实」倡导求真务实、脚踏实地，反对浮躁与空谈；「善知敏行」鼓励主动求知、勤于实践，把课堂所学转化为解决实际问题的能力。</p>' +
      '<p>学校注重课堂教学、实验实训、学科竞赛与社会实践相结合，鼓励同学们早进实验室、早进项目、早进团队，在真实场景中锻炼专业素养与协作能力。三校区各具特色：龙子湖开阔现代、英才商科底蕴深厚、北林牧科传统鲜明，共同构成牧院多元而统一的校园文化。</p>' +
      '<p><img src="/campus-official/campus-yingcai-lake.webp" alt="英才校区风景湖" /></p>',
  },
  {
    title: '办学实力',
    content:
      '<p>学校现有21个二级教学单位、53个本科专业，拥有动物科学国家级一流本科专业建设点，以及动物医学、食品科学与工程、财务管理等11个省级一流本科专业建设点。教学科研仪器设备总值约2.77亿元，馆藏纸质图书约299.7万册。</p>' +
      '<p>学校与行业龙头企业共建智慧牧业、食品、预制菜、冷链物流、数智财金等产业学院，推进产教融合与校企协同育人；信息工程学院（软件学院）与华为等企业共建 ICT 学院，为信息技术类人才培养提供工程化平台。</p>' +
      '<p>对新生而言，可先通过本模块了解三校区分工与到校路线，再按学院指引熟悉本专业主要上课与实验地点，报到前准备好证件、生活用品与常用 App（地图、校园服务类），能更从容地开启大学阶段。</p>' +
      '<p><img src="/campus-official/campus-longzi-library.webp" alt="龙子湖校区图书馆" /></p>',
  },
]

export interface IntroClubFilter {
  clubIds?: string[]
  categories?: string[]
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
    college: '信息工程学院（软件学院）',
    shortName: '信工',
    tagline: '河南省特色化示范性软件学院',
    summary:
      '位于英才校区，开设软件工程、物联网工程等 5 个本科专业，建有 60 余个实验实训室，与华为共建 ICT 学院，注重项目驱动教学与学科竞赛，培养能落地、能协作的信息技术应用型人才。',
    coverImage: '/campus-official/campus-yingcai-lake.webp',
    officialUrl: 'https://xxdz.hnuahe.edu.cn',
    stats: [
      { label: '本科专业', value: '5个' },
      { label: '实验实训室', value: '60余个' },
      { label: '产教融合', value: '华为ICT学院' },
    ],
    overviewCategory: 'intro_sie_overview',
    facultyCategory: 'intro_sie_faculty',
    overviewFallback: [
      {
        title: '学院简介',
        content:
          '<p>信息工程学院（软件学院）是河南牧业经济学院二级教学单位，学院官网：<a href="https://xxdz.hnuahe.edu.cn" target="_blank" rel="noopener">xxdz.hnuahe.edu.cn</a>。学院面向信息技术与数字经济，培养具备工程实践、团队协作与创新创业能力的应用型专门人才，是河南省特色化示范性软件学院建设依托单位。</p>' +
          '<p>学院位于<strong>英才校区</strong>（郑州市惠济区英才街2号），信工类新生的专业课程、上机实验、课程设计、学科竞赛集训与多数团学活动均在此校区完成。日常动线一般为「教学楼 — 实验楼 — 图书馆/自习 — 学子广场」，开学第一周建议熟悉各楼栋位置与机房开放时间。</p>' +
          '<p>学院现开设<strong>软件工程、物联网工程、数据科学与大数据技术、数字媒体技术、智慧牧业科学与工程</strong>等 5 个本科专业，兼顾通用信息技术能力与学校牧业学科交叉特色，便于同学们在就业时向软件开发、数据应用、物联网集成、数字内容或智慧农业信息化等方向拓展。</p>' +
          '<p><img src="/campus-official/campus-yingcai-lake.webp" alt="英才校区风景湖" class="intro-inline-photo" /></p>',
      },
      {
        title: '办学特色',
        content:
          '<ul>' +
          '<li>被河南省教育厅确定为<strong>特色化示范性软件学院</strong>，软件人才培养方案强调工程化与项目化</li>' +
          '<li>与华为技术有限公司、深圳市讯方技术股份有限公司联合成立<strong>华为 ICT 学院</strong>，开展认证培训与工程实践</li>' +
          '<li>与黄河科技集团创新有限公司联合成立<strong>鲲鹏产业学院</strong>，对接国产化算力与软件开发生态</li>' +
          '<li>建有 60 余个实验实训室，占地 5300 余平方米，仪器设备总值约 3000 万元，覆盖软件开发、网络、大数据、物联网、数字媒体等方向</li>' +
          '<li>注重「课赛结合」：鼓励参与蓝桥杯、中国大学生计算机设计大赛、华为 ICT 大赛等，以赛促学、以赛促练</li>' +
          '<li>校企协同：部分课程引入企业导师与真实项目案例，帮助同学们提前了解行业工作流程与交付标准</li>' +
          '<li>结合牧院学科优势，智慧牧业科学与工程专业面向现代牧场、食品冷链、农业信息化等场景培养交叉型人才</li>' +
          '</ul>',
      },
      {
        title: '专业方向',
        content:
          '<p><strong>软件工程</strong>：面向 Web/移动端应用、企业信息化系统与软件项目管理，核心能力包括需求分析、架构设计、编码实现、测试与运维；适合希望从事后端、全栈或项目协调岗位的同学。</p>' +
          '<p><strong>数据科学与大数据技术</strong>：聚焦数据采集、清洗、存储、分析与可视化，结合 Python/SQL/大数据组件完成业务分析任务；适合数据分析、数据开发、商业智能等方向。</p>' +
          '<p><strong>物联网工程</strong>：融合嵌入式、传感器、通信网络与云平台，完成设备接入、数据采集与远程控制；适合智能硬件、工业互联网、智慧校园等场景。</p>' +
          '<p><strong>数字媒体技术</strong>：涵盖图形图像、音视频、交互设计与前端呈现，培养数字内容制作与多媒体系统开发能力；适合 UI/UX、新媒体技术、游戏与互动展示等方向。</p>' +
          '<p><strong>智慧牧业科学与工程</strong>：将信息技术应用于现代牧业生产与管理，涉及养殖环境监控、生产数据分析、牧业信息化系统等；体现学校办学特色，适合对「IT + 农牧」交叉领域感兴趣的同学。</p>' +
          '<p>入学后可通过学院官网、辅导员与专业负责人介绍进一步了解各专业的培养方案、核心课程与毕业去向，第一学期重点打好数学、英语与编程基础。</p>',
      },
    ],
    facultyFallback: [
      {
        title: '师资概况',
        content:
          '<p>学院拥有一支结构合理、工程经验丰富的师资队伍，涵盖软件工程、大数据、物联网、数字媒体与智慧牧业信息化等方向。许多教师具有企业研发或项目交付背景，承担专业课、课程设计、毕业设计与大学生创新创业项目指导。</p>' +
          '<p>教学中强调「能讲清原理、能带队做项目」：既有理论讲授，也有实验、实训与竞赛辅导；同学们可在 office hour、实验室开放时间与导师沟通学习路径与竞赛选题。</p>' +
          '<p>具体教师名单与研究方向以学院官网及开学后公布的信息为准；本页「师资队伍」栏目可在迎新期间持续更新。</p>',
      },
    ],
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

export const INTRO_TABS = [
  { id: 'wiki', label: '牧院大百科', shortLabel: '大百科', path: '/intro/wiki' },
  { id: 'colleges', label: '学院概况', shortLabel: '学院', path: '/intro/colleges' },
  { id: 'clubs', label: '社团招新', shortLabel: '社团', path: '/intro/clubs' },
] as const

/** @deprecated */
export const INTRO_COLLEGE = INTRO_COLLEGES[0]
export const INTRO_CATEGORY_OVERVIEW = INTRO_COLLEGE.overviewCategory
export const INTRO_CATEGORY_FACULTY = INTRO_COLLEGE.facultyCategory
export const INTRO_FALLBACK_OVERVIEW = INTRO_COLLEGE.overviewFallback
export const INTRO_FALLBACK_FACULTY = INTRO_COLLEGE.facultyFallback
