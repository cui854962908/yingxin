<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LoginPage from './components/LoginPage.vue'
import HomePage from './components/HomePage.vue'

interface Student {
  name: string; student_id: string; photo: string; class_name: string
  dormitory: string; role: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const student = ref<Student | null>(null)
const loading = ref(true)

// 自动登录
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) { loading.value = false; return }
  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const d = await res.json()
    if (d.success) {
      const saved = localStorage.getItem('student')
      if (saved) student.value = JSON.parse(saved)
    } else {
      clearAuth()
    }
  } catch { clearAuth() }
  loading.value = false
})

function onLoginSuccess(s: Record<string, any>, token: string) {
  student.value = s as Student
  localStorage.setItem('token', token)
  localStorage.setItem('student', JSON.stringify(s))
}

function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('student')
}

function onLogout() {
  clearAuth()
  student.value = null
}
</script>

<template>
  <div v-if="loading" class="loading">
    <span class="loading-spinner" />
  </div>
  <LoginPage v-else-if="!student" @login-success="onLoginSuccess" />
  <HomePage v-else :student="student" @logout="onLogout" />
</template>

<style>
.loading {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #fefcf9;
}
.loading-spinner {
  width: 28px; height: 28px; border: 2.5px solid #e5dbcc;
  border-top-color: #b5343a; border-radius: 50%; animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg) } }
</style>
