<!-- 瓒呮爣渚嬪锛歴cript+template=395琛岋紝2D鍦板浘闆嗘垚POI妫€绱?鍒嗙被/璇︽儏/鏍″噯闈㈡澘/搴曞浘浜や簰锛屾媶鍒嗕細閫犳垚澶ч噺prop-drilling -->
<script setup lang="ts">
import { computed, markRaw, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CampusMapCalibratePanel from './campus-map/CampusMapCalibratePanel.vue'
import CampusMapDetail from './campus-map/CampusMapDetail.vue'
import CampusMapHeader from './campus-map/CampusMapHeader.vue'
import CampusMapPoiSearch from './campus-map/CampusMapPoiSearch.vue'
import CampusMapSidebar from './campus-map/CampusMapSidebar.vue'
import CampusRouteOriginPrompt from './campus-map/desktop/CampusRouteOriginPrompt.vue'
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
import { useDesktopRouteOrigin } from '../composables/campus-map/useDesktopRouteOrigin'
import { useBreakpoint } from '../composables/useBreakpoint'
import { useCampusRoadCalibrate } from '../composables/useCampusRoadCalibrate'
import { useAuth } from '../composables/useAuth'
import { useCampusRouteNavigation } from '../composables/campus-map/useCampusRouteNavigation'
import { planCampusRoute } from './campus-map/campusPathfind'
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
const placeSheetExpanded = ref(false)
const placeDetailOpen = ref(false)
const userPickedPlace = ref(false)
const sheetDetail = computed(() => !placeSheetExpanded.value && userPickedPlace.value)
const { width } = useBreakpoint()
const isDesktopMap = computed(() => width.value > 1100)

function useMobileDetailSheet(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(max-width: 1100px)').matches
}

let map: any = null
let AMapRef: any = null
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
  getProfileDormitory: () => student.value?.dormitory,
})

const {
  status: geoStatus, message: geoMessage, position: userLocation,
  userLocationLabel, routeOriginKind, profileDormLabel,
  locateMyPosition, locateAtProfileDorm, setPlaceAsOrigin,
  refreshMarker, clearMarker: clearUserMarker,
} = location

const {
  routeMessage,
  routeDistance,
  routePlanning,
  activeRouteTarget,
  clearRoute,
  planRouteToPlace,
  rerouteToActiveTarget,
} = useCampusRouteNavigation({
  getMap: () => map,
  getAMap: () => AMapRef,
  getOrigin: () => userLocation.value,
  getOriginLabel: () => userLocationLabel.value,
  getRoadSegments: () => drawnRoadSegments.value,
  planRoute: planCampusRoute,
  setGeoMessage: (message) => { geoMessage.value = message },
})

const desktopOrigin = useDesktopRouteOrigin({
  isDesktop: isDesktopMap,
  hasOrigin: computed(() => !!userLocation.value),
  profileDormLabel,
  locateAtProfileDorm,
  locateMyPosition,
  setPlaceAsOrigin,
  planRoute: planRouteToPlace,
  onMobileMissing: () => { geoMessage.value = '\u8bf7\u9009\u62e9\u5730\u56fe\u4e0a\u7684\u5730\u70b9\u4f5c\u4e3a\u8def\u7ebf\u8d77\u70b9\uff0c\u7136\u540e\u7ee7\u7eed\u5bfc\u822a' },
  getGeoMessage: () => geoMessage.value,
})
const { promptOpen, promptMessage, choosingOrigin } = desktopOrigin

function categoryColor(key: CategoryKey) {
  return campusCategories.find((item) => item.key === key)?.color || '#7b3294'
}

function saveMovedPlace(id: string, lnglat: [number, number]) {
  localPoiOverrides.value = { ...localPoiOverrides.value, [id]: lnglat }
  savePoiOverrides(localPoiOverrides.value)
  if (selected.value.id === id) selected.value = { ...selected.value, location: lnglat }
}

function selectPlace(place: CampusPlace) {
  if (desktopOrigin.useSelectedPlace(place)) return
  selected.value = place
  clearRoute()
  userPickedPlace.value = true
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
  desktopOrigin.requestRoute(place)
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

function goToSelectedPlace() {
  dismissMobileSheets()
  desktopOrigin.requestRoute(selected.value)
}

function startMapOriginSelection() {
  geoMessage.value = '璇烽€夋嫨鍦板浘鏍囪鎴栧乏渚у湴鐐癸紝浣滀负鏍″唴璺嚎璧风偣'
  desktopOrigin.beginMapSelection()
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
    /* 鑷姩瀹氫綅鏄撹娴忚鍣ㄥ洜闈炵敤鎴锋墜鍔胯€岄潤榛樻嫆缁濓紱鏀逛负鐢ㄦ埛鏄惧紡鐐瑰嚮 "GPS瀹氫綅" */
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '\u5730\u56fe\u521d\u59cb\u5316\u5931\u8d25'
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
  if (userLocation.value) rerouteToActiveTarget()
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
      'campus-map-page--sheet-detail': sheetDetail,
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
        :detail-place="placeSheetExpanded || !userPickedPlace ? null : selected"
        @select="selectPlace"
        @go="goToSelectedPlace"
      />
      <div class="campus-map-center">
        <section class="campus-map-stage">
          <div ref="mapEl" class="campus-map-canvas" />
          <CampusMapPoiSearch
            v-if="!calibrateMode && !loading && !error"
            :places="allPlaces"
            @select="pickDestination"
          />
          <CampusRouteOriginPrompt
            v-if="isDesktopMap"
            :open="promptOpen"
            :message="promptMessage"
            :dorm-label="profileDormLabel"
            :locating="geoStatus === 'loading'"
            @dorm="desktopOrigin.chooseDorm"
            @device="desktopOrigin.chooseDevice"
            @map="startMapOriginSelection"
            @cancel="desktopOrigin.cancelPrompt"
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
              :aria-label="`\u5b9a\u4f4d\u5230${profileDormLabel}`"
              @click="desktopOrigin.chooseDorm"
            >
              <span class="map-tool-btn__icon" aria-hidden="true">⌂</span>
              <span class="map-tool-btn__label">{{ isDesktopMap ? profileDormLabel : '鎴戠殑瀹胯垗' }}</span>
            </button>
            <button
              class="locate-me map-tool-btn"
              type="button"
              :disabled="geoStatus === 'loading'"
              aria-label="璁惧瀹氫綅"
              @click="desktopOrigin.chooseDevice"
            >
              <span class="map-tool-btn__icon" aria-hidden="true">◎</span>
              <span class="map-tool-btn__label">{{ geoStatus === 'loading' ? '\u5b9a\u4f4d\u4e2d' : (isDesktopMap ? '\u8bbe\u5907\u5b9a\u4f4d' : 'GPS\u5b9a\u4f4d') }}</span>
            </button>
            <button class="locate-me map-tool-btn" type="button" @click="startMapOriginSelection">
              <span class="map-tool-btn__icon" aria-hidden="true">⌖</span>
              <span class="map-tool-btn__label">{{ choosingOrigin ? '\u6b63\u5728\u9009\u8d77\u70b9' : '\u9009\u62e9\u8d77\u70b9' }}</span>
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
            <span v-if="userLocation && !calibrateMode"><i class="legend-user-dot" />{{ routeOriginKind === 'gps' ? '当前位置' : `路线起点：${userLocationLabel}` }}</span>
            <span v-for="item in campusCategories" :key="item.key"><i :style="{ background: item.color }" />{{ item.label }}</span>
          </div>
          <div v-if="showMapCoordinate" class="map-coordinate">涓績 {{ centerText }} 路 缂╂斁 {{ zoom }}</div>
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
