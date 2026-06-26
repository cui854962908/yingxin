<script setup lang="ts">
import { computed, markRaw, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import CampusMapDetail from './campus-map/CampusMapDetail.vue'
import CampusMapHeader from './campus-map/CampusMapHeader.vue'
import CampusMapSidebar from './campus-map/CampusMapSidebar.vue'
import { campusCategories, campusPlaces } from './campus-map/campusPlaces'
import {
  campusLimitBoundsFromLocations,
  campusOrigin,
  CAMPUS_DEFAULT_ZOOM,
  CAMPUS_MAP_ZOOMS,
} from './campus-map/campusGeo'
import type { CampusPlace, CampusTab, CategoryKey } from './campus-map/types'
import './campus-map/campus-map.css'

declare global {
  interface Window {
    AMap?: any
    _AMapSecurityConfig?: { serviceHost: string }
  }
}

const router = useRouter()
const mapEl = ref<HTMLElement | null>(null)
const loading = ref(true)
const error = ref('')
const query = ref('')
const category = ref<CategoryKey | 'all'>('all')
const activeTab = ref<CampusTab>('map')
const selected = ref<CampusPlace>(
  campusPlaces.find((place) => place.id === 'scenery-lake') ?? campusPlaces[0],
)
const favorites = ref<string[]>([])
const zoom = ref(17)
const centerText = ref('113.641689, 34.862226')
const routeMode = ref<'walk' | 'ride' | 'drive'>('walk')

let map: any = null
let markers: any[] = []
let routeLine: any = null
let campusCenter: [number, number] = campusOrigin()
let campusZoom = CAMPUS_DEFAULT_ZOOM
let campusBounds: [[number, number], [number, number]] = campusLimitBoundsFromLocations(
  campusPlaces.map((place) => place.location),
)

function applyCampusViewport() {
  if (!map || !window.AMap) return
  const bounds = new window.AMap.Bounds(campusBounds[0], campusBounds[1])
  map.setLimitBounds(bounds)
  map.setBounds(bounds, false, [48, 48, 48, 48])
  const center = map.getCenter()
  campusCenter = [center.lng, center.lat]
  campusZoom = map.getZoom()
  zoom.value = campusZoom
}

const filteredPlaces = computed(() => {
  const text = query.value.trim().toLowerCase()
  return campusPlaces.filter((place) => {
    const matchesCategory = category.value === 'all' || place.category === category.value
    const searchable = `${place.name} ${place.address} ${place.description} ${place.tags.join(' ')}`.toLowerCase()
    const matchesText = !text || searchable.includes(text)
    const matchesFavorite = activeTab.value !== 'favorites' || favorites.value.includes(place.id)
    return matchesCategory && matchesText && matchesFavorite
  })
})

const selectedFavorite = computed(() => favorites.value.includes(selected.value.id))

function loadAmap(key: string): Promise<any> {
  if (window.AMap) return Promise.resolve(window.AMap)
  window._AMapSecurityConfig = { serviceHost: `${window.location.origin}/_AMapService` }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(key)}&plugin=AMap.ToolBar`
    script.async = true
    script.onload = () => window.AMap ? resolve(window.AMap) : reject(new Error('高德地图加载失败'))
    script.onerror = () => reject(new Error('高德地图脚本加载失败'))
    document.head.appendChild(script)
  })
}

function categoryColor(key: CategoryKey) {
  return campusCategories.find((item) => item.key === key)?.color || '#7b3294'
}

function clearMarkers() {
  if (map && markers.length) map.remove(markers)
  markers = []
}

function selectPlace(place: CampusPlace) {
  selected.value = place
  map?.panTo(place.location)
  map?.setZoom(Math.max(map.getZoom(), 17))
}

function renderMarkers(places: CampusPlace[]) {
  if (!map || !window.AMap) return
  clearMarkers()
  markers = places.map((place) => {
    const marker = new window.AMap.Marker({
      position: place.location,
      anchor: 'center',
      content: `<button class="campus-poi-dot" style="--poi:${categoryColor(place.category)}" aria-label="校园地点"></button>`,
      zIndex: selected.value.id === place.id ? 150 : 120,
    })
    marker.on('click', () => selectPlace(place))
    return marker
  })
  map.add(markers)
}

function resetView() {
  clearRoute()
  applyCampusViewport()
}

function toggleFavorite() {
  const id = selected.value.id
  favorites.value = favorites.value.includes(id)
    ? favorites.value.filter((item) => item !== id)
    : [...favorites.value, id]
  localStorage.setItem('campus-map-favorites', JSON.stringify(favorites.value))
}

function clearRoute() {
  if (routeLine && map) map.remove(routeLine)
  routeLine = null
}

function planRoute() {
  if (!window.AMap || !map) return
  clearRoute()
  routeLine = new window.AMap.Polyline({
    path: [campusCenter, selected.value.location],
    strokeColor: routeMode.value === 'walk' ? '#7b3294' : routeMode.value === 'ride' ? '#278b70' : '#3579b8',
    strokeWeight: 6,
    strokeOpacity: .9,
    strokeStyle: routeMode.value === 'walk' ? 'dashed' : 'solid',
    showDir: true,
    lineJoin: 'round',
  })
  map.add(routeLine)
  map.setFitView([routeLine], false, [80, 80, 80, 80])
}

function changeTab(tab: CampusTab) {
  activeTab.value = tab
  if (tab !== 'route') clearRoute()
}

function openRoute() {
  activeTab.value = 'route'
  planRoute()
}

async function initMap() {
  try {
    const response = await fetch('/api/campus-map/config')
    const payload = await response.json()
    if (!response.ok || !payload.success) throw new Error(payload.message || '地图配置不可用')
    campusCenter = payload.data.center
    campusZoom = payload.data.zoom ?? CAMPUS_DEFAULT_ZOOM
    const AMap = await loadAmap(payload.data.key)
    if (!mapEl.value) return
    map = markRaw(new AMap.Map(mapEl.value, {
      viewMode: '2D',
      zoom: campusZoom,
      zooms: CAMPUS_MAP_ZOOMS,
      center: campusCenter,
      mapStyle: 'amap://styles/normal',
      resizeEnable: true,
      dragEnable: true,
      scrollWheel: true,
      keyboardEnable: false,
      showLabel: true,
      features: ['bg', 'road', 'building', 'point'],
    }))
    applyCampusViewport()
    map.addControl(new AMap.ToolBar({ position: { top: '16px', left: '16px' }, liteStyle: false }))
    map.on('mapmove', () => {
      const center = map.getCenter()
      centerText.value = `${center.lng.toFixed(6)}, ${center.lat.toFixed(6)}`
    })
    map.on('zoomchange', () => { zoom.value = map.getZoom() })
    renderMarkers(filteredPlaces.value)
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '地图初始化失败'
  } finally {
    loading.value = false
  }
}

watch(filteredPlaces, (places) => {
  renderMarkers(places)
  if (places.length && !places.some((place) => place.id === selected.value.id)) {
    selected.value = places[0]
  }
})

watch(selected, () => renderMarkers(filteredPlaces.value))

onMounted(() => {
  try {
    favorites.value = JSON.parse(localStorage.getItem('campus-map-favorites') || '[]')
  } catch {
    favorites.value = []
  }
  initMap()
})

onUnmounted(() => {
  clearMarkers()
  clearRoute()
  map?.destroy()
  map = null
})
</script>

<template>
  <main class="campus-map-page">
    <CampusMapHeader
      :active-tab="activeTab"
      :favorite-count="favorites.length"
      @change="changeTab"
      @back="router.push('/campus')"
    />
    <div class="campus-map-layout">
      <CampusMapSidebar
        v-model:query="query"
        v-model:category="category"
        :places="filteredPlaces"
        :selected-id="selected.id"
        @select="selectPlace"
      />
      <section class="campus-map-stage">
        <div ref="mapEl" class="campus-map-canvas" />
        <div v-if="loading" class="campus-map-state">正在加载真实高德校园地图…</div>
        <div v-else-if="error" class="campus-map-state error">{{ error }}</div>
        <button class="reset-campus" type="button" @click="resetView">↶ 重置校园视野</button>
        <div v-if="activeTab === 'route'" class="route-planner">
          <header><strong>路线规划</strong><span>校区中心 → {{ selected.name }}</span></header>
          <div class="route-modes">
            <button v-for="mode in ['walk', 'ride', 'drive'] as const" :key="mode" type="button" :class="{ active: routeMode === mode }" @click="routeMode = mode">
              {{ mode === 'walk' ? '步行' : mode === 'ride' ? '骑行' : '驾车' }}
            </button>
          </div>
          <button class="route-submit" type="button" @click="planRoute">在地图中显示路线</button>
        </div>
        <div v-if="activeTab === 'data'" class="data-card">
          <strong>数据说明</strong>
          <p>底图由高德地图提供。地点坐标与 3D 导览模型对齐；拖动范围限制在英才校区内，个别点位仍建议现场复核。</p>
        </div>
        <div class="map-legend">
          <span v-for="item in campusCategories" :key="item.key"><i :style="{ background: item.color }" />{{ item.label }}</span>
        </div>
        <div class="map-coordinate">中心 {{ centerText }} · 缩放 {{ zoom }}</div>
      </section>
      <CampusMapDetail
        :place="selected"
        :favorite="selectedFavorite"
        @favorite="toggleFavorite"
        @route="openRoute"
        @locate="selectPlace(selected)"
      />
    </div>
  </main>
</template>
