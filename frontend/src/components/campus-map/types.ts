export type CategoryKey = 'service' | 'teaching' | 'dining' | 'scenery' | 'sports'

export interface CampusCategory {
  key: CategoryKey
  label: string
  color: string
}

export interface CampusPlace {
  id: string
  name: string
  address: string
  description: string
  category: CategoryKey
  location: [number, number]
  area: '北区' | '中区' | '南区' | '西区' | '东区'
  tags: string[]
  openTime?: string
  coordinateSystem: 'GCJ-02'
  coordinateSource: 'amap_visual_calibration'
  calibrationStatus: 'verified' | 'needs_review'
  calibrationNote: string
}
