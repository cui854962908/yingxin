import type { RoadLngLatSegment } from './campusRoadCalibration'

export interface RoadDrawLayer {
  clear: () => void
  render: (segments: RoadLngLatSegment[], pendingStart: [number, number] | null) => void
  bindClick: (handler: (lnglat: [number, number]) => void) => void
  unbindClick: () => void
}

export function createRoadDrawLayer(options: {
  getMap: () => any
  getAMap: () => any
  isActive: () => boolean
}): RoadDrawLayer {
  let polylines: any[] = []
  let pendingMarker: any = null
  let clickHandler: ((event: { lnglat: { lng: number; lat: number } }) => void) | null = null

  function clear() {
    const map = options.getMap()
    if (map && polylines.length) map.remove(polylines)
    polylines = []
    if (map && pendingMarker) map.remove(pendingMarker)
    pendingMarker = null
  }

  function render(segments: RoadLngLatSegment[], pendingStart: [number, number] | null) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return
    clear()

    for (const seg of segments) {
      polylines.push(new AMap.Polyline({
        path: [seg.start, seg.end],
        strokeColor: '#278b70',
        strokeWeight: 8,
        strokeOpacity: 0.85,
        zIndex: 90,
      }))
    }

    if (pendingStart) {
      pendingMarker = new AMap.Marker({
        position: pendingStart,
        anchor: 'center',
        content: '<span class="road-pending-dot" aria-hidden="true"></span>',
        zIndex: 95,
      })
      polylines.push(pendingMarker)
    }

    if (polylines.length) map.add(polylines)
  }

  function bindClick(handler: (lnglat: [number, number]) => void) {
    unbindClick()
    const map = options.getMap()
    if (!map) return
    clickHandler = (event: { lnglat: { lng: number; lat: number } }) => {
      if (!options.isActive()) return
      handler([event.lnglat.lng, event.lnglat.lat])
    }
    map.on('click', clickHandler)
  }

  function unbindClick() {
    const map = options.getMap()
    if (map && clickHandler) map.off('click', clickHandler)
    clickHandler = null
  }

  return { clear, render, bindClick, unbindClick }
}
