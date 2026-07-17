import { ref } from 'vue'
import type { CampusPlace } from '../../components/campus-map/types'
import type { CampusRoadSegment } from '../../components/campus-map/campusRoadNetwork'

type LngLat = [number, number]
type RouteTarget = Pick<CampusPlace, 'id' | 'name' | 'location'>

interface RouteResult {
  distanceMeters: number
  mode: 'campus-road' | 'straight-fallback'
  path: LngLat[]
  message?: string
}

interface CampusRouteNavigationOptions {
  getMap: () => any
  getAMap: () => any
  getOrigin: () => LngLat | null
  getOriginLabel: () => string | null
  getRoadSegments: () => CampusRoadSegment[]
  planRoute: (origin: LngLat, destination: LngLat, segments: CampusRoadSegment[]) => RouteResult
  setGeoMessage: (message: string) => void
}

/** Encapsulates route rendering and lifecycle so the map page only coordinates UI state. */
export function useCampusRouteNavigation(options: CampusRouteNavigationOptions) {
  const routeMessage = ref('')
  const routeDistance = ref(0)
  const routePlanning = ref(false)
  const activeRouteTarget = ref<RouteTarget | null>(null)
  let routeLine: any = null

  function clearRoute() {
    const map = options.getMap()
    if (routeLine && map) map.remove(routeLine)
    routeLine = null
    routeMessage.value = ''
    routeDistance.value = 0
    activeRouteTarget.value = null
  }

  function drawRouteLine(result: RouteResult) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return
    routeDistance.value = result.distanceMeters
    routeLine = new AMap.Polyline({
      path: result.path,
      strokeColor: '#B5343A',
      strokeWeight: 6,
      strokeOpacity: 0.9,
      strokeStyle: result.mode === 'straight-fallback' ? 'dashed' : 'solid',
      showDir: true,
      lineJoin: 'round',
    })
    map.add(routeLine)
    map.setFitView([routeLine], false, [80, 80, 80, 80])
  }

  function planRouteToPlace(place: RouteTarget) {
    const map = options.getMap()
    const AMap = options.getAMap()
    const origin = options.getOrigin()
    if (!map || !AMap || routePlanning.value) return
    if (!origin) {
      options.setGeoMessage('请先点「定位当前位置」或「手动选择当前位置」设置起点')
      return
    }

    routePlanning.value = true
    const originLabel = options.getOriginLabel() || '当前位置'
    routeMessage.value = `正在规划从${originLabel}前往${place.name}…`
    try {
      if (routeLine) map.remove(routeLine)
      routeLine = null
      const result = options.planRoute(origin, place.location, options.getRoadSegments())
      drawRouteLine(result)
      activeRouteTarget.value = place
      routeMessage.value = `从${originLabel}前往 ${place.name}${result.message ? ` · ${result.message}` : ''}`
    } finally {
      routePlanning.value = false
    }
  }

  function rerouteToActiveTarget() {
    if (activeRouteTarget.value) planRouteToPlace(activeRouteTarget.value)
  }

  return {
    routeMessage,
    routeDistance,
    routePlanning,
    activeRouteTarget,
    clearRoute,
    planRouteToPlace,
    rerouteToActiveTarget,
  }
}
