<script setup lang="ts">
import { ref, onMounted, provide, computed } from 'vue'
import { useRouter } from 'vue-router'
import LoginPage from './components/LoginPage.vue'
import XiaoXinAssistant from './components/XiaoXinAssistant.vue'
import AppSpinner from './components/AppSpinner.vue'
import { usePreload } from './composables/usePreload'
import { GUEST_STUDENT, isGuestRole, readGuestSession, setGuestSession } from './composables/useGuest'
import { MOBILE_MAX } from './composables/useBreakpoint'
import { viewportWidth } from './composables/useViewport'
import { setAccessToken, onForceLogout } from './composables/useAuthFetch'

import type { Student } from './types/student'

const router = useRouter()
const { preload } = usePreload()

const student = ref<Student | null>(null)
const loading = ref(true)
const showWelcome = ref(false)
const xinOpen = ref(false)
const sidebarOpen = ref(typeof window !== 'undefined' ? window.innerWidth > 768 : true)

onMounted(async () => {
  // 注册强制登出回调（供 authFetch 在 refresh 也失败时调用）
  onForceLogout(() => {
    student.value = null
  })

  // 优先用 refresh token 恢复会话
  const savedToken = localStorage.getItem('token')
  const refreshToken = localStorage.getItem('refresh_token')
  if (refreshToken) {
    try {
      // 尝试刷新 token 以获取新的 access token（避免旧 token 已过期）
      const refreshRes = await fetch('/api/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      const refreshData = await refreshRes.json()
      if (refreshData.success) {
        // 刷新成功，用新 token 获取用户信息
        const newToken = refreshData.data.access_token
        setAccessToken(newToken)
        localStorage.setItem('token', newToken)
        localStorage.setItem('refresh_token', refreshData.data.refresh_token)

        const res = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${newToken}` },
        })
        const d = await res.json()
        if (d.success) {
          applyLoginSession(d.data, newToken)
          loading.value = false
          return
        }
      }
    } catch { console.warn('Refresh token 恢复会话失败，退回登录页') }
    clearAuth()
  } else if (savedToken) {
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${savedToken}` },
      })
      const d = await res.json()
      if (d.success) {
        setAccessToken(savedToken)
        applyLoginSession(d.data, savedToken)
        loading.value = false
        return
      }
    } catch { console.warn('自动登录验证失败，退回登录页') }
    clearAuth()
  }
  if (readGuestSession()) {
    student.value = { ...GUEST_STUDENT }
    loading.value = false
    preload()
    if (viewportWidth() <= MOBILE_MAX) {
      router.replace('/intro/wiki')
    }
    return
  }
  loading.value = false
  showWelcome.value = true
  setTimeout(() => { showWelcome.value = false }, 2800)
})

function buildStudent(s: Record<string, any>): Student {
  return {
    id: typeof s.id === 'number' ? s.id : undefined,
    name: s.name || '',
    student_id: s.student_id || '',
    photo: s.photo || '',
    class_name: s.class_name || '',
    dormitory: s.dormitory || '',
    role: s.role || 'student',
    advisor: s.advisor && typeof s.advisor === 'object' && s.advisor.name
      ? { name: s.advisor.name || '', phone: s.advisor.phone || '' }
      : { name: s.advisor_name || '', phone: s.advisor_phone || '' },
    class_teacher: s.class_teacher && typeof s.class_teacher === 'object' && s.class_teacher.name
      ? { name: s.class_teacher.name || '', phone: s.class_teacher.phone || '' }
      : { name: s.class_teacher_name || '', phone: s.class_teacher_phone || '' },
    assistants: Array.isArray(s.assistants) && s.assistants.length
      ? s.assistants.map((a: { name?: string; phone?: string; class_name?: string }) => ({ name: a.name || '', phone: a.phone || '', class_name: a.class_name || '' }))
      : (s.assistant_name ? [{ name: s.assistant_name || '', phone: s.assistant_phone || '', class_name: s.assistant_class_name || '' }] : []),
  }
}

function applyLoginSession(s: Record<string, any>, token: string): Student {
  setGuestSession(false)
  const safe = buildStudent(s)
  student.value = safe
  setAccessToken(token)
  localStorage.setItem('token', token)
  localStorage.setItem('student', JSON.stringify(safe))
  preload()
  return safe
}

function onLoginSuccess(s: Record<string, any>, token: string, refreshToken?: string) {
  // 先持久化 token，再导航，最后设置 student 以避免闪现首页
  setGuestSession(false)
  const safe = buildStudent(s)
  setAccessToken(token)
  localStorage.setItem('token', token)
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken)
  }
  localStorage.setItem('student', JSON.stringify(safe))
  const target = viewportWidth() <= MOBILE_MAX ? '/intro/wiki' : '/'
  router.replace(target).then(() => {
    student.value = safe
    preload()
  })
}

function clearAuth() {
  setAccessToken(null)
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('student')
  setGuestSession(false)
}

async function onGuestEnter() {
  setAccessToken(null)
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('student')
  setGuestSession(true)
  showWelcome.value = false
  preload()
  // 先导航到认识牧院，再设置 student，避免 router-view 在 '/' 路径渲染一帧
  await router.push('/intro/wiki')
  student.value = { ...GUEST_STUDENT }
}

async function onLogout() {
  // 通知服务端撤销 refresh token
  const rt = localStorage.getItem('refresh_token')
  if (rt) {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: rt }),
      })
    } catch { /* 网络异常不影响本地登出 */ }
  }
  clearAuth()
  student.value = null
}

provide('student', student)
provide('logout', onLogout)
provide('xinOpen', xinOpen)
provide('sidebarOpen', sidebarOpen)

/** 供 HomePage 判断个人信息卡等登录态 UI */
const isAuthenticated = computed(
  () => !!student.value && !isGuestRole(student.value.role),
)
provide('isAuthenticated', isAuthenticated)
</script>

<template>
  <!-- 欢迎开场动画 -->
  <Transition name="welcome">
    <div v-if="showWelcome" class="welcome-overlay">
      <div class="welcome-content">
        <p class="welcome-line-1">新同学，你好</p>
        <p class="welcome-line-2">
          <span class="welcome-prefix">欢迎来到</span>
          <span class="welcome-school">河南牧业经济学院</span>
        </p>
      </div>
    </div>
  </Transition>

  <div v-if="loading" class="loading">
    <AppSpinner />
  </div>

  <Transition v-else name="login" mode="out-in">
    <LoginPage v-if="!student" key="login" @login-success="onLoginSuccess" @guest-enter="onGuestEnter" />
    <div v-else key="home" class="app-main">
      <router-view v-slot="{ Component }">
        <Transition name="module" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
      <XiaoXinAssistant v-if="isAuthenticated" />
    </div>
  </Transition>
</template>

<style>
/* 全局滚动条 —— 统一 Windows Chrome 默认粗滚动条 */
html { scrollbar-width: thin; scrollbar-color: #d4c8b0 transparent }
::-webkit-scrollbar { width: 6px; height: 6px }
::-webkit-scrollbar-track { background: transparent }
::-webkit-scrollbar-thumb { background: #d4c8b0; border-radius: 3px }
::-webkit-scrollbar-thumb:hover { background: #b0a090 }

/* iOS：输入框字号 < 16px 会触发自动缩放，真机与 DevTools 表现不一致 */
@media (max-width: 768px) {
  input, textarea, select { font-size: 16px; }
}

.app-main { width: 100%; min-height: 100vh; min-height: calc(var(--vh, 1vh) * 100); background: #fefcf9 }

.loading {
  min-height: 100vh; min-height: calc(var(--vh, 1vh) * 100); display: flex; align-items: center; justify-content: center;
  background: #fefcf9;
}

/* ===== 欢迎开场动画 ===== */
.welcome-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: linear-gradient(170deg, #3d1114 0%, #591a1e 30%, #4a1519 60%, #361012 100%);
  display: flex; align-items: center; justify-content: center;
}
.welcome-content { text-align: center }
.welcome-line-1 {
  font-size: 2.8rem; font-weight: 700; color: #f2e6d0;
  letter-spacing: .15em; font-family: 'Georgia', 'Noto Serif SC', 'KaiTi', serif;
  font-style: italic;
  animation: welcomeFade 1s cubic-bezier(.33,1,.68,1) both;
}
.welcome-line-2 { margin-top: 20px; animation: welcomeFade 1s .6s cubic-bezier(.33,1,.68,1) both }
.welcome-prefix { font-size: 1.25rem; font-weight: 600; color: rgba(242,230,208,.7); letter-spacing: .08em }
.welcome-school { display: block; font-size: 2rem; font-weight: 700; color: #f2e6d0; letter-spacing: .1em; margin-top: 8px; font-style: normal }
@keyframes welcomeFade { from { opacity: 0; transform: translateY(12px) } to { opacity: 1; transform: translateY(0) } }

.welcome-leave-active { animation: welcomeOut .6s .2s ease-in both }
@keyframes welcomeOut { to { opacity: 0 } }

/* ===== 登录→首页 分层揭幕 ===== */
.login-leave-active{animation:loginOut .3s ease-in both}
.login-enter-active{animation:loginIn .6s cubic-bezier(.33,1,.68,1) both}
@keyframes loginOut{to{opacity:0;transform:scale(1.02)}}
@keyframes loginIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
</style>
