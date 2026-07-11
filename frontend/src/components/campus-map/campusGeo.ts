/** 3D 校园坐标 (x 东 / z 南) → 高德 GCJ-02；锚点：风景湖 (0,0) + 南门方向 (0,100) */
const ORIGIN: [number, number] = [113.641689, 34.862226]
const LNG_PER_X = 0.00004925
const LNG_PER_Z = 0.00001328
const LAT_PER_X = -0.0000025
const LAT_PER_Z = -0.00001919

/** 重置视野时 POI 外包范围的外扩留白 */
const FIT_BOUNDS_PADDING = 0.0012

/** 定位验证的边界外扩——IP 定位精度较低，需比视野留白更大 */
export const CAMPUS_GEO_PADDING = 0.006

const AFFINE_DET =
  LNG_PER_X * LAT_PER_Z - LNG_PER_Z * LAT_PER_X

export function campusXzToLngLat(x: number, z: number): [number, number] {
  return [
    ORIGIN[0] + x * LNG_PER_X + z * LNG_PER_Z,
    ORIGIN[1] + x * LAT_PER_X + z * LAT_PER_Z,
  ]
}

/** 与 ``campusXzToLngLat`` 互逆，供路网寻路使用 */
export function campusLngLatToXz(lng: number, lat: number): [number, number] {
  const dLng = lng - ORIGIN[0]
  const dLat = lat - ORIGIN[1]
  return [
    (dLng * LAT_PER_Z - dLat * LNG_PER_Z) / AFFINE_DET,
    (dLat * LNG_PER_X - dLng * LAT_PER_X) / AFFINE_DET,
  ]
}

export function campusOrigin(): [number, number] {
  return [...ORIGIN]
}

/** 根据 POI 外包计算重置视野用的范围（西南角、东北角） */
export function campusFitBoundsFromLocations(
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
    [minLng - FIT_BOUNDS_PADDING, minLat - FIT_BOUNDS_PADDING],
    [maxLng + FIT_BOUNDS_PADDING, maxLat + FIT_BOUNDS_PADDING],
  ]
}

export const CAMPUS_MAP_ZOOMS: [number, number] = [16, 19]
export const CAMPUS_DEFAULT_ZOOM = 17

export function isLngLatInBounds(
  lnglat: [number, number],
  bounds: [[number, number], [number, number]],
): boolean {
  const [lng, lat] = lnglat
  const [[swLng, swLat], [neLng, neLat]] = bounds
  return lng >= swLng && lat >= swLat && lng <= neLng && lat <= neLat
}

export function haversineMeters(a: [number, number], b: [number, number]): number {
  const toRad = (d: number) => (d * Math.PI) / 180
  const [lng1, lat1] = a
  const [lng2, lat2] = b
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const s1 = Math.sin(dLat / 2)
  const s2 = Math.sin(dLng / 2)
  const h = s1 * s1 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * s2 * s2
  return 6371000 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h))
}
