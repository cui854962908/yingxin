import type { CampusPlace, CategoryKey } from './types'

function escapeHtmlAttr(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;')
}

export interface CampusMarkerLayer {
  clear: () => void
  render: (places: CampusPlace[], selectedId: string) => void
}

interface MarkerLayerOptions {
  getMap: () => any
  getAMap: () => any
  getPoiDraggable: () => boolean
  categoryColor: (key: CategoryKey) => string
  onSelect: (place: CampusPlace) => void
  onMoved: (id: string, lnglat: [number, number]) => void
  refreshUserMarker: () => void
}

export function createCampusMarkerLayer(options: MarkerLayerOptions): CampusMarkerLayer {
  let markers: any[] = []

  function clear() {
    const map = options.getMap()
    if (map && markers.length) map.remove(markers)
    markers = []
  }

  function render(places: CampusPlace[], selectedId: string) {
    const map = options.getMap()
    const AMap = options.getAMap()
    if (!map || !AMap) return
    clear()
    const draggable = options.getPoiDraggable()
    markers = places.map((place) => {
      const dotClass = draggable ? 'campus-poi-dot campus-poi-dot--drag' : 'campus-poi-dot'
      const marker = new AMap.Marker({
        position: place.location,
        anchor: 'center',
        draggable,
        cursor: draggable ? 'move' : 'pointer',
        content: `<button type="button" class="${dotClass}" style="--poi:${options.categoryColor(place.category)}" aria-label="${escapeHtmlAttr(place.name)}"></button>`,
        zIndex: selectedId === place.id ? 150 : 120,
      })
      marker.on('click', () => options.onSelect(place))
      if (draggable) {
        marker.on('dragend', () => {
          const pos = marker.getPosition()
          options.onMoved(place.id, [pos.lng, pos.lat])
        })
      }
      return marker
    })
    map.add(markers)
    options.refreshUserMarker()
  }

  return { clear, render }
}
