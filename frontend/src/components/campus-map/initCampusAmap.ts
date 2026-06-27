import { CAMPUS_DEFAULT_ZOOM, CAMPUS_MAP_ZOOMS } from './campusGeo'

declare global {
  interface Window {
    AMap?: any
    _AMapSecurityConfig?: { serviceHost: string }
  }
}

export interface CampusAmapInitResult {
  map: any
  AMap: any
  center: [number, number]
  zoom: number
}

function isValidAmap(amap: unknown): amap is typeof window.AMap {
  return !!(amap && typeof amap === 'object' && (amap as any).Map)
}

function loadAmapScript(key: string): Promise<any> {
  if (isValidAmap(window.AMap)) return Promise.resolve(window.AMap)
  window._AMapSecurityConfig = { serviceHost: `${window.location.origin}/_AMapService` }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(key)}&plugin=AMap.ToolBar,AMap.Geolocation`
    script.async = true
    script.onload = () => {
      try {
        if (isValidAmap(window.AMap)) {
          resolve(window.AMap)
        } else {
          reject(new Error('高德地图加载失败：AMap 对象不可用'))
        }
      } catch (err) {
        reject(err instanceof Error ? err : new Error('高德地图初始化异常'))
      }
    }
    script.onerror = () => reject(new Error('高德地图脚本加载失败'))
    document.head.appendChild(script)
  })
}

function parseConfigError(payload: unknown, status: number): string {
  if (payload && typeof payload === 'object') {
    const record = payload as Record<string, unknown>
    if (typeof record.message === 'string') return record.message
    if (typeof record.detail === 'string') return record.detail
  }
  return status === 503 ? '校园地图服务尚未配置' : '地图配置不可用'
}

export async function initCampusAmapMap(
  mapEl: HTMLElement,
  handlers: {
    onCenterChange: (lng: number, lat: number) => void
    onZoomChange: (zoom: number) => void
  },
): Promise<CampusAmapInitResult> {
  const response = await fetch('/api/campus-map/config')
  const payload = await response.json()
  if (!response.ok || !payload.success) {
    throw new Error(parseConfigError(payload, response.status))
  }

  const center: [number, number] = payload.data.center
  const zoom: number = payload.data.zoom ?? CAMPUS_DEFAULT_ZOOM
  const AMap = await loadAmapScript(payload.data.key)

  const map = new AMap.Map(mapEl, {
    viewMode: '2D',
    zoom,
    zooms: CAMPUS_MAP_ZOOMS,
    center,
    mapStyle: 'amap://styles/normal',
    resizeEnable: true,
    dragEnable: true,
    scrollWheel: true,
    keyboardEnable: false,
    showLabel: true,
    features: ['bg', 'road', 'building', 'point'],
  })

  map.addControl(new AMap.ToolBar({ position: { top: '16px', left: '16px' }, liteStyle: false }))
  map.on('mapmove', () => {
    const c = map.getCenter()
    handlers.onCenterChange(c.lng, c.lat)
  })
  map.on('zoomchange', () => handlers.onZoomChange(map.getZoom()))

  // 容器在 flex/grid 布局稳定后再刷新尺寸，避免 PC 端初始高度为 0
  requestAnimationFrame(() => {
    map.resize()
  })

  return { map, AMap, center, zoom }
}
