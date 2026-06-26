<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ForumCategory, ForumPostBrief } from '../types/forum'
import { FORUM_CATEGORIES, FORUM_CATEGORY_COLORS } from '../types/forum'
import { authHeaders, useAuth } from '../composables/useAuth'
import { formatForumAuthor } from '../utils/forumAuthor'
import { formatRelativeTime } from '../utils/formatTime'
import AppSpinner from './AppSpinner.vue'
import '../styles/forum-mobile.css'
import '../styles/panel-enter.css'

const router = useRouter()
const { token, isAdmin, isGuest } = useAuth()

const items = ref<ForumPostBrief[]>([])
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const pageSize = 15
const sort = ref<'latest' | 'hot' | 'open'>('latest')
const category = ref<ForumCategory | ''>('')
const searchQ = ref('')
const mineOnly = ref(false)

const totalPages = ref(1)

async function load() {
  loading.value = true
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
      items.value = d.data.items
      total.value = d.data.total
      totalPages.value = Math.max(1, Math.ceil(d.data.total / pageSize))
    }
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function goDetail(id: string) {
  router.push(`/wall/${id}`)
}

function authorInitial(item: ForumPostBrief): string {
  const name = formatForumAuthor(item.author.name, item.author.class_name, isGuest.value)
  return name.charAt(0) || '新'
}

function cardClass(item: ForumPostBrief): Record<string, boolean> {
  return {
    'wall-card--pinned': item.is_pinned,
    'wall-card--solved': item.has_accepted,
    'wall-card--closed': item.is_closed && !item.has_accepted,
    'wall-card--await': !item.has_accepted && !item.is_closed && item.answer_count === 0,
  }
}

function categoryColor(cat: ForumCategory): string {
  return FORUM_CATEGORY_COLORS[cat] ?? '#8b7b65'
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
    await load()
  } catch (err) {
    console.warn(err instanceof Error ? err.message : '删除失败')
  }
}

async function togglePostLike(item: ForumPostBrief, e: Event) {
  e.stopPropagation()
  if (!token.value || isGuest.value) {
    window.alert('登录后可点赞')
    return
  }
  const res = await fetch(`/api/forum/posts/${item.id}/like`, {
    method: 'POST', headers: authHeaders(),
  })
  const d = await res.json()
  if (!d.success) return
  item.like_count = d.data.like_count
  item.liked_by_me = d.data.liked_by_me
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
    <div class="wall-sticky-head wall-enter-head">
      <div class="wall-hero">
        <div class="wall-hero-text">
          <h2 class="wall-title">问牧墙</h2>
          <p class="wall-sub">新生互助 · 学长学姐来答 · 小信答不上来这里问</p>
        </div>
        <button v-if="!isGuest" type="button" class="wall-ask-btn" @click="goAsk">我要提问</button>
        <p v-else class="wall-guest-hint">登录后可提问 · 当前仅浏览</p>
      </div>

      <div class="wall-toolbar">
        <div class="wall-tabs-scroll">
          <div class="wall-tabs">
            <button :class="{ active: sort === 'latest' && !mineOnly }" @click="mineOnly = false; setSort('latest')">最新</button>
            <button :class="{ active: sort === 'hot' && !mineOnly }" @click="mineOnly = false; setSort('hot')">热门</button>
            <button :class="{ active: sort === 'open' && !mineOnly }" @click="mineOnly = false; setSort('open')">待解答</button>
            <button v-if="!isGuest" :class="{ active: mineOnly }" @click="toggleMine">我的提问</button>
          </div>
        </div>
        <div class="wall-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
          <input v-model="searchQ" placeholder="搜索问题…" />
        </div>
        <div class="wall-cats-scroll">
          <div class="wall-cats">
            <button :class="{ active: !category }" @click="category = ''">全部</button>
            <button
              v-for="c in FORUM_CATEGORIES" :key="c"
              :class="{ active: category === c }"
              @click="category = c"
            >{{ c }}</button>
          </div>
        </div>
      </div>
    </div>

    <div class="wall-body wall-enter-body">
    <div v-if="loading" class="wall-loading"><AppSpinner /></div>
    <div v-else-if="items.length === 0" class="wall-empty">
      <p class="wall-empty-icon">🌾</p>
      <p>还没有提问，来做第一个吧</p>
    </div>
    <div v-else class="wall-list">
      <article
        v-for="(item, idx) in items" :key="item.id"
        class="wall-card panel-reveal__card"
        :class="cardClass(item)"
        :style="{ '--wall-accent': categoryColor(item.category), '--enter-i': idx }"
        @click="goDetail(item.id)"
      >
        <span class="wall-card-mark" aria-hidden="true">问</span>
        <div class="wall-card-top">
          <span v-if="item.is_pinned" class="wall-pin">置顶</span>
          <span class="wall-cat">{{ item.category }}</span>
          <span v-if="item.has_accepted" class="wall-solved">已采纳</span>
          <span v-else-if="item.is_closed" class="wall-closed">已关闭</span>
          <span v-else-if="item.answer_count === 0" class="wall-await">待解答</span>
        </div>
        <h3 class="wall-card-title">{{ item.title }}</h3>
        <p class="wall-card-preview">{{ item.content_preview }}</p>
        <div class="wall-card-foot">
          <div class="wall-author-chip">
            <span class="wall-author-avatar">{{ authorInitial(item) }}</span>
            <span class="wall-author">{{ formatForumAuthor(item.author.name, item.author.class_name, isGuest) }}</span>
          </div>
          <div class="wall-card-stats">
            <span class="wall-stat" :class="{ 'wall-stat--hot': item.answer_count > 0 }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              {{ item.answer_count }}
            </span>
            <span class="wall-stat">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
              {{ formatRelativeTime(item.created_at) }}
            </span>
          </div>
          <div v-if="!isGuest" class="wall-card-actions" @click.stop>
            <button
              type="button"
              class="wall-like-btn"
              :class="{ 'wall-like-btn--on': item.liked_by_me }"
              @click="togglePostLike(item, $event)"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
              {{ item.like_count > 0 ? item.like_count : '赞' }}
            </button>
            <button
              v-if="item.is_mine || isAdmin"
              type="button"
              class="wall-del-btn"
              @click="deletePost(item, $event)"
            >删除</button>
          </div>
        </div>
      </article>
    </div>

    <div v-if="totalPages > 1 && !loading" class="wall-pages">
      <button :disabled="page <= 1" @click="page--; load()">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++; load()">下一页</button>
    </div>
    </div>
  </div>
</template>

<style scoped>
.wall { display: flex; flex-direction: column; min-height: 100%; padding-bottom: 8px }

/* Hero + 筛选栏整体吸顶（滚动容器为 section-card） */
.wall-sticky-head {
  position: sticky;
  top: 0;
  z-index: 12;
  margin: -24px -28px 0;
  padding: 0 28px 12px;
  background: linear-gradient(180deg, #fff 0%, #fff 78%, rgba(255,255,255,.97) 100%);
  box-shadow: 0 10px 24px rgba(60,48,40,.07);
}
.wall-body { display: flex; flex-direction: column; gap: 14px; padding-top: 14px }

.wall-hero {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 16px 20px 14px; border-radius: 14px 14px 0 0;
  background: linear-gradient(135deg, #75171d 0%, #8c2028 45%, #540b13 100%);
  color: #f2e6d0; box-shadow: none;
}
.wall-title { margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: .12em; font-family: 'Noto Serif SC', Georgia, serif }
.wall-sub { margin: 6px 0 0; font-size: .78rem; opacity: .82; letter-spacing: .04em }
.wall-ask-btn {
  flex-shrink: 0; height: 38px; padding: 0 18px; border: 1px solid rgba(242,230,208,.35);
  border-radius: 10px; background: rgba(255,255,255,.12); color: #fff;
  font-size: .82rem; font-weight: 600; cursor: pointer; font-family: inherit;
  backdrop-filter: blur(6px); transition: background .2s;
}
.wall-ask-btn:hover { background: rgba(255,255,255,.22) }
.wall-guest-hint {
  margin: 0; font-size: .72rem; opacity: .85; text-align: right; line-height: 1.45;
}

.wall-toolbar {
  display: flex; flex-direction: column; gap: 10px;
  padding: 12px 0 0;
  border-top: 1px solid rgba(242,230,208,.12);
  background: transparent;
}
.wall-tabs-scroll, .wall-cats-scroll {
  overflow-x: auto; -webkit-overflow-scrolling: touch;
  scrollbar-width: none; margin: 0 -2px; padding: 0 2px;
}
.wall-tabs-scroll::-webkit-scrollbar, .wall-cats-scroll::-webkit-scrollbar { display: none }
.wall-tabs, .wall-cats { display: flex; flex-wrap: nowrap; gap: 8px; width: max-content; min-width: 100% }
.wall-tabs button, .wall-cats button {
  flex-shrink: 0;
  height: 32px; padding: 0 14px; border: 1px solid #e5dbcc; border-radius: 999px;
  background: #fefcf9; color: #6b5e4e; font-size: .78rem; cursor: pointer; font-family: inherit;
  transition: background .2s, border-color .2s, color .2s;
}
.wall-tabs button.active, .wall-cats button.active {
  background: #b5343a; color: #fff; border-color: #b5343a;
}
.wall-search {
  position: relative; max-width: 420px; width: 100%;
}
.wall-search svg { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #b0a090 }
.wall-search input {
  width: 100%; height: 40px; padding: 0 14px 0 38px; border: 1.5px solid #e5dbcc;
  border-radius: 12px; background: #fefcf9; font-size: .86rem; font-family: inherit; outline: none;
}
.wall-search input:focus { border-color: #b5343a; box-shadow: 0 0 0 3px rgba(181,52,58,.08) }

.wall-loading { display: flex; justify-content: center; padding: 40px 0 }
.wall-empty { text-align: center; padding: 48px 16px; color: #b0a090 }
.wall-empty-icon { font-size: 2rem; margin-bottom: 8px }

.wall-pages { display: flex; align-items: center; justify-content: center; gap: 12px; padding-top: 4px }
.wall-pages button {
  height: 34px; padding: 0 14px; border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; cursor: pointer; font-family: inherit; font-size: .8rem;
}
.wall-pages button:disabled { opacity: .4; cursor: default }

@media (max-width: 768px) {
  .wall {
    padding-bottom: var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px)));
  }
  .wall-sticky-head {
    margin: 0;
    padding: 0 0 10px;
    box-shadow: 0 8px 22px rgba(60,48,40,.08);
    backdrop-filter: blur(8px);
  }
  .wall-body {
    padding: 12px 14px 8px;
    gap: 12px;
  }
  .wall-hero {
    flex-direction: column; align-items: stretch;
    margin: 0; padding: 18px 16px 14px;
    border-radius: 0;
    background:
      radial-gradient(circle at 50% 10%, rgba(255,255,255,.12), transparent 24%),
      linear-gradient(180deg, #75171d 0%, #8c2028 38%, #540b13 100%);
  }
  .wall-title { font-size: 1.28rem }
  .wall-sub { font-size: .72rem; line-height: 1.55; max-width: none }
  .wall-ask-btn {
    width: 100%; height: 44px; margin-top: 12px;
    border-radius: 12px; font-size: .88rem; letter-spacing: .1em;
    background: linear-gradient(135deg, rgba(255,255,255,.2), rgba(255,255,255,.08));
    box-shadow: 0 8px 20px rgba(0,0,0,.15);
    -webkit-tap-highlight-color: transparent;
  }
  .wall-toolbar {
    gap: 12px; padding: 10px 14px 0;
    background: rgba(255,255,255,.98);
    border-top: none;
  }
  .wall-tabs button, .wall-cats button {
    height: 36px; min-height: 40px; padding: 0 16px; font-size: .8rem;
  }
  .wall-search { max-width: none }
  .wall-search input {
    height: 44px; font-size: 16px; border-radius: 13px;
  }
  .wall-card-foot { flex-wrap: wrap; gap: 10px }
  .wall-card-actions { width: 100%; justify-content: flex-end }
  .wall-like-btn, .wall-del-btn { min-height: 36px; padding: 0 14px; font-size: .76rem }
  .wall-pages {
    padding-bottom: 8px;
    gap: 16px;
  }
  .wall-pages button { min-height: 44px; min-width: 88px; padding: 0 18px; font-size: .84rem }
}

@media (max-width: 480px) {
  .wall-body { padding: 10px 12px 8px }
  .wall-hero { padding: 16px 14px 12px }
  .wall-toolbar { padding: 8px 12px 0 }
}
</style>
