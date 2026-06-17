<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBreakpoint } from '../composables/useBreakpoint'

const router = useRouter()
const loading = ref(true)
const { isMobile } = useBreakpoint()

const galleryImages = [
  { src: '/campus/track-field-new-8BPgcsJr.jpg', label: '田径场' },
  { src: '/campus/basketball-court-BbXm4vee.jpg', label: '篮球场' },
  { src: '/campus/tennis-court-DqtrJ6oM.jpg', label: '网球场' },
  { src: '/campus/volleyball-court-Bxf0g7_t.jpg', label: '排球场' },
]

function onIframeLoad() {
  loading.value = false
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') router.push('/')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="campus-view">
    <header class="campus-topbar">
      <button class="back-btn" @click="router.push('/')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/>
        </svg>
        <span class="back-label">返回</span>
      </button>
      <span class="campus-title">校园导览 · 英才校区</span>
      <span v-if="!isMobile" class="campus-hint">ESC 返回</span>
    </header>

    <!-- 移动端：静态图集，避免 WebGL 卡顿 -->
    <div v-if="isMobile" class="campus-gallery">
      <p class="campus-gallery-tip">手机端展示校园实景图册；完整 3D 漫游请在电脑端打开。</p>
      <div class="campus-gallery-grid">
        <figure v-for="img in galleryImages" :key="img.src" class="campus-gallery-item">
          <img :src="img.src" :alt="img.label" loading="lazy" decoding="async" />
          <figcaption>{{ img.label }}</figcaption>
        </figure>
      </div>
    </div>

    <!-- 桌面端：3D iframe -->
    <template v-else>
      <Transition name="fade">
        <div v-if="loading" class="loading-overlay">
          <span class="loading-spinner" />
          <p>3D 校园加载中…</p>
        </div>
      </Transition>
      <iframe
        src="/campus/app.html"
        class="campus-iframe"
        title="校园 3D 漫游"
        allow="accelerometer; autoplay; clipboard-write; gyroscope"
        @load="onIframeLoad"
      />
    </template>
  </div>
</template>

<style scoped>
.campus-view {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: #1a1a2e;
  display: flex;
  flex-direction: column;
}

.campus-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: env(safe-area-inset-top, 0px) 12px 0;
  min-height: 48px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  color: #fff;
  z-index: 10;
  flex-shrink: 0;
  gap: 8px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 44px;
  min-width: 44px;
  padding: 0 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #fff;
  font-size: 0.82rem;
  cursor: pointer;
  flex-shrink: 0;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.2) }

.campus-title {
  flex: 1;
  font-size: 0.85rem;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.campus-hint {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
}

.loading-overlay {
  position: absolute;
  inset: 48px 0 0;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: #1a1a2e;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2.5px solid rgba(255, 255, 255, 0.15);
  border-top-color: #87ceeb;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg) } }

.fade-leave-active { transition: opacity 0.4s ease-out }
.fade-leave-to { opacity: 0 }

.campus-iframe {
  flex: 1;
  width: 100%;
  border: none;
}

.campus-gallery {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 12px 12px calc(16px + env(safe-area-inset-bottom, 0px));
  background: #fefcf9;
}

.campus-gallery-tip {
  margin: 0 0 12px;
  font-size: 0.8rem;
  color: #8b7b65;
  line-height: 1.5;
  text-align: center;
}

.campus-gallery-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.campus-gallery-item {
  margin: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
}

.campus-gallery-item img {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
  display: block;
}

.campus-gallery-item figcaption {
  padding: 8px;
  font-size: 0.78rem;
  color: #5c5040;
  text-align: center;
}

@media (max-width: 480px) {
  .back-label { display: none }
  .campus-title { font-size: 0.78rem }
}
</style>
