<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import LoginPage from './components/LoginPage.vue'
import XiaoXinAssistant from './components/XiaoXinAssistant.vue'

interface Student {
  name: string; student_id: string; photo: string; class_name: string
  dormitory: string; role: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const student = ref<Student | null>(null)
const loading = ref(true)
const showWelcome = ref(false)

// 自动登录（有 token 则跳过欢迎动画）
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      const d = await res.json()
      if (d.success) {
        const saved = localStorage.getItem('student')
        if (saved) student.value = JSON.parse(saved)
        loading.value = false
        return
      }
    } catch { /* */ }
    clearAuth()
  }
  // 无 token，播放欢迎动画 → 登录页
  loading.value = false
  showWelcome.value = true
  setTimeout(() => { showWelcome.value = false }, 2800)
})

function onLoginSuccess(s: Record<string, any>, token: string) {
  // 防御后端返回字段缺失/为 null，兼容嵌套和扁平两种格式
  const safe: Student = {
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
      ? s.assistants.map((a: any) => ({ name: a.name || '', phone: a.phone || '', class_name: a.class_name || '' }))
      : (s.assistant_name ? [{ name: s.assistant_name || '', phone: s.assistant_phone || '', class_name: s.assistant_class_name || '' }] : []),
  }
  student.value = safe
  localStorage.setItem('token', token)
  localStorage.setItem('student', JSON.stringify(safe))
}

function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('student')
}

function onLogout() {
  clearAuth()
  student.value = null
}

provide('student', student)
provide('logout', onLogout)
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
    <span class="loading-spinner" />
  </div>

  <Transition v-else name="login" mode="out-in">
    <LoginPage v-if="!student" key="login" @login-success="onLoginSuccess" />
    <div v-else key="home" class="app-main">
      <router-view v-slot="{ Component }">
        <Transition name="module" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
      <XiaoXinAssistant />
    </div>
  </Transition>
</template>

<style>
.app-main { width: 100%; min-height: 100vh }

.loading {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #fefcf9;
}
.loading-spinner {
  width: 28px; height: 28px; border: 2.5px solid #e5dbcc;
  border-top-color: #b5343a; border-radius: 50%; animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg) } }

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
