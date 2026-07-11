<script setup lang="ts">
import { inject, ref, type Ref } from 'vue'
import XinAvatar from '../XinAvatar.vue'

const emit = defineEmits<{ pickTopic: [keyword: string] }>()
const xinOpen = inject<Ref<boolean>>('xinOpen')
const isAuthenticated = inject<Ref<boolean>>('isAuthenticated', ref(false))
const logout = inject<() => void>('logout', () => {})
const loginRequiredModal = ref(false)
const topicIndex = ref(0)

const topicSets = [
  ['#新生报到', '#宿舍生活', '#选课攻略', '#专业学习', '#校园美食', '#社团招新'],
  ['#龙子湖校区', '#英才校区', '#北林校区', '#校园地图', '#图书馆', '#军训须知'],
]

function rotateTopics() {
  topicIndex.value = (topicIndex.value + 1) % topicSets.length
}

function openXin() {
  if (!isAuthenticated.value) {
    loginRequiredModal.value = true
    return
  }
  if (xinOpen) xinOpen.value = true
}

function goToLogin() {
  loginRequiredModal.value = false
  logout()
}
</script>

<template>
  <aside class="wall-aside" aria-label="牧院新生说侧边栏">
    <section class="wall-aside-card wall-guide-card">
      <header class="wall-aside-head">
        <h2 class="wall-aside-title">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5Zm16 0A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22V5.5Z"/></svg>
          提问说明
        </h2>
      </header>
      <ol class="wall-aside-tips">
        <li><span>1</span>先搜索，看看是否已有相似问题</li>
        <li><span>2</span>清晰描述问题，便于获得准确解答</li>
        <li><span>3</span>文明提问，共建互助友爱的校园氛围</li>
      </ol>
    </section>

    <section class="wall-aside-card">
      <header class="wall-aside-head">
        <h2 class="wall-aside-title">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2s1 4-2 6c-2-2-3-3-3-5-3 3-5 6-5 10a9 9 0 0 0 18 0c0-3-2-7-5-9 0 3-1 5-3 6 1-4 0-6 0-8Z"/></svg>
          热门话题
        </h2>
        <button type="button" class="wall-aside-link" @click="rotateTopics">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.3-5.7L20 8M20 3v5h-5"/></svg>
          换一换
        </button>
      </header>
      <div class="wall-aside-tags">
        <button
          v-for="tag in topicSets[topicIndex]"
          :key="tag"
          type="button"
          @click="emit('pickTopic', tag.slice(1))"
        >
          {{ tag }}
        </button>
      </div>
    </section>

    <section class="wall-aside-card wall-aside-xin">
      <div class="wall-aside-xin-text">
        <h2 class="wall-aside-title wall-xin-title">
          <span class="wall-xin-mini"><XinAvatar :size="26" /></span>
          小信助手
        </h2>
        <p>有问题找小信，<br />24小时为你解答校园疑问～</p>
        <button type="button" class="wall-aside-xin-btn" @click="openXin">去咨询小信</button>
      </div>
      <div class="wall-aside-robot" aria-hidden="true">
        <span class="wall-robot-antenna"></span>
        <svg viewBox="0 0 120 112">
          <path class="robot-arm" d="M25 62 10 54 4 66l22 15M95 62l15-8 6 12-22 15" />
          <circle class="robot-hand" cx="7" cy="58" r="8" />
          <circle class="robot-hand" cx="113" cy="58" r="8" />
          <path class="robot-body" d="M35 72c0-10 11-18 25-18s25 8 25 18v23H35V72Z" />
          <rect class="robot-head" x="24" y="18" width="72" height="57" rx="27" />
          <rect class="robot-face" x="34" y="29" width="52" height="35" rx="17" />
          <circle class="robot-eye" cx="49" cy="46" r="5" />
          <circle class="robot-eye" cx="71" cy="46" r="5" />
          <path class="robot-smile" d="M49 57c6 5 16 5 22 0" />
          <path class="robot-leg" d="M47 92v12m26-12v12" />
          <circle class="robot-joint" cx="60" cy="81" r="4" />
        </svg>
      </div>
    </section>
  </aside>

  <Teleport to="body">
    <Transition name="login-required-modal">
      <div v-if="loginRequiredModal" class="login-required-overlay" @click="loginRequiredModal = false">
        <div class="login-required-card" role="dialog" aria-modal="true" aria-labelledby="login-required-title" @click.stop>
          <button type="button" class="login-required-close" aria-label="关闭" @click="loginRequiredModal = false">
            <svg viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
          <span class="login-required-brand-tag">小信助手</span>
          <p id="login-required-title" class="login-required-msg">登录后可使用小信 AI 助手</p>
          <button type="button" class="login-required-goto" @click="goToLogin">去登录</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
