import { describe, expect, it } from 'vitest'
import { campusFitBoundsFromLocations, isLngLatInBounds } from '../../components/campus-map/campusGeo'
import { campusPlaces } from '../../components/campus-map/campusPlaces'
import { formatRoutePointLabel } from '../useCampusRoutePick'

describe('useCampusRoutePick helpers', () => {
  it('formats empty and selected point labels', () => {
    expect(formatRoutePointLabel(null)).toBe('点击地图选择')
    expect(formatRoutePointLabel([113.641689, 34.862226])).toMatch(/^113\.64169, 34\.86223$/)
  })

  it('accepts clicks inside campus bounds', () => {
    const bounds = campusFitBoundsFromLocations(campusPlaces.map((place) => place.location))
    const lake = campusPlaces.find((place) => place.id === 'scenery-lake')!.location
    expect(isLngLatInBounds(lake, bounds)).toBe(true)
    expect(isLngLatInBounds([113.5, 34.5], bounds)).toBe(false)
  })
})
