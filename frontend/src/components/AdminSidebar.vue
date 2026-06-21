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
  { id: 'home',             label: '首页',     icon: 'home' },
  { id: 'announcements',    label: '校园公告', icon: 'megaphone' },
  { id: 'faq',              label: '问题答疑', icon: 'message-circle' },
  { id: 'wall',             label: '问牧墙',   icon: 'wall' },
  { id: 'intro',            label: '认识牧院', icon: 'building' },
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

// ===== 右划关闭手势（仅移动端） =====
const swipeStartX = ref(0)
const swipeStartY = ref(0)
const swipeDX = ref(0)
const swipeDY = ref(0)
const swiping = ref(false)
let swipePointerId: number | null = null
let swipeCaptureEl: HTMLElement | null = null

function onSwipeDown(e: PointerEvent) {
  if (window.innerWidth > 768) return
  swiping.value = true
  swipePointerId = e.pointerId
  swipeStartX.value = e.clientX
  swipeStartY.value = e.clientY
  swipeDX.value = 0
  swipeDY.value = 0
  swipeCaptureEl = e.currentTarget as HTMLElement
  swipeCaptureEl.setPointerCapture(e.pointerId)
}

function onSwipeMove(e: PointerEvent) {
  if (!swiping.value || e.pointerId !== swipePointerId) return
  swipeDX.value = Math.min(0, e.clientX - swipeStartX.value)
  swipeDY.value = e.clientY - swipeStartY.value
}

function finishSwipe(e: PointerEvent) {
  if (!swiping.value || e.pointerId !== swipePointerId) return
  swiping.value = false
  if (swipeCaptureEl?.hasPointerCapture?.(e.pointerId)) {
    swipeCaptureEl.releasePointerCapture(e.pointerId)
  }
  swipeCaptureEl = null
  swipePointerId = null
  if (swipeDX.value < -70 && Math.abs(swipeDX.value) > Math.abs(swipeDY.value)) {
    close()
  }
  swipeDX.value = 0
  swipeDY.value = 0
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

<style scoped>
/* ===== 侧边栏主体 ===== */
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9000;
  width: 260px;
  height: 100vh;
  height: calc(var(--vh, 1vh) * 100);
  display: flex;
  flex-direction: column;
  background-image: image-set(
    url('/beijing1.webp') type('image/webp'),
    url('/beijing1.png') type('image/png')
  );
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  padding: 40px 20px 20px;
  overflow-y: auto;
  overflow-x: clip;
  touch-action: pan-y; /* 允许竖滚，保留横划给手势 */
}

/* ===== 移动端关闭按钮（仅移动端可见） ===== */
.mobile-close {
  display: none;
  position: absolute;
  top: 16px;
  left: 12px;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(242, 230, 208, 0.7);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* ===== 移动端遮罩 ===== */
.sidebar-overlay {
  display: none;
}

/* ===== 顶部品牌区 ===== */
.brand {
  text-align: center;
  margin-bottom: 36px;
}

.logo-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  padding: 3px;
  margin: 0 auto;
  transform: translateX(-8px);
  background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e);
  overflow: hidden;
  position: relative;
}

.logo-img {
  position: absolute;
  top: 50%;
  left: 48%;
  width: 125%;
  height: 125%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  object-fit: cover;
  background: transparent;
}

.school-name-zh {
  margin-top: 14px;
  font-size: 1rem;
  font-weight: 700;
  color: #f2e6d0;
  letter-spacing: 0.06em;
  font-family: 'Georgia', 'Noto Serif SC', 'KaiTi', serif;
}

.school-name-en {
  margin-top: 4px;
  font-size: 0.7rem;
  color: rgba(242, 230, 208, 0.55);
  letter-spacing: 0.03em;
  font-style: italic;
}

/* ===== 用户信息区 ===== */
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 32px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #6b6b7b;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-char {
  color: #f2e6d0;
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Noto Serif SC', serif;
}

.user-text {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #f2e6d0;
  letter-spacing: 0.03em;
  line-height: 1;
}

.user-role {
  display: inline-block;
  width: fit-content;
  font-size: 0.68rem;
  font-weight: 600;
  color: #f2e6d0;
  background: #3d1114;
  padding: 1px 10px;
  border-radius: 999px;
  letter-spacing: 0.05em;
  line-height: 1.5;
}

/* ===== 导航菜单 ===== */
.nav-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(242, 230, 208, 0.7);
  font-size: 0.94rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  letter-spacing: 0.04em;
}

.nav-item:hover {
  color: #f2e6d0;
  background: rgba(255, 255, 255, 0.04);
}

.nav-item--active {
  color: #f2e6d0;
  background: rgba(255, 255, 255, 0.1);
  font-weight: 500;
}

.nav-item svg {
  flex-shrink: 0;
  opacity: 0.75;
  transition: opacity 0.2s;
}

.nav-item:hover svg,
.nav-item--active svg {
  opacity: 1;
}

/* ===== 登出按钮 ===== */
.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  border: none;
  border-radius: 8px;
  margin-top: auto;
  background: transparent;
  color: rgba(242, 230, 208, 0.35);
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.logout-btn:hover {
  color: rgba(242, 230, 208, 0.75);
  background: rgba(255, 255, 255, 0.04);
}

.logout-btn svg {
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.logout-btn:hover svg {
  opacity: 0.9;
}

/* ===== 过渡动画 ===== */
.sidebar-enter-active {
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.sidebar-leave-active {
  transition: transform 0.25s cubic-bezier(0.55, 0, 1, 0.45);
}
.sidebar-enter-from,
.sidebar-leave-to {
  transform: translateX(-100%);
}

/* ===== 桌面端：始终可见 ===== */
@media (min-width: 769px) {
  .sidebar-overlay {
    display: none !important;
  }
  .mobile-close {
    display: none !important;
  }
}

/* ===== 移动端：浮层模式 ===== */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 100vw;
    width: 100dvw;
    z-index: 9100;
    background-size: 100% 100%;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 9050;
    background: rgba(0, 0, 0, 0.55);
  }

  .overlay-enter-active {
    transition: opacity 0.3s ease-out;
  }
  .overlay-leave-active {
    transition: opacity 0.25s ease-in;
  }
  .overlay-enter-from,
  .overlay-leave-to {
    opacity: 0;
  }

  .mobile-close {
    display: flex;
  }
}
</style>
