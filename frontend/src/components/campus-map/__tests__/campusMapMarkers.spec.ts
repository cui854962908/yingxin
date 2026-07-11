import { describe, expect, it, vi } from 'vitest'
import { campusPlaces } from '../campusPlaces'
import { createCampusMarkerLayer } from '../campusMapMarkers'

describe('campusMapMarkers mobile selection', () => {
  it('binds selection directly to each marker button', () => {
    const created: Array<{ options: { content: unknown }; on: ReturnType<typeof vi.fn> }> = []
    const map = { add: vi.fn(), remove: vi.fn() }
    const AMap = {
      Marker: vi.fn(function Marker(options: { content: unknown }) {
        const marker = { options, on: vi.fn() }
        created.push(marker)
        return marker
      }),
    }
    const onSelect = vi.fn()
    const layer = createCampusMarkerLayer({
      getMap: () => map,
      getAMap: () => AMap,
      getPoiDraggable: () => false,
      categoryColor: () => '#b5343a',
      onSelect,
      onMoved: vi.fn(),
      refreshUserMarker: vi.fn(),
    })

    layer.render(campusPlaces.slice(0, 2), campusPlaces[0].id)
    const secondButton = created[1].options.content

    expect(secondButton).toBeInstanceOf(HTMLButtonElement)
    ;(secondButton as HTMLButtonElement).click()
    expect(onSelect).toHaveBeenCalledWith(campusPlaces[1])
  })

  it('supports draggable markers and removes existing markers on clear', () => {
    const dragHandlers: Array<() => void> = []
    const map = { add: vi.fn(), remove: vi.fn() }
    const AMap = {
      Marker: vi.fn(function Marker(options: { content: unknown }) {
        return {
          options,
          on: vi.fn((event: string, handler: () => void) => {
            if (event === 'dragend') dragHandlers.push(handler)
          }),
          getPosition: () => ({ lng: 113.6, lat: 34.8 }),
        }
      }),
    }
    const onMoved = vi.fn()
    const layer = createCampusMarkerLayer({
      getMap: () => map,
      getAMap: () => AMap,
      getPoiDraggable: () => true,
      categoryColor: () => '#b5343a',
      onSelect: vi.fn(),
      onMoved,
      refreshUserMarker: vi.fn(),
    })

    layer.render(campusPlaces.slice(0, 1), campusPlaces[0].id)
    dragHandlers[0]()
    layer.clear()

    expect(onMoved).toHaveBeenCalledWith(campusPlaces[0].id, [113.6, 34.8])
    expect(map.remove).toHaveBeenCalledTimes(1)
  })

  it('returns early when map runtime is unavailable', () => {
    const map = { add: vi.fn(), remove: vi.fn() }
    const AMap = {
      Marker: vi.fn(),
    }
    const layer = createCampusMarkerLayer({
      getMap: () => null,
      getAMap: () => AMap,
      getPoiDraggable: () => false,
      categoryColor: () => '#b5343a',
      onSelect: vi.fn(),
      onMoved: vi.fn(),
      refreshUserMarker: vi.fn(),
    })

    layer.render(campusPlaces.slice(0, 1), campusPlaces[0].id)
    layer.clear()

    expect(AMap.Marker).not.toHaveBeenCalled()
    expect(map.add).not.toHaveBeenCalled()
  })
})
