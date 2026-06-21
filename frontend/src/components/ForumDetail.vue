<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ForumPostDetail } from '../types/forum'
import { FORUM_CATEGORY_COLORS } from '../types/forum'
import { authHeaders, useAuth } from '../composables/useAuth'
import { formatForumAuthor } from '../utils/forumAuthor'
import { useAppNavigate } from '../composables/useAppNavigate'
import { formatRelativeTime } from '../utils/formatTime'
import AppSpinner from './AppSpinner.vue'
import '../styles/forum-mobile.css'

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

async function load() {
  loading.value = true
  try {
    const headers = token.value ? authHeaders() : {}
    const res = await fetch(`/api/forum/posts/${postId.value}`, { headers })
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
    const res = await fetch(`/api/forum/posts/${post.value.id}/answers`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
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
  const res = await fetch(`/api/forum/answers/${answerId}/accept`, {
    method: 'POST', headers: authHeaders(),
  })
  const d = await res.json()
  if (d.success) post.value = d.data
}

async function closePost() {
  if (!post.value) return
  const res = await fetch(`/api/forum/posts/${post.value.id}/close`, {
    method: 'POST', headers: authHeaders(),
  })
  const d = await res.json()
  if (d.success) post.value = d.data
}

async function adminHide() {
  if (!post.value) return
  await fetch(`/api/admin/forum/posts/${post.value.id}/hide`, { method: 'POST', headers: authHeaders() })
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
    const res = await fetch(`/api/forum/posts/${post.value.id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
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
  const res = await fetch(`/api/forum/posts/${post.value.id}/like`, {
    method: 'POST', headers: authHeaders(),
  })
  const d = await res.json()
  if (d.success && post.value) {
    post.value.like_count = d.data.like_count
    post.value.liked_by_me = d.data.liked_by_me
  }
}

async function toggleAnswerLike(answerId: string) {
  if (!post.value || !requireLoginForLike()) return
  const res = await fetch(`/api/forum/answers/${answerId}/like`, {
    method: 'POST', headers: authHeaders(),
  })
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
  <div v-if="loading" class="wd-loading"><AppSpinner /></div>
  <div v-else-if="post" class="wall-detail" :class="{ 'wall-detail--reply': canAnswer }">
    <div class="forum-mobile-sticky-top">
      <button type="button" class="forum-mobile-back" @click="appGoBackTo('/wall')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
        返回问牧墙
      </button>
    </div>

    <article class="wd-question">
      <div class="wd-tags">
        <span v-if="post.is_pinned" class="wd-pin">置顶</span>
        <span class="wd-cat" :style="{ color: FORUM_CATEGORY_COLORS[post.category], background: FORUM_CATEGORY_COLORS[post.category] + '18' }">{{ post.category }}</span>
        <span v-if="post.has_accepted" class="wd-solved">已采纳</span>
        <span v-if="post.is_closed" class="wd-closed">已关闭</span>
      </div>
      <h1 class="wd-title">{{ post.title }}</h1>
      <p class="wd-content">{{ post.content }}</p>
      <div class="wd-meta">
        <span>{{ formatForumAuthor(post.author.name, post.author.class_name, isGuest) }}</span>
        <span>{{ formatRelativeTime(post.created_at) }} · {{ post.answer_count }} 回答</span>
      </div>
      <button
        v-if="!isGuest"
        type="button"
        class="wd-like"
        :class="{ 'wd-like--on': post.liked_by_me }"
        @click="togglePostLike"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
        {{ post.like_count > 0 ? post.like_count : '赞' }}
      </button>
      <div v-if="!isGuest && (post.is_mine || isAdmin)" class="wd-actions">
        <button v-if="post.is_mine && !post.is_closed" type="button" class="wd-act" @click="closePost">关闭提问</button>
        <button
          v-if="post.is_mine || isAdmin"
          type="button"
          class="wd-act wd-act--danger"
          :disabled="deleting"
          @click="deletePost"
        >{{ deleting ? '删除中…' : (isAdmin && !post.is_mine ? '删除帖子' : '删除提问') }}</button>
        <button v-if="isAdmin" type="button" class="wd-act" @click="adminHide">隐藏帖子</button>
      </div>
      <p v-if="msg && !canAnswer" class="wd-action-msg wd-action-msg--err">{{ msg }}</p>
    </article>

    <section class="wd-answers">
      <h3 class="wd-ans-head">回答 ({{ post.answers.length }})</h3>
      <div v-if="post.answers.length === 0" class="wd-ans-empty">还没有回答，来做第一个帮忙的人吧</div>
      <div v-for="a in post.answers" :key="a.id" class="wd-ans-card" :class="{ accepted: a.is_accepted }">
        <div class="wd-ans-top">
          <span v-if="a.is_accepted" class="wd-accept-badge">最佳回答</span>
          <span class="wd-ans-author">{{ formatForumAuthor(a.author.name, a.author.class_name, isGuest) }}</span>
          <span class="wd-ans-time">{{ formatRelativeTime(a.created_at) }}</span>
          <button
            v-if="!isGuest"
            type="button"
            class="wd-like wd-like--sm"
            :class="{ 'wd-like--on': a.liked_by_me }"
            @click="toggleAnswerLike(a.id)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
            {{ a.like_count > 0 ? a.like_count : '赞' }}
          </button>
        </div>
        <p class="wd-ans-body">{{ a.content }}</p>
        <button
          v-if="!isGuest && post.is_mine && !post.has_accepted && !a.is_accepted"
          type="button" class="wd-accept-btn" @click="acceptAnswer(a.id)"
        >采纳此回答</button>
      </div>
    </section>

    <div v-if="canAnswer" class="wd-reply-dock">
      <div class="wd-reply">
        <textarea v-model="answerText" rows="3" maxlength="2000" placeholder="写下你的回答…" />
        <div class="wd-reply-bar">
          <span v-if="msg" class="wd-msg" :class="{ 'wd-msg--err': msg !== '回答已发布' }">{{ msg }}</span>
          <button type="button" :disabled="submitting || !answerText.trim()" @click="submitAnswer">
            {{ submitting ? '发送中…' : '发布回答' }}
          </button>
        </div>
      </div>
    </div>
    <p v-else-if="!token || isGuest" class="wd-login-hint">登录后可回答提问</p>
    <p v-else-if="post.is_closed" class="wd-login-hint">楼主已关闭此提问</p>
  </div>
</template>

<style scoped>
.wall-detail { display: flex; flex-direction: column; gap: 16px; padding-bottom: 24px; min-height: 100% }
.wd-loading { display: flex; justify-content: center; padding: 48px 0 }
.wd-question {
  padding: 20px 22px; border-radius: 14px; background: #fff;
  border: 1px solid #f2ebe0; border-left: 4px solid #b5343a;
  box-shadow: 0 4px 16px rgba(60,48,40,.05);
}
.wd-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px }
.wd-pin, .wd-cat, .wd-solved, .wd-closed { font-size: .68rem; font-weight: 600; padding: 2px 8px; border-radius: 999px }
.wd-pin { background: #3d1114; color: #f2e6d0 }
.wd-solved { background: #edf6ef; color: #4a8c5c }
.wd-closed { background: #f5f0ea; color: #8b7b65 }
.wd-title { margin: 0 0 12px; font-size: 1.15rem; color: #3c3028; line-height: 1.45; font-weight: 700 }
.wd-content { margin: 0 0 14px; font-size: .9rem; color: #5c5040; line-height: 1.75; white-space: pre-wrap }
.wd-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; font-size: .74rem; color: #b0a090 }
.wd-like {
  display: inline-flex; align-items: center; gap: 5px; margin-top: 10px;
  height: 32px; padding: 0 12px; border: 1px solid #e5dbcc; border-radius: 999px;
  background: #fefcf9; color: #8b7b65; font-size: .76rem; cursor: pointer; font-family: inherit;
  -webkit-tap-highlight-color: transparent; transition: background .15s, border-color .15s, color .15s;
}
.wd-like--on { background: #fff5f5; border-color: rgba(181,52,58,.35); color: #b5343a }
.wd-like--sm { margin-top: 0; margin-left: auto; height: 28px; padding: 0 10px; font-size: .72rem }
.wd-actions { display: flex; gap: 8px; margin-top: 14px }
.wd-act {
  height: 32px; padding: 0 12px; border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; font-size: .76rem; cursor: pointer; font-family: inherit; color: #6b5e4e;
}
.wd-act--danger { color: #b5343a; border-color: rgba(181,52,58,.35) }
.wd-act:disabled { opacity: .5; cursor: default }
.wd-action-msg { margin: 10px 0 0; font-size: .78rem; color: #4a8c5c }
.wd-action-msg--err { color: #b5343a }

.wd-ans-head { margin: 0 0 10px; font-size: .95rem; color: #3c3028; font-weight: 600 }
.wd-ans-empty { text-align: center; color: #b0a090; font-size: .84rem; padding: 20px 0 }
.wd-ans-card {
  padding: 14px 16px; margin-bottom: 10px; border-radius: 12px;
  background: #fefcf9; border: 1px solid #f2ebe0;
}
.wd-ans-card.accepted { border-color: #4a8c5c; background: #f6fbf7 }
.wd-ans-top { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px; font-size: .72rem; color: #b0a090 }
.wd-accept-badge { background: #4a8c5c; color: #fff; padding: 2px 8px; border-radius: 999px; font-weight: 600 }
.wd-ans-author { color: #6b5e4e; font-weight: 600 }
.wd-ans-body { margin: 0; font-size: .86rem; color: #5c5040; line-height: 1.65; white-space: pre-wrap }
.wd-accept-btn {
  margin-top: 10px; height: 30px; padding: 0 12px; border: 1px solid #4a8c5c; border-radius: 8px;
  background: #fff; color: #4a8c5c; font-size: .74rem; cursor: pointer; font-family: inherit;
}

.wd-msg { font-size: .78rem; color: #4a8c5c; flex: 1; min-width: 0 }
.wd-msg--err { color: #b5343a }
.wd-reply button {
  flex-shrink: 0;
  height: 38px; padding: 0 18px; border: none; border-radius: 10px; cursor: pointer;
  background: #b5343a; color: #fff; font-size: .82rem; font-weight: 600; font-family: inherit;
}
.wd-reply button:disabled { opacity: .5; cursor: default }
.wd-login-hint {
  text-align: center; color: #b0a090; font-size: .84rem; padding: 12px;
  margin: 0 -4px; border-radius: 12px; background: #fefcf9; border: 1px dashed #e5dbcc;
}

.wd-reply-dock { position: sticky; bottom: 8px; z-index: 6 }
.wd-reply {
  padding: 16px; border-radius: 12px; background: #fff; border: 1px solid #e5dbcc;
  box-shadow: 0 -4px 20px rgba(60,48,40,.08);
}
.wd-reply textarea {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e5dbcc; border-radius: 10px;
  font-size: .86rem; font-family: inherit; resize: vertical; outline: none; box-sizing: border-box;
  min-height: 72px;
}
.wd-reply textarea:focus { border-color: #b5343a; box-shadow: 0 0 0 3px rgba(181,52,58,.08) }
.wd-reply-bar { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; gap: 10px }

@media (max-width: 768px) {
  .wall-detail {
    gap: 12px;
    padding-bottom: var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px)));
  }
  .wall-detail--reply {
    padding-bottom: calc(140px + var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px))));
  }
  .wd-question {
    margin: 0; padding: 16px 14px;
    border-radius: 0;
    border-left-width: 3px;
    box-shadow: none;
    border-top: 1px solid #f2ebe0;
    border-right: none;
    border-bottom: 1px solid #f2ebe0;
  }
  .wd-title { font-size: 1.05rem; line-height: 1.5 }
  .wd-content { font-size: .88rem; line-height: 1.7 }
  .wd-meta { flex-direction: column; align-items: flex-start; gap: 4px }
  .wd-actions { flex-wrap: wrap; gap: 10px }
  .wd-act { min-height: 44px; padding: 0 16px; font-size: .78rem; flex: 1; min-width: calc(50% - 5px) }
  .wd-like { min-height: 40px; padding: 0 14px }
  .wd-like--sm { min-height: 36px }
  .wd-answers { padding: 0 14px }
  .wd-ans-card { padding: 12px 14px; border-radius: 14px; margin-bottom: 12px }
  .wd-accept-btn { min-height: 44px; padding: 0 14px; font-size: .78rem; width: 100% }
  .wd-reply-dock {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 8500;
    padding: 8px 14px var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px)));
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.92) 28%, #fff 100%);
    pointer-events: none;
  }
  .wd-reply-dock .wd-reply {
    pointer-events: auto;
    padding: 12px 14px; border-radius: 16px;
    border: 1px solid rgba(181,52,58,.15);
    box-shadow: 0 8px 28px rgba(84,11,19,.12);
  }
  .wd-reply textarea {
    font-size: 16px; min-height: 64px; border-radius: 12px;
  }
  .wd-reply button {
    min-height: 44px; padding: 0 20px; border-radius: 12px; width: 100%;
    background: linear-gradient(135deg, #bd1f2e, #8f101c);
    box-shadow: 0 6px 16px rgba(143,16,28,.25);
  }
  .wd-reply-bar {
    flex-direction: column; align-items: stretch; gap: 8px;
  }
  .wd-login-hint {
    margin: 0 14px; padding: 16px; font-size: .82rem;
  }
}

@media (max-width: 480px) {
  .wd-answers { padding: 0 12px }
  .wd-question { padding: 14px 12px }
  .wd-reply-dock { padding-left: 12px; padding-right: 12px }
  .wd-login-hint { margin: 0 12px }
}
</style>
