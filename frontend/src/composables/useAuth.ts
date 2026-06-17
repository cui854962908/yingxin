import { inject, computed, type Ref, type ComputedRef } from 'vue'
import type { Student } from '../types/student'

/**
 * 共享的认证请求头构造器。
 * 统一了 8 处分散定义的差异：无 token 时也返回 Content-Type，
 * 避免部分组件少发 Content-Type 导致的请求格式问题。
 */
export function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('token')
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' }
}

/**
 * 响应式认证状态 —— 替代各组件中直接的 localStorage.getItem 读取。
 * 从 App.vue 的 provide('student') 派生，保证与登录/登出状态同步。
 *
 * 仅在登录后页面使用；登录页 student 为 null，isAdmin/isClubAdmin 均为 false。
 */
export function useAuth(): {
  student: ComputedRef<Student | null>
  isAdmin: ComputedRef<boolean>
  isClubAdmin: ComputedRef<boolean>
  token: ComputedRef<string | null>
} {
  const studentRef = inject<Ref<Student | null> | null>('student', null)
  const student = computed(() => studentRef?.value ?? null)
  const isAdmin = computed(() => student.value?.role === 'admin')
  const isClubAdmin = computed(() => student.value?.role === 'club_admin')
  const token = computed(() => localStorage.getItem('token'))

  return { student, isAdmin, isClubAdmin, token }
}
