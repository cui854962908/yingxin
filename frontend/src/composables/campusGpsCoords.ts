import {
  campusFitBoundsFromLocations,
  campusOrigin,
  haversineMeters,
  isLngLatInBounds,
} from '../components/campus-map/campusGeo'
import { campusPlaces } from '../components/campus-map/campusPlaces'

const CAMPUS_CENTER = campusOrigin()

function campusBounds() {
  return campusFitBoundsFromLocations(campusPlaces.map((place) => place.location))
}

/** 与校区中心距离（米），用于判断坐标系是否选错 */
export function distanceToCampusCenter(lnglat: [number, number]): number {
  return haversineMeters(lnglat, CAMPUS_CENTER)
}

export function isNearCampus(lnglat: [number, number], maxMeters = 1500): boolean {
  return isLngLatInBounds(lnglat, campusBounds()) || distanceToCampusCenter(lnglat) <= maxMeters
}

/**
 * 浏览器 GPS 常为 WGS-84，但部分国产机已返回 GCJ-02；再 convert 会偏 ~300m。
 * 在 WGS→GCJ 与原始坐标中，选更靠近校区中心且合理的一项。
 */
export function pickGcjLngLat(
  AMap: { convertFrom?: (...args: unknown[]) => void },
  lng: number,
  lat: number,
): Promise<[number, number]> {
  const raw: [number, number] = [lng, lat]
  if (typeof AMap.convertFrom !== 'function') {
    return Promise.resolve(raw)
  }

  return new Promise((resolve) => {
    AMap.convertFrom(raw, 'gps', (status: string, result: { locations?: Array<{ lng: number; lat: number }> }) => {
      const converted = result?.locations?.[0]
      if (status !== 'complete' || !converted) {
        resolve(raw)
        return
      }
      const gcj: [number, number] = [converted.lng, converted.lat]
      const distRaw = distanceToCampusCenter(raw)
      const distGcj = distanceToCampusCenter(gcj)

      if (distRaw + 100 < distGcj && distRaw < 1200) {
        resolve(raw)
        return
      }
      if (distGcj + 100 < distRaw && distGcj < 1200) {
        resolve(gcj)
        return
      }
      resolve(gcj)
    })
  })
}
