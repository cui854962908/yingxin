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
}>()

const emit = defineEmits<{
  'update:query': [value: string]
  'update:category': [value: CategoryKey | 'all']
  'update:sheetExpanded': [value: boolean]
  select: [place: CampusPlace]
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
</script>

<template>
  <aside
    class="campus-sidebar"
    :class="{ 'campus-sidebar--expanded': expanded, 'campus-sidebar--collapsed': !expanded }"
  >
    <button
      type="button"
      class="campus-sheet-handle"
      :aria-expanded="expanded"
      aria-label="展开或收起地点列表"
      @click="toggleSheet"
    >
      <span class="campus-sheet-handle__bar" aria-hidden="true" />
      <span class="campus-sheet-handle__label">地点列表 · {{ resultText }}</span>
      <span class="campus-sheet-handle__chevron" aria-hidden="true">{{ expanded ? '▼' : '▲' }}</span>
    </button>
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
  </aside>
</template>
