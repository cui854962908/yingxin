import { computed, ref, type ComputedRef } from 'vue'
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
  getCampusBounds: () => [[number, number], [number, number]]
  getProfileDormitory?: () => string | null | undefined
}

export function useCampusMapLocation(options: CampusMapLocationOptions) {
  const geo = useCampusGeolocation({
    isWithinCampus: (lnglat) => isLngLatInBounds(lnglat, options.getCampusBounds()),
  })
  const userLocationLabel = ref('')

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

  function placeAtDormId(dormId: string, sourceLabel: string) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return false
    const dorm = dormPlaces.value.find((place) => place.id === dormId)
    if (!dorm) return false
    geo.setPosition(map, AMap, dorm.location)
    userLocationLabel.value = sourceLabel
    geo.message.value = `定位已设在${dorm.name}（校内导览坐标，非 GPS）`
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
    userLocationLabel.value = ''
    const lnglat = await geo.locate(map, AMap)
    if (!lnglat) return
    map.panTo(lnglat)
    map.setZoom(Math.max(map.getZoom(), 18))
  }

  return {
    ...geo,
    userLocationLabel,
    profileDormId,
    profileDormLabel,
    locateMyPosition,
    locateAtProfileDorm,
    placeAtDormId,
  }
}
