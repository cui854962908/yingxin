import type { CampusPlace } from './types'

export const DORM_HOURS = '06:00—22:30'

type DormLayout = { x: number; z: number; area: CampusPlace['area'] }

type DormPlaceDraft = Omit<CampusPlace, 'location' | 'coordinateSystem' | 'coordinateSource' | 'calibrationStatus' | 'calibrationNote'> & {
  x: number
  z: number
  review?: boolean
}

const DORM_LAYOUT: DormLayout[] = [
  { x: -36.53, z: -11.55, area: '北区' },
  { x: -32.65, z: -25.29, area: '北区' },
  { x: -27.90, z: -41.49, area: '北区' },
  { x: -19.02, z: -70.79, area: '北区' },
  { x: -13.01, z: -93.62, area: '北区' },
  { x: -16.66, z: -10.04, area: '中区' },
  { x: -12.99, z: -24.78, area: '中区' },
  { x: -8.50, z: -41.73, area: '中区' },
  { x: 1.13, z: -74.46, area: '中区' },
  { x: 6.15, z: -94.86, area: '中区' },
  { x: -3.20, z: -19.59, area: '中区' },
  { x: 1.76, z: -39.68, area: '中区' },
  { x: 6.34, z: -56.64, area: '中区' },
  { x: 10.93, z: -74.12, area: '北区' },
  { x: 17.53, z: -96.19, area: '北区' },
  { x: -32.64, z: -69.02, area: '西区' },
  { x: -26.31, z: -91.57, area: '西区' },
  { x: -53.23, z: -86.24, area: '西区' },
]

const DORM_ADDRESSES: Record<number, string> = {
  1: '生活区西侧前排，梅园餐厅与商业街以东',
  2: '生活区西侧，1 号学生公寓以北',
  3: '生活区西侧，2 号学生公寓以北',
  4: '生活区北部西列，3 号学生公寓以北',
  5: '生活区北部东列，4 号学生公寓以东',
  6: '生活区中部西列，靠近 W 教学楼方向',
  7: '生活区中部，6 号学生公寓以北',
  8: '生活区中部，7 号学生公寓以北',
  9: '生活区中北部东列，8 号学生公寓以东',
  10: '生活区东北部，9 号学生公寓以北',
  11: '生活区中部东列，靠近中心湖西侧',
  12: '生活区中部东列，11 号学生公寓以北',
  13: '生活区中北部，12 号学生公寓以北',
  14: '生活区东北部，10 号学生公寓以东',
  15: '生活区最北端东侧，14 号学生公寓以北',
  16: '生活区西部，澡堂与 18 号楼组团',
  17: '生活区西部，16 号学生公寓以北',
  18: '生活区西北角，17 号学生公寓以西',
}

export function createDormPlaces(build: (draft: DormPlaceDraft) => CampusPlace): CampusPlace[] {
  return DORM_LAYOUT.map((item, index) => {
    const no = index + 1
    return build({
      id: `dorm-${no}`,
      name: `学生公寓 ${no} 号楼`,
      address: DORM_ADDRESSES[no],
      description: '新生住宿以学院安排为准，报到后可在公寓管理科确认具体楼栋与房间。',
      category: 'service',
      x: item.x,
      z: item.z,
      area: item.area,
      tags: ['学生公寓', '宿舍'],
      openTime: DORM_HOURS,
    })
  })
}
