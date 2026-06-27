import { computed, ref, watch, type ComputedRef } from 'vue'
import {
  dormPlaceLabel,
  getDormPlaces,
  parseDormPlaceId,
} from '../components/campus-map/campusPlaces'
import { isLngLatInBounds } from '../components/campus-map/campusGeo'
import type { CampusPlace } from '../components/campus-map/types'
import { useCampusGeolocation } from './useCampusGeolocation'

interface CampusMapLocationOptions {
  getMap: () => any
  getAMap: () => any
  allPlaces: ComputedRef<CampusPlace[]>
  getCampusCenter: () => [number, number]
  getCampusBounds: () => [[number, number], [number, number]]
  isLocationPickAllowed: () => boolean
  getProfileDormitory?: () => string | null | undefined
}

export function useCampusMapLocation(options: CampusMapLocationOptions) {
  const geo = useCampusGeolocation({
    isWithinCampus: (lnglat) => isLngLatInBounds(lnglat, options.getCampusBounds()),
  })
  const userLocationLabel = ref('')
  const locationPickActive = ref(false)

  let clickHandler: ((event: { lnglat: { lng: number; lat: number } }) => void) | null = null

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

  function bindLocationPick() {
    const map = options.getMap()
    if (!map || clickHandler) return
    clickHandler = (event) => markLocationAt([event.lnglat.lng, event.lnglat.lat])
    map.on('click', clickHandler)
  }

  function unbindLocationPick() {
    const map = options.getMap()
    if (!map || !clickHandler) return
    map.off('click', clickHandler)
    clickHandler = null
  }

  function syncLocationPickBinding() {
    if (locationPickActive.value && options.isLocationPickAllowed()) bindLocationPick()
    else unbindLocationPick()
  }

  function beginLocationPick() {
    if (!options.isLocationPickAllowed()) return
    if (locationPickActive.value) {
      cancelLocationPick()
      geo.message.value = ''
      return
    }
    locationPickActive.value = true
    geo.message.value = '请在地图上点击标注您的当前位置'
    syncLocationPickBinding()
  }

  function cancelLocationPick() {
    locationPickActive.value = false
    unbindLocationPick()
  }

  function markLocationAt(lnglat: [number, number]): boolean {
    if (!isLngLatInBounds(lnglat, options.getCampusBounds())) {
      geo.message.value = '请在校园地图范围内标注'
      return false
    }
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return false
    userLocationLabel.value = '当前位置'
    geo.setPosition(map, AMap, lnglat)
    geo.message.value = '已标注当前位置'
    locationPickActive.value = false
    unbindLocationPick()
    map.panTo(lnglat)
    map.setZoom(Math.max(map.getZoom(), 18))
    return true
  }

  function placeAtDormId(dormId: string, sourceLabel: string) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return false
    const dorm = dormPlaces.value.find((place) => place.id === dormId)
    if (!dorm) return false
    cancelLocationPick()
    geo.setPosition(map, AMap, dorm.location)
    userLocationLabel.value = sourceLabel
    geo.message.value = `红点已设在${dorm.name}（校内导览坐标，非 GPS）`
    map.panTo(dorm.location)
    map.setZoom(Math.max(map.getZoom(), 18))
    return true
  }

  function locateAtProfileDorm(): boolean {
    const dormId = profileDormId.value
    if (!dormId) return false
    const label = profileDormLabel.value ?? `学生公寓 ${dormId.replace('dorm-', '')} 号楼`
    return placeAtDormId(dormId, label)
  }

  async function locateMyPosition() {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap || geo.status.value === 'loading') return
    cancelLocationPick()
    userLocationLabel.value = ''
    const lnglat = await geo.locate(map, AMap)
    if (!lnglat) return
    map.panTo(lnglat)
    map.setZoom(Math.max(map.getZoom(), 18))
  }

  watch(
    () => options.isLocationPickAllowed(),
    (allowed) => {
      if (!allowed) {
        cancelLocationPick()
        geo.stopTracking()
      }
    },
  )

  function cleanupLocationPick() {
    cancelLocationPick()
  }

  return {
    ...geo,
    userLocationLabel,
    locationPickActive,
    profileDormId,
    profileDormLabel,
    beginLocationPick,
    syncLocationPickBinding,
    cleanupLocationPick,
    locateMyPosition,
    locateAtProfileDorm,
    placeAtDormId,
  }
}
