import { describe, expect, it } from 'vitest'
import { campusLngLatToXz } from '../campusGeo'
import {
  applyPoiOverrides,
  formatOverridesForSource,
  hasCampusCalibrateQuery,
  isCampusCalibrateMode,
  parsePoiOverrides,
  resolveDisplayPoiOverrides,
} from '../campusCalibration'
import { campusPlaces, parseDormPlaceId } from '../campusPlaces'

describe('campusCalibration', () => {
  it('detects calibrate query flag', () => {
    expect(hasCampusCalibrateQuery({ calibrate: '1' })).toBe(true)
    expect(hasCampusCalibrateQuery({ calibrate: 'true' })).toBe(true)
    expect(hasCampusCalibrateQuery({})).toBe(false)
  })

  it('gates calibrate mode to dev or admin', () => {
    const q = { calibrate: '1' }
    expect(isCampusCalibrateMode(q, { isDev: true, isAdmin: false })).toBe(true)
    expect(isCampusCalibrateMode(q, { isDev: false, isAdmin: true })).toBe(true)
    expect(isCampusCalibrateMode(q, { isDev: false, isAdmin: false })).toBe(false)
    expect(isCampusCalibrateMode({}, { isDev: true, isAdmin: true })).toBe(false)
  })

  it('applies lng/lat overrides onto places', () => {
    const sample = campusPlaces[0]
    const lnglat: [number, number] = [113.641263, 34.862948]
    const merged = applyPoiOverrides(campusPlaces, { [sample.id]: lnglat })
    expect(merged[0].location).toEqual(lnglat)
  })

  it('parses and resolves display overrides', () => {
    const local = { library: [113.64, 34.86] as [number, number] }
    const published = { library: [113.65, 34.87] as [number, number] }
    expect(parsePoiOverrides({ library: [113.65, 34.87], bad: 'x' })).toEqual(published)
    expect(resolveDisplayPoiOverrides(true, local)).toEqual(local)
    expect(resolveDisplayPoiOverrides(false, local)).toEqual({})
  })

  it('exports x/z snippet for dorm 12–14 reference coords', () => {
    const overrides = {
      'dorm-12': [113.641263, 34.862948] as [number, number],
      'dorm-13': [113.641263, 34.863374] as [number, number],
      'dorm-14': [113.641263, 34.863629] as [number, number],
    }
    const text = formatOverridesForSource(campusPlaces, overrides)
    expect(text).toContain('dorm-12')
    expect(text).toContain('x:')
    const [x12, z12] = campusLngLatToXz(113.641263, 34.862948)
    expect(text).toContain(`x: ${x12.toFixed(2)}, z: ${z12.toFixed(2)}`)
  })
})

describe('parseDormPlaceId', () => {
  it('parses building number from dormitory string', () => {
    expect(parseDormPlaceId('北苑12号楼419室')).toBe('dorm-12')
    expect(parseDormPlaceId('12号楼')).toBe('dorm-12')
    expect(parseDormPlaceId('')).toBeNull()
    expect(parseDormPlaceId('无宿舍')).toBeNull()
  })
})

describe('merged POI write-back', () => {
  it('keeps dorm-15 lng/lat from calibration export', () => {
    const d15 = campusPlaces.find((p) => p.id === 'dorm-15')!
    expect(d15.location[0]).toBeCloseTo(113.641275, 5)
    expect(d15.location[1]).toBeCloseTo(34.864028, 5)
  })
})
