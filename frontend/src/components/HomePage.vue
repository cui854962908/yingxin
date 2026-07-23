<script setup lang="ts">
import { ref, inject, computed, watch, onMounted, onUnmounted, type Ref, type ComputedRef } from 'vue'
import { useRoute, type RouteLocationNormalizedLoaded } from 'vue-router'
import { useAppNavigate } from '../composables/useAppNavigate'
import { useBreakpoint } from '../composables/useBreakpoint'
import { prefetchMobileTabChunks } from '../composables/usePreload'
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
// ref + sync watch：布局类与路由同步切换，避免 nextTick 延迟导致闪动
function isFullBleedPath(path: string): boolean {
  return path.startsWith('/clubs') || path.startsWith('/wall') || path.startsWith('/account')
}

/** 布局敏感路径：离开这些路径到非敏感路径时，冻结布局态避免内容区闪移 */
function isLayoutSensitivePath(path: string): boolean {
  return isFullBleedPath(path) || path.startsWith('/intro')
}

/** 模块切换离开动画期间，暂用旧路径的布局态，动画完成后再切回新路径 */
const leavingLayoutPath = ref<string | null>(null)
const layoutPath = computed(() => leavingLayoutPath.value ?? route.path)

const isFullBleedModule = computed(() => isFullBleedPath(layoutPath.value))
const isIntroModule = computed(() => layoutPath.value.startsWith('/intro'))
const isWallModule = computed(() => layoutPath.value.startsWith('/wall'))
const isMotionModule = computed(() => isIntroModule.value || isWallModule.value)

watch(
  () => route.path,
  (_path, oldPath) => {
    if (!isMobile.value && oldPath && isLayoutSensitivePath(oldPath as string)) {
      leavingLayoutPath.value = oldPath as string
    }
  },
  { flush: 'sync' },
)

/** 移动端底栏 Tab 壳内路由（含从认识牧院进入的社团详情） */
function isMobileTabRoute(path: string): boolean {
  if (path === '/') return true
  if (path.startsWith('/intro')) return true
  if (path.startsWith('/wall')) return true
  if (path.startsWith('/announcements')) return true
  if (path.startsWith('/faq')) return true
  if (/^\/clubs\/[^/]+$/.test(path) && path !== '/clubs/add') return true
  return false
}

const mobileTabShell = computed(() => isMobile.value && isMobileTabRoute(route.path))
const mobileTabBodyRef = ref<HTMLElement | null>(null)

/** 移动端切 Tab：统一滚动容器回顶（牧院内部子 Tab 切换除外） */
function isIntroShellPath(path: string) {
  return path === '/intro/wiki'
    || path === '/intro/colleges'
    || path === '/intro/clubs'
    || path.startsWith('/intro/sie')
}

watch(
  () => route.path,
  (path, prev) => {
    if (!mobileTabShell.value) return
    if (prev && isIntroShellPath(path) && isIntroShellPath(prev)) return
    if (path.startsWith('/intro')) {
      const introBody = mobileTabBodyRef.value?.querySelector('.intro-body')
      if (introBody instanceof HTMLElement) introBody.scrollTop = 0
      return
    }
    if (/^\/clubs\/[^/]+$/.test(path) && path !== '/clubs/add') {
      if (mobileTabBodyRef.value) mobileTabBodyRef.value.scrollTop = 0
      return
    }
    if (mobileTabBodyRef.value) mobileTabBodyRef.value.scrollTop = 0
  },
  { flush: 'sync' },
)

/** 移动端底栏切 Tab：缓存主模块实例，避免每次销毁重建 */
function mobileViewKey(r: RouteLocationNormalizedLoaded): string {
  const path = r.path
  if (path === '/') return 'home'
  if (path.startsWith('/intro')) return 'intro'
  if (path === '/wall') return 'wall'
  if (path.startsWith('/wall/')) return r.fullPath
  if (path === '/announcements') return 'announcements'
  if (path.startsWith('/announcements/')) return r.fullPath
  if (path === '/faq') return 'faq'
  if (path.startsWith('/faq/')) return r.fullPath
  if (path.startsWith('/clubs')) return path === '/clubs' ? 'clubs' : r.fullPath
  return r.fullPath
}

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
  if (/^\/clubs\/[^/]+$/.test(route.path) && route.path !== '/clubs/add') return 'intro'
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

function tabRootPath(key: string): string | undefined {
  const routeMap: Record<string, string> = {
    home: '/',
    intro: '/intro/wiki',
    announcements: '/announcements',
    faq: '/faq',
    wall: '/wall',
    campus: '/campus',
  }
  return routeMap[key]
}

function handleNavigate(key: string) {
  const target = tabRootPath(key)
  if (!target) return
  if (route.path === target) return

  if (!isMobile.value) {
    if (isNavigating.value) return
    isNavigating.value = true
    appNavigate(target)
    setTimeout(() => { isNavigating.value = false }, 500)
    return
  }

  appNavigate(target)
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

/** 左缘宽一点，方便唤起菜单；内容区需横向意图明确后再接管 */
const EDGE_SWIPE_ZONE_PX = 40

function onEdgeDown(e: PointerEvent) {
  if (window.innerWidth > 768 || sidebarOpen.value || e.button !== 0) return
  // 触摸走 touch 事件链，避免与 touchstart/touchmove 重复跟踪
  if (e.pointerType === 'touch') return
  const target = e.target as HTMLElement
  if (target.closest('button, a, input, textarea, select, [contenteditable="true"], .xin-panel')) return
  if (e.clientX > EDGE_SWIPE_ZONE_PX) return
  edgeSwipe.value = { startX: e.clientX, startY: e.clientY, active: true, dx: 0, dy: 0 }
  edgePointerId = e.pointerId
  edgeCaptureEl = e.currentTarget as HTMLElement
  edgeCaptureEl.setPointerCapture(e.pointerId)
}

const touchSwipe = ref({
  startX: 0,
  startY: 0,
  dx: 0,
  dy: 0,
  active: false,
  /** 左缘起手或已判定为横向侧滑 */
  committed: false,
})

function onPageTouchStart(e: TouchEvent) {
  if (window.innerWidth > 768 || sidebarOpen.value || e.touches.length !== 1) return
  const target = e.target as HTMLElement
  if (target.closest('.bottom-nav, button, a, input, textarea, select, [contenteditable="true"], .xin-panel')) return
  const touch = e.touches[0]
  const fromEdge = touch.clientX <= EDGE_SWIPE_ZONE_PX
  // 内容区横向滚动条（分类 Tab 等）右滑不开菜单，左缘仍保留
  if (!fromEdge && target.closest('.wall-cats-scroll, .clubs-categories, .intro-tabs')) return
  touchSwipe.value = {
    startX: touch.clientX,
    startY: touch.clientY,
    dx: 0,
    dy: 0,
    active: true,
    committed: fromEdge,
  }
}

function onPageTouchMove(e: TouchEvent) {
  if (!touchSwipe.value.active || e.touches.length !== 1) return
  const touch = e.touches[0]
  const dx = touch.clientX - touchSwipe.value.startX
  const dy = touch.clientY - touchSwipe.value.startY
  touchSwipe.value.dx = dx
  touchSwipe.value.dy = dy

  if (!touchSwipe.value.committed) {
    if (Math.abs(dy) > Math.abs(dx) + 8) {
      touchSwipe.value.active = false
      return
    }
    if (dx > 12 && dx > Math.abs(dy)) {
      touchSwipe.value.committed = true
    } else {
      return
    }
  }

  if (dx > 12 && dx > Math.abs(dy) && e.cancelable) {
    e.preventDefault()
  }
}

function finishPageTouch() {
  const { dx, dy, active } = touchSwipe.value
  touchSwipe.value.active = false
  touchSwipe.value.committed = false
  if (active && dx > 70 && dx > Math.abs(dy) * 1.25) sidebarOpen.value = true
}

function cancelPageTouch() {
  touchSwipe.value.active = false
  touchSwipe.value.committed = false
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

/** 模块离开动画完成后，释放布局冻结 */
function onAfterModuleLeave() {
  leavingLayoutPath.value = null
}

onMounted(() => {
  if (isMobile.value) prefetchMobileTabChunks()
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
        'main--mobile-tab-shell': mobileTabShell,
        'main--fixed': isFullBleedModule || mobileTabShell,
        'main--fullbleed': isFullBleedModule || mobileTabShell,
        'main--wall': isWallModule,
        'main--intro': isIntroModule,
      }"
    >
      <div
        ref="mobileTabBodyRef"
        class="mobile-tab-body"
        :class="{ 'mobile-tab-body--profile': mobileTabShell && showProfileCard }"
      >
        <section v-show="showProfileCard" class="profile-section">
          <ProfileCard />
        </section>

        <section
          class="bottom-section"
          :class="{
            'bottom-section--mobile-tab': mobileTabShell,
            'bottom-section--full': isFullBleedModule || mobileTabShell,
            'bottom-section--intro': isIntroModule,
          }"
        >
          <div
            class="section-card"
            :class="{
              'section-card--mobile-tab': mobileTabShell,
              'section-card--fullbleed': isFullBleedModule || mobileTabShell,
              'section-card--intro': isIntroModule,
              'section-card--motion': isMotionModule,
              'section-card--wall': isWallModule,
            }"
          >
            <router-view v-slot="{ Component, route: childRoute }">
              <KeepAlive v-if="isMobile" :max="6">
                <component :is="Component" v-if="Component" :key="mobileViewKey(childRoute)" />
              </KeepAlive>
              <Transition v-else name="module" mode="out-in" @after-leave="onAfterModuleLeave">
                <component :is="Component" v-if="Component" :key="childRoute.fullPath" />
              </Transition>
            </router-view>
          </div>
        </section>
      </div>
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
    --yx-mobile-nav: calc(62px + env(safe-area-inset-bottom, 0px));
    /* 底栏「牧院」圆形按钮上凸高度，固定底栏需额外让位 */
    --yx-mobile-nav-brand-bump: 18px;
  }
  .dashboard::after {
    display: none;
  }
  .main { margin-left: 0; padding: 8px 14px calc(68px + env(safe-area-inset-bottom, 0px)); gap: 10px; transition: none }
  .main--intro {
    padding: 0 8px calc(68px + env(safe-area-inset-bottom, 0px));
    gap: 0;
  }
  .main--fullbleed {
    padding: 4px 8px calc(62px + env(safe-area-inset-bottom, 0px));
    gap: 0;
  }
  .main--fullbleed.main--wall {
    padding: 0 0 var(--yx-mobile-nav);
    gap: 0;
  }
  .profile-section { flex: 0 0 auto }
  .bottom-section { flex: 1; min-height: 0; transition: none }

  /* 底栏五 Tab：统一外壳 padding，布局类（intro/wall/fullbleed）仍生效以撑满高度 */
  .main--mobile-tab-shell {
    padding: 0 0 var(--yx-mobile-nav);
    gap: 0;
    height: calc(var(--vh, 1vh) * 100);
    max-height: calc(var(--vh, 1vh) * 100);
    overflow: hidden;
  }

  .main--mobile-tab-shell.main--intro,
  .main--mobile-tab-shell.main--fullbleed,
  .main--mobile-tab-shell.main--wall {
    padding: 0 0 var(--yx-mobile-nav);
    gap: 0;
  }

  .mobile-tab-body {
    display: flex;
    flex-direction: column;
    flex: 1 1 0;
    min-height: 0;
  }

  .main--mobile-tab-shell .mobile-tab-body {
    overflow-x: hidden;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }

  .main--mobile-tab-shell .mobile-tab-body--profile {
    background: #f3ede3;
  }

  .main--mobile-tab-shell .mobile-tab-body--profile .profile-section {
    padding: 4px 6px 0;
    flex: 0 0 auto;
    background: transparent;
  }

  .main--mobile-tab-shell .mobile-tab-body--profile :deep(.card) {
    border-radius: 10px 10px 0 0;
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 8px;
  }

  .main--mobile-tab-shell .bottom-section--mobile-tab,
  .main--mobile-tab-shell .bottom-section--full,
  .main--mobile-tab-shell .bottom-section--intro {
    flex: 0 0 auto;
    min-height: auto;
    display: flex;
    flex-direction: column;
    padding: 0;
  }

  .main--mobile-tab-shell .mobile-tab-body--profile .bottom-section--mobile-tab,
  .main--mobile-tab-shell .mobile-tab-body--profile .bottom-section--full {
    padding: 0 6px;
    background: transparent;
  }

  .main--mobile-tab-shell .section-card--mobile-tab:not(.section-card--intro):not(.section-card--wall),
  .main--mobile-tab-shell .section-card--fullbleed:not(.section-card--intro):not(.section-card--wall) {
    flex: 0 0 auto;
    min-height: auto;
    height: auto;
    overflow: visible;
    padding: 10px 10px 14px;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: #fff;
  }

  .main--mobile-tab-shell .mobile-tab-body--profile .section-card--mobile-tab:not(.section-card--intro):not(.section-card--wall),
  .main--mobile-tab-shell .mobile-tab-body--profile .section-card--fullbleed:not(.section-card--intro):not(.section-card--wall) {
    border: 1px solid #ebe4d8;
    border-top: 1px solid #f2ebe0;
    border-radius: 0 0 10px 10px;
  }

  .main--mobile-tab-shell .section-card--mobile-tab:not(.section-card--intro):not(.section-card--wall) > *,
  .main--mobile-tab-shell .section-card--fullbleed:not(.section-card--intro):not(.section-card--wall) > * {
    flex: 0 1 auto;
    min-height: auto;
    display: block;
    width: 100%;
  }

  /* 牧院：与新生说/首页一致，由 mobile-tab-body 整页纵向滚动 */
  .main--mobile-tab-shell .section-card--intro {
    flex: 0 0 auto;
    min-height: auto;
    height: auto;
    width: 100%;
    display: block;
    padding: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: #fff;
    overflow: visible;
  }

  .main--mobile-tab-shell .section-card--mobile-tab.section-card--wall {
    flex: 0 0 auto;
    min-height: auto;
    height: auto;
    overflow: visible;
    padding: 0;
    background: #fffaf6;
  }

  .main--mobile-tab-shell .section-card--intro > * {
    flex: 0 1 auto;
    min-height: auto;
    display: block;
    width: 100%;
  }

  /* 新生说：:deep 确保生产构建下 .wall 纵向堆叠，不被 fullbleed 内滚规则压扁 */
  .main--mobile-tab-shell .section-card--wall :deep(.wall) {
    display: flex;
    flex-direction: column;
    flex: 0 0 auto;
    min-height: auto;
    height: auto;
    width: 100%;
  }

  /* 认识牧院贴边顶栏（父级已无 horizontal padding） */
  .main--mobile-tab-shell .section-card--intro :deep(.intro-choreo .intro-head--sticky) {
    --intro-sticky-bleed: 0;
    margin-inline: 0;
    width: 100%;
    padding-inline: 12px;
  }

  @media (max-width: 480px) {
    .main--mobile-tab-shell .mobile-tab-body--profile .profile-section {
      padding: 3px 4px 0;
    }

    .main--mobile-tab-shell .mobile-tab-body--profile .bottom-section--mobile-tab,
    .main--mobile-tab-shell .mobile-tab-body--profile .bottom-section--full {
      padding: 0 4px;
    }

    .main--mobile-tab-shell .mobile-tab-body--profile :deep(.card) {
      border-radius: 8px 8px 0 0;
    }

    .main--mobile-tab-shell .mobile-tab-body--profile .section-card--mobile-tab:not(.section-card--intro):not(.section-card--wall),
    .main--mobile-tab-shell .mobile-tab-body--profile .section-card--fullbleed:not(.section-card--intro):not(.section-card--wall) {
      border-radius: 0 0 8px 8px;
      padding: 8px 8px 12px;
    }
  }
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

.mobile-tab-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

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
  overflow-x: hidden;
  overflow-y: auto;
}

/* 认识牧院：PC 整页滚动；移动端顶栏固定、intro-body 内滚动 */
@media (min-width: 769px) {
  .section-card--intro {
    height: auto;
    overflow-y: visible;
  }
}

@media (max-width: 768px) {
  /* 非底栏 Tab 壳（旧布局）：顶栏固定、intro-body 内滚动 */
  .main--intro:not(.main--mobile-tab-shell) {
    height: calc(var(--vh, 1vh) * 100);
    max-height: calc(var(--vh, 1vh) * 100);
    overflow: hidden;
  }

  .main--intro:not(.main--mobile-tab-shell) .bottom-section--intro {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .main--intro:not(.main--mobile-tab-shell) .section-card--intro {
    flex: 1;
    min-height: 0;
    height: auto;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    overscroll-behavior: none;
    isolation: auto;
  }

  /* 底栏 Tab 壳：覆盖上方 intro 内滚动规则，整页交给 mobile-tab-body */
  .main--mobile-tab-shell.main--intro .section-card--intro {
    flex: 0 0 auto;
    min-height: auto;
    overflow: visible;
    display: block;
  }

  .main--mobile-tab-shell.main--intro .section-card--intro > * {
    flex: 0 1 auto;
    min-height: auto;
    display: block;
  }
}

@media(max-width:768px){
  .section-card:not(.section-card--mobile-tab):not(.section-card--fullbleed):not(.section-card--intro):not(.section-card--wall) {
    border-radius: 12px;
    padding: 14px;
  }
}
@media (max-width: 768px) {
  .section-card--wall,
  .section-card--fullbleed.section-card--wall {
    padding: 0;
    border-radius: 0;
  }
}
@media (max-width: 768px) {
  .main--mobile-tab-shell .section-card--intro {
    overflow: visible;
  }

  .main--mobile-tab-shell .section-card--intro > * {
    flex: 0 1 auto;
    min-height: auto;
    display: block;
    flex-direction: unset;
  }

  .section-card--intro:not(.section-card--mobile-tab) {
    padding: 0;
    border-radius: 0;
    border-left: 0;
    border-right: 0;
    border-top: 0;
    overflow: hidden;
  }

  /* Transition 根节点与 intro 页同高，滚动交给 intro-body */
  .section-card--intro:not(.section-card--mobile-tab) > * {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
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
  /* 仅旧布局（非底栏 Tab 壳）使用 fullbleed 内滚；Tab 壳由 mobile-tab-body 整页滚动 */
  .main--fullbleed:not(.main--mobile-tab-shell) {
    height: calc(var(--vh, 1vh) * 100);
    max-height: calc(var(--vh, 1vh) * 100);
    overflow: hidden;
  }

  .main--mobile-tab-shell.main--fullbleed {
    overflow: hidden;
  }

  .main--fullbleed:not(.main--mobile-tab-shell) .bottom-section--full {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .main--fullbleed:not(.main--mobile-tab-shell) .section-card--fullbleed {
    flex: 1;
    min-height: 0;
    height: auto;
    overflow-y: auto;
    overflow-x: hidden;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }

  .main--mobile-tab-shell .bottom-section--full {
    flex: 0 0 auto;
    min-height: auto;
  }

  .main--mobile-tab-shell .section-card--fullbleed {
    flex: 0 0 auto;
    min-height: auto;
    height: auto;
    overflow: visible;
  }

  .main--mobile-tab-shell .section-card--fullbleed.section-card--wall {
    display: block;
    overflow: visible;
  }

  .main--mobile-tab-shell .section-card--fullbleed :deep(.club-detail .cd-main) {
    padding-bottom: calc(14px + var(--yx-mobile-nav, calc(62px + env(safe-area-inset-bottom, 0px))));
  }
}
@media(max-width:480px){
  .section-card:not(.section-card--mobile-tab):not(.section-card--fullbleed):not(.section-card--intro):not(.section-card--wall) {
    border-radius: 10px;
    padding: 14px 12px;
  }
}
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
  .main:not(.main--mobile-tab-shell){padding:12px 12px calc(68px + env(safe-area-inset-bottom, 0px));gap:12px}
}

@media (max-width: 768px) {
  .main--mobile-tab-shell .mobile-tab-body {
    display: flex;
    flex-direction: column;
    min-height: 0;
    flex: 1 1 0;
  }

  .main:not(.main--mobile-tab-shell):not(.main--fullbleed) .bottom-section {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .main:not(.main--mobile-tab-shell):not(.main--fullbleed) .section-card {
    flex: 1;
    min-height: 0;
    height: auto;
  }

  .main--mobile-tab-shell .mobile-tab-body {
    touch-action: pan-y pinch-zoom;
  }

  .dashboard { touch-action: manipulation; }
}
</style>
