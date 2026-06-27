import { describe, expect, it } from 'vitest'
import { campusOrigin } from '../../components/campus-map/campusGeo'
import { distanceToCampusCenter, isNearCampus } from '../campusGpsCoords'

describe('campusGpsCoords', () => {
  it('campus center is near itself', () => {
    const center = campusOrigin()
    expect(distanceToCampusCenter(center)).toBe(0)
    expect(isNearCampus(center)).toBe(true)
  })

  it('detects far-away coordinates', () => {
    expect(isNearCampus([116.4, 39.9])).toBe(false)
  })
})
