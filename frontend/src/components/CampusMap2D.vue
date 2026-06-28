<!-- 超标例外：script+template=395行，2D地图集成POI检索/分类/详情/校准面板/底图交互，拆分会造成大量prop-drilling -->
<script setup lang="ts">
import { computed, markRaw, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CampusMapCalibratePanel from './campus-map/CampusMapCalibratePanel.vue'
import CampusMapDetail from './campus-map/CampusMapDetail.vue'
import CampusMapHeader from './campus-map/CampusMapHeader.vue'
import CampusMapPoiSearch from './campus-map/CampusMapPoiSearch.vue'
import CampusMapSidebar from './campus-map/CampusMapSidebar.vue'
import {
  applyPoiOverrides,
  clearPoiOverrides,
  isCampusCalibrateMode,
  loadPoiOverrides,
  resolveDisplayPoiOverrides,
  savePoiOverrides,
} from './campus-map/campusCalibration'
import { createCampusMarkerLayer } from './campus-map/campusMapMarkers'
import { campusCategories, campusPlaces, filterCampusPlacesByQuery } from './campus-map/campusPlaces'
import { campusFitBoundsFromLocations, campusOrigin } from './campus-map/campusGeo'
import { initCampusAmapMap } from './campus-map/initCampusAmap'
import type { CampusPlace, CategoryKey } from './campus-map/types'
import { useCampusMapLocation } from '../composables/useCampusMapLocation'
import { useCampusRoadCalibrate } from '../composables/useCampusRoadCalibrate'
import { useAuth } from '../composables/useAuth'
import { planCampusRoute } from './campus-map/campusPathfind'
import type { CampusRouteResult } from './campus-map/campusPathfind'
import './campus-map/campus-map.css'

const router = useRouter()
const route = useRoute()
const { isAdmin, student } = useAuth()
const calibrateMode = computed(() =>
  isCampusCalibrateMode(route.query as Record<string, string | string[] | null | undefined>, {
    isDev: import.meta.env.DEV,
    isAdmin: isAdmin.value,
  }),
)
const showMapCoordinate = computed(() => calibrateMode.value || import.meta.env.DEV)
const localPoiOverrides = ref<Record<string, [number, number]>>(loadPoiOverrides())
const poiOverrides = computed(() =>
  resolveDisplayPoiOverrides(calibrateMode.value, localPoiOverrides.value),
)
const allPlaces = computed(() => applyPoiOverrides(campusPlaces, poiOverrides.value))
const campusBounds = computed(() =>
  campusFitBoundsFromLocations(allPlaces.value.map((place) => place.location)),
)

const mapEl = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref('')
const query = ref('')
const category = ref<CategoryKey | 'all'>('all')
const selected = ref<CampusPlace>(
  allPlaces.value.find((place) => place.id === 'scenery-lake') ?? allPlaces.value[0],
)
const zoom = ref(17)
const centerText = ref('113.641689, 34.862226')
const routeMessage = ref('')
const routeDistance = ref(0)
const routePlanning = ref(false)
const placeSheetExpanded = ref(false)
const placeDetailOpen = ref(false)
const activeRouteTarget = ref<CampusPlace | null>(null)

function useMobileDetailSheet(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(max-width: 1100px)').matches
}

let map: any = null
let AMapRef: any = null
let routeLine: any = null
let campusCenter: [number, number] = campusOrigin()

const {
  calibrateTool,
  roadOverrides,
  pendingRoadStart,
  drawnRoadSegments,
  refreshRoadOverlay,
  undoRoadSegment,
  clearRoadSegments,
  reloadRoadOverrides,
  cleanupRoadLayer,
} = useCampusRoadCalibrate({
  getMap: () => map,
  getAMap: () => AMapRef,
  calibrateMode,
})

const location = useCampusMapLocation({
  getMap: () => map,
  getAMap: () => AMapRef,
  allPlaces,
  getCampusBounds: () => campusBounds.value,
  getProfileDormitory: () => student.value?.dormitory,
})

const {
  status: geoStatus, message: geoMessage, position: userLocation,
  profileDormLabel,
  locateMyPosition, locateAtProfileDorm, refreshMarker, clearMarker: clearUserMarker,
} = location

function categoryColor(key: CategoryKey) {
  return campusCategories.find((item) => item.key === key)?.color || '#7b3294'
}

function saveMovedPlace(id: string, lnglat: [number, number]) {
  localPoiOverrides.value = { ...localPoiOverrides.value, [id]: lnglat }
  savePoiOverrides(localPoiOverrides.value)
  if (selected.value.id === id) selected.value = { ...selected.value, location: lnglat }
}

function selectPlace(place: CampusPlace) {
  selected.value = place
  clearRoute()
  placeDetailOpen.value = useMobileDetailSheet()
  placeSheetExpanded.value = false
  map?.panTo(place.location)
  map?.setZoom(Math.max(map.getZoom(), 17))
}

function dismissMobileSheets() {
  if (useMobileDetailSheet()) {
    placeDetailOpen.value = false
    placeSheetExpanded.value = false
  }
}

function pickDestination(place: CampusPlace) {
  selected.value = place
  dismissMobileSheets()
  planRouteToPlace(place)
}

function closePlaceDetail() {
  placeDetailOpen.value = false
}

const markerLayer = createCampusMarkerLayer({
  getMap: () => map,
  getAMap: () => AMapRef,
  getPoiDraggable: () => calibrateMode.value && calibrateTool.value === 'poi',
  categoryColor,
  onSelect: selectPlace,
  onMoved: saveMovedPlace,
  refreshUserMarker: () => refreshMarker(map, AMapRef),
})

function syncSelectedFromPlaces(places: CampusPlace[]) {
  const next = places.find((place) => place.id === selected.value.id) ?? places[0]
  if (next) selected.value = next
}

function applyCampusViewport() {
  if (!map || !AMapRef) return
  const bounds = campusFitBoundsFromLocations(allPlaces.value.map((place) => place.location))
  map.setBounds(new AMapRef.Bounds(bounds[0], bounds[1]), false, [48, 48, 48, 48])
  const center = map.getCenter()
  campusCenter = [center.lng, center.lat]
  zoom.value = map.getZoom()
}

const filteredPlaces = computed(() =>
  filterCampusPlacesByQuery(allPlaces.value, query.value, category.value),
)

function renderMarkers(places: CampusPlace[]) {
  markerLayer.render(places, selected.value.id)
}

function clearSavedOverrides() {
  clearPoiOverrides()
  localPoiOverrides.value = {}
  syncSelectedFromPlaces(allPlaces.value)
  renderMarkers(filteredPlaces.value)
}

function onPoiMergedToSource() {
  clearPoiOverrides()
  localPoiOverrides.value = {}
  syncSelectedFromPlaces(campusPlaces)
  renderMarkers(filteredPlaces.value)
}

function clearRoute() {
  if (routeLine && map) map.remove(routeLine)
  routeLine = null
  routeMessage.value = ''
  routeDistance.value = 0
  activeRouteTarget.value = null
}

function drawRouteLine(result: CampusRouteResult) {
  if (!AMapRef || !map) return
  routeDistance.value = result.distanceMeters
  const solid = result.mode !== 'straight-fallback'
  routeLine = new AMapRef.Polyline({
    path: result.path,
    strokeColor: '#7b3294',
    strokeWeight: 6,
    strokeOpacity: .9,
    strokeStyle: solid ? 'solid' : 'dashed',
    showDir: true,
    lineJoin: 'round',
  })
  map.add(routeLine)
  map.setFitView([routeLine], false, [80, 80, 80, 80])
}

function planRouteToPlace(place: CampusPlace) {
  if (!AMapRef || !map || routePlanning.value) return
  if (!userLocation.value) {
    geoMessage.value = '尚未获取当前位置，请使用 GPS 定位或稍后再试'
    return
  }
  routePlanning.value = true
  routeMessage.value = `正在规划前往${place.name}…`
  const result = planCampusRoute(userLocation.value, place.location, drawnRoadSegments.value)
  if (routeLine && map) map.remove(routeLine)
  routeLine = null
  drawRouteLine(result)
  activeRouteTarget.value = place
  routeMessage.value = `前往 ${place.name}${result.message ? ` · ${result.message}` : ''}`
  routePlanning.value = false
}

function goToSelectedPlace() {
  dismissMobileSheets()
  planRouteToPlace(selected.value)
}

async function initMap() {
  try {
    if (!mapEl.value) return
    const result = await initCampusAmapMap(mapEl.value, {
      onCenterChange: (lng, lat) => { centerText.value = `${lng.toFixed(6)}, ${lat.toFixed(6)}` },
      onZoomChange: (value) => { zoom.value = value },
    })
    map = markRaw(result.map)
    AMapRef = result.AMap
    campusCenter = result.center
    applyCampusViewport()
    renderMarkers(filteredPlaces.value)
    refreshRoadOverlay()
    if (!calibrateMode.value) await locateMyPosition()
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '地图初始化失败'
  } finally {
    loading.value = false
  }
}

watch(calibrateMode, () => {
  localPoiOverrides.value = loadPoiOverrides()
  reloadRoadOverrides()
  renderMarkers(filteredPlaces.value)
})

watch(calibrateTool, () => {
  renderMarkers(filteredPlaces.value)
  refreshRoadOverlay()
})

watch(filteredPlaces, (places) => {
  renderMarkers(places)
  if (places.length && !places.some((place) => place.id === selected.value.id)) {
    selected.value = places[0]
  }
})

watch(selected, () => {
  renderMarkers(filteredPlaces.value)
})
watch(poiOverrides, () => syncSelectedFromPlaces(allPlaces.value), { deep: true })
watch(drawnRoadSegments, () => {
  if (activeRouteTarget.value && userLocation.value) {
    planRouteToPlace(activeRouteTarget.value)
  }
})

onMounted(async () => {
  await initMap()
})

onUnmounted(() => {
  markerLayer.clear()
  cleanupRoadLayer()
  clearRoute()
  clearUserMarker(map)
  map?.destroy()
  map = null
  AMapRef = null
})
</script>

<template>
  <main
    class="campus-map-page"
    :class="{
      'campus-map-page--calibrate': calibrateMode,
      'campus-map-page--sheet-expanded': placeSheetExpanded,
      'campus-map-page--detail-open': placeDetailOpen,
      'campus-map-page--route': !!activeRouteTarget && !placeDetailOpen,
    }"
  >
    <CampusMapHeader @back="router.push('/campus')" />
    <div class="campus-map-layout">
      <CampusMapSidebar
        v-model:query="query"
        v-model:category="category"
        v-model:sheet-expanded="placeSheetExpanded"
        :places="filteredPlaces"
        :selected-id="selected.id"
        @select="selectPlace"
      />
      <div class="campus-map-center">
        <section class="campus-map-stage">
          <div ref="mapEl" class="campus-map-canvas" />
          <CampusMapPoiSearch
            v-if="!calibrateMode && !loading && !error"
            :places="allPlaces"
            @select="pickDestination"
          />
          <div v-if="loading" class="campus-map-state">正在加载真实高德校园地图…</div>
          <div v-else-if="error" class="campus-map-state error">{{ error }}</div>
          <CampusMapCalibratePanel
            v-if="calibrateMode && !loading && !error"
            v-model:tool="calibrateTool"
            :selected="selected"
            :overrides="localPoiOverrides"
            :base-places="campusPlaces"
            :road-segments="roadOverrides"
            :pending-road="!!pendingRoadStart"
            @clear-poi="clearSavedOverrides"
            @merged="onPoiMergedToSource"
            @undo-road="undoRoadSegment"
            @clear-road="clearRoadSegments"
          />
          <div v-if="!calibrateMode" class="map-toolstack">
            <button
              v-if="profileDormLabel"
              class="locate-dorm map-tool-btn"
              type="button"
              :aria-label="`定位到${profileDormLabel}`"
              @click="locateAtProfileDorm"
            >
              <span class="map-tool-btn__icon" aria-hidden="true">◎</span>
              <span class="map-tool-btn__label">我的宿舍</span>
            </button>
            <button
              class="locate-me map-tool-btn"
              type="button"
              :disabled="geoStatus === 'loading'"
              aria-label="GPS 定位"
              @click="locateMyPosition"
            >
              <span class="map-tool-btn__icon" aria-hidden="true">⊙</span>
              <span class="map-tool-btn__label">{{ geoStatus === 'loading' ? '定位中' : 'GPS定位' }}</span>
            </button>
          </div>
          <p
            v-if="routeDistance && !calibrateMode"
            class="route-result-toast"
            role="status"
          >
            {{ routeMessage }} · 约 {{ routeDistance }} 米
          </p>
          <p v-else-if="geoMessage && !calibrateMode" class="geo-toast" role="status">{{ geoMessage }}</p>
          <div class="map-legend">
            <span v-if="userLocation && !calibrateMode"><i class="legend-user-dot" />我的位置</span>
            <span v-for="item in campusCategories" :key="item.key"><i :style="{ background: item.color }" />{{ item.label }}</span>
          </div>
          <div v-if="showMapCoordinate" class="map-coordinate">中心 {{ centerText }} · 缩放 {{ zoom }}</div>
        </section>
        <CampusMapDetail
          v-if="!calibrateMode && placeDetailOpen"
          sheet
          :place="selected"
          :route-planning="routePlanning"
          @close="closePlaceDetail"
          @go="goToSelectedPlace"
          @locate="selectPlace(selected)"
        />
      </div>
      <CampusMapDetail
        v-if="!calibrateMode"
        class="campus-detail-desktop"
        :place="selected"
        :route-planning="routePlanning"
        @go="goToSelectedPlace"
        @locate="selectPlace(selected)"
      />
    </div>
  </main>
</template>
