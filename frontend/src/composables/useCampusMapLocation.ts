import { computed, ref, type ComputedRef } from 'vue'
import {
  dormPlaceLabel,
  getDormPlaces,
  parseDormPlaceId,
} from '../components/campus-map/campusPlaces'
import { CAMPUS_GEO_PADDING, isLngLatInBounds } from '../components/campus-map/campusGeo'
import type { CampusPlace } from '../components/campus-map/types'
import { useCampusGeolocation } from './useCampusGeolocation'

interface CampusMapLocationOptions {
  getMap: () => any
  getAMap: () => any
  allPlaces: ComputedRef<CampusPlace[]>
  getProfileDormitory?: () => string | null | undefined
}

export type CampusRouteOriginKind = 'gps' | 'dorm' | 'manual'

export function useCampusMapLocation(options: CampusMapLocationOptions) {
  /** 定位验证使用比视野留白更宽松的边界，兼容 IP 定位精度 */
  const geoBounds = computed(() => {
    const locations = options.allPlaces.value.map((p) => p.location)
    if (!locations.length) return [[0, 0], [0, 0]] as [[number, number], [number, number]]
    let minLng = Infinity; let minLat = Infinity; let maxLng = -Infinity; let maxLat = -Infinity
    for (const [lng, lat] of locations) {
      minLng = Math.min(minLng, lng); minLat = Math.min(minLat, lat)
      maxLng = Math.max(maxLng, lng); maxLat = Math.max(maxLat, lat)
    }
    return [[minLng - CAMPUS_GEO_PADDING, minLat - CAMPUS_GEO_PADDING], [maxLng + CAMPUS_GEO_PADDING, maxLat + CAMPUS_GEO_PADDING]] as [[number, number], [number, number]]
  })

  const geo = useCampusGeolocation({
    isWithinCampus: (lnglat) => isLngLatInBounds(lnglat, geoBounds.value),
  })
  const userLocationLabel = ref('')
  const routeOriginKind = ref<CampusRouteOriginKind | null>(null)

  const dormPlaces = computed(() =>
    getDormPlaces().map((dorm) => options.allPlaces.value.find((p) => p.id === dorm.id) ?? dorm),
  )

  const profileDormId = computed(() => {
    const dormitory = options.getProfileDormitory?.()
    return dormitory ? parseDormPlaceId(dormitory) : null
  })

  const profileDormLabel = computed(() => {
    const id = profileDormId.value
    return id ? dormPlaceLabel(id) : null
  })

  function applyPlaceOrigin(place: CampusPlace, label: string, kind: CampusRouteOriginKind) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return false
    geo.setPosition(map, AMap, place.location)
    userLocationLabel.value = label
    routeOriginKind.value = kind
    geo.message.value = `路线起点已设为${label}（校内导览坐标，非 GPS）`
    map.panTo(place.location)
    map.setZoom(Math.max(map.getZoom(), 18))
    return true
  }

  function placeAtDormId(dormId: string, sourceLabel: string) {
    const dorm = dormPlaces.value.find((place) => place.id === dormId)
    return dorm ? applyPlaceOrigin(dorm, sourceLabel, 'dorm') : false
  }

  function locateAtProfileDorm(): boolean {
    const dormId = profileDormId.value
    if (!dormId) return false
    const label = profileDormLabel.value ?? `学生公寓 ${dormId.replace('dorm-', '')} 号楼`
    return placeAtDormId(dormId, label)
  }

  function setPlaceAsOrigin(place: CampusPlace): boolean {
    return applyPlaceOrigin(place, place.name, 'manual')
  }

  async function locateMyPosition(): Promise<boolean> {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap || geo.status.value === 'loading') return false
    const lnglat = await geo.locate(map, AMap)
    if (!lnglat) return false
    userLocationLabel.value = '当前位置'
    routeOriginKind.value = 'gps'
    map.panTo(lnglat)
    map.setZoom(Math.max(map.getZoom(), 18))
    return true
  }

  return {
    ...geo,
    userLocationLabel,
    routeOriginKind,
    profileDormId,
    profileDormLabel,
    locateMyPosition,
    locateAtProfileDorm,
    placeAtDormId,
    setPlaceAsOrigin,
  }
}
