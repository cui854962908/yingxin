<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ForumCategory } from '../types/forum'
import { FORUM_CATEGORIES, FORUM_CATEGORY_COLORS } from '../types/forum'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useAppNavigate } from '../composables/useAppNavigate'
import { FORUM_MODULE_NAME } from '../constants/product'
import '../styles/forum-mobile.css'
import '../styles/forum/forum-compose.css'

const route = useRoute()
const router = useRouter()
const { appGoBackTo } = useAppNavigate()
const { token } = useAuth()

const title = ref('')
const content = ref('')
const category = ref<ForumCategory>('其他')
const saving = ref(false)
const errMsg = ref('')
const fromXin = ref(false)
const titleFocused = ref(false)
const contentFocused = ref(false)

const titleLen = computed(() => title.value.length)
const contentLen = computed(() => content.value.length)
const canSubmit = computed(() => title.value.trim() && content.value.trim().length >= 5 && !saving.value)

async function submit() {
  if (!canSubmit.value) {
    if (!title.value.trim()) errMsg.value = '请填写标题'
    else if (content.value.trim().length < 5) errMsg.value = '描述至少需要 5 个字'
    return
  }
  saving.value = true
  errMsg.value = ''
  try {
    const res = await fetch('/api/forum/posts', {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title.value.trim(),
        content: content.value.trim(),
        category: category.value,
      }),
    })
    const d = await res.json()
    if (!res.ok || !d.success) throw new Error(d.message || '发布失败')
    router.replace(`/wall/${d.data.id}`)
  } catch (e) {
    errMsg.value = e instanceof Error ? e.message : '发布失败，请重试'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (!token.value) {
    appGoBackTo('/wall')
    return
  }
  const raw = route.query.title
  if (typeof raw === 'string' && raw.trim()) {
    title.value = raw.trim().slice(0, 120)
    fromXin.value = true
    router.replace({ path: '/wall/new' })
  }
})
</script>

<template>
  <div class="fcompose">
    <div class="fcompose-layout">
      <aside class="fcompose-intro" aria-label="提问说明">
        <div class="fcompose-intro-mark">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a8 8 0 0 0-4.8 14.4L6 21l3.6-1.2A8 8 0 1 0 12 3Z"/><path d="M9.4 10a2.7 2.7 0 0 1 5.2.9c0 1.9-2.6 2.1-2.6 3.6M12 17.3h.01"/></svg>
        </div>
        <p class="fcompose-intro-kicker">牧院新生说</p>
        <h1><span>问题说清楚</span><span>回答更准确</span></h1>
        <p class="fcompose-intro-copy">向学长学姐描述你在报到、学习和校园生活中遇到的问题。</p>
        <ol class="fcompose-steps">
          <li><span>01</span><strong>概括问题</strong></li>
          <li><span>02</span><strong>选择分类</strong></li>
          <li><span>03</span><strong>补充细节</strong></li>
        </ol>
      </aside>

      <section class="fcompose-card">
        <header class="fcompose-card-head">
          <div>
            <p class="fcompose-card-eyebrow">新生互动问答</p>
            <h2 class="fcompose-card-title">发布提问</h2>
          </div>
          <button type="button" class="fcompose-card-close" @click="appGoBackTo('/wall')">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18 9 12l6-6"/></svg>
            返回{{ FORUM_MODULE_NAME }}
          </button>
        </header>

        <p v-if="fromXin" class="fcompose-xin-badge">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a8 8 0 0 1 8 8c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 8-8z"/><circle cx="12" cy="10" r="3"/></svg>
          <span>标题已从小信带入，请补充问题细节</span>
        </p>

        <label class="fcompose-field" :class="{ focused: titleFocused }">
          <span class="fcompose-label"><b>01</b> 问题标题 <em>必填</em></span>
          <div class="fcompose-input-wrap">
            <input v-model="title" maxlength="120" placeholder="用一句话概括你的问题" @focus="titleFocused = true" @blur="titleFocused = false" />
            <span class="fcompose-count" :class="{ near: titleLen > 100 }">{{ titleLen }}<span class="fcompose-count-max"> / 120</span></span>
          </div>
        </label>

        <fieldset class="fcompose-cats">
          <legend class="fcompose-label"><b>02</b> 问题分类</legend>
          <div class="fcompose-cats-row">
            <button v-for="c in FORUM_CATEGORIES" :key="c" type="button" class="fcompose-cat" :class="{ active: category === c }" :style="category === c ? { '--cat-color': FORUM_CATEGORY_COLORS[c] } : undefined" @click="category = c">{{ c }}</button>
          </div>
        </fieldset>

        <label class="fcompose-field" :class="{ focused: contentFocused }">
          <span class="fcompose-label"><b>03</b> 详细描述 <em>至少 5 个字</em></span>
          <div class="fcompose-input-wrap">
            <textarea v-model="content" rows="8" maxlength="2000" placeholder="补充事情经过、时间地点或你已经尝试过的方法，方便大家准确回答" @focus="contentFocused = true" @blur="contentFocused = false" />
            <span class="fcompose-count" :class="{ near: contentLen > 1700 }">{{ contentLen }}<span class="fcompose-count-max"> / 2000</span></span>
          </div>
        </label>

        <div class="fcompose-foot">
          <p v-if="errMsg" class="fcompose-err">{{ errMsg }}</p>
          <div class="fcompose-actions">
            <p v-if="!errMsg" class="fcompose-foot-hint">发布后 24 小时内可编辑，每日限 5 条</p>
            <button type="button" class="fcompose-submit" :class="{ ready: canSubmit }" :disabled="!canSubmit" @click="submit">
              <span>{{ saving ? '发布中…' : '确认发布' }}</span>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 14-7-4 14-3-5-7-2Z"/><path d="m12 14 7-9"/></svg>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
