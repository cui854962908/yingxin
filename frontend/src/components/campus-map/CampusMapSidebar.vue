<script setup lang="ts">
import { computed } from 'vue'
import { campusCategories, countPlacesByCategory } from './campusPlaces'
import type { CampusPlace, CategoryKey } from './types'

const props = defineProps<{
  places: CampusPlace[]
  selectedId?: string
  query: string
  category: CategoryKey | 'all'
}>()

const emit = defineEmits<{
  'update:query': [value: string]
  'update:category': [value: CategoryKey | 'all']
  select: [place: CampusPlace]
}>()

const resultText = computed(() => `${props.places.length} 个结果`)

function categoryLabel(key: CategoryKey | 'all', label: string) {
  return `${label} ${countPlacesByCategory(key)}`
}
</script>

<template>
  <aside class="campus-sidebar">
    <label class="place-search">
      <span>⌕</span>
      <input
        :value="query"
        placeholder="搜索名称、标签、简介…"
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
        @click="emit('select', place)"
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
