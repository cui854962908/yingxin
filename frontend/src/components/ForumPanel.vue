<!-- 超标例外：script+template=302行，论坛列表页聚合排序/筛选/搜索/分页/加载更多，拆分后子组件无复用价值 -->
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ForumCategory, ForumPostBrief } from '../types/forum'
import { authHeaders, useAuth } from '../composables/useAuth'
import { formatForumAuthor } from '../utils/forumAuthor'
import { formatRelativeTime } from '../utils/formatTime'
import {
  FORUM_CATEGORY_ORDER,
  categoryAccent,
  categoryIconPath,
  categoryTint,
} from '../utils/forumCategoryUi'
import ForumWallSidebar from './forum-wall/ForumWallSidebar.vue'
import { FORUM_MODULE_NAME } from '../constants/product'
import AppSpinner from './AppSpinner.vue'
import '../styles/forum-mobile.css'
import '../styles/forum-wall.css'
import '../styles/panel-enter.css'

const router = useRouter()
const { token, isAdmin, isGuest } = useAuth()

const items = ref<ForumPostBrief[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 15
const sort = ref<'latest' | 'hot' | 'open'>('latest')
const category = ref<ForumCategory | ''>('')
const searchQ = ref('')
const mineOnly = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const hasMore = computed(() => page.value < totalPages.value)

async function load(append = false) {
  if (append) loadingMore.value = true
  else loading.value = true
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize),
      sort: sort.value,
    })
    if (category.value) params.set('category', category.value)
    if (searchQ.value.trim()) params.set('q', searchQ.value.trim())
    if (mineOnly.value) params.set('mine', 'true')
    const headers: Record<string, string> = token.value ? authHeaders() : {}
    const res = await fetch(`/api/forum/posts?${params}`, { headers })
    const d = await res.json()
    if (d.success) {
      items.value = append ? [...items.value, ...d.data.items] : d.data.items
      total.value = d.data.total
    }
  } catch {
    if (!append) items.value = []
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function goDetail(id: string) {
  router.push(`/wall/${id}`)
}

function authorInitial(item: ForumPostBrief): string {
  const name = formatForumAuthor(item.author.name, item.author.class_name, isGuest.value)
  return name.charAt(0) || '新'
}

function cardStyle(item: ForumPostBrief) {
  const accent = categoryAccent(item.category)
  return {
    '--wall-accent': accent,
    '--wall-icon-bg': categoryTint(item.category),
  }
}

function statusClass(item: ForumPostBrief): string {
  if (item.has_accepted) return 'wall-status--solved'
  if (item.is_closed) return 'wall-status--closed'
  if (item.answer_count === 0) return 'wall-status--await'
  return ''
}

function statusLabel(item: ForumPostBrief): string {
  if (item.has_accepted) return '已解决'
  if (item.is_closed) return '已关闭'
  if (item.answer_count === 0) return '待解答'
  return ''
}

function goAsk() {
  if (!token.value || isGuest.value) {
    window.alert('登录后可向学长学姐提问')
    return
  }
  router.push('/wall/new')
}

function deleteConfirmText(answerCount: number): string {
  if (answerCount > 0) return '删除后所有回答也将一并移除，确定删除这条提问吗？'
  return '确定删除这条提问吗？'
}

async function deletePost(item: ForumPostBrief, e: Event) {
  e.stopPropagation()
  if (!item.is_mine && !isAdmin.value) return
  const forAdmin = isAdmin.value && !item.is_mine
  const tip = forAdmin
    ? '确定永久删除这条帖子吗？删除后不可恢复。'
    : deleteConfirmText(item.answer_count)
  if (!confirm(tip)) return

  try {
    const res = await fetch(`/api/forum/posts/${item.id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    const d = await res.json()
    if (!res.ok || !d.success) throw new Error(d.message || '删除失败')
    page.value = 1
    await load()
  } catch (err) {
    console.warn(err instanceof Error ? err.message : '删除失败')
  }
}

function setSort(s: typeof sort.value) {
  sort.value = s
  page.value = 1
  load()
}

function toggleMine() {
  if (!token.value) return
  mineOnly.value = !mineOnly.value
  page.value = 1
  load()
}

function submitSearch() {
  page.value = 1
  load()
}

function pickTopic(keyword: string) {
  searchQ.value = keyword
  page.value = 1
  load()
}

function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  page.value += 1
  load(true)
}

watch(category, () => { page.value = 1; load() })

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchQ, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 350)
})

onMounted(load)
</script>

<template>
  <div class="wall">
    <header class="wall-hero wall-enter-head">
      <div class="wall-hero-text">
        <h2 class="wall-title">{{ FORUM_MODULE_NAME }}</h2>
        <p class="wall-sub">新生互助 · 学长学姐答疑 · 小信答不上来这里问</p>
      </div>
      <button v-if="!isGuest" type="button" class="wall-ask-btn" @click="goAsk">
        <span class="wall-ask-btn-icon">+</span>
        我要提问
      </button>
      <p v-else class="wall-guest-hint">登录后可提问 · 当前仅浏览</p>
    </header>

    <div class="wall-search-row">
      <div class="wall-search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
        <input
          v-model="searchQ"
          placeholder="搜索问题、关键词、话题…"
          @keydown.enter.prevent="submitSearch"
        />
      </div>
      <button type="button" class="wall-search-btn" @click="submitSearch">搜索</button>
    </div>

    <div class="wall-main-grid wall-enter-body">
      <div class="wall-feed">
        <nav class="wall-tabs" aria-label="排序">
          <button :class="{ active: sort === 'latest' && !mineOnly }" @click="mineOnly = false; setSort('latest')">最新</button>
          <button :class="{ active: sort === 'hot' && !mineOnly }" @click="mineOnly = false; setSort('hot')">热门</button>
          <button :class="{ active: sort === 'open' && !mineOnly }" @click="mineOnly = false; setSort('open')">待解答</button>
          <button v-if="!isGuest" :class="{ active: mineOnly }" @click="toggleMine">我的提问</button>
        </nav>

        <div class="wall-cats-scroll">
          <div class="wall-cats">
            <button :class="{ active: !category }" @click="category = ''">全部</button>
            <button
              v-for="c in FORUM_CATEGORY_ORDER"
              :key="c"
              :class="{ active: category === c }"
              @click="category = c"
            >{{ c }}</button>
          </div>
        </div>

        <div v-if="loading" class="wall-loading"><AppSpinner /></div>
        <div v-else-if="items.length === 0" class="wall-empty">
          <p class="wall-empty-icon">🌾</p>
          <p>还没有提问，来做第一个吧</p>
        </div>
        <div v-else class="wall-list">
          <article
            v-for="(item, idx) in items"
            :key="item.id"
            class="wall-card panel-reveal__card"
            :class="{ 'wall-card--pinned': item.is_pinned }"
            :style="{ ...cardStyle(item), '--enter-i': idx }"
            @click="goDetail(item.id)"
          >
            <div
              v-if="item.is_mine || isAdmin"
              class="wall-card-admin"
              @click.stop
            >
              <button type="button" class="wall-del-btn" @click="deletePost(item, $event)">删除</button>
            </div>

            <div class="wall-card-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path :d="categoryIconPath(item.category)" />
              </svg>
            </div>

            <div class="wall-card-body">
              <div v-if="item.is_pinned" class="wall-card-top">
                <span class="wall-pin">置顶</span>
              </div>

              <div class="wall-card-head">
                <h3 class="wall-card-title">{{ item.title }}</h3>
                <span v-if="statusLabel(item)" class="wall-status" :class="statusClass(item)">
                  {{ statusLabel(item) }}
                </span>
              </div>

              <p class="wall-card-preview">{{ item.content_preview }}</p>

              <div class="wall-card-foot">
                <div class="wall-card-foot-meta">
                  <span class="wall-cat">{{ item.category }}</span>
                  <div class="wall-author-chip">
                    <span class="wall-author-avatar">{{ authorInitial(item) }}</span>
                    <span class="wall-author">{{ formatForumAuthor(item.author.name, item.author.class_name, isGuest) }}</span>
                    <span class="wall-time-dot">·</span>
                    <span class="wall-author">{{ formatRelativeTime(item.created_at) }}</span>
                  </div>
                </div>
                <div class="wall-card-stats">
                  <span class="wall-stat" :class="{ 'wall-stat--hot': item.answer_count > 0 }">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    {{ item.answer_count }}
                  </span>
                  <span class="wall-stat">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
                    {{ item.like_count }}
                  </span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="hasMore && !loading && items.length > 0" class="wall-load-more">
          <button
            type="button"
            class="wall-load-more-btn"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? '加载中…' : '加载更多' }}
            <svg v-if="!loadingMore" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </button>
        </div>
      </div>

      <ForumWallSidebar @pick-topic="pickTopic" />
    </div>
  </div>
</template>
