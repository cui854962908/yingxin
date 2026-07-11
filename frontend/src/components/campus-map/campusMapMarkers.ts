import type { CampusPlace, CategoryKey } from './types'

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

  function createMarkerButton(place: CampusPlace, draggable: boolean) {
    const button = document.createElement('button')
    button.type = 'button'
    button.className = draggable ? 'campus-poi-dot campus-poi-dot--drag' : 'campus-poi-dot'
    button.style.setProperty('--poi', options.categoryColor(place.category))
    button.setAttribute('aria-label', place.name)
    button.addEventListener('click', (event) => {
      event.stopPropagation()
      options.onSelect(place)
    })
    return button
  }

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
      const marker = new AMap.Marker({
        position: place.location,
        anchor: 'center',
        draggable,
        cursor: draggable ? 'move' : 'pointer',
        content: createMarkerButton(place, draggable),
        zIndex: selectedId === place.id ? 150 : 120,
      })
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
