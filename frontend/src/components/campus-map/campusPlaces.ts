import type { CampusCategory, CampusPlace } from './types'
import { campusXzToLngLat } from './campusGeo'

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
  calibrationNote: '与 3D 导览模型坐标换算，建议校方现场复核。',
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

/** 1–18 号学生公寓（3D 模型坐标） */
const DORM_LAYOUT: Array<{ x: number; z: number; area: CampusPlace['area'] }> = [
  { x: -36.53, z: -11.55, area: '北区' },
  { x: -36.02, z: -26.25, area: '北区' },
  { x: -36.23, z: -40.3, area: '北区' },
  { x: -35.32, z: -65.34, area: '北区' },
  { x: -35.02, z: -84.24, area: '北区' },
  { x: -16.66, z: -10.04, area: '中区' },
  { x: -15.91, z: -25.12, area: '中区' },
  { x: -16.16, z: -39.12, area: '中区' },
  { x: -15.66, z: -66.17, area: '中区' },
  { x: -16.08, z: -83.27, area: '中区' },
  { x: 1.43, z: -19.74, area: '中区' },
  { x: 0.75, z: -34.31, area: '中区' },
  { x: 1.52, z: -51.37, area: '中区' },
  { x: 1.19, z: -65.5, area: '北区' },
  { x: 1.1, z: -82.06, area: '北区' },
  { x: -53.7, z: -65.4, area: '西区' },
  { x: -53.56, z: -83.54, area: '西区' },
  { x: -100.26, z: -85.32, area: '西区' },
]

const dormPlaces: CampusPlace[] = DORM_LAYOUT.map((item, index) =>
  p({
    id: `dorm-${index + 1}`,
    name: `学生公寓 ${index + 1} 号楼`,
    address: `英才校区学生宿舍区 · ${item.area}`,
    description: '新生住宿以学院安排为准，报到后可在公寓管理科确认具体楼栋与房间。',
    category: 'service',
    x: item.x,
    z: item.z,
    area: item.area,
    tags: ['学生公寓', '宿舍'],
  }),
)

export const campusPlaces: CampusPlace[] = [
  ...dormPlaces,
  p({
    id: 'bathhouse',
    name: '澡堂',
    address: '西北宿舍区中部',
    description: '公共浴室，开放时段以公寓管理通知为准。',
    category: 'service',
    x: -67.46,
    z: -81.73,
    area: '西区',
    tags: ['澡堂', '生活服务'],
  }),
  p({
    id: 'sewing-dry-clean',
    name: '牧院缝纫干洗店',
    address: '西北生活配套区、商业街附近',
    description: '提供缝纫、干洗等日常衣物护理服务。',
    category: 'service',
    x: -81,
    z: -38,
    area: '西区',
    tags: ['缝纫', '干洗'],
    review: true,
  }),
  p({
    id: 'w-building',
    name: 'W 教学楼',
    address: '中心风景湖北侧 · 教学中轴西段',
    description: '教学中轴西侧主楼，与 E 楼、综合实验楼连通成教学带。',
    category: 'teaching',
    x: 24,
    z: -25,
    area: '中区',
    tags: ['教学楼', 'W楼'],
  }),
  p({
    id: 'e-building',
    name: 'E 教学楼',
    address: '中心风景湖北侧 · 教学中轴东段',
    description: '教学中轴东侧教学楼，与 W 楼、综合实验楼形成一字教学带。',
    category: 'teaching',
    x: 66,
    z: -25,
    area: '东区',
    tags: ['教学楼', 'E楼'],
  }),
  p({
    id: 's-building',
    name: '综合实验楼',
    address: '中心风景湖北侧 · 教学中轴中部',
    description: '综合实验与上机教学场所，信工等专业实验课程常在此进行。',
    category: 'teaching',
    x: 45,
    z: -24,
    area: '中区',
    tags: ['实验楼', '综合实验楼'],
  }),
  p({
    id: 'a-building',
    name: 'A 教学楼',
    address: '校园东南部 · 连体教学楼群',
    description: '东南教学区 A 楼，与 B 楼内部连通。',
    category: 'teaching',
    x: 45,
    z: 60,
    area: '南区',
    tags: ['教学楼', 'A楼'],
  }),
  p({
    id: 'b-building',
    name: 'B 教学楼',
    address: '校园东南部 · 连体教学楼群',
    description: '东南教学区 B 楼，与 A 楼内部连通。',
    category: 'teaching',
    x: 45,
    z: 42,
    area: '南区',
    tags: ['教学楼', 'B楼'],
  }),
  p({
    id: 'canteen-mei',
    name: '梅餐厅',
    address: '西北餐饮区 · 美食广场一带',
    description: '「梅兰桃菊」学生餐厅之一，日常三餐就餐点。',
    category: 'dining',
    x: -58,
    z: -48,
    area: '西区',
    tags: ['食堂', '梅餐厅'],
    openTime: '以餐厅实际开放时间为准',
    review: true,
  }),
  p({
    id: 'canteen-lan',
    name: '兰餐厅',
    address: '西北餐饮区 · 美食广场一带',
    description: '「梅兰桃菊」学生餐厅之一。',
    category: 'dining',
    x: -66,
    z: -44,
    area: '西区',
    tags: ['食堂', '兰餐厅'],
    openTime: '以餐厅实际开放时间为准',
    review: true,
  }),
  p({
    id: 'canteen-tao',
    name: '桃餐厅',
    address: '西北餐饮区 · 美食广场一带',
    description: '「梅兰桃菊」学生餐厅之一。',
    category: 'dining',
    x: -64,
    z: -52,
    area: '西区',
    tags: ['食堂', '桃餐厅'],
    openTime: '以餐厅实际开放时间为准',
    review: true,
  }),
  p({
    id: 'canteen-ju',
    name: '菊餐厅',
    address: '西北餐饮区 · 美食广场一带',
    description: '「梅兰桃菊」学生餐厅之一。',
    category: 'dining',
    x: -54,
    z: -46,
    area: '西区',
    tags: ['食堂', '菊餐厅'],
    openTime: '以餐厅实际开放时间为准',
    review: true,
  }),
  p({
    id: 'food-plaza',
    name: '美食广场',
    address: '西北生活区',
    description: '档口与小食聚集区，适合快餐、小吃与课后简餐。',
    category: 'dining',
    x: -51.08,
    z: -34.73,
    area: '西区',
    tags: ['美食广场', '小吃'],
    openTime: '以各档口营业时间为准',
  }),
  p({
    id: 'scenery-lake',
    name: '风景湖',
    address: '校园中心',
    description: '英才校区中心湖泊，周边为教学区与广场，新生报到常在此熟悉路线。',
    category: 'scenery',
    x: 0,
    z: 0,
    area: '中区',
    tags: ['风景湖', '打卡'],
  }),
  p({
    id: 'scenery-pigu-lake',
    name: '屁股湖',
    address: '校园东部',
    description: '校园东侧景观湖，同学常以此昵称指代，正式导览以现场标识为准。',
    category: 'scenery',
    x: 85,
    z: 35,
    area: '东区',
    tags: ['景观湖', '打卡'],
  }),
  p({
    id: 'red-flower',
    name: '红色花蕊',
    address: '风景湖北岸',
    description: '校园地标雕塑，红色金属花瓣造型，适合新生合影打卡。',
    category: 'scenery',
    x: 0,
    z: -10,
    area: '中区',
    tags: ['雕塑', '地标'],
  }),
  p({
    id: 'track-field',
    name: '田径场',
    address: '校园西南部',
    description: '400 米标准塑胶跑道与足球场，体育课与课余锻炼使用。',
    category: 'sports',
    x: -145,
    z: 95,
    area: '西区',
    tags: ['田径场', '足球场'],
  }),
  p({
    id: 'basketball-courts',
    name: '篮球场',
    address: '东北教学运动区',
    description: '室外篮球场群，晚间使用请注意安全。',
    category: 'sports',
    x: 40,
    z: -75,
    area: '东区',
    tags: ['篮球场', '室外'],
  }),
  p({
    id: 'volleyball-courts',
    name: '排球场',
    address: '校园西部',
    description: '室外排球场，可进行排球课与业余练习。',
    category: 'sports',
    x: -140,
    z: 40,
    area: '西区',
    tags: ['排球场', '室外'],
  }),
  p({
    id: 'tennis-courts',
    name: '网球场',
    address: '东北教学运动区',
    description: '室外网球场，使用规则以体育部安排为准。',
    category: 'sports',
    x: 40,
    z: -45,
    area: '东区',
    tags: ['网球场', '室外'],
  }),
  p({
    id: 'gymnasium',
    name: '室内体育馆',
    address: '风景湖南侧 · 文体区',
    description: '室内篮球、羽毛球等活动场地，二楼设有社团活动空间。',
    category: 'sports',
    x: -42,
    z: 18,
    area: '西区',
    tags: ['体育馆', '室内'],
    openTime: '以场馆开放时间为准',
  }),
]

export function countPlacesByCategory(category: CampusPlace['category'] | 'all'): number {
  if (category === 'all') return campusPlaces.length
  return campusPlaces.filter((place) => place.category === category).length
}
