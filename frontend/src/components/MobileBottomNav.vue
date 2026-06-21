<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const emit = defineEmits<{
  navigate: [key: string]
  openMenu: []
}>()

const route = useRoute()

const tabs = [
  { key: 'home', label: '首页' },
  { key: 'faq', label: '答疑' },
  { key: 'intro', label: '介绍' },
  { key: 'menu', label: '菜单' },
] as const

const activeKey = computed(() => {
  if (route.path.startsWith('/intro')) return 'intro'
  if (route.path === '/') return 'home'
  if (route.path.startsWith('/faq')) return 'faq'
  return ''
})

function onClick(key: string) {
  if (key === 'menu') {
    emit('openMenu')
    return
  }
  if (key !== activeKey.value) {
    emit('navigate', key)
  }
}
</script>

<template>
  <nav class="bottom-nav">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="bottom-nav__tab"
      :class="{ 'bottom-nav__tab--active': activeKey === tab.key }"
      @click="onClick(tab.key)"
    >
      <svg v-if="tab.key === 'home'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <svg v-else-if="tab.key === 'faq'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <svg v-else-if="tab.key === 'intro'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="4" y="2" width="16" height="20" rx="2"/>
        <path d="M9 22v-4h6v4"/>
        <path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/>
        <path d="M12 10h.01"/><path d="M12 14h.01"/>
        <path d="M16 10h.01"/><path d="M16 14h.01"/>
        <path d="M8 10h.01"/><path d="M8 14h.01"/>
      </svg>
      <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
      <span class="bottom-nav__label">{{ tab.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav { display: none }

@media (max-width: 768px) {
  .bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 8000;
    background: rgba(255, 255, 255, 0.98);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.04);
    padding: 4px 0 calc(4px + env(safe-area-inset-bottom, 0px));
    justify-content: space-around;
  }

  .bottom-nav__tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    flex: 1;
    min-height: 48px;
    max-width: 88px;
    padding: 4px 6px;
    border: none;
    background: transparent;
    color: #b0a090;
    cursor: pointer;
    font-family: inherit;
    transition: color 0.2s;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  .bottom-nav__tab--active {
    color: #b5343a;
  }

  .bottom-nav__label {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }
}
</style>
