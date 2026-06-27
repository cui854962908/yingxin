import { campusLngLatToXz } from './campusGeo'
import { CAMPUS_ROAD_POI_OFFSET, type CampusRoadSegment } from './campusRoadNetwork'

export const ROAD_OVERRIDES_STORAGE_KEY = 'campus-map-road-overrides'

/** 手绘路段：高德经纬度起终点 */
export interface RoadLngLatSegment {
  start: [number, number]
  end: [number, number]
}

export function loadRoadOverrides(): RoadLngLatSegment[] {
  try {
    const raw = localStorage.getItem(ROAD_OVERRIDES_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as RoadLngLatSegment[]
    return parsed.filter(
      (seg) =>
        Array.isArray(seg.start) &&
        Array.isArray(seg.end) &&
        seg.start.length === 2 &&
        seg.end.length === 2,
    )
  } catch {
    return []
  }
}

export function saveRoadOverrides(segments: RoadLngLatSegment[]): void {
  localStorage.setItem(ROAD_OVERRIDES_STORAGE_KEY, JSON.stringify(segments))
}

export function clearRoadOverrides(): void {
  localStorage.removeItem(ROAD_OVERRIDES_STORAGE_KEY)
}

export function roadOverridesToPoiSegments(segments: RoadLngLatSegment[]): CampusRoadSegment[] {
  return segments.map((seg) => {
    const [x1, z1] = campusLngLatToXz(seg.start[0], seg.start[1])
    const [x2, z2] = campusLngLatToXz(seg.end[0], seg.end[1])
    return { x1, z1, x2, z2, width: 3 }
  })
}

/** 导出可粘贴进 campusRoadNetwork.ts 的 GLB 线段 */
export function formatRoadOverridesForSource(segments: RoadLngLatSegment[]): string {
  const { x: ox, z: oz } = CAMPUS_ROAD_POI_OFFSET
  const lines = ['// 粘贴到 campusRoadNetwork.ts 的 CAMPUS_ROAD_SEGMENTS', '']
  for (const seg of segments) {
    const [x1, z1] = campusLngLatToXz(seg.start[0], seg.start[1])
    const [x2, z2] = campusLngLatToXz(seg.end[0], seg.end[1])
    const gx1 = (x1 + ox).toFixed(2)
    const gz1 = (z1 + oz).toFixed(2)
    const gx2 = (x2 + ox).toFixed(2)
    const gz2 = (z2 + oz).toFixed(2)
    lines.push(`{ x1: ${gx1}, z1: ${gz1}, x2: ${gx2}, z2: ${gz2}, width: 3 },`)
  }
  return lines.join('\n')
}
