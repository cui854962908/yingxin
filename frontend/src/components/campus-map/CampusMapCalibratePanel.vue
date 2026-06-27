<script setup lang="ts">
import { computed, ref } from 'vue'
import { campusLngLatToXz } from './campusGeo'
import { formatLngLat, formatOverridesForSource } from './campusCalibration'
import {
  formatRoadOverridesForSource,
  type RoadLngLatSegment,
} from './campusRoadCalibration'
import type { CalibrateTool } from '../../composables/useCampusRoadCalibrate'
import type { CampusPlace } from './types'
import type { PoiOverrides } from './campusCalibration'

const props = defineProps<{
  tool: CalibrateTool
  selected: CampusPlace
  overrides: PoiOverrides
  basePlaces: CampusPlace[]
  roadSegments: RoadLngLatSegment[]
  pendingRoad: boolean
}>()

const emit = defineEmits<{
  'update:tool': [value: CalibrateTool]
  clearPoi: []
  merged: []
  published: []
  undoRoad: []
  clearRoad: []
}>()

const isDev = import.meta.env.DEV
const copyHint = ref('')

const overrideCount = computed(() => Object.keys(props.overrides).length)

const selectedXz = computed(() => {
  const [x, z] = campusLngLatToXz(props.selected.location[0], props.selected.location[1])
  return { x: x.toFixed(2), z: z.toFixed(2) }
})

async function copyPoiSnippet() {
  if (!overrideCount.value) {
    copyHint.value = '请先拖动至少一个地点并松手保存'
    return
  }
  const text = formatOverridesForSource(props.basePlaces, props.overrides)
  try {
    await navigator.clipboard.writeText(text)
    copyHint.value = '已复制 POI x/z 片段'
  } catch {
    copyHint.value = '复制失败，请改用下载 JSON'
  }
}

function downloadPoiJson() {
  if (!overrideCount.value) {
    copyHint.value = '暂无已调整坐标'
    return
  }
  downloadJson('campus-poi-overrides.json', props.overrides)
  copyHint.value = '已下载 POI JSON'
}

async function copyRoadSnippet() {
  if (!props.roadSegments.length) {
    copyHint.value = '请先在地图上标至少一段路'
    return
  }
  try {
    await navigator.clipboard.writeText(formatRoadOverridesForSource(props.roadSegments))
    copyHint.value = '已复制路网片段，可粘贴进 campusRoadNetwork.ts'
  } catch {
    copyHint.value = '复制失败，请改用下载 JSON'
  }
}

function downloadRoadJson() {
  if (!props.roadSegments.length) {
    copyHint.value = '暂无手绘路网'
    return
  }
  downloadJson('campus-road-overrides.json', props.roadSegments)
  copyHint.value = '已下载路网 JSON'
}

function downloadJson(name: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = name
  link.click()
  URL.revokeObjectURL(url)
}

async function publishPoiToLan() {
  if (!overrideCount.value) {
    copyHint.value = '请先拖动至少一个地点并松手保存'
    return
  }
  copyHint.value = '正在发布到局域网…'
  try {
    const res = await fetch('/__dev/publish-campus-poi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(props.overrides),
    })
    const data = await res.json() as { ok: boolean; updated?: number; error?: string }
    if (!res.ok || !data.ok) {
      copyHint.value = data.error ?? '发布失败'
      return
    }
    emit('published')
    copyHint.value = `已发布 ${data.updated ?? overrideCount.value} 个 POI，手机刷新 /campus/2d 即可`
  } catch {
    copyHint.value = '发布失败，请确认 npm run dev 已启动'
  }
}

async function mergeToSource() {
  if (!overrideCount.value) {
    copyHint.value = '请先拖动至少一个 POI'
    return
  }
  copyHint.value = '正在写进 campusPlaces.ts…'
  try {
    const res = await fetch('/__dev/merge-campus-poi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(props.overrides),
    })
    const data = await res.json() as { ok: boolean; updated?: number; error?: string }
    if (!res.ok || !data.ok) {
      copyHint.value = data.error ?? '写死失败'
      return
    }
    emit('merged')
    copyHint.value = `已写死 ${data.updated ?? overrideCount.value} 个 POI`
  } catch {
    copyHint.value = '写死请求失败，请确认 npm run dev 已启动'
  }
}
</script>

<template>
  <aside class="calibrate-panel" aria-label="地图校准">
    <header>
      <strong>校准模式</strong>
      <span>维护用 · 普通用户不可见</span>
    </header>
    <div class="calibrate-tool-tabs" role="tablist">
      <button
        type="button"
        role="tab"
        :class="{ active: tool === 'poi' }"
        :aria-selected="tool === 'poi'"
        @click="emit('update:tool', 'poi')"
      >
        标 POI
      </button>
      <button
        type="button"
        role="tab"
        :class="{ active: tool === 'road' }"
        :aria-selected="tool === 'road'"
        @click="emit('update:tool', 'road')"
      >
        标路网
      </button>
    </div>

    <template v-if="tool === 'poi'">
      <p class="calibrate-tip">拖动圆点对齐底图位置，松手自动保存。</p>
      <dl class="calibrate-current">
        <div><dt>当前选中</dt><dd>{{ selected.name }}</dd></div>
        <div><dt>高德坐标</dt><dd>{{ formatLngLat(selected.location) }}</dd></div>
        <div><dt>源码 x/z</dt><dd>{{ selectedXz.x }}, {{ selectedXz.z }}</dd></div>
        <div><dt>已调整 POI</dt><dd>{{ overrideCount }} 个</dd></div>
      </dl>
      <div class="calibrate-actions">
        <button v-if="isDev" type="button" class="primary" @click="publishPoiToLan">发布 POI 到局域网</button>
        <button v-if="isDev" type="button" @click="mergeToSource">写死 POI 进源码</button>
        <button type="button" @click="copyPoiSnippet">复制 POI 片段</button>
        <button type="button" @click="downloadPoiJson">下载 POI JSON</button>
        <button type="button" @click="emit('clearPoi')">清除 POI 暂存</button>
      </div>
    </template>

    <template v-else>
      <p class="calibrate-tip">
        沿底图<strong>可步行的大路</strong>点击：第一次点起点，第二次点终点 → 生成一段绿线。
        多段首尾相接即可；标完后路线只走绿线，不再穿楼。
      </p>
      <dl class="calibrate-current">
        <div><dt>状态</dt><dd>{{ pendingRoad ? '已选起点，请点击终点' : '请点击路段起点' }}</dd></div>
        <div><dt>已标路段</dt><dd>{{ roadSegments.length }} 段</dd></div>
      </dl>
      <div class="calibrate-actions">
        <button type="button" @click="copyRoadSnippet">复制路网片段</button>
        <button type="button" @click="downloadRoadJson">下载路网 JSON</button>
        <button type="button" @click="emit('undoRoad')">撤销上一段</button>
        <button type="button" @click="emit('clearRoad')">清除路网暂存</button>
      </div>
    </template>

    <p v-if="copyHint" class="calibrate-hint" role="status">{{ copyHint }}</p>
  </aside>
</template>
