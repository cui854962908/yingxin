<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { campusCategories, countPlacesByCategory } from './campusPlaces'
import type { CampusPlace, CategoryKey } from './types'

const props = defineProps<{
  places: CampusPlace[]
  selectedId?: string
  query: string
  category: CategoryKey | 'all'
  sheetExpanded?: boolean
  detailPlace?: CampusPlace | null
}>()

const emit = defineEmits<{
  'update:query': [value: string]
  'update:category': [value: CategoryKey | 'all']
  'update:sheetExpanded': [value: boolean]
  select: [place: CampusPlace]
  go: []
}>()

const expanded = ref(props.sheetExpanded ?? false)

watch(
  () => props.sheetExpanded,
  (value) => {
    if (value !== undefined) expanded.value = value
  },
)

watch(expanded, (value) => emit('update:sheetExpanded', value))

const resultText = computed(() => `${props.places.length} 个结果`)
const detailCategory = computed(() =>
  campusCategories.find((item) => item.key === props.detailPlace?.category),
)

function categoryLabel(key: CategoryKey | 'all', label: string) {
  return `${label} ${countPlacesByCategory(key)}`
}

function toggleSheet() {
  expanded.value = !expanded.value
}

function onSelect(place: CampusPlace) {
  emit('select', place)
  expanded.value = false
}

function onSearchFocus() {
  expanded.value = true
}

function backToList() {
  expanded.value = true
}

// ---------- 触摸拖拽手势 ----------
const swipeY = ref(0)
const swiping = ref(false)
let swipeStartY = 0
let swipeStartExpanded = false
/** 有效拖动阈值（px），上拉超过此距离展开，下拉超过此距离收起 */
const SWIPE_THRESHOLD = 16

const swipeTranslateStyle = computed(() => {
  if (!swiping.value) return undefined
  const capped = Math.max(-60, Math.min(60, swipeY.value))
  return { transform: `translateY(${capped}px)`, transition: 'none' }
})

function onTouchStart(e: TouchEvent) {
  if (e.touches.length !== 1) return
  swiping.value = true
  swipeStartY = e.touches[0].clientY
  swipeStartExpanded = expanded.value
  swipeY.value = 0
}

function onTouchMove(e: TouchEvent) {
  if (!swiping.value || e.touches.length !== 1) return
  const dy = e.touches[0].clientY - swipeStartY
  swipeY.value = dy
  if (!swipeStartExpanded && dy < -SWIPE_THRESHOLD) {
    expanded.value = true
  } else if (swipeStartExpanded && dy > SWIPE_THRESHOLD) {
    expanded.value = false
  }
  e.preventDefault()
}

function onTouchEnd() {
  swiping.value = false
  swipeY.value = 0
}
</script>

<template>
  <aside
    class="campus-sidebar"
    :class="{
      'campus-sidebar--expanded': expanded,
      'campus-sidebar--collapsed': !expanded && !detailPlace,
      'campus-sidebar--detail': !expanded && !!detailPlace,
    }"
    :style="swipeTranslateStyle"
  >
    <button
      type="button"
      class="campus-sheet-handle"
      :aria-expanded="expanded"
      aria-label="展开或收起地点列表"
      @click="toggleSheet"
      @touchstart="onTouchStart"
      @touchmove.prevent="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
    >
      <span class="campus-sheet-handle__bar" aria-hidden="true" />
      <span class="campus-sheet-handle__label">
        <template v-if="detailPlace && !expanded">{{ detailPlace.name }}</template>
        <template v-else>地点列表 · {{ resultText }}</template>
      </span>
      <span class="campus-sheet-handle__chevron" aria-hidden="true">{{ expanded ? '▼' : '▲' }}</span>
    </button>

    <!-- 详情态：地点摘要卡片 -->
    <div v-if="detailPlace && !expanded" class="place-detail-card">
      <div class="place-detail-head">
        <i :style="{ background: detailCategory?.color }">
          {{ detailCategory?.label[0] }}
        </i>
        <div>
          <strong>{{ detailPlace.name }}</strong>
          <em>{{ detailCategory?.label }} · {{ detailPlace.tags[0] }}</em>
        </div>
      </div>
      <p>{{ detailPlace.description }}</p>
      <div class="place-detail-actions">
        <button class="primary" type="button" @click="$emit('go')">去这里</button>
        <button class="secondary" type="button" @click="backToList">返回列表</button>
      </div>
    </div>

    <!-- 展开/收起态：完整地点列表 -->
    <template v-else>
      <label class="place-search">
        <span>⌕</span>
        <input
          :value="query"
          placeholder="搜索名称、标签、简介…"
          @focus="onSearchFocus"
          @input="emit('update:query', ($event.target as HTMLInputElement).value)"
        />
      </label>
      <div class="category-grid" role="tablist" aria-label="地点分类">
        <button
          type="button"
          role="tab"
          :class="{ active: category === 'all' }"
          :aria-selected="category === 'all'"
          @click="emit('update:category', 'all')"
        >
          <i class="all-dot">全</i>{{ categoryLabel('all', '全部') }}
        </button>
        <button
          v-for="item in campusCategories"
          :key="item.key"
          type="button"
          role="tab"
          :class="{ active: category === item.key }"
          :aria-selected="category === item.key"
          @click="emit('update:category', item.key)"
        >
          <i :style="{ color: item.color, background: `${item.color}18` }">{{ item.label[0] }}</i>
          {{ categoryLabel(item.key, item.label) }}
        </button>
      </div>
      <div class="list-title"><strong>地点列表</strong><span>{{ resultText }}</span></div>
      <div class="place-list" @wheel.stop>
        <button
          v-for="place in places"
          :key="place.id"
          type="button"
          :class="{ selected: selectedId === place.id }"
          @click="onSelect(place)"
        >
          <i
            :style="{ background: campusCategories.find((item) => item.key === place.category)?.color }"
          >{{ campusCategories.find((item) => item.key === place.category)?.label[0] }}</i>
          <span>
            <strong>{{ place.name }}</strong>
            <p>{{ place.description }}</p>
            <em>{{ campusCategories.find((item) => item.key === place.category)?.label }} · {{ place.tags[0] }}</em>
          </span>
        </button>
        <p v-if="!places.length" class="empty-list">没有找到符合条件的地点</p>
      </div>
    </template>
  </aside>
</template>
