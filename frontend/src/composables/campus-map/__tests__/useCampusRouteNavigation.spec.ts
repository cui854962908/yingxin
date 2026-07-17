import { ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useCampusRouteNavigation } from '../useCampusRouteNavigation'

const destination = { id: 'library', name: '图书馆', location: [113.641, 34.862] as [number, number] }

function createHarness(origin: [number, number] | null = [113.64, 34.86]) {
  const map = { add: vi.fn(), remove: vi.fn(), setFitView: vi.fn() }
  const AMap = {
    Polyline: vi.fn(function Polyline(options: unknown) { return options }),
  }
  const planRoute = vi.fn(() => ({
    distanceMeters: 280,
    mode: 'campus-road' as const,
    path: [[113.64, 34.86] as [number, number], destination.location],
    message: '沿校内道路步行',
  }))
  const geoMessage = ref('')
  const navigation = useCampusRouteNavigation({
    getMap: () => map,
    getAMap: () => AMap,
    getOrigin: () => origin,
    getOriginLabel: () => '学生公寓 5 号楼',
    getRoadSegments: () => [],
    planRoute,
    setGeoMessage: (message) => { geoMessage.value = message },
  })
  return { navigation, map, planRoute, geoMessage }
}

describe('useCampusRouteNavigation', () => {
  it('draws a campus route and exposes the selected destination', () => {
    const { navigation, map, planRoute } = createHarness()

    navigation.planRouteToPlace(destination)

    expect(planRoute).toHaveBeenCalledOnce()
    expect(map.add).toHaveBeenCalledOnce()
    expect(navigation.routeDistance.value).toBe(280)
    expect(navigation.activeRouteTarget.value).toEqual(destination)
  })

  it('clears the existing route state and rendered line', () => {
    const { navigation, map } = createHarness()
    navigation.planRouteToPlace(destination)

    navigation.clearRoute()

    expect(map.remove).toHaveBeenCalledOnce()
    expect(navigation.routeDistance.value).toBe(0)
    expect(navigation.activeRouteTarget.value).toBeNull()
  })

  it('guides the user to choose an origin instead of planning without one', () => {
    const { navigation, planRoute, geoMessage } = createHarness(null)

    navigation.planRouteToPlace(destination)

    expect(planRoute).not.toHaveBeenCalled()
    expect(geoMessage.value).toContain('起点')
  })
})
