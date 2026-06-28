import { ref } from 'vue'
import { haversineMeters } from '../components/campus-map/campusGeo'
import { pickGcjLngLat } from './campusGpsCoords'

export type CampusGeoStatus = 'idle' | 'loading' | 'ok' | 'error'

const BRAND_RED = '#b5343a'
const OUT_OF_CAMPUS_MSG = '您当前不在学校范围内，无法定位'
/** 移动小于此距离不刷新 marker，避免 GPS 抖动 */
const MIN_TRACK_MOVE_METERS = 4
/** 定位结果缓存 5 分钟，避免页面来回切换时重复调高德 IP 定位 API */
const GEO_CACHE_TTL_MS = 5 * 60 * 1000

interface GeoCache {
  lnglat: [number, number]
  accuracy: number | null
  timestamp: number
}

let _geoCache: GeoCache | null = null

interface GpsReading {
  lnglat: [number, number]
  accuracy: number | null
}

interface CampusGeolocationOptions {
  isWithinCampus?: (lnglat: [number, number]) => boolean
}

function createUserDotElement(): HTMLDivElement {
  const wrap = document.createElement('div')
  wrap.className = 'campus-user-dot-wrap'
  wrap.style.cssText =
    'width:24px;height:24px;display:flex;align-items:center;justify-content:center;pointer-events:none;'
  const dot = document.createElement('div')
  dot.className = 'campus-user-dot'
  dot.setAttribute('aria-label', '我的位置')
  dot.style.cssText = [
    'width:16px',
    'height:16px',
    'border:3px solid #fff',
    'border-radius:50%',
    `background:${BRAND_RED}`,
    'box-shadow:0 0 0 5px rgba(181,52,58,0.35),0 2px 8px rgba(0,0,0,0.28)',
    'box-sizing:border-box',
  ].join(';')
  wrap.appendChild(dot)
  return wrap
}

/** 高德 Geolocation + 浏览器 GPS；统一 GCJ-02，并修正国产机双重偏移 */
export function useCampusGeolocation(options: CampusGeolocationOptions = {}) {
  const status = ref<CampusGeoStatus>('idle')
  const message = ref('')
  const position = ref<[number, number] | null>(null)
  const accuracyMeters = ref<number | null>(null)
  let marker: any = null
  let watchId: number | null = null
  let trackingMap: any = null
  let trackingAMap: any = null

  function isWithinCampus(lnglat: [number, number]): boolean {
    return options.isWithinCampus?.(lnglat) ?? true
  }

  function stopTracking() {
    if (watchId != null && typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId)
    }
    watchId = null
    trackingMap = null
    trackingAMap = null
  }

  function removeMarkerFromMap(map: any) {
    if (marker && map) {
      map.remove(marker)
      marker = null
    }
  }

  function clearMarker(map: any) {
    stopTracking()
    removeMarkerFromMap(map)
  }

  function rejectOutsideCampus(map: any) {
    removeMarkerFromMap(map)
    position.value = null
    accuracyMeters.value = null
    status.value = 'error'
    message.value = OUT_OF_CAMPUS_MSG
  }

  function placeMarker(map: any, AMap: any, lnglat: [number, number]) {
    if (!map || !AMap) return
    if (marker) {
      marker.setPosition(lnglat)
      return
    }
    marker = new AMap.Marker({
      position: lnglat,
      anchor: 'center',
      zIndex: 999,
      bubble: true,
      content: createUserDotElement(),
    })
    map.add(marker)
  }

  function applyPosition(
    map: any,
    AMap: any,
    lnglat: [number, number],
    accuracy: number | null = null,
  ) {
    if (!map || !AMap) return
    placeMarker(map, AMap, lnglat)
    position.value = lnglat
    accuracyMeters.value = accuracy
    status.value = 'ok'
    if (message.value === OUT_OF_CAMPUS_MSG) message.value = ''
  }

  function applyGpsPosition(
    map: any,
    AMap: any,
    lnglat: [number, number],
    accuracy: number | null,
    fromWatch = false,
  ): boolean {
    if (!isWithinCampus(lnglat)) {
      rejectOutsideCampus(map)
      if (!fromWatch) stopTracking()
      return false
    }
    applyPosition(map, AMap, lnglat, accuracy)
    return true
  }

  function shouldApplyTrackUpdate(lnglat: [number, number]): boolean {
    if (!position.value) return true
    return haversineMeters(position.value, lnglat) >= MIN_TRACK_MOVE_METERS
  }

  function startTracking(map: any, AMap: any) {
    if (!map || !AMap || typeof navigator === 'undefined' || !navigator.geolocation) return
    stopTracking()
    trackingMap = map
    trackingAMap = AMap
    watchId = navigator.geolocation.watchPosition(
      async (pos) => {
        if (!trackingMap || !trackingAMap) return
        const accuracy = Number.isFinite(pos.coords.accuracy) ? pos.coords.accuracy : null
        try {
          const lnglat = await pickGcjLngLat(
            trackingAMap,
            pos.coords.longitude,
            pos.coords.latitude,
          )
          if (!shouldApplyTrackUpdate(lnglat)) return
          applyGpsPosition(trackingMap, trackingAMap, lnglat, accuracy, true)
        } catch {
          /* 持续定位偶发失败时保留上次位置 */
        }
      },
      () => {
        /* watch 回调失败不覆盖已有定位 */
      },
      { enableHighAccuracy: true, maximumAge: 3000, timeout: 20000 },
    )
  }

  function refreshMarker(map: any, AMap: any) {
    if (!position.value || !map || !AMap) return
    placeMarker(map, AMap, position.value)
  }

  function setPosition(map: any, AMap: any, lnglat: [number, number]) {
    if (!map || !AMap) return
    stopTracking()
    applyPosition(map, AMap, lnglat, null)
    message.value = ''
  }

  function fail(text: string) {
    status.value = 'error'
    message.value = text
    return null as [number, number] | null
  }

  function viaBrowser(AMap: any): Promise<GpsReading | null> {
    if (!navigator.geolocation) return Promise.resolve(null)
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const accuracy = Number.isFinite(pos.coords.accuracy) ? pos.coords.accuracy : null
          try {
            const lnglat = await pickGcjLngLat(AMap, pos.coords.longitude, pos.coords.latitude)
            resolve({ lnglat, accuracy })
          } catch {
            resolve(null)
          }
        },
        () => resolve(null),
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
      )
    })
  }

  function viaAmap(AMap: any): Promise<GpsReading | null> {
    return new Promise((resolve) => {
      AMap.plugin('AMap.Geolocation', () => {
        const geo = new AMap.Geolocation({
          enableHighAccuracy: true,
          timeout: 15000,
          convert: true,
          GeoLocationFirst: true,
          showButton: false,
          showMarker: false,
          showCircle: false,
          panToLocation: false,
        })
        geo.getCurrentPosition((st: string, result: {
          position?: { lng: number; lat: number }
          accuracy?: number
        }) => {
          if (st !== 'complete' || !result?.position) {
            resolve(null)
            return
          }
          resolve({
            lnglat: [result.position.lng, result.position.lat],
            accuracy: typeof result.accuracy === 'number' ? result.accuracy : null,
          })
        })
      })
    })
  }

  function pickInCampusReading(...readings: Array<GpsReading | null>): GpsReading | null {
    for (const reading of readings) {
      if (reading && isWithinCampus(reading.lnglat)) return reading
    }
    return null
  }

  function _updateCache(lnglat: [number, number], accuracy: number | null) {
    _geoCache = { lnglat, accuracy, timestamp: Date.now() }
  }

  async function locate(map: any, AMap: any): Promise<[number, number] | null> {
    if (!map || !AMap) return fail('地图尚未就绪')

    // 5 分钟内直接复用缓存，避免重复调高德 IP 定位（付费）
    if (_geoCache && Date.now() - _geoCache.timestamp < GEO_CACHE_TTL_MS) {
      const cached = _geoCache
      if (isWithinCampus(cached.lnglat)) {
        applyPosition(map, AMap, cached.lnglat, cached.accuracy)
        startTracking(map, AMap)
        message.value = ''
        return cached.lnglat
      }
    }

    if (!navigator.geolocation) return fail('当前浏览器不支持定位')
    status.value = 'loading'
    message.value = ''

    const browserReading = await viaBrowser(AMap)
    const inCampus = pickInCampusReading(browserReading)
    if (inCampus) {
      applyPosition(map, AMap, inCampus.lnglat, inCampus.accuracy)
      startTracking(map, AMap)
      _updateCache(inCampus.lnglat, inCampus.accuracy)
      return inCampus.lnglat
    }

    const amapReading = await viaAmap(AMap)
    const fallback = pickInCampusReading(amapReading)
    if (fallback) {
      applyPosition(map, AMap, fallback.lnglat, fallback.accuracy)
      startTracking(map, AMap)
      _updateCache(fallback.lnglat, fallback.accuracy)
      return fallback.lnglat
    }

    if (!browserReading && !amapReading) {
      return fail('无法获取当前位置，请检查定位权限')
    }

    rejectOutsideCampus(map)
    return null
  }

  return {
    status,
    message,
    position,
    accuracyMeters,
    locate,
    setPosition,
    refreshMarker,
    clearMarker,
    stopTracking,
    startTracking,
  }
}

export { OUT_OF_CAMPUS_MSG }
