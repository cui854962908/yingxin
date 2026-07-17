<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const emit = defineEmits<{
  navigate: [key: string]
}>()

const route = useRoute()

const tabs = [
  { key: 'home', label: '首页', aria: '首页' },
  { key: 'wall', label: '新生说', aria: '牧院新生说' },
  { key: 'intro', label: '牧院', aria: '认识牧院' },
  { key: 'announcements', label: '公告', aria: '校园公告' },
  { key: 'faq', label: '答疑', aria: '问题答疑' },
] as const

const activeKey = computed(() => {
  if (route.path.startsWith('/intro')) return 'intro'
  if (route.path === '/') return 'home'
  if (route.path.startsWith('/announcements')) return 'announcements'
  if (route.path.startsWith('/faq')) return 'faq'
  if (route.path.startsWith('/wall')) return 'wall'
  return ''
})

function onClick(key: string) {
  if (key === activeKey.value) return
  emit('navigate', key)
}
</script>

<template>
  <nav class="bottom-nav" aria-label="主导航">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="bottom-nav__tab"
      :class="{
        'bottom-nav__tab--active': activeKey === tab.key,
        'bottom-nav__tab--brand': tab.key === 'intro',
      }"
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
          v-else-if="tab.key === 'announcements'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M4 13.5V9.8a2 2 0 0 1 2-2h3l8-3.3v14.3l-8-3.3H6a2 2 0 0 1-2-2Z" />
          <path d="M9 15.5 10.5 21H7l-1-5.5M20 8v7" />
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
          v-else-if="tab.key === 'wall'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M5 4.5h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H10l-5 3v-3H5a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2Z" />
          <path d="M7.5 9h9M7.5 13h6" />
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
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 8000;
    gap: 0;
    padding: 6px 4px calc(6px + env(safe-area-inset-bottom, 0px));
    background: rgba(255, 255, 255, 0.96);
    border-top: 1px solid #dedee3;
    box-shadow: 0 -6px 22px rgba(21, 21, 26, 0.07);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
  }

  .bottom-nav__tab {
    position: relative;
    display: flex;
    flex: 1;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    min-width: 0;
    min-height: 50px;
    padding: 2px;
    border: none;
    background: transparent;
    color: #9a8b7a;
    cursor: pointer;
    font-family: inherit;
    -webkit-tap-highlight-color: transparent;
    -webkit-appearance: none;
    appearance: none;
    outline: none;
    user-select: none;
    transition: color 0.18s ease, transform 0.18s ease;
  }

  .bottom-nav__tab:focus,
  .bottom-nav__tab:focus-visible,
  .bottom-nav__tab:active {
    outline: none !important;
    box-shadow: none;
  }

  .bottom-nav__tab::before {
    content: '';
    position: absolute;
    top: -6px;
    left: 50%;
    width: 18px;
    height: 3px;
    border-radius: 0 0 3px 3px;
    background: #b5343a;
    opacity: 0;
    transform: translateX(-50%) scaleX(0.4);
    transition: opacity 0.18s ease, transform 0.18s ease;
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

  .bottom-nav__tab--active::before {
    opacity: 1;
    transform: translateX(-50%) scaleX(1);
  }

  .bottom-nav__tab--active .bottom-nav__icon {
    background: rgba(181, 52, 58, 0.12);
    color: #b5343a;
  }

  .bottom-nav__tab--brand {
    z-index: 1;
    transform: translateY(-9px);
    color: #7e1820;
  }

  .bottom-nav__tab--brand::before { display: none; }

  .bottom-nav__tab--brand:active { transform: translateY(-8px) scale(.96); }

  .bottom-nav__tab--brand .bottom-nav__icon {
    width: 46px;
    height: 46px;
    border: 4px solid rgba(255, 255, 255, .98);
    border-radius: 50%;
    color: #fff8ef;
    background: linear-gradient(145deg, #b72b36, #75121b);
    box-shadow: 0 7px 18px rgba(117, 18, 27, .28);
  }

  .bottom-nav__tab--brand .bottom-nav__icon svg { width: 23px; height: 23px; stroke-width: 1.9; }

  .bottom-nav__tab--brand .bottom-nav__label {
    margin-top: -1px;
    color: #7e1820;
    font-weight: 700;
  }

  .bottom-nav__tab--brand.bottom-nav__tab--active .bottom-nav__icon {
    color: #fff9ec;
    background: linear-gradient(145deg, #c83a43, #85151f);
    border-color: #f4dfbd;
    box-shadow: 0 8px 22px rgba(117, 18, 27, .34), 0 0 0 2px rgba(200, 160, 91, .2);
    transform: translateY(-2px);
  }

  .bottom-nav__label {
    font-size: 0.625rem;
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }
}
</style>
