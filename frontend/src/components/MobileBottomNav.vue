<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const emit = defineEmits<{
  navigate: [key: string]
  openMenu: []
}>()

const route = useRoute()

const tabs = [
  { key: 'home', label: '首页', aria: '首页' },
  { key: 'faq', label: '答疑', aria: '问题答疑' },
  { key: 'intro', label: '介绍', aria: '认识牧院' },
  { key: 'menu', label: '菜单', aria: '打开菜单' },
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
  <nav class="bottom-nav" aria-label="主导航">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="bottom-nav__tab"
      :class="{ 'bottom-nav__tab--active': activeKey === tab.key }"
      :aria-label="tab.aria"
      :aria-current="activeKey === tab.key ? 'page' : undefined"
      @click="onClick(tab.key)"
    >
      <span class="bottom-nav__icon" aria-hidden="true">
        <svg
          v-if="tab.key === 'home'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M4.5 10.2 12 4l7.5 6.2V20a1.5 1.5 0 0 1-1.5 1.5H6a1.5 1.5 0 0 1-1.5-1.5v-9.8Z" />
          <path d="M9.5 21.5V13h5v8.5" />
        </svg>
        <svg
          v-else-if="tab.key === 'faq'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <path d="M8 10h.01" />
          <path d="M12 10h4" />
          <path d="M8 14h8" />
        </svg>
        <svg
          v-else-if="tab.key === 'intro'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M4 21V8.5L12 4l8 4.5V21" />
          <path d="M4 21h16" />
          <path d="M9 21v-5h6v5" />
          <path d="M9.5 10h5" />
          <path d="M9.5 13.5h5" />
        </svg>
        <svg
          v-else
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <rect x="4" y="4" width="6.5" height="6.5" rx="1.5" />
          <rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5" />
          <rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5" />
          <rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5" />
        </svg>
      </span>
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
    justify-content: space-around;
    gap: 4px;
    padding: 6px 10px calc(6px + env(safe-area-inset-bottom, 0px));
    background: rgba(255, 252, 249, 0.94);
    border-top: 1px solid rgba(181, 52, 58, 0.08);
    box-shadow: 0 -8px 28px rgba(44, 35, 47, 0.07);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
  }

  .bottom-nav__tab {
    display: flex;
    flex: 1;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    min-width: 0;
    max-width: 88px;
    min-height: 50px;
    padding: 2px 4px;
    border: none;
    background: transparent;
    color: #9a8b7a;
    cursor: pointer;
    font-family: inherit;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
    transition: color 0.18s ease;
  }

  .bottom-nav__tab:active {
    transform: scale(0.97);
  }

  .bottom-nav__icon {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    border-radius: 11px;
    color: inherit;
    transition:
      background 0.18s ease,
      color 0.18s ease,
      transform 0.18s ease;
  }

  .bottom-nav__tab--active {
    color: #b5343a;
  }

  .bottom-nav__tab--active .bottom-nav__icon {
    background: rgba(181, 52, 58, 0.12);
    color: #b5343a;
  }

  .bottom-nav__label {
    font-size: 0.6875rem;
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }
}
</style>
