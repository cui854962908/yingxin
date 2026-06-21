import { computed, inject, type Ref, type ComputedRef } from 'vue'
import type { Student } from '../types/student'

export const GUEST_SESSION_KEY = 'guest'

export const GUEST_STUDENT: Student = {
  name: '访客',
  student_id: '',
  photo: '',
  class_name: '',
  dormitory: '',
  role: 'guest',
  advisor: { name: '', phone: '' },
  class_teacher: { name: '', phone: '' },
  assistants: [],
}

export function isGuestRole(role: string | undefined): boolean {
  return role === 'guest'
}

export function readGuestSession(): boolean {
  return sessionStorage.getItem(GUEST_SESSION_KEY) === '1'
}

export function setGuestSession(on: boolean) {
  if (on) sessionStorage.setItem(GUEST_SESSION_KEY, '1')
  else sessionStorage.removeItem(GUEST_SESSION_KEY)
}

export function readStoredStudent(): Student | null {
  try {
    const raw = localStorage.getItem('student')
    return raw ? (JSON.parse(raw) as Student) : null
  } catch {
    return null
  }
}

export function hasAuthToken(): boolean {
  return !!localStorage.getItem('token')
}

export function useGuest(): {
  isGuest: ComputedRef<boolean>
  isLoggedIn: ComputedRef<boolean>
} {
  const studentRef = inject<Ref<Student | null> | null>('student', null)
  const isGuest = computed(() => isGuestRole(studentRef?.value?.role))
  const isLoggedIn = computed(() => !!studentRef?.value && !isGuest.value)
  return { isGuest, isLoggedIn }
}
