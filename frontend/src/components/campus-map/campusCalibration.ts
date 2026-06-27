import { campusLngLatToXz } from './campusGeo'
import type { CampusPlace } from './types'

export const POI_OVERRIDES_STORAGE_KEY = 'campus-map-poi-overrides'
export const PUBLISHED_POI_OVERRIDES_URL = '/campus-map/poi-overrides.json'

export type PoiOverrides = Record<string, [number, number]>

export function parsePoiOverrides(raw: unknown): PoiOverrides {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return {}
  return Object.fromEntries(
    Object.entries(raw as Record<string, unknown>).filter(
      ([, loc]) => Array.isArray(loc) && loc.length === 2 && loc.every((n) => typeof n === 'number'),
    ),
  ) as PoiOverrides
}

/** 普通地图只读 campusPlaces.ts；校准页用本机 localStorage */
export function resolveDisplayPoiOverrides(
  calibrateMode: boolean,
  local: PoiOverrides,
  _published: PoiOverrides,
): PoiOverrides {
  return calibrateMode ? local : {}
}

export async function fetchPublishedPoiOverrides(): Promise<PoiOverrides> {
  try {
    const res = await fetch(`${PUBLISHED_POI_OVERRIDES_URL}?t=${Date.now()}`)
    if (!res.ok) return {}
    return parsePoiOverrides(await res.json())
  } catch {
    return {}
  }
}

export function isCampusCalibrateMode(
  query: Record<string, string | string[] | null | undefined>,
): boolean {
  const value = query.calibrate
  if (Array.isArray(value)) return value.includes('1') || value.includes('true')
  return value === '1' || value === 'true'
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
