import { computed, ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { campusPlaces } from '../../components/campus-map/campusPlaces'
import { useCampusMapLocation } from '../useCampusMapLocation'

function createMapHarness(dormitory?: string) {
  const marker = { setPosition: vi.fn() }
  const map = {
    add: vi.fn(),
    remove: vi.fn(),
    panTo: vi.fn(),
    setZoom: vi.fn(),
    getZoom: vi.fn(() => 17),
  }
  const AMap = {
    Marker: vi.fn(function Marker() { return marker }),
  }
  const studentDormitory = ref<string | undefined>(dormitory)
  const location = useCampusMapLocation({
    getMap: () => map,
    getAMap: () => AMap,
    allPlaces: computed(() => campusPlaces),
    getProfileDormitory: () => studentDormitory.value,
  })
  return { location, map }
}

describe('useCampusMapLocation route origin', () => {
  it('uses the profile dormitory as an explicit dorm route origin', () => {
    const { location, map } = createMapHarness('5号楼')

    expect(location.locateAtProfileDorm()).toBe(true)
    expect(location.routeOriginKind.value).toBe('dorm')
    expect(location.userLocationLabel.value).toBe('学生公寓 5 号楼')
    expect(map.panTo).toHaveBeenCalledWith(location.position.value)
  })

  it('supports selecting any campus place as a manual route origin', () => {
    const { location, map } = createMapHarness()
    const place = campusPlaces.find((item) => item.id === 'scenery-lake')!

    expect(location.setPlaceAsOrigin(place)).toBe(true)
    expect(location.routeOriginKind.value).toBe('manual')
    expect(location.userLocationLabel.value).toBe(place.name)
    expect(map.panTo).toHaveBeenCalledWith(place.location)
  })

  it('does not invent a dorm origin when the student has no dormitory', () => {
    const { location } = createMapHarness()

    expect(location.locateAtProfileDorm()).toBe(false)
    expect(location.routeOriginKind.value).toBeNull()
    expect(location.position.value).toBeNull()
  })
})
