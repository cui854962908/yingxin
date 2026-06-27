import type { CampusCategory, CampusPlace } from './types'
import { campusXzToLngLat, haversineMeters } from './campusGeo'
import { createDormPlaces } from './campusPlaceDorms'

function xz(x: number, z: number): [number, number] {
  return campusXzToLngLat(x, z)
}

export const campusCategories: CampusCategory[] = [
  { key: 'service', label: '生活', color: '#3579b8' },
  { key: 'teaching', label: '教学', color: '#7b3294' },
  { key: 'dining', label: '食堂', color: '#e79a27' },
  { key: 'scenery', label: '景观', color: '#278b70' },
  { key: 'sports', label: '运动', color: '#c45d52' },
]

const verified = {
  coordinateSystem: 'GCJ-02' as const,
  coordinateSource: 'amap_visual_calibration' as const,
  calibrationStatus: 'verified' as const,
  calibrationNote: '已与高德底图对照校准。',
}

const needsReview = {
  ...verified,
  calibrationStatus: 'needs_review' as const,
  calibrationNote: '依据校园模型与底图估算，名称或入口位置需校方复核。',
}

type PlaceDraft = Omit<CampusPlace, 'location' | keyof typeof verified> & {
  x: number
  z: number
  review?: boolean
}

function p(d: PlaceDraft): CampusPlace {
  const { x, z, review, ...rest } = d
  return { ...rest, location: xz(x, z), ...(review ? needsReview : verified) }
}

const dormPlaces = createDormPlaces(p)

export const campusPlaces: CampusPlace[] = [
  ...dormPlaces,
  p({
    id: 'bathhouse',
    name: '澡堂',
    address: '生活区西部，16—18 号学生公寓与公共浴室组团',
    description: '公共浴室，开放时段以公寓管理通知为准。',
    category: 'service',
    x: -46.08,
    z: -76.49,
    area: '西区',
    tags: ['澡堂', '生活服务'],
  }),
  p({
    id: 'sewing-dry-clean',
    name: '牧院缝纫干洗店',
    address: '生活区中部，3 号学生公寓东南侧、商业街入口附近',
    description: '提供缝纫、干洗等日常衣物护理服务。',
    category: 'service',
    x: -23.14,
    z: -50.03,
    area: '西区',
    tags: ['缝纫', '干洗'],
  }),
  p({
    id: 'w-building',
    name: 'W 教学楼',
    address: '中心风景湖北侧，西侧主教学楼（W 楼）',
    description: '教学中轴西侧主楼，与 E 楼、综合实验楼连通成教学带。',
    category: 'teaching',
    x: 25.32,
    z: -26.80,
    area: '中区',
    tags: ['教学楼', 'W楼'],
  }),
  p({
    id: 'e-building',
    name: 'E 教学楼',
    address: '中心风景湖北侧，东侧主教学楼（E 楼）',
    description: '教学中轴东侧教学楼，与 W 楼、综合实验楼形成一字教学带。',
    category: 'teaching',
    x: 58.41,
    z: -29.86,
    area: '东区',
    tags: ['教学楼', 'E楼'],
  }),
  p({
    id: 's-building',
    name: '综合实验楼',
    address: '中心风景湖北侧，W 楼与 E 楼之间',
    description: '综合实验与上机教学场所，信工等专业实验课程常在此进行。',
    category: 'teaching',
    x: 38.35,
    z: -24.59,
    area: '中区',
    tags: ['实验楼', '综合实验楼'],
  }),
  p({
    id: 'a-building',
    name: 'A 教学楼',
    address: '校区东南部，A/B 连体教学楼东段',
    description: '东南教学区 A 楼，与 B 楼内部连通。',
    category: 'teaching',
    x: 1.02,
    z: 49.22,
    area: '南区',
    tags: ['教学楼', 'A楼'],
  }),
  p({
    id: 'library',
    name: '图书馆',
    address: '校区东南部，A/B 教学楼东侧；自南门进入后沿路前行左侧',
    description: '从南门进入校园后右手边。借书、自习请携带学生证；平日 21:30 闭馆，每周四 14:30—17:30 闭馆维护。',
    category: 'teaching',
    x: 39.41,
    z: 43.07,
    area: '南区',
    tags: ['图书馆', '自习'],
    openTime: '21:30 闭馆；周四 14:30—17:30 闭馆',
  }),
  p({
    id: 'b-building',
    name: 'B 教学楼',
    address: '校区东南部，A/B 连体教学楼西段',
    description: '东南教学区 B 楼，与 A 楼内部连通。',
    category: 'teaching',
    x: 7.78,
    z: 25.15,
    area: '南区',
    tags: ['教学楼', 'B楼'],
  }),
  p({
    id: 'canteen-mei',
    name: '梅餐厅',
    address: '生活区西北部，美食广场西端（梅园二楼）',
    description: '梅兰桃菊四座餐厅之一，梅园位于二楼，日常三餐均可在此就餐。',
    category: 'dining',
    x: -58,
    z: -48,
    area: '西区',
    tags: ['食堂', '梅餐厅'],
    openTime: '以餐厅实际开放时间为准',
  }),
  p({
    id: 'canteen-lan',
    name: '兰餐厅',
    address: '生活区西北部，梅园东侧（兰园二楼）',
    description: '梅兰桃菊四座餐厅之一，兰园位于二楼。',
    category: 'dining',
    x: -38.34,
    z: -48.31,
    area: '西区',
    tags: ['食堂', '兰餐厅'],
    openTime: '以餐厅实际开放时间为准',
  }),
  p({
    id: 'canteen-tao',
    name: '桃餐厅',
    address: '生活区西北部，兰园南侧（桃园一楼）',
    description: '梅兰桃菊四座餐厅之一，桃园位于一楼。',
    category: 'dining',
    x: -38.55,
    z: -42.82,
    area: '西区',
    tags: ['食堂', '桃餐厅'],
    openTime: '以餐厅实际开放时间为准',
    review: true,
  }),
  p({
    id: 'canteen-ju',
    name: '菊餐厅',
    address: '生活区西北部，桃园西侧（菊园一楼）',
    description: '梅兰桃菊四座餐厅之一，菊园位于一楼。',
    category: 'dining',
    x: -53.74,
    z: -45.58,
    area: '西区',
    tags: ['食堂', '菊餐厅'],
    openTime: '以餐厅实际开放时间为准',
  }),
  p({
    id: 'food-plaza',
    name: '美食广场',
    address: '生活区西北部，梅兰菊餐厅北侧',
    description: '档口与小食聚集区，适合快餐、小吃与课后简餐。',
    category: 'dining',
    x: -60.16,
    z: -22.28,
    area: '西区',
    tags: ['美食广场', '小吃'],
    openTime: '以各档口营业时间为准',
  }),
  p({
    id: 'express-station',
    name: '快递站',
    address: '生活区西北部，菊园餐厅西侧、商业街旁',
    description: '位于菊园餐厅西侧、紧邻商业街。凭淘宝或短信取件码到对应货架找件，扫码取走即可。',
    category: 'service',
    x: -64.22,
    z: -43.17,
    area: '西区',
    tags: ['快递', '菜鸟驿站'],
    openTime: '以驿站实际营业时间为准',
  }),
  p({
    id: 'dorm-admin-office',
    name: '宿管科',
    address: '生活区中部，8 号学生公寓南侧',
    description: '公寓管理科（宿管科），负责住宿登记、调宿与日常管理，具体办公时间与窗口以公寓管理通知为准。',
    category: 'service',
    x: -20.40,
    z: -56.64,
    area: '中区',
    tags: ['宿管科', '公寓管理'],
    openTime: '以公寓管理科办公时间为准',
  }),
  p({
    id: 'hospital',
    name: '校医院',
    address: '校区东南部，图书馆以南',
    description: '校内医疗服务点，日常就诊与迎新体检等以校医院通知为准。',
    category: 'service',
    x: 48.00,
    z: 72.38,
    area: '北区',
    tags: ['校医院', '医疗'],
    openTime: '以校医院开放时间为准',
  }),
  p({
    id: 'scenery-lake',
    name: '风景湖',
    address: '校区中心偏东，主景观湖泊',
    description: '英才校区中心湖泊，周边为教学区与广场，新生报到常在此熟悉路线。',
    category: 'scenery',
    x: 61.10,
    z: 42.17,
    area: '中区',
    tags: ['风景湖', '打卡'],
  }),
  p({
    id: 'scenery-pigu-lake',
    name: '屁股湖',
    address: '校区中心东侧，小型景观湖',
    description: '校园东侧景观湖，同学常以此昵称指代，正式导览以现场标识为准。',
    category: 'scenery',
    x: 29.63,
    z: 6.67,
    area: '东区',
    tags: ['景观湖', '打卡'],
  }),
  p({
    id: 'red-flower',
    name: '红色花蕊',
    address: '中心湖北侧，「红色花蕊」雕塑广场',
    description: '校园地标雕塑，红色金属花瓣造型，适合新生合影打卡。',
    category: 'scenery',
    x: -10.40,
    z: 4.06,
    area: '中区',
    tags: ['雕塑', '地标'],
  }),
  p({
    id: 'track-field',
    name: '田径场',
    address: '校区西南角，400 米塑胶跑道与足球场',
    description: '400 米标准塑胶跑道与足球场，体育课与课余锻炼使用。',
    category: 'sports',
    x: -88.67,
    z: 63.40,
    area: '西区',
    tags: ['田径场', '塑胶跑道'],
  }),
  p({
    id: 'natural-grass-field',
    name: '天然足球场',
    address: '校区东北部，天然草皮足球场',
    description: '天然草皮足球场，含 400 米标准跑道，体育课与课余足球活动使用。',
    category: 'sports',
    x: 39.45,
    z: -85.75,
    area: '东区',
    tags: ['足球场', '天然草', '跑道'],
  }),
  p({
    id: 'basketball-courts',
    name: '篮球场',
    address: '校区中西部，室外篮球场群',
    description: '室外篮球场群，晚间使用请注意安全。',
    category: 'sports',
    x: -58.18,
    z: 39.58,
    area: '东区',
    tags: ['篮球场', '室外'],
  }),
  p({
    id: 'volleyball-courts',
    name: '排球场',
    address: '校区西南部，田径场北侧',
    description: '室外排球场，可进行排球课与业余练习。',
    category: 'sports',
    x: -76.20,
    z: 82.99,
    area: '西区',
    tags: ['排球场', '室外'],
  }),
  p({
    id: 'tennis-courts',
    name: '网球场',
    address: '校区中西部，篮球场南侧',
    description: '室外网球场，使用规则以体育部安排为准。',
    category: 'sports',
    x: -30.32,
    z: 38.03,
    area: '东区',
    tags: ['网球场', '室外'],
  }),
  p({
    id: 'auditorium',
    name: '大礼堂',
    address: '校区西南部，室内体育馆以北',
    description: '校园大礼堂，大型集会与文体活动场地，与室内体育馆相邻。',
    category: 'sports',
    x: -54.76,
    z: 87.49,
    area: '西区',
    tags: ['大礼堂', '文体'],
    openTime: '以活动安排为准',
  }),
  p({
    id: 'gymnasium',
    name: '室内体育馆',
    address: '校区西南部，大礼堂以南',
    description: '室内篮球、羽毛球等活动场地，二楼设有社团活动空间。',
    category: 'sports',
    x: -42.61,
    z: 84.45,
    area: '西区',
    tags: ['体育馆', '室内'],
    openTime: '以场馆开放时间为准',
  }),
]

export function countPlacesByCategory(category: CampusPlace['category'] | 'all'): number {
  if (category === 'all') return campusPlaces.length
  return campusPlaces.filter((place) => place.category === category).length
}

export function filterCampusPlacesByQuery(
  places: CampusPlace[],
  query: string,
  category: CampusPlace['category'] | 'all' = 'all',
  limit?: number,
): CampusPlace[] {
  const text = query.trim().toLowerCase()
  let result = places.filter((place) => {
    const matchesCategory = category === 'all' || place.category === category
    if (!matchesCategory) return false
    if (!text) return true
    const searchable =
      `${place.name} ${place.address} ${place.description} ${place.tags.join(' ')}`.toLowerCase()
    return searchable.includes(text)
  })
  if (limit != null) result = result.slice(0, limit)
  return result
}

export function getDormPlaces(): CampusPlace[] {
  return campusPlaces.filter((place) => place.id.startsWith('dorm-'))
}

/** 从学籍宿舍字段解析 POI id，如「北苑12号楼419室」→ dorm-12 */
export function parseDormPlaceId(dormitory: string): string | null {
  const text = dormitory.trim()
  if (!text) return null
  const match = text.match(/(\d{1,2})\s*号楼/)
  if (!match) return null
  const num = Number.parseInt(match[1], 10)
  if (num < 1 || num > 18) return null
  return `dorm-${num}`
}

export function dormPlaceLabel(dormId: string): string | null {
  const place = campusPlaces.find((item) => item.id === dormId)
  return place?.name ?? null
}

export function findNearestDorm(
  lnglat: [number, number],
  places: CampusPlace[] = getDormPlaces(),
): { place: CampusPlace; meters: number } | null {
  let best: { place: CampusPlace; meters: number } | null = null
  for (const place of places.filter((item) => item.id.startsWith('dorm-'))) {
    const meters = haversineMeters(lnglat, place.location)
    if (!best || meters < best.meters) best = { place, meters }
  }
  return best
}
