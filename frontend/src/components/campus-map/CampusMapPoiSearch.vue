<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { campusCategories, filterCampusPlacesByQuery } from './campusPlaces'
import type { CampusPlace } from './types'

const props = defineProps<{
  places: CampusPlace[]
}>()

const emit = defineEmits<{
  select: [place: CampusPlace]
}>()

const query = ref('')
const open = ref(false)
const rootEl = ref<HTMLElement | null>(null)

const trimmedQuery = computed(() => query.value.trim())

const results = computed(() => {
  if (!trimmedQuery.value) return []
  return filterCampusPlacesByQuery(props.places, trimmedQuery.value, 'all', 8)
})

const showDropdown = computed(() => open.value && trimmedQuery.value.length > 0)

function categoryMeta(key: CampusPlace['category']) {
  return campusCategories.find((item) => item.key === key)
}

function onFocus() {
  open.value = true
}

function onInput(event: Event) {
  query.value = (event.target as HTMLInputElement).value
  open.value = true
}

function clearQuery() {
  query.value = ''
  open.value = false
}

function pick(place: CampusPlace) {
  emit('select', place)
  query.value = ''
  open.value = false
}

function onDocPointerDown(event: PointerEvent) {
  if (!rootEl.value?.contains(event.target as Node)) open.value = false
}

onMounted(() => document.addEventListener('pointerdown', onDocPointerDown, true))
onUnmounted(() => document.removeEventListener('pointerdown', onDocPointerDown, true))
</script>

<template>
  <div ref="rootEl" class="map-poi-search" role="search">
    <label class="map-poi-search__field">
      <span class="map-poi-search__icon" aria-hidden="true">⌕</span>
      <input
        :value="query"
        type="search"
        enterkeyhint="search"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
        placeholder="搜索目的地、地点…"
        aria-label="搜索校园地点"
        aria-autocomplete="list"
        :aria-expanded="showDropdown"
        @focus="onFocus"
        @input="onInput"
      />
      <button
        v-if="query"
        type="button"
        class="map-poi-search__clear"
        aria-label="清除搜索"
        @click="clearQuery"
      >
        ×
      </button>
    </label>
    <ul v-if="showDropdown" class="map-poi-search__dropdown" role="listbox">
      <li v-for="place in results" :key="place.id" role="option">
        <button type="button" @click="pick(place)">
          <i
            :style="{ background: categoryMeta(place.category)?.color }"
            aria-hidden="true"
          >{{ categoryMeta(place.category)?.label[0] }}</i>
          <span>
            <strong>{{ place.name }}</strong>
            <small>{{ categoryMeta(place.category)?.label }} · {{ place.area }}</small>
          </span>
        </button>
      </li>
      <li v-if="!results.length" class="map-poi-search__empty" role="status">
        未找到「{{ trimmedQuery }}」相关地点
      </li>
    </ul>
  </div>
</template>
