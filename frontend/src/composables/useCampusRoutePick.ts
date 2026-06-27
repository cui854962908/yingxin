import { computed, ref, watch } from 'vue'
import { createRoutePointMarker } from '../components/campus-map/campusMapRouteMarkers'
import { isLngLatInBounds } from '../components/campus-map/campusGeo'

export type RoutePickStep = 'start' | 'end'

export function formatRoutePointLabel(lnglat: [number, number] | null): string {
  if (!lnglat) return '点击地图选择'
  return `${lnglat[0].toFixed(5)}, ${lnglat[1].toFixed(5)}`
}

interface RoutePlacePoint {
  location: [number, number]
  name: string
}

interface Options {
  getMap: () => any
  getAMap: () => any
  getCampusBounds: () => [[number, number], [number, number]]
  isActive: () => boolean
  onBothPicked?: () => void
}

export function useCampusRoutePick(options: Options) {
  const routeStart = ref<[number, number] | null>(null)
  const routeEnd = ref<[number, number] | null>(null)
  const routeStartName = ref('')
  const routeEndName = ref('')
  const pickStep = ref<RoutePickStep>('start')
  const pickMessage = ref('请点击地图选择起点，或使用 GPS / 标记当前位置')

  let startMarker: any = null
  let endMarker: any = null
  let clickHandler: ((event: { lnglat: { lng: number; lat: number } }) => void) | null = null

  const startLabel = computed(() =>
    routeStartName.value
    || (routeStart.value ? formatRoutePointLabel(routeStart.value) : '点击地图选起点'),
  )
  const endLabel = computed(() =>
    routeEndName.value
    || (routeEnd.value ? formatRoutePointLabel(routeEnd.value) : '点击地点标记'),
  )
  const canPlan = computed(() => routeStart.value !== null && routeEnd.value !== null)

  function isInCampus(lnglat: [number, number]): boolean {
    return isLngLatInBounds(lnglat, options.getCampusBounds())
  }

  function clearMarkers(map: any) {
    if (!map) return
    if (startMarker) {
      map.remove(startMarker)
      startMarker = null
    }
    if (endMarker) {
      map.remove(endMarker)
      endMarker = null
    }
  }

  function renderMarkers() {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return
    clearMarkers(map)
    if (routeStart.value) {
      startMarker = createRoutePointMarker(AMap, routeStart.value, 'start')
      map.add(startMarker)
    }
    if (routeEnd.value) {
      endMarker = createRoutePointMarker(AMap, routeEnd.value, 'end')
      map.add(endMarker)
    }
  }

  function syncPickBinding() {
    if (!options.isActive()) {
      unbindPick()
      return
    }
    if (pickStep.value === 'start' || !routeStart.value) bindPick()
    else unbindPick()
  }

  function updatePickMessage() {
    if (!routeStart.value) {
      pickMessage.value = '请点击地图选择起点，或使用 GPS / 标记当前位置'
      pickStep.value = 'start'
      syncPickBinding()
      return
    }
    if (!routeEnd.value) {
      pickMessage.value = '请点击地图上的地点标记选择终点'
      pickStep.value = 'end'
      syncPickBinding()
      return
    }
    pickMessage.value = '起终点已选定，可重新选点或规划路线'
    pickStep.value = 'end'
    syncPickBinding()
  }

  function applyStartPick(lnglat: [number, number]): boolean {
    if (!isInCampus(lnglat)) {
      pickMessage.value = '请在校园地图范围内选择起点'
      return false
    }
    routeStart.value = lnglat
    routeStartName.value = ''
    updatePickMessage()
    renderMarkers()
    if (routeEnd.value) options.onBothPicked?.()
    return true
  }

  function handleMapClick(event: { lnglat: { lng: number; lat: number } }) {
    if (pickStep.value === 'end') {
      pickMessage.value = '终点请点击地图上的地点标记，不能在空白处标定'
      return
    }
    applyStartPick([event.lnglat.lng, event.lnglat.lat])
  }

  function bindPick() {
    const map = options.getMap()
    if (!map || clickHandler) return
    clickHandler = handleMapClick
    map.on('click', clickHandler)
  }

  function unbindPick() {
    const map = options.getMap()
    if (!map || !clickHandler) return
    map.off('click', clickHandler)
    clickHandler = null
  }

  function beginPickStart() {
    pickStep.value = 'start'
    pickMessage.value = '请点击地图选择起点，或使用 GPS / 标记当前位置'
    syncPickBinding()
  }

  function beginPickEnd() {
    if (!routeStart.value) {
      beginPickStart()
      return
    }
    routeEnd.value = null
    routeEndName.value = ''
    pickStep.value = 'end'
    pickMessage.value = '请点击地图上的地点标记选择终点'
    syncPickBinding()
  }

  function presetEndPlace(place: RoutePlacePoint) {
    if (!isInCampus(place.location)) return
    routeEnd.value = place.location
    routeEndName.value = place.name
    updatePickMessage()
    renderMarkers()
    if (routeStart.value) options.onBothPicked?.()
  }

  function usePointAsStart(lnglat: [number, number], name = '当前位置') {
    if (!isInCampus(lnglat)) return
    routeStart.value = lnglat
    routeStartName.value = name
    updatePickMessage()
    renderMarkers()
    if (routeEnd.value) options.onBothPicked?.()
  }

  function resetRoutePoints() {
    routeStart.value = null
    routeEnd.value = null
    routeStartName.value = ''
    routeEndName.value = ''
    beginPickStart()
    clearMarkers(options.getMap())
  }

  function cleanup() {
    unbindPick()
    clearMarkers(options.getMap())
  }

  watch(
    () => options.isActive(),
    () => syncPickBinding(),
  )

  return {
    routeStart,
    routeEnd,
    pickStep,
    pickMessage,
    startLabel,
    endLabel,
    canPlan,
    applyStartPick,
    beginPickStart,
    beginPickEnd,
    presetEndPlace,
    usePointAsStart,
    resetRoutePoints,
    renderMarkers,
    syncPickBinding,
    cleanup,
  }
}
