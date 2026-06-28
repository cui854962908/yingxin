<script setup lang="ts">
import { ref, inject, computed, watch, nextTick, onMounted, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { useRoute } from 'vue-router'
import { useAppNavigate } from '../composables/useAppNavigate'
import { useBreakpoint } from '../composables/useBreakpoint'
import ProfileCard from './ProfileCard.vue'
import AdminSidebar from './AdminSidebar.vue'
import MobileBottomNav from './MobileBottomNav.vue'
import '../styles/panel-enter.css'

import type { Student } from '../types/student'
import { studentGradeLabel } from '../utils/gradeLabel'
import { GUEST_STUDENT, isGuestRole, readStoredStudent, hasAuthToken } from '../composables/useGuest'
import { GUEST_ROLE_LABEL } from '../constants/product'

const studentRef = inject<Ref<Student | null>>('student', ref(null))
const isAuthenticated = inject<ComputedRef<boolean>>(
  'isAuthenticated',
  computed(() => hasAuthToken() && !isGuestRole(studentRef.value?.role)),
)

/** 优先 inject，其次 localStorage（防止 inject 链断裂时误显示为游客） */
const student = computed(() => {
  const live = studentRef.value
  if (live && !isGuestRole(live.role)) return live
  const stored = readStoredStudent()
  if (stored && !isGuestRole(stored.role)) return stored
  return live ?? GUEST_STUDENT
})

const logout = inject<() => void>('logout', () => {
  console.warn('[HomePage] logout 未注入')
})

const route = useRoute()
const { appNavigate } = useAppNavigate()
const { isMobile } = useBreakpoint()
const isGuest = computed(() => isGuestRole(student.value.role))
const isAdmin = computed(() => student.value.role === 'admin')
const isClubAdmin = computed(() => student.value.role === 'club_admin')
// computed 改为 ref + watch + nextTick，避免布局类切换与 Vue Transition 动画同时触发导致组件被"淹没"
function isFullBleedPath(path: string): boolean {
  return path.startsWith('/clubs') || path.startsWith('/wall')
}

const isIntroModule = computed(() => route.path.startsWith('/intro'))
const isWallModule = computed(() => route.path.startsWith('/wall'))
const isMotionModule = computed(() => isIntroModule.value || isWallModule.value)

const isFullBleedModule = ref(isFullBleedPath(route.path))
watch(() => route.path, (path) => {
  if (isFullBleedPath(path)) {
    nextTick(() => { isFullBleedModule.value = true })
  } else {
    isFullBleedModule.value = false
  }
})

/** 登录/游客均展示身份卡片（牧院新生说/社团全屏页除外；认识牧院移动端不展示） */
const showProfileCard = computed(
  () =>
    !isFullBleedModule.value
    && (isAuthenticated.value || isGuest.value)
    && !(isIntroModule.value && isMobile.value),
)

// 侧边栏显隐（桌面常驻，移动端 v-model 控制；状态提升至 App.vue 以供 XiaoXin 感知）
const sidebarOpen = inject<Ref<boolean>>('sidebarOpen', ref(true))

// 根据当前路由反推侧边栏选中项
const activeKey = computed(() => {
  if (route.path.startsWith('/intro')) return 'intro'
  if (route.path === '/') return 'home'
  if (route.path.startsWith('/announcements')) return 'announcements'
  if (route.path.startsWith('/faq')) return 'faq'
  if (route.path.startsWith('/wall')) return 'wall'
  return 'home'
})

// 用户角色文案
const userRoleLabel = computed(() => {
  if (isGuest.value) return GUEST_ROLE_LABEL
  if (isAdmin.value) return '管理员'
  if (isClubAdmin.value) return '社团管理员'
  return studentGradeLabel(student.value.student_id)
})

const isNavigating = ref(false)
function handleNavigate(key: string) {
  if (isNavigating.value) return
  const routeMap: Record<string, string> = {
    home: '/',
    intro: '/intro/wiki',
    announcements: '/announcements',
    faq: '/faq',
    wall: '/wall',
    campus: '/campus',
  }
  const target = routeMap[key]
  if (!target || route.path === target) return // 同页不跳
  isNavigating.value = true
  appNavigate(target)
  setTimeout(() => { isNavigating.value = false }, 500)
}

function handleLogout() {
  logout!()
}

// 从手机端切回桌面端时自动恢复侧边栏
function onResize() {
  if (window.innerWidth > 768) sidebarOpen.value = true
}

// 页面内容区右划呼出侧边栏（document 级跟踪，真机滑出区域后仍跟手）
const edgeSwipe = ref({ startX: 0, startY: 0, active: false, dx: 0, dy: 0 })
let edgePointerId: number | null = null
let edgeCaptureEl: HTMLElement | null = null

function onEdgeDown(e: PointerEvent) {
  if (window.innerWidth > 768 || sidebarOpen.value || e.button !== 0) return
  if (e.pointerType === 'touch') return
  const target = e.target as HTMLElement
  if (target.closest('button, a, input, textarea, select, [contenteditable="true"]')) return
  edgeSwipe.value = { startX: e.clientX, startY: e.clientY, active: true, dx: 0, dy: 0 }
  edgePointerId = e.pointerId
  edgeCaptureEl = e.currentTarget as HTMLElement
  edgeCaptureEl.setPointerCapture(e.pointerId)
}

const touchSwipe = ref({ startX: 0, startY: 0, dx: 0, dy: 0, active: false })

function onPageTouchStart(e: TouchEvent) {
  if (window.innerWidth > 768 || sidebarOpen.value || e.touches.length !== 1) return
  const target = e.target as HTMLElement
  if (target.closest('input, textarea, select, [contenteditable="true"]')) return
  const touch = e.touches[0]
  touchSwipe.value = { startX: touch.clientX, startY: touch.clientY, dx: 0, dy: 0, active: true }
}

function onPageTouchMove(e: TouchEvent) {
  if (!touchSwipe.value.active || e.touches.length !== 1) return
  const touch = e.touches[0]
  touchSwipe.value.dx = touch.clientX - touchSwipe.value.startX
  touchSwipe.value.dy = touch.clientY - touchSwipe.value.startY
  if (touchSwipe.value.dx > 12 && touchSwipe.value.dx > Math.abs(touchSwipe.value.dy)) {
    e.preventDefault()
  }
}

function finishPageTouch() {
  const { dx, dy, active } = touchSwipe.value
  touchSwipe.value.active = false
  if (active && dx > 70 && dx > Math.abs(dy) * 1.25) sidebarOpen.value = true
}

function cancelPageTouch() {
  touchSwipe.value.active = false
}

function onEdgeMove(e: PointerEvent) {
  if (!edgeSwipe.value.active || e.pointerId !== edgePointerId) return
  edgeSwipe.value.dx = e.clientX - edgeSwipe.value.startX
  edgeSwipe.value.dy = e.clientY - edgeSwipe.value.startY
}

function finishEdge(e: PointerEvent) {
  if (!edgeSwipe.value.active || e.pointerId !== edgePointerId) return
  edgeSwipe.value.active = false
  if (edgeCaptureEl?.hasPointerCapture?.(e.pointerId)) {
    edgeCaptureEl.releasePointerCapture(e.pointerId)
  }
  edgeCaptureEl = null
  edgePointerId = null
  if (edgeSwipe.value.dx > 70 && edgeSwipe.value.dx > Math.abs(edgeSwipe.value.dy) * 1.25) {
    sidebarOpen.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  document.addEventListener('pointermove', onEdgeMove)
  document.addEventListener('pointerup', finishEdge)
  document.addEventListener('pointercancel', finishEdge)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  document.removeEventListener('pointermove', onEdgeMove)
  document.removeEventListener('pointerup', finishEdge)
  document.removeEventListener('pointercancel', finishEdge)
})
</script>

<template>
  <div
    class="dashboard"
    @pointerdown.capture="onEdgeDown"
    @touchstart.passive="onPageTouchStart"
    @touchmove="onPageTouchMove"
    @touchend="finishPageTouch"
    @touchcancel="cancelPageTouch"
  >
    <!-- 主内容区 -->
    <main
      class="main"
      :class="{
        'main--fixed': isFullBleedModule,
        'main--fullbleed': isFullBleedModule,
        'main--intro': isIntroModule,
      }"
    >
      <section v-show="showProfileCard" class="profile-section">
        <ProfileCard />
      </section>

      <section
        class="bottom-section"
        :class="{ 'bottom-section--full': isFullBleedModule, 'bottom-section--intro': isIntroModule }"
      >
        <div
          class="section-card"
          :class="{
            'section-card--fullbleed': isFullBleedModule,
            'section-card--intro': isIntroModule,
            'section-card--motion': isMotionModule,
            'section-card--wall': isWallModule,
          }"
        >
          <Transition name="module" mode="out-in">
            <router-view :key="route.fullPath" />
          </Transition>
        </div>
      </section>
    </main>

    <!-- 侧边栏 -->
    <AdminSidebar
      v-model="sidebarOpen"
      :user="{ name: student.name, role: userRoleLabel }"
      :active-menu="activeKey"
      :is-guest="isGuest"
      @navigate="handleNavigate"
      @logout="handleLogout"
    />

    <!-- 移动端底部导航栏 -->
    <MobileBottomNav
      @navigate="handleNavigate"
    />
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh; min-height: calc(var(--vh, 1vh) * 100); position: relative;
  background-image: image-set(
    url('/beijing2.webp') type('image/webp'),
    url('/beijing2.png') type('image/png')
  );
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
}
/* 建筑线稿水印 — 呼应登录页品牌感 */
.dashboard::after {
  content: ''; position: fixed; bottom: -40px; right: -20px; z-index: 0;
  width: 380px; height: 180px; pointer-events: none;
  background: url('/building-illustration.svg') no-repeat right bottom / contain;
  opacity: .06;
}

/* ===== 主内容 ===== */
.main {
  min-height: 100vh; min-height: calc(var(--vh, 1vh) * 100);
  display: flex;
  flex-direction: column;
  padding: 16px 32px 20px;
  gap: 18px;
  transition: margin-left 0.35s cubic-bezier(0.33, 1, 0.68, 1);
}
.main--fixed {
  height: 100vh; height: calc(var(--vh, 1vh) * 100);
  overflow: hidden;
}

/* 桌面端：为固定侧边栏留出空间 */
@media (min-width: 769px) {
  .main { margin-left: 280px }
}

@media (max-width: 768px) {
  .dashboard {
    background-attachment: scroll;
    /* 论坛/社团等全屏模块与底栏、回答框共用 */
    --yx-mobile-nav: calc(52px + env(safe-area-inset-bottom, 0px));
  }
  .dashboard::after {
    display: none;
  }
  .main { margin-left: 0; padding: 8px 14px calc(68px + env(safe-area-inset-bottom, 0px)); gap: 10px }
  .main--intro {
    padding: 6px 8px calc(68px + env(safe-area-inset-bottom, 0px));
    gap: 8px;
  }
  .main--fullbleed {
    padding: 4px 8px calc(52px + env(safe-area-inset-bottom, 0px));
    gap: 0;
  }
  .profile-section { flex: 0 0 auto }
  .bottom-section { flex: 1; min-height: 0 }
}

/* ===== 内容区 ===== */
.profile-section {
  flex: 0 0 auto;
  flex-shrink: 0;
  overflow: visible;
  opacity: 1;
  margin-bottom: 0;
}
.bottom-section { flex: 1; min-height: 0; transition: flex .45s cubic-bezier(.33,1,.68,1) }
.bottom-section--full { flex: 1 }

.section-card {
  height: 100%; background: #fff; border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 6px 20px rgba(0,0,0,.05);
  padding: 24px 28px; overflow-y: auto; overflow-x: hidden;
}
.section-card--intro {
  padding: 0;
  border: 1px solid rgba(222, 222, 227, 0.85);
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03), 0 6px 20px rgba(0, 0, 0, 0.05);
  isolation: isolate;
}

.section-card--wall {
  padding: 0;
  background: transparent;
  box-shadow: none;
  border-radius: 12px;
  overflow: hidden;
}

/* 认识牧院：PC 整页滚动；移动端顶栏 sticky 时滚动锁在卡片内 */
@media (min-width: 769px) {
  .section-card--intro {
    height: auto;
    overflow-y: visible;
  }
}

@media (max-width: 768px) {
  .main--intro {
    height: calc(var(--vh, 1vh) * 100);
    max-height: calc(var(--vh, 1vh) * 100);
    overflow: hidden;
  }

  .main--intro .bottom-section--intro {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .main--intro .section-card--intro {
    flex: 1;
    min-height: 0;
    height: auto;
    overflow-y: auto;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
}

@media(max-width:768px){ .section-card { border-radius: 12px; padding: 14px } }
@media (max-width: 768px) {
  .section-card--intro {
    padding: 0;
    border-radius: 12px;
    overflow-x: hidden;
    overflow-y: auto;
  }
}
@media(max-width:768px){
  .section-card--fullbleed {
    padding: 0;
    border-radius: 10px;
    overflow-x: hidden;
  }
}
@media (max-width: 768px) {
  .main--fullbleed {
    height: calc(var(--vh, 1vh) * 100);
    max-height: calc(var(--vh, 1vh) * 100);
    overflow: hidden;
  }

  .main--fullbleed .bottom-section--full {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .main--fullbleed .section-card--fullbleed {
    flex: 1;
    min-height: 0;
    height: auto;
    overflow-y: auto;
    overflow-x: hidden;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }
}
@media(max-width:480px){ .section-card { border-radius: 10px; padding: 14px 12px } }
@media(max-width:480px){ .section-card--fullbleed { padding: 0; border-radius: 10px } }

/* ===== 模块切换动画 ===== */
.module-enter-active{animation:velvetIn .5s cubic-bezier(.33,1,.68,1) both}
.module-leave-active{animation:velvetOut .15s ease-in both}
@keyframes velvetIn{from{opacity:0;transform:scale(.98)}to{opacity:1;transform:scale(1)}}
@keyframes velvetOut{to{opacity:0}}

.module-enter-active > :nth-child(1){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.06s}
.module-enter-active > :nth-child(2){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.11s}
.module-enter-active > :nth-child(3){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.16s}
.module-enter-active > :nth-child(4){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.20s}
.module-enter-active > :nth-child(5){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.24s}
.module-enter-active > :nth-child(6){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.28s}
.module-enter-active > :nth-child(7){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.31s}
.module-enter-active > :nth-child(8){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.34s}
.module-enter-active > :nth-child(9){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.37s}
.module-enter-active > :nth-child(10){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.40s}
.module-enter-active > :nth-child(11){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.42s}
.module-enter-active > :nth-child(12){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.44s}
.module-enter-active > :nth-child(13){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.46s}
.module-enter-active > :nth-child(14){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.48s}
.module-enter-active > :nth-child(15){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.50s}
.module-enter-active > :nth-child(n+16){animation:fadeUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.52s}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}

/* ===== 入场动画 ===== */
.profile-section{animation:fadeInUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.2s}
.bottom-section{animation:fadeInUp .45s cubic-bezier(.16,1,.3,1) both;animation-delay:.38s}
@keyframes fadeInUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}

/* 移动端：模块切换直出，避免重型组件双渲染卡顿 */
@media(max-width:768px){
  .module-enter-active,.module-leave-active{animation:none}
  .module-enter-active > * {animation:none}
  .profile-section,.bottom-section{animation:none}
}

@media(max-width:1024px){
  .main{padding:20px 24px 24px}
}
@media(max-width:480px){
  .main{padding:12px 12px calc(68px + env(safe-area-inset-bottom, 0px));gap:12px}
}

@media (max-width: 768px) {
  .dashboard { touch-action: pan-y }
}
</style>
