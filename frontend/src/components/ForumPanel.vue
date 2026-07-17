<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authFetch, optionalAuthFetch, useAuth } from '../composables/useAuth'
import { usePreload } from '../composables/usePreload'
import type { ForumCategory, ForumPostBrief } from '../types/forum'
import AppSpinner from './AppSpinner.vue'
import ForumQuestionCard from './forum-wall/ForumQuestionCard.vue'
import ForumWallFilters, { type ForumSort } from './forum-wall/ForumWallFilters.vue'
import ForumWallHero from './forum-wall/ForumWallHero.vue'
import ForumWallSidebar from './forum-wall/ForumWallSidebar.vue'
import '../styles/forum-wall.css'
import '../styles/forum-mobile.css'
import '../styles/panel-enter.css'

const router = useRouter()
const { token, isAdmin, isGuest } = useAuth()
const { forumPosts: cachedPosts, forumTotal: cachedTotal } = usePreload()

const items = ref<ForumPostBrief[]>(cachedPosts.value.length ? cachedPosts.value : [])
const loading = ref(!cachedPosts.value.length)
const switchingPage = ref(false)
const total = ref(cachedTotal.value || 0)
const page = ref(1)
const sort = ref<ForumSort>('latest')
const category = ref<ForumCategory | ''>('')
const searchQ = ref('')
const mineOnly = ref(false)
const pageSize = 4

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value < totalPages.value)

async function load(options: { silent?: boolean } = {}) {
  if (!options.silent) loading.value = true
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize),
      sort: sort.value,
    })
    if (category.value) params.set('category', category.value)
    if (searchQ.value.trim()) params.set('q', searchQ.value.trim())
    if (mineOnly.value) params.set('mine', 'true')
    const response = await optionalAuthFetch(
      `/api/forum/posts?${params}`,
      {},
      !mineOnly.value,
    )
    const result = await response.json()
    if (result.success) {
      items.value = result.data.items
      total.value = result.data.total
      if (page.value === 1 && !category.value && !searchQ.value.trim() && !mineOnly.value && sort.value === 'latest') {
        cachedPosts.value = result.data.items
        cachedTotal.value = result.data.total
      }
    }
  } catch {
    if (!options.silent) items.value = []
  } finally {
    loading.value = false
    switchingPage.value = false
  }
}

function reload() {
  page.value = 1
  load()
}

function goPage(n: number) {
  if (n < 1 || n > totalPages.value || switchingPage.value) return
  switchingPage.value = true
  page.value = n
  load()
}

function selectSort(value: ForumSort) {
  mineOnly.value = false
  sort.value = value
  reload()
}

function selectCategory(value: ForumCategory | '') {
  category.value = value
}

function toggleMine() {
  if (!token.value) return
  mineOnly.value = !mineOnly.value
  reload()
}

function pickTopic(keyword: string) {
  searchQ.value = keyword
  reload()
}

function goAsk() {
  if (!token.value || isGuest.value) {
    window.alert('登录后可向学长学姐提问')
    return
  }
  router.push('/wall/new')
}

async function deletePost(item: ForumPostBrief, event: Event) {
  event.stopPropagation()
  if (!item.is_mine && !isAdmin.value) return
  const message = item.answer_count > 0
    ? '删除后所有回答也将一并移除，确定删除这条提问吗？'
    : '确定删除这条提问吗？'
  if (!confirm(message)) return
  const response = await authFetch(`/api/forum/posts/${item.id}`, { method: 'DELETE' })
  const result = await response.json()
  if (!response.ok || !result.success) {
    console.warn(result.message || '删除失败')
    return
  }
  reload()
}

watch(category, reload)

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchQ, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(reload, 350)
})

onMounted(() => {
  if (cachedPosts.value.length) {
    load({ silent: true })
    return
  }
  load()
})
	</script>

<template>
  <main class="wall">
    <ForumWallHero @ask="goAsk" />
    <ForumWallFilters
      v-model:query="searchQ"
      :sort="sort"
      :category="category"
      :mine-only="mineOnly"
      :show-mine="!isGuest"
      @search="reload"
      @sort="selectSort"
      @category="selectCategory"
      @mine="toggleMine"
    />

    <div class="wall-main-grid">
      <section class="wall-feed" aria-label="问题列表">
        <div v-show="loading && items.length === 0" class="wall-loading"><AppSpinner /></div>
        <div v-show="!loading && items.length === 0" class="wall-empty">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4V5Z"/><path d="M8 9h8M8 12h5"/></svg>
          <p>暂时没有符合条件的问题</p>
          <button type="button" @click="goAsk">发布第一个提问</button>
        </div>
        <div v-show="items.length > 0" class="wall-list">
          <ForumQuestionCard
            v-for="item in items"
            :key="item.id"
            :item="item"
            :is-guest="isGuest"
            :can-delete="item.is_mine || isAdmin"
            @open="router.push(`/wall/${item.id}`)"
            @delete="deletePost(item, $event)"
          />
        </div>

        <nav v-if="totalPages > 1 && !loading && items.length" class="wall-pager" aria-label="分页导航">
          <button
            type="button"
            class="wall-pager-btn"
            :disabled="!canPrev"
            @click="goPage(page - 1)"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14 18-6-6 6-6"/></svg>
            上一页
          </button>
          <span class="wall-pager-info">
            <strong>{{ page }}</strong> / {{ totalPages }}
          </span>
          <button
            type="button"
            class="wall-pager-btn"
            :disabled="!canNext"
            @click="goPage(page + 1)"
          >
            下一页
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m10 18 6-6-6-6"/></svg>
          </button>
        </nav>
      </section>

      <ForumWallSidebar @pick-topic="pickTopic" />
    </div>
  </main>
</template>
