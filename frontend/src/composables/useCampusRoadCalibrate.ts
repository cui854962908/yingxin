import { computed, ref, watch, type Ref } from 'vue'
import {
  clearRoadOverrides,
  loadRoadOverrides,
  roadOverridesToPoiSegments,
  saveRoadOverrides,
  type RoadLngLatSegment,
} from '../components/campus-map/campusRoadCalibration'
import { createRoadDrawLayer } from '../components/campus-map/campusMapRoadDraw'
import type { CampusRoadSegment } from '../components/campus-map/campusRoadNetwork'

export type CalibrateTool = 'poi' | 'road'

interface Options {
  getMap: () => any
  getAMap: () => any
  calibrateMode: Ref<boolean>
}

export function useCampusRoadCalibrate(options: Options) {
  const calibrateTool = ref<CalibrateTool>('poi')
  const roadOverrides = ref<RoadLngLatSegment[]>(loadRoadOverrides())
  const pendingRoadStart = ref<[number, number] | null>(null)

  const drawnRoadSegments = computed<CampusRoadSegment[]>(() =>
    roadOverridesToPoiSegments(roadOverrides.value),
  )

  const roadLayer = createRoadDrawLayer({
    getMap: options.getMap,
    getAMap: options.getAMap,
    isActive: () => options.calibrateMode.value && calibrateTool.value === 'road',
  })

  function refreshRoadOverlay() {
    if (!options.calibrateMode.value) {
      roadLayer.clear()
      roadLayer.unbindClick()
      return
    }
    roadLayer.render(roadOverrides.value, pendingRoadStart.value)
    if (calibrateTool.value === 'road') {
      roadLayer.bindClick(handleMapClick)
    } else {
      roadLayer.unbindClick()
    }
  }

  function handleMapClick(lnglat: [number, number]) {
    if (!pendingRoadStart.value) {
      pendingRoadStart.value = lnglat
      refreshRoadOverlay()
      return
    }
    roadOverrides.value = [
      ...roadOverrides.value,
      { start: pendingRoadStart.value, end: lnglat },
    ]
    saveRoadOverrides(roadOverrides.value)
    pendingRoadStart.value = null
    refreshRoadOverlay()
  }

  function undoRoadSegment() {
    if (pendingRoadStart.value) {
      pendingRoadStart.value = null
    } else if (roadOverrides.value.length) {
      roadOverrides.value = roadOverrides.value.slice(0, -1)
      saveRoadOverrides(roadOverrides.value)
    }
    refreshRoadOverlay()
  }

  function clearRoadSegments() {
    clearRoadOverrides()
    roadOverrides.value = []
    pendingRoadStart.value = null
    refreshRoadOverlay()
  }

  function reloadRoadOverrides() {
    roadOverrides.value = loadRoadOverrides()
    pendingRoadStart.value = null
    refreshRoadOverlay()
  }

  watch([options.calibrateMode, calibrateTool], () => refreshRoadOverlay())

  return {
    calibrateTool,
    roadOverrides,
    pendingRoadStart,
    drawnRoadSegments,
    refreshRoadOverlay,
    undoRoadSegment,
    clearRoadSegments,
    reloadRoadOverrides,
    cleanupRoadLayer: () => {
      roadLayer.unbindClick()
      roadLayer.clear()
    },
  }
}
