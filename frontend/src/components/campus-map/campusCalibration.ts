import { campusLngLatToXz } from './campusGeo'
import type { CampusPlace } from './types'

export const POI_OVERRIDES_STORAGE_KEY = 'campus-map-poi-overrides'

export type PoiOverrides = Record<string, [number, number]>

export function parsePoiOverrides(raw: unknown): PoiOverrides {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return {}
  return Object.fromEntries(
    Object.entries(raw as Record<string, unknown>).filter(
      ([, loc]) => Array.isArray(loc) && loc.length === 2 && loc.every((n) => typeof n === 'number'),
    ),
  ) as PoiOverrides
}

/** 校准模式下使用本机 localStorage 覆盖；正式地图直读 campusPlaces.ts（POI 修正通过 merge → commit 流程合入源文件） */
export function resolveDisplayPoiOverrides(
  calibrateMode: boolean,
  local: PoiOverrides,
): PoiOverrides {
  return calibrateMode ? local : {}
}

export function hasCampusCalibrateQuery(
  query: Record<string, string | string[] | null | undefined>,
): boolean {
  const value = query.calibrate
  if (Array.isArray(value)) return value.includes('1') || value.includes('true')
  return value === '1' || value === 'true'
}

/** 开发环境或已登录 admin 才允许进入校准模式（生产普通用户带 ?calibrate=1 无效） */
export function isCampusCalibrateMode(
  query: Record<string, string | string[] | null | undefined>,
  access: { isDev: boolean; isAdmin: boolean },
): boolean {
  if (!hasCampusCalibrateQuery(query)) return false
  return access.isDev || access.isAdmin
}

export function loadPoiOverrides(): PoiOverrides {
  try {
    const raw = localStorage.getItem(POI_OVERRIDES_STORAGE_KEY)
    if (!raw) return {}
    return parsePoiOverrides(JSON.parse(raw))
  } catch {
    return {}
  }
}

export function savePoiOverrides(overrides: PoiOverrides): void {
  localStorage.setItem(POI_OVERRIDES_STORAGE_KEY, JSON.stringify(overrides))
}

export function clearPoiOverrides(): void {
  localStorage.removeItem(POI_OVERRIDES_STORAGE_KEY)
}

export function applyPoiOverrides(places: CampusPlace[], overrides: PoiOverrides): CampusPlace[] {
  if (!Object.keys(overrides).length) return places
  return places.map((place) => {
    const location = overrides[place.id]
    return location ? { ...place, location } : place
  })
}

/** 生成可粘贴进 campusPlaces.ts 的 x/z 片段（写死坐标用） */
export function formatOverridesForSource(
  places: CampusPlace[],
  overrides: PoiOverrides,
): string {
  const lines = ['// 粘贴到 campusPlaces.ts 的 DORM_LAYOUT 或 p({ x, z }) 中', '']
  for (const [id, [lng, lat]] of Object.entries(overrides)) {
    const place = places.find((item) => item.id === id)
    const [x, z] = campusLngLatToXz(lng, lat)
    lines.push(`// ${id} · ${place?.name ?? '未知地点'}`)
    lines.push(`// 高德 lng ${lng.toFixed(6)}, lat ${lat.toFixed(6)}`)
    lines.push(`x: ${x.toFixed(2)}, z: ${z.toFixed(2)},`)
    lines.push('')
  }
  return lines.join('\n').trim()
}

export function formatLngLat(lnglat: [number, number]): string {
  return `${lnglat[0].toFixed(6)}, ${lnglat[1].toFixed(6)}`
}
