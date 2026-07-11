<script setup lang="ts">
import type { ForumCategory } from '../../types/forum'
import { FORUM_CATEGORY_ORDER } from '../../utils/forumCategoryUi'

export type ForumSort = 'latest' | 'hot' | 'open'

const props = defineProps<{
  query: string
  sort: ForumSort
  category: ForumCategory | ''
  mineOnly: boolean
  showMine: boolean
}>()

const emit = defineEmits<{
  'update:query': [value: string]
  search: []
  sort: [value: ForumSort]
  category: [value: ForumCategory | '']
  mine: []
}>()

function updateQuery(event: Event) {
  emit('update:query', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <section class="wall-filter-panel" aria-label="问题筛选">
    <div class="wall-search-row">
      <label class="wall-search">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-4-4" />
        </svg>
        <input
          :value="props.query"
          type="search"
          placeholder="搜索问题、关键词、话题..."
          @input="updateQuery"
          @keydown.enter.prevent="emit('search')"
        />
      </label>
      <button type="button" class="wall-search-btn" @click="emit('search')">搜索</button>
    </div>

    <nav class="wall-tabs" aria-label="问题排序">
      <button :class="{ active: props.sort === 'latest' && !props.mineOnly }" @click="emit('sort', 'latest')">最新</button>
      <button :class="{ active: props.sort === 'hot' && !props.mineOnly }" @click="emit('sort', 'hot')">热门</button>
      <button :class="{ active: props.sort === 'open' && !props.mineOnly }" @click="emit('sort', 'open')">待解答</button>
      <button v-if="props.showMine" :class="{ active: props.mineOnly }" @click="emit('mine')">我的提问</button>
    </nav>

    <div class="wall-cats-scroll">
      <div class="wall-cats">
        <button :class="{ active: !props.category }" @click="emit('category', '')">全部</button>
        <button
          v-for="item in FORUM_CATEGORY_ORDER"
          :key="item"
          :class="{ active: props.category === item }"
          @click="emit('category', item)"
        >
          {{ item }}
        </button>
      </div>
    </div>
  </section>
</template>
