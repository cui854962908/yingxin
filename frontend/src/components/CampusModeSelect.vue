<script setup lang="ts">
import { useRouter } from 'vue-router'
import { CAMPUS_3D_TRIAL_LABEL, CAMPUS_3D_TRIAL_NOTE } from '../constants/product'

const router = useRouter()

function enterCampus(path: '/campus/2d' | '/campus/3d') {
  router.push(path).catch(() => {})
}
</script>

<template>
  <main class="mode-page">
    <header class="mode-header">
      <button class="back-button" type="button" @click="router.push('/')">返回首页</button>
      <div>
        <p>河南牧业经济学院 · 英才校区</p>
        <h1>选择校园导览方式</h1>
        <p class="mode-subtitle">可按习惯任选 2D 地图或 3D 漫游</p>
      </div>
    </header>

    <section class="mode-grid" aria-label="校园导览方式">
      <button class="mode-card mode-card--map" type="button" @click="enterCampus('/campus/2d')">
        <span class="mode-visual">
          <svg viewBox="0 0 280 180" aria-hidden="true">
            <path d="M16 36 86 12l70 24 108-26v136l-108 26-70-24-70 24Z" fill="#f5f0e8" stroke="#b5343a" stroke-width="3"/>
            <path d="M86 12v136m70-112v136M16 76l70-22 70 26 108-30M16 124l70-24 70 24 108-28" fill="none" stroke="#d8b9a3" stroke-width="3"/>
            <path d="m53 54 26-8 23 9-6 24-35 7Z" fill="#9cc99f"/>
            <path d="m176 57 47-12 18 8-8 34-54 11Z" fill="#9bcbd1"/>
            <circle cx="135" cy="102" r="14" fill="#b5343a"/>
            <path d="M135 121c-18-20-20-30-20-37a20 20 0 1 1 40 0c0 7-2 17-20 37Z" fill="#b5343a"/>
            <circle cx="135" cy="84" r="7" fill="#fff"/>
          </svg>
        </span>
        <span class="mode-copy mode-copy--plain">
          <span class="mode-number">01</span>
          <strong>2D 校园地图</strong>
          <small>真实高德底图 · 地点检索 · 校内路线规划</small>
          <span class="mode-action">进入 2D 地图</span>
        </span>
      </button>

      <button class="mode-card mode-card--scene" type="button" @click="enterCampus('/campus/3d')">
        <span class="mode-visual mode-visual--scene">
          <img src="/campus-2d/yingcai-official-plan.jpg" alt="" />
        </span>
        <span class="mode-copy">
          <span class="mode-number">02</span>
          <strong>3D 校园漫游</strong>
          <span class="mode-badge mode-badge--trial">{{ CAMPUS_3D_TRIAL_LABEL }}</span>
          <small>沉浸式场景 · 自由移动 · 建筑互动</small>
          <span class="mode-trial-note">{{ CAMPUS_3D_TRIAL_NOTE }}</span>
          <span class="mode-action">进入 3D 漫游</span>
        </span>
      </button>
    </section>
  </main>
</template>

<style scoped>
.mode-page {
  min-height: 100vh;
  padding: clamp(24px, 5vw, 72px);
  color: #2f2926;
  background:
    linear-gradient(rgba(181, 52, 58, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(181, 52, 58, .045) 1px, transparent 1px),
    #fff;
  background-size: 48px 48px;
}
.mode-header {
  max-width: 1180px;
  margin: 0 auto clamp(32px, 7vh, 72px);
  display: grid;
  grid-template-columns: 160px 1fr;
  align-items: end;
  border-bottom: 1px solid #d7cec7;
  padding-bottom: 24px;
}
.mode-header p { margin: 0 0 8px; color: #897c74; font-size: 14px; letter-spacing: .08em }
.mode-header h1 { margin: 0; font-size: clamp(32px, 5vw, 64px); line-height: 1; letter-spacing: -.04em }
.mode-subtitle { margin: 12px 0 0; color: #897c74; font-size: 15px; letter-spacing: 0 }
.back-button {
  justify-self: start; border: 0; padding: 0; color: #b5343a; background: transparent;
  font: inherit; font-weight: 650; cursor: pointer;
}
.mode-grid {
  max-width: 1180px; margin: 0 auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: clamp(20px, 3vw, 38px);
}
.mode-card {
  min-height: 500px; padding: 0; border: 1px solid #d7cec7; border-radius: 0;
  background: #fff; text-align: left; cursor: pointer; overflow: hidden;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
.mode-card:hover { transform: translateY(-8px); border-color: #b5343a; box-shadow: 14px 14px 0 rgba(181, 52, 58, .12) }
.mode-visual { height: 300px; display: grid; place-items: center; background: #f6f3ef; overflow: hidden }
.mode-visual svg { width: 72%; max-height: 78% }
.mode-visual img { width: 100%; height: 100%; object-fit: cover }
.mode-visual--scene { background: #2f2926 }
.mode-copy {
  display: grid; grid-template-columns: 52px 1fr auto; padding: 28px;
  gap: 8px 16px; align-items: baseline;
}
.mode-copy--plain { grid-template-columns: 52px 1fr }
.mode-number { grid-row: 1 / 6; color: #b5343a; font-size: 13px; font-weight: 750 }
.mode-copy strong { grid-column: 2; font-size: 27px }
.mode-badge {
  grid-column: 3; align-self: center; padding: 4px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 700; letter-spacing: .04em; white-space: nowrap;
}
.mode-badge--trial { color: #6b5a2e; background: #f6efd8; border: 1px solid #e6d7a8 }
.mode-copy--plain small,
.mode-copy small { grid-column: 2 / 4; color: #897c74; font-size: 14px }
.mode-copy--plain small { grid-column: 2 }
.mode-trial-note { grid-column: 2 / 4; color: #a08a5c; font-size: 12px; line-height: 1.5 }
.mode-copy--plain .mode-action,
.mode-action { grid-column: 2 / 4; margin-top: 10px; color: #b5343a; font-weight: 700; font-size: 14px }
.mode-copy--plain .mode-action { grid-column: 2 }
@media (max-width: 760px) {
  .mode-page { padding: 18px 14px 28px }
  .mode-header { grid-template-columns: 1fr; gap: 28px; margin-bottom: 24px }
  .mode-grid { grid-template-columns: 1fr }
  .mode-card { min-height: 390px }
  .mode-visual { height: 220px }
}
</style>
