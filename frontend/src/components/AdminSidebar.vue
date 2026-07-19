<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'

// ===== 类型定义 =====
interface UserInfo {
  name: string
  role: string
  avatar?: string
}

interface MenuItem {
  id: string
  label: string
  icon: 'home' | 'megaphone' | 'message-circle' | 'building' | 'wall'
}

// ===== Props & Emits =====
const props = withDefaults(defineProps<{
  user: UserInfo
  activeMenu?: string
  modelValue?: boolean
  isGuest?: boolean
}>(), {
  activeMenu: 'home',
  modelValue: true,
  isGuest: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  navigate: [key: string]
  logout: []
}>()

const menuItems: MenuItem[] = [
  { id: 'intro',            label: '认识牧院', icon: 'building' },
  { id: 'home',             label: '首页',     icon: 'home' },
  { id: 'announcements',    label: '校园公告', icon: 'megaphone' },
  { id: 'faq',              label: '问题答疑', icon: 'message-circle' },
  { id: 'wall',             label: '牧院新生说',   icon: 'wall' },
]

const avatarChar = computed(() => props.user.name?.charAt(0) || '')

function onNavigate(id: string) {
  emit('navigate', id)
  if (window.innerWidth <= 768) emit('update:modelValue', false)
}

function onLogout() {
  emit('logout')
  if (window.innerWidth <= 768) emit('update:modelValue', false)
}

function close() {
  emit('update:modelValue', false)
}

// ===== 左划关闭手势（仅移动端） =====
const swipeStartX = ref(0)
const swipeStartY = ref(0)
const swipeDX = ref(0)
const swipeDY = ref(0)
const swiping = ref(false)
let swipePointerId: number | null = null
let swipeCaptureEl: HTMLElement | null = null

function onSwipeDown(e: PointerEvent) {
  if (window.innerWidth > 768) return
  if (e.pointerType === 'touch') return
  swiping.value = true
  swipePointerId = e.pointerId
  swipeStartX.value = e.clientX
  swipeStartY.value = e.clientY
  swipeDX.value = 0
  swipeDY.value = 0
  swipeCaptureEl = e.currentTarget as HTMLElement
  swipeCaptureEl.setPointerCapture(e.pointerId)
}

function onSwipeTouchStart(e: TouchEvent) {
  if (window.innerWidth > 768 || e.touches.length !== 1) return
  const touch = e.touches[0]
  swiping.value = true
  swipeStartX.value = touch.clientX
  swipeStartY.value = touch.clientY
  swipeDX.value = 0
  swipeDY.value = 0
}

function onSwipeTouchMove(e: TouchEvent) {
  if (!swiping.value || e.touches.length !== 1) return
  const touch = e.touches[0]
  swipeDX.value = Math.min(0, touch.clientX - swipeStartX.value)
  swipeDY.value = touch.clientY - swipeStartY.value
  if (swipeDX.value < -12 && Math.abs(swipeDX.value) > Math.abs(swipeDY.value) && e.cancelable) {
    e.preventDefault()
  }
}

function finishSwipeState() {
  if (!swiping.value) return
  swiping.value = false
  if (swipeDX.value < -70 && Math.abs(swipeDX.value) > Math.abs(swipeDY.value)) close()
  swipeDX.value = 0
  swipeDY.value = 0
}

function onSwipeMove(e: PointerEvent) {
  if (!swiping.value || e.pointerId !== swipePointerId) return
  swipeDX.value = Math.min(0, e.clientX - swipeStartX.value)
  swipeDY.value = e.clientY - swipeStartY.value
}

function finishSwipe(e: PointerEvent) {
  if (!swiping.value || e.pointerId !== swipePointerId) return
  if (swipeCaptureEl?.hasPointerCapture?.(e.pointerId)) {
    swipeCaptureEl.releasePointerCapture(e.pointerId)
  }
  swipeCaptureEl = null
  swipePointerId = null
  finishSwipeState()
}

onMounted(() => {
  document.addEventListener('pointermove', onSwipeMove)
  document.addEventListener('pointerup', finishSwipe)
  document.addEventListener('pointercancel', finishSwipe)
})
onUnmounted(() => {
  document.removeEventListener('pointermove', onSwipeMove)
  document.removeEventListener('pointerup', finishSwipe)
  document.removeEventListener('pointercancel', finishSwipe)
})
</script>

<template>
  <!-- ===== 移动端遮罩 ===== -->
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="props.modelValue" class="sidebar-overlay" @click="close" />
    </Transition>
  </Teleport>

  <!-- ===== 侧边栏主体 ===== -->
  <Transition name="sidebar">
    <aside
      v-if="props.modelValue"
      class="admin-sidebar"
      :class="{ swiping }"
      :style="swiping ? { transform: `translateX(${swipeDX}px)`, transition: 'none' } : {}"
      @pointerdown="onSwipeDown"
      @touchstart.passive="onSwipeTouchStart"
      @touchmove="onSwipeTouchMove"
      @touchend="finishSwipeState"
      @touchcancel="finishSwipeState"
    >
      <!-- 移动端关闭按钮 -->
      <button class="mobile-close" @click="close" aria-label="关闭菜单">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>

      <!-- 顶部品牌区 -->
      <div class="brand">
        <div class="logo-ring">
          <img src="/logo-1.webp" alt="校徽" class="logo-img" decoding="async" />
        </div>
        <h1 class="school-name-zh">河南牧业经济学院</h1>
        <p class="school-name-en">Henan University of Animal Husbandry and Economy</p>
      </div>

      <!-- 用户信息区 -->
      <div class="user-card">
        <div class="user-avatar">
          <img v-if="user.avatar" :src="user.avatar" alt="" class="user-avatar-img" />
          <span v-else class="user-avatar-char">{{ avatarChar }}</span>
        </div>
        <div class="user-text">
          <span class="user-name">{{ user.name }}</span>
          <span class="user-role">{{ user.role }}</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-list">
        <button
          v-for="item in menuItems"
          :key="item.id"
          class="nav-item"
          :class="{ 'nav-item--active': activeMenu === item.id }"
          @click="onNavigate(item.id)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <template v-if="item.icon === 'home'">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </template>
            <template v-else-if="item.icon === 'megaphone'">
              <path d="M11 6V3l8 2v14l-8 2v-3"/><path d="M3 10v4h2l4 3V7L5 10H3z"/><path d="M19 10a3 3 0 0 1 0 4"/>
            </template>
            <template v-else-if="item.icon === 'message-circle'">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </template>
            <template v-else-if="item.icon === 'wall'">
              <path d="M4 19h16"/><path d="M4 15h10"/><path d="M4 11h16"/><path d="M4 7h7"/>
            </template>
            <template v-else-if="item.icon === 'building'">
              <rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>
            </template>
          </svg>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <!-- 登出 -->
      <button class="logout-btn" @click="onLogout">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        <span>{{ props.isGuest ? '退出浏览' : '退出登录' }}</span>
      </button>
    </aside>
  </Transition>
</template>

<style scoped src="../styles/sidebar/admin-sidebar.css"></style>

