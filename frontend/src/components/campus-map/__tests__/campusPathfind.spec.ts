import { describe, expect, it } from 'vitest'
import { campusLngLatToXz, campusXzToLngLat } from '../campusGeo'
import { planCampusRoute } from '../campusPathfind'
import { campusPlaces } from '../campusPlaces'

function placeLocation(id: string): [number, number] {
  const place = campusPlaces.find((p) => p.id === id)
  if (!place) throw new Error(`missing place ${id}`)
  return place.location
}

describe('campusPathfind', () => {
  it('round-trips xz ↔ lnglat', () => {
    const lnglat = campusXzToLngLat(24, -25)
    const xz = campusLngLatToXz(lnglat[0], lnglat[1])
    expect(xz[0]).toBeCloseTo(24, 3)
    expect(xz[1]).toBeCloseTo(-25, 3)
  })

  it('finds multi-point campus road between lake and canteen', () => {
    const result = planCampusRoute(placeLocation('scenery-lake'), placeLocation('canteen-mei'))
    expect(result.mode).toBe('campus-road')
    expect(result.path.length).toBeGreaterThan(2)
    expect(result.distanceMeters).toBeGreaterThan(50)
  })

  it('routes dorm-11 to library along campus roads', () => {
    const result = planCampusRoute(placeLocation('dorm-11'), placeLocation('library'))
    expect(result.mode).toBe('campus-road')
    expect(result.path.length).toBeGreaterThan(2)
    expect(result.path.length).toBeLessThan(30)
  })

  it('does not keep redundant points on the same straight road segment', () => {
    const result = planCampusRoute(placeLocation('dorm-11'), placeLocation('library'))
    expect(result.mode).toBe('campus-road')
    const xz = result.path.map(([lng, lat]) => campusLngLatToXz(lng, lat))
    let straightRun = 0
    for (let i = 1; i < xz.length - 1; i++) {
      const ax = xz[i - 1][0] - xz[i][0]
      const az = xz[i - 1][1] - xz[i][1]
      const bx = xz[i + 1][0] - xz[i][0]
      const bz = xz[i + 1][1] - xz[i][1]
      const m1 = Math.hypot(ax, az)
      const m2 = Math.hypot(bx, bz)
      if (m1 < 0.01 || m2 < 0.01) continue
      const cos = (ax * bx + az * bz) / (m1 * m2)
      if (cos > 0.998) straightRun++
    }
    expect(straightRun).toBe(0)
  })

  it('includes library, express station and natural grass field', () => {
    const ids = ['library', 'express-station', 'natural-grass-field', 'dorm-admin-office', 'auditorium', 'hospital']
    for (const id of ids) {
      expect(campusPlaces.some((place) => place.id === id)).toBe(true)
    }
  })
})
