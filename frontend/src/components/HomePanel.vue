<script setup lang="ts">
import { computed, ref, inject, type Ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { MILESTONES, SERVICE_CARDS, REGISTER_DATE } from '../constants/timeline'
import { ICON_PATHS, TL_TO_PHOSPHOR } from '../constants/icons'
import ServiceIcons from './ServiceIcons.vue'

const router = useRouter()
const xinOpen = inject<Ref<boolean>>('xinOpen')
const isAuthenticated = inject<Ref<boolean>>('isAuthenticated', ref(false))
function openChat() { if (xinOpen) xinOpen.value = true }
function handleServiceClick(id: string) {
  if (id === 'ai') {
    if (!isAuthenticated.value) {
      window.alert('登录后可使用小信 AI 助手')
      return
    }
    openChat()
    return
  }
  if (id === 'map') { router.push('/campus').catch(() => {}); return }
  if (id === 'notice') { router.push('/guide'); return }
  if (id === 'tips') { router.push('/tips'); return }
  // 有外链的卡片 → 新标签页打开
  const card = SERVICE_CARDS.find(c => c.id === id)
  if (card?.link) { window.open(card.link, '_blank', 'noopener'); return }
}

function tlSvg(icon: string): string {
  const key = TL_TO_PHOSPHOR[icon]
  const p = key ? ICON_PATHS[key] : ''
  if (!p) return ''
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">${p}</svg>`
}

const today = new Date()
const todayStr = today.toISOString().slice(0, 10)
const registerDate = new Date(REGISTER_DATE)
const countdown = computed(() => Math.max(0, Math.round((registerDate.getTime() - today.getTime()) / 86400000)))

// 响应式节点宽度
const viewW = ref(900)
const NODE_W = ref(170)
function updateSizes() {
  const w = window.innerWidth
  if (w <= 480) NODE_W.value = 120
  else if (w <= 768) NODE_W.value = 140
  else NODE_W.value = 170
  viewW.value = scrollEl.value?.clientWidth ?? 900
}
onMounted(() => { updateSizes(); window.addEventListener('resize', updateSizes) })
onUnmounted(() => window.removeEventListener('resize', updateSizes))

// 已过百分比
const pastPct = computed(() => {
  if (nextIdx.value <= 0) return 10
  if (nextIdx.value >= MILESTONES.length) return 90
  return Math.round((nextIdx.value / MILESTONES.length) * 100)
})

const GAP_PX = 50
const totalW = computed(() => (MILESTONES.length - 1) * (NODE_W.value + GAP_PX))
const trackW = computed(() => (MILESTONES.length - 1) * (NODE_W.value + GAP_PX))
const trackTop = computed(() => {
  if (window.innerWidth <= 480) return 22  // dot 44px / 2
  if (window.innerWidth <= 768) return 26  // dot 52px / 2
  return 32  // dot 64px / 2
})
const trackLeft = computed(() => NODE_W.value / 2)
const scrollX = ref(0)
const scrollEl = ref<HTMLElement | null>(null)
const maxScroll = computed(() => Math.max(0, totalW.value - viewW.value))

function scrollLeft() {
  if (!scrollEl.value) return
  viewW.value = scrollEl.value.clientWidth
  clampedX.value = Math.max(0, clampedX.value - 400)
}
function scrollRight() {
  if (!scrollEl.value) return
  viewW.value = scrollEl.value.clientWidth
  clampedX.value = Math.min(maxScroll.value, clampedX.value + 400)
}
const clampedX = computed({
  get: () => Math.max(0, Math.min(maxScroll.value, scrollX.value)),
  set: (v: number) => { scrollX.value = Math.max(0, Math.min(maxScroll.value, v)) },
})

// 拖拽（document 级跟踪，避免手指滑出时间轴区域后中断）
const dragging = ref(false)
const dragStart = ref(0)
const dragStartX = ref(0)
let activePointerId: number | null = null
let captureEl: HTMLElement | null = null

function onPointerDown(e: PointerEvent) {
  e.preventDefault()
  dragging.value = true
  dragStart.value = e.clientX
  dragStartX.value = clampedX.value
  activePointerId = e.pointerId
  captureEl = e.currentTarget as HTMLElement
  captureEl.setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value || e.pointerId !== activePointerId) return
  clampedX.value = dragStartX.value - (e.clientX - dragStart.value)
}

function finishDrag(e: PointerEvent) {
  if (!dragging.value) return
  dragging.value = false
  activePointerId = null
  if (captureEl?.hasPointerCapture?.(e.pointerId)) {
    captureEl.releasePointerCapture(e.pointerId)
  }
  captureEl = null
}

onMounted(() => {
  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', finishDrag)
  document.addEventListener('pointercancel', finishDrag)
})

onUnmounted(() => {
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', finishDrag)
  document.removeEventListener('pointercancel', finishDrag)
})

function shortDate(d: string): string {
  return d.slice(5, 7).replace(/^0/, '') + '/' + d.slice(8, 10).replace(/^0/, '')
}

const nextIdx = computed(() => MILESTONES.findIndex(m => m.date >= todayStr))
function dayLabel(d: string, i: number): 'past' | 'today' | 'future' {
  if (d < todayStr) return 'past'
  if (i === nextIdx.value) return 'today'
  return 'future'
}
</script>

<template>
  <div class="home-panel">
    <!-- 顶部：标题 + 日历卡片 -->
    <div class="top-bar">
      <div class="top-left">
        <h3 class="section-title"><span class="title-icon">◆</span> 迎新流程</h3>
        <p class="tl-hint">按顺序完成，开始享受大学生活</p>
      </div>
      <div class="countdown-card">
        <span class="cd-label">距离报到</span>
        <span class="cd-days">{{ countdown }}</span>
        <span class="cd-unit">天</span>
      </div>
    </div>

    <!-- 时间轴 -->
    <section class="tl-section" :style="{ '--past-pct': pastPct + '%' }">
      <div
        ref="scrollEl"
        class="tl-scroll"
        :class="{ dragging }"
        @pointerdown.prevent="onPointerDown"
      >
        <div class="tl-nodes" :style="{ transform: `translateX(${-clampedX}px)`, width: totalW + 'px' }">
          <div class="tl-track" :style="{ width: trackW + 'px', top: trackTop + 'px', left: trackLeft + 'px' }" />
          <div
            v-for="(m, i) in MILESTONES"
            :key="m.id"
            class="tl-node"
            :class="`tl-node--${dayLabel(m.date, i)}`"
          >
            <!-- Phosphor 图标（有映射的） -->
            <div v-if="tlSvg(m.icon)" class="tl-dot" v-html="tlSvg(m.icon)" />
            <!-- 原生图标（无映射的，保持原样） -->
            <div v-else class="tl-dot">
              <svg class="tl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <template v-if="m.icon === 'flag'"><line x1="4" y1="22" x2="4" y2="2"/><path d="M4 5h16l-3 6 3 6H4"/></template>
                <template v-else-if="m.icon === 'edit'"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></template>
                <template v-else-if="m.icon === 'doc'"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></template>
                <template v-else-if="m.icon === 'letter'"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2 7 12 15 22 7"/></template>
                <template v-else-if="m.icon === 'check'"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></template>
                <template v-else-if="m.icon === 'star'"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></template>
                <template v-else><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></template>
              </svg>
            </div>
            <span class="tl-title">{{ m.title }}</span>
            <span class="tl-date">{{ shortDate(m.date) }}</span>
          </div>
        </div>
      </div>
      <button class="tl-arrow tl-arrow--left" @click="scrollLeft">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <button class="tl-arrow tl-arrow--right" @click="scrollRight">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M9 18l6-6-6-6"/></svg>
      </button>
    </section>

    <!-- 功能入口 -->
    <section class="service-section">
      <h3 class="section-title"><span class="title-icon">◆</span> 常用服务</h3>
      <div class="service-grid">
        <div v-for="card in SERVICE_CARDS" :key="card.id" class="svc-card" @click="handleServiceClick(card.id)">
          <ServiceIcons :name="card.icon" class="svc-icon" />
          <div class="svc-text">
            <h4 class="svc-title">{{ card.title }}</h4>
            <p class="svc-desc">{{ card.desc }}</p>
          </div>
          <span class="svc-link">进入 →</span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-panel { padding: 4px 0 8px; display: flex; flex-direction: column; gap: 16px }

/* ===== 顶部：标题 + 日历卡片 ===== */
.top-bar {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: 20px; flex-wrap: wrap;
}
.top-left { display: flex; flex-direction: column; gap: 2px }
.cd-label { font-size: .78rem; color: #a09888; letter-spacing: .04em }
.cd-days {
  font-size: 2.4rem; font-weight: 700; color: #b5343a;
  font-family: 'Georgia', 'Noto Serif SC', serif; line-height: 1;
}
.cd-unit { font-size: .82rem; color: #b5343a; margin-left: 4px; font-weight: 500 }
.countdown-card {
  display: flex; align-items: baseline; gap: 4px;
  padding: 10px 20px 8px; border-radius: 12px;
  background: linear-gradient(135deg, #fef7f7 0%, #fdf0f0 100%);
  border: 1px solid rgba(181,52,58,.1);
}

/* ===== 标题通用 ===== */
.section-title {
  font-size: .92rem; font-weight: 600; color: #2c2c2c; letter-spacing: .06em;
  margin: 0; display: flex; align-items: center; gap: 8px;
}
.title-icon { color: #b5343a; font-size: .52rem }

/* ===== 时间轴 ===== */
.tl-section {
  position: relative; padding: 8px 12px 8px 56px;
}
.tl-track {
  position: absolute; top: 32px; left: 32px; height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg,
    #4caf50 0%, #4caf50 var(--past-pct, 20%),
    #e5dbcc var(--past-pct, 20%), #e5dbcc 100%);
}
.tl-scroll {
  overflow: hidden; cursor: grab; user-select: none;
  margin-right: 44px; touch-action: none;
}
.tl-scroll.dragging { cursor: grabbing }
.tl-nodes {
  display: flex; justify-content: flex-start; gap: 50px;
  position: relative; z-index: 1;
  transition: transform .1s linear;
}
.tl-nodes.dragging { transition: none }

/* 箭头 */
.tl-arrow {
  position: absolute; top: 8px; z-index: 5;
  width: 36px; height: 36px; border-radius: 50%;
  border: 1.5px solid #e5dbcc; background: #fff;
  color: #8b7b65; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: border-color .2s, color .2s, box-shadow .2s;
}
.tl-arrow:hover { border-color: #b5343a; color: #b5343a; box-shadow: 0 0 0 4px rgba(181,52,58,.05) }
.tl-arrow--left { left: 4px }
.tl-arrow--right { right: 4px }
.tl-arrow { top: 22px }

.tl-node {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; flex: 0 0 auto; width: v-bind(NODE_W + 'px');
}

.tl-dot {
  width: 64px; height: 64px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 10px; position: relative; z-index: 2;
}
.tl-node--past .tl-dot {
  background: #4caf50; color: #fff;
  box-shadow: 0 0 0 9px rgba(76,175,80,.1);
}
.tl-node--today .tl-dot {
  background: #b5343a; color: #fff;
  box-shadow: 0 0 0 13px rgba(181,52,58,.1);
  animation: todayPulse 2s ease-in-out infinite;
}
@keyframes todayPulse {
  0%, 100% { box-shadow: 0 0 0 9px rgba(181,52,58,.08) }
  50% { box-shadow: 0 0 0 18px rgba(181,52,58,.04) }
}
.tl-node--future .tl-dot {
  background: #f2ebe0; color: #d4c8b0;
  box-shadow: 0 0 0 7px rgba(0,0,0,.02);
}
.tl-icon { width: 30px; height: 30px }
.tl-dot :deep(svg) {
  width: 30px; height: 30px;
  fill: currentColor;
}

.tl-title {
  font-size: .72rem; font-weight: 600; color: #3c3028;
  letter-spacing: .03em; margin-bottom: 1px; white-space: nowrap;
}
.tl-node--past .tl-title { color: #8b7b65 }
.tl-node--future .tl-title { color: #b0a090 }
.tl-date {
  font-size: .58rem; color: #c4b8a8;
}

.tl-hint {
  font-size: .74rem; color: #c4b8a8; letter-spacing: .03em; margin: 0;
}

/* ===== 功能入口 ===== */
.service-section { margin-top: 4px }

.service-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px;
}
.svc-card {
  border-radius: 18px; padding: 28px 22px;
  background: #fff;
  border: 1px solid #f0ebe4;
  box-shadow: 0 1px 3px rgba(0,0,0,.02), 0 4px 16px rgba(0,0,0,.03);
  display: flex; align-items: center; gap: 18px;
  cursor: pointer; min-height: 110px;
  transition: transform .25s cubic-bezier(.33,1,.68,1), box-shadow .25s, border-color .25s;
}
.svc-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(181,52,58,.08), 0 8px 24px rgba(0,0,0,.04);
  border-color: rgba(181,52,58,.2);
}
.svc-icon { width: 56px; height: 56px; transition: transform .25s; flex-shrink: 0 }
.svc-icon :deep(svg) { width: 100%; height: 100% }
.svc-card:hover .svc-icon { transform: scale(1.1) }
.svc-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 5px }
.svc-title {
  font-size: 1rem; font-weight: 700; color: #3c3028;
}
.svc-desc {
  font-size: .78rem; color: #b0a090; line-height: 1.45;
}
.svc-link {
  font-size: .8rem; color: #b5343a; font-weight: 600; flex-shrink: 0;
  transition: color .2s; white-space: nowrap;
}
.svc-card:hover .svc-link { color: #7a1f23 }

/* 交错入场 */
.svc-card {
  animation: cardIn .5s cubic-bezier(.16,1,.3,1) both;
}
.svc-card:nth-child(1) { animation-delay: .04s }
.svc-card:nth-child(2) { animation-delay: .08s }
.svc-card:nth-child(3) { animation-delay: .12s }
.svc-card:nth-child(4) { animation-delay: .16s }
.svc-card:nth-child(5) { animation-delay: .20s }
.svc-card:nth-child(6) { animation-delay: .24s }
.svc-card:nth-child(7) { animation-delay: .28s }
.svc-card:nth-child(8) { animation-delay: .32s }
@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px) }
  to { opacity: 1; transform: translateY(0) }
}

/* ===== 响应式 ===== */
@media(max-width: 1024px) {
  .service-grid { grid-template-columns: repeat(2, 1fr) }
}
@media(max-width: 768px) {
  .home-panel { padding: 4px 0 0; gap: 16px }
  .top-bar { position: relative; flex-direction: column; align-items: flex-start; padding-right: 0 }
  .tl-section { padding: 0 44px }
  .tl-scroll { margin-right: 0; padding-top: 20px; padding-bottom: 4px }
  .tl-nodes { gap: 32px }
  .tl-node { width: 140px }
  .tl-dot { width: 52px; height: 52px; margin-bottom: 8px }
  .tl-dot :deep(svg), .tl-icon { width: 26px; height: 26px }
  .tl-title { font-size: .66rem }
  .tl-date { font-size: .54rem }
  .tl-arrow { width: 34px; height: 34px; top: 29px }
  .tl-arrow--left { left: 6px }
  .tl-arrow--right { right: 6px }
  .countdown-card {
    position: absolute; top: 4px; right: 0;
    padding: 6px 14px 4px; border-radius: 10px;
  }
  .cd-days { font-size: 1.8rem }
  .cd-label { font-size: .7rem }
  .cd-unit { font-size: .72rem }
}
@media(max-width: 480px) {
  .tl-section { padding: 0 40px }
  .tl-scroll { padding-top: 14px; padding-bottom: 2px }
  .tl-nodes { gap: 24px }
  .tl-node { width: 120px }
  .tl-dot { width: 44px; height: 44px; margin-bottom: 6px }
  .tl-dot :deep(svg), .tl-icon { width: 22px; height: 22px }
  .tl-title { font-size: .62rem }
  .tl-arrow { width: 30px; height: 30px; top: 21px }
  .service-grid { grid-template-columns: repeat(2, 1fr); gap: 10px }
  .svc-card { padding: 16px 12px; gap: 12px; border-radius: 12px }
  .svc-icon { width: 36px; height: 36px }
  .svc-title { font-size: .8rem }
  .svc-desc { font-size: .7rem }
  .svc-link { font-size: .7rem }
  .tl-node--today .tl-dot { animation: none } /* 移动端关闭脉冲动画 */
}
</style>
