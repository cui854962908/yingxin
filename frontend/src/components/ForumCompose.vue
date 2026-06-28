<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ForumCategory } from '../types/forum'
import { FORUM_CATEGORIES } from '../types/forum'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useAppNavigate } from '../composables/useAppNavigate'
import { FORUM_MODULE_NAME } from '../constants/product'
import '../styles/forum-mobile.css'

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

async function submit() {
  if (!title.value.trim() || content.value.trim().length < 5) {
    errMsg.value = '请填写标题和至少 5 字的描述'
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
  <div class="wall-compose">
    <div class="forum-mobile-sticky-top">
      <button type="button" class="forum-mobile-back" @click="appGoBackTo('/wall')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
        返回{{ FORUM_MODULE_NAME }}
      </button>
    </div>

    <div class="wc-card">
      <h2 class="wc-title">发布提问</h2>
      <p class="wc-hint">
        {{ fromXin ? '标题已从小信带入，补充详细描述后发布即可' : '描述清楚你的问题，方便同学帮你解答' }}
      </p>

      <label class="wc-field">
        <span>标题</span>
        <input v-model="title" maxlength="120" placeholder="例如：军训需要带什么？" />
      </label>
      <label class="wc-field">
        <span>分类</span>
        <select v-model="category">
          <option v-for="c in FORUM_CATEGORIES" :key="c" :value="c">{{ c }}</option>
        </select>
      </label>
      <label class="wc-field">
        <span>详细描述</span>
        <textarea v-model="content" rows="6" maxlength="2000" placeholder="补充背景、你已了解的信息…" />
      </label>

      <p v-if="errMsg" class="wc-err">{{ errMsg }}</p>
    </div>

    <div class="wc-submit-dock">
      <button type="button" class="wc-submit" :disabled="saving" @click="submit">
        {{ saving ? '发布中…' : `发布到${FORUM_MODULE_NAME}` }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.wall-compose { display: flex; flex-direction: column; gap: 14px; max-width: 640px; margin: 0 auto; min-height: 100% }
.wc-card {
  padding: 22px 24px; border-radius: 14px; background: #fff;
  border: 1px solid #f2ebe0; box-shadow: 0 4px 18px rgba(60,48,40,.06);
}
.wc-title { margin: 0; font-size: 1.1rem; color: #3c3028; font-weight: 700; letter-spacing: .06em }
.wc-hint { margin: 6px 0 18px; font-size: .8rem; color: #b0a090 }
.wc-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px }
.wc-field span { font-size: .78rem; font-weight: 600; color: #6b5e4e; letter-spacing: .08em }
.wc-field input, .wc-field select, .wc-field textarea {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e5dbcc; border-radius: 10px;
  font-size: .88rem; font-family: inherit; color: #3c3028; background: #fefcf9; outline: none; box-sizing: border-box;
}
.wc-field input:focus, .wc-field select:focus, .wc-field textarea:focus {
  border-color: #b5343a; box-shadow: 0 0 0 3px rgba(181,52,58,.08);
}
.wc-err { color: #b5343a; font-size: .82rem; margin: 0 0 10px }
.wc-submit {
  width: 100%; height: 44px; border: none; border-radius: 11px; cursor: pointer;
  background: linear-gradient(135deg, #bd1f2e, #8f101c); color: #fff;
  font-size: .92rem; font-weight: 700; letter-spacing: .12em; font-family: inherit;
}
.wc-submit:disabled { opacity: .55; cursor: default }

.wc-submit-dock { margin-top: 8px }

@media (min-width: 769px) {
  .wc-submit-dock {
    position: static;
    padding: 0;
    background: none;
  }
}

@media (max-width: 768px) {
  .wall-compose {
    max-width: none; gap: 0;
    padding-bottom: calc(80px + var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px))));
  }
  .wc-card {
    margin: 0; padding: 18px 14px 24px;
    border-radius: 0; border: none;
    border-top: 1px solid #f2ebe0;
    box-shadow: none;
  }
  .wc-title { font-size: 1.05rem }
  .wc-hint { font-size: .78rem; margin-bottom: 16px }
  .wc-field input, .wc-field select, .wc-field textarea {
    font-size: 16px; min-height: 48px; padding: 12px 14px; border-radius: 12px;
  }
  .wc-field textarea { min-height: 140px }
  .wc-submit-dock {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 8500;
    padding: 10px 14px var(--yx-mobile-nav, calc(52px + env(safe-area-inset-bottom, 0px)));
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.94) 30%, #fff 100%);
  }
  .wc-submit {
    width: 100%; height: 48px; border-radius: 13px; margin: 0;
    box-shadow: 0 10px 24px rgba(143,16,28,.28);
  }
}

@media (max-width: 480px) {
  .wc-card { padding: 16px 12px 20px }
  .wc-submit-dock { padding-left: 12px; padding-right: 12px }
}
</style>
