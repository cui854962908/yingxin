/** 3D 校园坐标 (x 东 / z 南) → 高德 GCJ-02；锚点：风景湖 (0,0) + 南门方向 (0,100) */
const ORIGIN: [number, number] = [113.641689, 34.862226]
const LNG_PER_X = 0.00004925
const LNG_PER_Z = 0.00001328
const LAT_PER_X = -0.0000025
const LAT_PER_Z = -0.00001919

const BOUNDS_PADDING = 0.00055

export function campusXzToLngLat(x: number, z: number): [number, number] {
  return [
    ORIGIN[0] + x * LNG_PER_X + z * LNG_PER_Z,
    ORIGIN[1] + x * LAT_PER_X + z * LAT_PER_Z,
  ]
}

export function campusOrigin(): [number, number] {
  return [...ORIGIN]
}

/** 根据 POI 外包计算限制范围（西南角、东北角） */
export function campusLimitBoundsFromLocations(
  locations: Array<[number, number]>,
): [[number, number], [number, number]] {
  let minLng = Infinity
  let minLat = Infinity
  let maxLng = -Infinity
  let maxLat = -Infinity
  for (const [lng, lat] of locations) {
    minLng = Math.min(minLng, lng)
    minLat = Math.min(minLat, lat)
    maxLng = Math.max(maxLng, lng)
    maxLat = Math.max(maxLat, lat)
  }
  return [
    [minLng - BOUNDS_PADDING, minLat - BOUNDS_PADDING],
    [maxLng + BOUNDS_PADDING, maxLat + BOUNDS_PADDING],
  ]
}

export const CAMPUS_MAP_ZOOMS: [number, number] = [16, 19]
export const CAMPUS_DEFAULT_ZOOM = 17
