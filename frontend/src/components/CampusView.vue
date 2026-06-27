<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useAppNavigate } from '../composables/useAppNavigate'
import { CAMPUS_3D_TRIAL_LABEL } from '../constants/product'

const { appGoBackTo } = useAppNavigate()
const loading = ref(true)

function onIframeLoad() {
  loading.value = false
}

function goBack() {
  appGoBackTo('/')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') goBack()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="campus-view">
    <header class="campus-topbar">
      <button class="back-btn" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/>
        </svg>
        <span class="back-label">返回首页</span>
      </button>
      <span class="campus-title">
        校园导览 · 英才校区
        <span class="campus-trial">{{ CAMPUS_3D_TRIAL_LABEL }}</span>
      </span>
      <span class="campus-hint" aria-hidden="true" />
    </header>

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
      allow="accelerometer; autoplay; clipboard-write; gyroscope; xr-spatial-tracking"
      @load="onIframeLoad"
    />
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 0;
}

.campus-trial {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(246, 239, 216, 0.16);
  border: 1px solid rgba(230, 215, 168, 0.45);
  color: #f6efd8;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.campus-hint {
  width: 88px;
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
  min-height: 0;
  border: none;
}

@media (max-width: 768px) {
  .loading-overlay { inset: calc(48px + env(safe-area-inset-top, 0px)) 0 0; }
}

@media (max-width: 480px) {
  .back-label { display: none }
  .campus-title { font-size: 0.78rem }
}
</style>
