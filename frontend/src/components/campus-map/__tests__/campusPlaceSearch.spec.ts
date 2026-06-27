import { describe, expect, it } from 'vitest'
import { campusPlaces, filterCampusPlacesByQuery } from '../campusPlaces'

describe('filterCampusPlacesByQuery', () => {
  it('matches place name and tags', () => {
    const lake = campusPlaces.find((place) => place.id === 'scenery-lake')
    expect(lake).toBeTruthy()
    expect(filterCampusPlacesByQuery(campusPlaces, '风景湖')).toContainEqual(lake)
    expect(filterCampusPlacesByQuery(campusPlaces, '食堂', 'dining').length).toBeGreaterThan(0)
  })

  it('respects category and result limit', () => {
    const dining = filterCampusPlacesByQuery(campusPlaces, '', 'dining')
    expect(dining.every((place) => place.category === 'dining')).toBe(true)
    expect(filterCampusPlacesByQuery(campusPlaces, '楼', 'all', 3)).toHaveLength(3)
  })

  it('returns empty list when nothing matches', () => {
    expect(filterCampusPlacesByQuery(campusPlaces, '不存在的地点xyz')).toEqual([])
  })
})
