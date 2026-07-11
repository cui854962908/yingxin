import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { campusOrigin } from '../../components/campus-map/campusGeo'
import { OUT_OF_CAMPUS_MSG, useCampusGeolocation } from '../useCampusGeolocation'

function mockMap() {
  const markers: unknown[] = []
  return {
    markers,
    add: vi.fn((m: unknown) => { markers.push(m) }),
    remove: vi.fn((m: unknown) => {
      const idx = markers.indexOf(m)
      if (idx >= 0) markers.splice(idx, 1)
    }),
  }
}

function mockAMap(reading: { lnglat: [number, number]; accuracy: number | null } | null = null) {
  return {
    Marker: vi.fn(function Marker(this: { setPosition: ReturnType<typeof vi.fn> }, opts: { position: [number, number] }) {
      this.setPosition = vi.fn()
      return { position: opts.position, setPosition: this.setPosition }
    }),
    convertFrom: undefined,
    plugin: vi.fn((_name: string, cb: () => void) => cb()),
    Geolocation: vi.fn(function Geolocation(this: Record<string, unknown>) {
      this.getCurrentPosition = vi.fn((callback: (st: string, result: unknown) => void) => {
        if (reading) {
          callback('complete', {
            position: { lng: reading.lnglat[0], lat: reading.lnglat[1] },
            accuracy: reading.accuracy,
          })
        } else {
          callback('error', null)
        }
      })
      return this
    }),
  }
}

function alwaysOnCampus() {
  return () => true
}

describe('useCampusGeolocation', () => {
  let clearWatch: ReturnType<typeof vi.fn>
  let watchCallback: ((pos: GeolocationPosition) => void) | null = null

  beforeEach(() => {
    vi.stubGlobal('isSecureContext', true)
    watchCallback = null
    clearWatch = vi.fn()
    vi.stubGlobal('navigator', {
      geolocation: {
        getCurrentPosition: vi.fn((success: PositionCallback) => {
          success({
            coords: {
              latitude: campusOrigin()[1],
              longitude: campusOrigin()[0],
              accuracy: 12,
            },
          } as GeolocationPosition)
        }),
        watchPosition: vi.fn((success: PositionCallback) => {
          watchCallback = success
          return 42
        }),
        clearWatch,
      },
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('starts watchPosition after locate succeeds on campus', async () => {
    const geo = useCampusGeolocation({ isWithinCampus: alwaysOnCampus() })
    const map = mockMap()
    const AMap = mockAMap()

    const lnglat = await geo.locate(map, AMap)

    expect(lnglat).not.toBeNull()
    expect(navigator.geolocation.watchPosition).toHaveBeenCalledOnce()
    expect(geo.position.value).toEqual(lnglat)
    expect(map.add).toHaveBeenCalled()
  })

  it('rejects gps outside campus without showing marker', async () => {
    const geo = useCampusGeolocation({ isWithinCampus: () => false })
    const map = mockMap()
    const AMap = mockAMap()

    const lnglat = await geo.locate(map, AMap)

    expect(lnglat).toBeNull()
    expect(geo.position.value).toBeNull()
    expect(geo.message.value).toBe(OUT_OF_CAMPUS_MSG)
    expect(map.add).not.toHaveBeenCalled()
    expect(navigator.geolocation.watchPosition).not.toHaveBeenCalled()
  })

  it('updates position when watch reports meaningful movement', async () => {
    const geo = useCampusGeolocation({ isWithinCampus: alwaysOnCampus() })
    const map = mockMap()
    const AMap = mockAMap()
    await geo.locate(map, AMap)
    const initial = geo.position.value!

    watchCallback?.({
      coords: {
        latitude: initial[1] + 0.00008,
        longitude: initial[0] + 0.00008,
        accuracy: 10,
      },
    } as GeolocationPosition)

    await vi.waitFor(() => {
      expect(geo.position.value).not.toEqual(initial)
    })
  })

  it('stops tracking when setPosition is used for manual mark', async () => {
    const geo = useCampusGeolocation({ isWithinCampus: alwaysOnCampus() })
    const map = mockMap()
    const AMap = mockAMap()
    await geo.locate(map, AMap)

    geo.setPosition(map, AMap, [113.642, 34.863])

    expect(clearWatch).toHaveBeenCalledWith(42)
  })

  it('stops tracking on clearMarker', async () => {
    const geo = useCampusGeolocation({ isWithinCampus: alwaysOnCampus() })
    const map = mockMap()
    const AMap = mockAMap()
    await geo.locate(map, AMap)

    geo.clearMarker(map)

    expect(clearWatch).toHaveBeenCalledWith(42)
    expect(map.remove).toHaveBeenCalled()
  })

  it('explains when desktop location permission is denied', async () => {
    vi.stubGlobal('navigator', {
      geolocation: {
        getCurrentPosition: vi.fn((_success: PositionCallback, error: PositionErrorCallback) => {
          error({ code: 1, message: 'denied' } as GeolocationPositionError)
        }),
        watchPosition: vi.fn(),
        clearWatch: vi.fn(),
      },
    })
    const geo = useCampusGeolocation({ isWithinCampus: () => false })

    await geo.locate(mockMap(), mockAMap())

    expect(geo.message.value).toContain('定位权限被拒绝')
  })

  it('explains that a non-secure desktop page requires HTTPS', async () => {
    vi.stubGlobal('isSecureContext', false)
    const geo = useCampusGeolocation({ isWithinCampus: () => false })

    await geo.locate(mockMap(), mockAMap())

    expect(geo.message.value).toContain('HTTPS')
  })

  it('can use AMap fallback when browser geolocation is unavailable', async () => {
    vi.stubGlobal('navigator', {})
    const origin = campusOrigin()
    const geo = useCampusGeolocation({ isWithinCampus: alwaysOnCampus() })

    const result = await geo.locate(mockMap(), mockAMap({ lnglat: origin, accuracy: 80 }))

    expect(result).toEqual(origin)
    expect(geo.status.value).toBe('ok')
  })
})
