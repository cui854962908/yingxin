<script setup lang="ts">
import { ref, computed, onMounted, type CSSProperties } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ForumPostDetail } from '../types/forum'
import { authFetch, optionalAuthFetch, useAuth } from '../composables/useAuth'
import { formatForumAuthor } from '../utils/forumAuthor'
import { categoryAccent, categoryIconPath, categoryTint } from '../utils/forumCategoryUi'
import { useAppNavigate } from '../composables/useAppNavigate'
import { formatRelativeTime } from '../utils/formatTime'
import { FORUM_MODULE_NAME } from '../constants/product'
import AppSpinner from './AppSpinner.vue'
import ForumDetailAside from './forum-wall/ForumDetailAside.vue'
import ForumDetailAnswerCard from './forum-wall/ForumDetailAnswerCard.vue'
import '../styles/forum-mobile.css'
import '../styles/forum/forum-content.css'
import '../styles/forum/forum-detail.css'

const route = useRoute()
const router = useRouter()
const { appGoBackTo } = useAppNavigate()
const { token, isAdmin, isGuest } = useAuth()

const post = ref<ForumPostDetail | null>(null)
const loading = ref(true)
const answerText = ref('')
const submitting = ref(false)
const deleting = ref(false)
const msg = ref('')

const postId = computed(() => route.params.id as string)
const canAnswer = computed(() => token.value && post.value && !post.value.is_closed)

const questionStyle = computed((): CSSProperties | undefined => {
  if (!post.value) return undefined
  return {
    '--wall-accent': categoryAccent(post.value.category),
    '--wall-icon-bg': categoryTint(post.value.category),
  } as CSSProperties
})

const statusLabel = computed(() => {
  if (!post.value) return ''
  if (post.value.has_accepted) return '已解决'
  if (post.value.is_closed) return '已关闭'
  if (post.value.answer_count === 0) return '待解答'
  return '讨论中'
})

const statusClass = computed(() => {
  if (!post.value) return ''
  if (post.value.has_accepted) return 'fthread-status--solved'
  if (post.value.is_closed) return 'fthread-status--closed'
  if (post.value.answer_count === 0) return 'fthread-status--await'
  return 'fthread-status--active'
})

function authorInitial(name: string): string {
  return (name.trim()[0] || '?').toUpperCase()
}

function canAcceptAnswer(answerId: string): boolean {
  if (!post.value || isGuest.value) return false
  const ans = post.value.answers.find(a => a.id === answerId)
  return !!(post.value.is_mine && !post.value.has_accepted && ans && !ans.is_accepted)
}

async function load() {
  loading.value = true
  try {
    const res = await optionalAuthFetch(`/api/forum/posts/${postId.value}`)
    const d = await res.json()
    if (d.success) post.value = d.data
    else router.replace('/wall')
  } catch {
    router.replace('/wall')
  } finally {
    loading.value = false
  }
}

async function submitAnswer() {
  if (!answerText.value.trim() || !post.value) return
  submitting.value = true
  msg.value = ''
  try {
    const res = await authFetch(`/api/forum/posts/${post.value.id}/answers`, {
      method: 'POST',
      body: JSON.stringify({ content: answerText.value.trim() }),
    })
    const d = await res.json()
    if (!res.ok || !d.success) throw new Error(d.message)
    post.value = d.data
    answerText.value = ''
    msg.value = '回答已发布'
    setTimeout(() => { msg.value = '' }, 2000)
  } catch (e) {
    msg.value = e instanceof Error ? e.message : '回答失败'
  } finally {
    submitting.value = false
  }
}

async function acceptAnswer(answerId: string) {
  const res = await authFetch(`/api/forum/answers/${answerId}/accept`, { method: 'POST' })
  const d = await res.json()
  if (d.success) post.value = d.data
}

async function closePost() {
  if (!post.value) return
  const res = await authFetch(`/api/forum/posts/${post.value.id}/close`, { method: 'POST' })
  const d = await res.json()
  if (d.success) post.value = d.data
}

async function adminHide() {
  if (!post.value) return
  await authFetch(`/api/admin/forum/posts/${post.value.id}/hide`, { method: 'POST' })
  appGoBackTo('/wall')
}

function deleteConfirmText(forAdmin: boolean, answerCount: number): string {
  if (forAdmin) return '确定永久删除这条帖子吗？删除后不可恢复。'
  if (answerCount > 0) return '删除后所有回答也将一并移除，确定删除这条提问吗？'
  return '确定删除这条提问吗？'
}

async function deletePost() {
  if (!post.value || deleting.value) return
  const forAdmin = isAdmin.value && !post.value.is_mine
  if (!post.value.is_mine && !isAdmin.value) return
  if (!confirm(deleteConfirmText(forAdmin, post.value.answer_count))) return

  deleting.value = true
  try {
    const res = await authFetch(`/api/forum/posts/${post.value.id}`, { method: 'DELETE' })
    const d = await res.json()
    if (!res.ok || !d.success) throw new Error(d.message || '删除失败')
    appGoBackTo('/wall')
  } catch (e) {
    msg.value = e instanceof Error ? e.message : '删除失败'
  } finally {
    deleting.value = false
  }
}

function requireLoginForLike(): boolean {
  if (token.value && !isGuest.value) return true
  window.alert('登录后可点赞')
  return false
}

async function togglePostLike() {
  if (!post.value || !requireLoginForLike()) return
  const res = await authFetch(`/api/forum/posts/${post.value.id}/like`, { method: 'POST' })
  const d = await res.json()
  if (d.success && post.value) {
    post.value.like_count = d.data.like_count
    post.value.liked_by_me = d.data.liked_by_me
  }
}

async function toggleAnswerLike(answerId: string) {
  if (!post.value || !requireLoginForLike()) return
  const res = await authFetch(`/api/forum/answers/${answerId}/like`, { method: 'POST' })
  const d = await res.json()
  if (!d.success || !post.value) return
  const ans = post.value.answers.find(a => a.id === answerId)
  if (ans) {
    ans.like_count = d.data.like_count
    ans.liked_by_me = d.data.liked_by_me
  }
}

onMounted(load)
</script>

<template>
  <div v-if="loading" class="fthread"><div class="fthread-loading"><AppSpinner /></div></div>
  <div v-else-if="post" class="fthread" :class="{ 'fthread--reply': canAnswer }">
    <div class="fthread-inner">
      <header class="fthread-top">
        <button type="button" class="fthread-back" @click="appGoBackTo('/wall')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
          返回{{ FORUM_MODULE_NAME }}
        </button>
      </header>

      <div class="fthread-grid">
        <div class="fthread-head">
          <div class="fthread-post">
            <header class="fthread-hero" :style="questionStyle">
            <div class="fthread-hero-inner">
              <div class="fthread-title-row">
                <div class="fthread-cat-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24"><path :d="categoryIconPath(post.category)" /></svg>
                </div>
                <div class="fthread-title-main">
                  <h1 class="fthread-title">{{ post.title }}</h1>
                  <span class="fthread-tag fthread-tag--cat">{{ post.category }}</span>
                </div>
              </div>
              <div v-if="post.is_pinned || post.has_accepted || post.is_closed" class="fthread-tags">
                <span v-if="post.is_pinned" class="fthread-tag fthread-tag--pin">置顶</span>
                <span v-if="post.has_accepted" class="fthread-tag fthread-tag--solved">已采纳</span>
                <span v-if="post.is_closed" class="fthread-tag fthread-tag--closed">已关闭</span>
              </div>
              <div class="fthread-hero-meta">
                <span class="fthread-avatar fthread-avatar--sm">{{ authorInitial(post.author.name) }}</span>
                <span>{{ formatForumAuthor(post.author.name, post.author.class_name, isGuest) }}</span>
                <span class="fthread-hero-dot" aria-hidden="true">·</span>
                <time :datetime="post.created_at">{{ formatRelativeTime(post.created_at) }}</time>
              </div>
            </div>
            <span class="fthread-hero-mark" aria-hidden="true">问</span>
          </header>

          <article class="fthread-question">
            <p class="fthread-body-label">问题描述</p>
            <div class="fthread-body">{{ post.content }}</div>
            <div v-if="!isGuest && (post.is_mine || isAdmin)" class="fthread-actions">
              <button v-if="post.is_mine && !post.is_closed" type="button" class="fthread-act" @click="closePost">关闭提问</button>
              <button
                v-if="post.is_mine || isAdmin"
                type="button"
                class="fthread-act fthread-act--danger"
                :disabled="deleting"
                @click="deletePost"
              >{{ deleting ? '删除中…' : (isAdmin && !post.is_mine ? '删除帖子' : '删除提问') }}</button>
              <button v-if="isAdmin" type="button" class="fthread-act" @click="adminHide">隐藏帖子</button>
            </div>
            <p v-if="msg && !canAnswer" class="fthread-msg" :class="{ 'fthread-msg--err': msg !== '回答已发布' }">{{ msg }}</p>
          </article>
          </div>

          <ForumDetailAside
            :post="post"
            :is-guest="isGuest"
            :author-initial="authorInitial(post.author.name)"
            :status-label="statusLabel"
            :status-class="statusClass"
            @like="togglePostLike"
          />
        </div>

        <section class="fthread-answers">
          <div class="fthread-ans-head">
              <h2 class="fthread-ans-title">全部回答</h2>
              <span class="fthread-ans-count">{{ post.answers.length }}</span>
            </div>
            <div v-if="post.answers.length === 0" class="fthread-ans-empty">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4V5Z"/><path d="M8 9h8M8 12h5"/></svg>
              <p>还没有回答，来做第一个帮忙的人吧</p>
            </div>
            <div v-else class="fthread-ans-list">
              <ForumDetailAnswerCard
                v-for="(a, idx) in post.answers"
                :key="a.id"
                :answer="a"
                :index="idx"
                :author-initial="authorInitial(a.author.name)"
                :is-guest="isGuest"
                :can-accept="canAcceptAnswer(a.id)"
                @like="toggleAnswerLike(a.id)"
                @accept="acceptAnswer(a.id)"
              />
            </div>
        </section>

        <div v-if="canAnswer" class="fthread-reply-dock">
          <div class="fthread-reply">
            <textarea v-model="answerText" rows="2" maxlength="2000" placeholder="写下你的回答…" />
            <div class="fthread-reply-bar">
              <span v-if="msg" class="fthread-msg" :class="{ 'fthread-msg--err': msg !== '回答已发布' }">{{ msg }}</span>
              <button type="button" class="fthread-reply-btn" :disabled="submitting || !answerText.trim()" @click="submitAnswer">
                {{ submitting ? '…' : '发布' }}
              </button>
            </div>
          </div>
        </div>
        <p v-else-if="!token || isGuest" class="fthread-hint">登录后可回答提问</p>
        <p v-else-if="post.is_closed" class="fthread-hint">楼主已关闭此提问</p>
      </div>
    </div>
  </div>
</template>
