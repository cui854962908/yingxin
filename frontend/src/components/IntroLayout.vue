<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { INTRO_SCHOOL, INTRO_TABS, getIntroCollege, getIntroCampus, getIntroCollegeTabPath } from '../constants/intro'
import { PRODUCT_TAGLINE } from '../constants/product'
import '../styles/intro-theme.css'
import '../styles/panel-enter.css'
import '../styles/intro-mobile.css'

const route = useRoute()
const router = useRouter()
const introRootRef = ref<HTMLElement | null>(null)
const introHeadRef = ref<HTMLElement | null>(null)
let headObserver: ResizeObserver | null = null

function syncStickyHeight() {
  const head = introHeadRef.value
  const root = introRootRef.value
  if (!head || !root) return
  root.style.setProperty('--intro-sticky-h', `${head.offsetHeight}px`)
}

onMounted(() => {
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      syncStickyHeight()
    })
  })
  if (typeof ResizeObserver !== 'undefined') {
    headObserver = new ResizeObserver(() => syncStickyHeight())
    if (introHeadRef.value) headObserver.observe(introHeadRef.value)
  }
})

onUnmounted(() => {
  headObserver?.disconnect()
})

watch(() => route.path, () => {
  nextTick(() => {
    syncStickyHeight()
    if (headObserver && introHeadRef.value) {
      headObserver.disconnect()
      headObserver.observe(introHeadRef.value)
    }
  })
})

const isDetailPage = computed(() => route.name === 'intro-college-detail')
const isCampusPage = computed(() => route.name === 'intro-campus-detail')
const isWikiPage = computed(() => route.path.includes('/wiki'))
const detailCollege = computed(() => {
  const id = route.params.id as string
  return id ? getIntroCollege(id) : undefined
})
const detailCampus = computed(() => {
  const id = route.params.campusId as string
  return id ? getIntroCampus(id) : undefined
})

const activeTab = computed(() => {
  if (route.path.includes('/clubs')) return 'clubs'
  if (route.path.includes('/wiki')) return 'wiki'
  if (route.path.includes('/colleges') || route.name === 'intro-college-detail') return 'colleges'
  return 'colleges'
})

const collegeTabPath = computed(() => getIntroCollegeTabPath())

const subtitle = computed(() => {
  if (isCampusPage.value && detailCampus.value) {
    return `${detailCampus.value.name} · ${detailCampus.value.tagline}`
  }
  if (isDetailPage.value && detailCollege.value) {
    return `${detailCollege.value.college} · ${detailCollege.value.tagline}`
  }
  if (isWikiPage.value) return '学校历史与定位 · 三校区分工 · 专业平台与到校指引'
  if (route.path.includes('/colleges')) return '学院简介 · 师资队伍 · 专业特色与社团'
  if (route.path.includes('/clubs')) return '按类别浏览社团 · 查看招新说明与联系方式'
  return PRODUCT_TAGLINE
})

function goTab(path: string) {
  if (path === '/intro/colleges') {
    const target = collegeTabPath.value
    if (route.path !== target) router.push(target)
    return
  }
  if (path === '/intro/clubs') {
    router.push('/intro/clubs')
    return
  }
  if (route.path !== path) router.push(path)
}
</script>

<template>
  <div
    ref="introRootRef"
    class="intro intro-page intro-choreo"
    :class="{
      'intro--detail': isDetailPage || isCampusPage,
      'intro--wiki': isWikiPage,
      'intro--clubs': activeTab === 'clubs',
    }"
  >
    <header
      v-if="!isDetailPage && !isCampusPage"
      ref="introHeadRef"
      class="intro-head intro-head--sticky"
    >
      <div class="intro-head__veil" aria-hidden="true" />
      <div class="intro-head-top">
        <div class="intro-brand">
          <p class="intro-eyebrow">{{ INTRO_SCHOOL }}</p>
          <h2 class="intro-title">认识牧院</h2>
          <p v-if="subtitle" class="intro-sub">{{ subtitle }}</p>
        </div>
      </div>
      <nav class="intro-tabs" aria-label="介绍分类">
        <button
          v-for="t in INTRO_TABS" :key="t.id"
          type="button"
          class="intro-tab"
          :class="{ 'intro-tab--on': activeTab === t.id }"
          @click="goTab(t.path)"
        >
          <span class="intro-tab__text intro-tab__text--full">{{ t.label }}</span>
          <span class="intro-tab__text intro-tab__text--short">{{ t.shortLabel }}</span>
        </button>
      </nav>
    </header>
    <header v-else-if="detailCollege" ref="introHeadRef" class="intro-head intro-head--detail intro-head--sticky">
      <div class="intro-head__veil" aria-hidden="true" />
      <div class="intro-head-top intro-head-top--detail">
        <div class="intro-brand intro-brand--detail">
          <p class="intro-eyebrow">{{ INTRO_SCHOOL }}</p>
          <h2 class="intro-title intro-title--sm">{{ detailCollege.college }}</h2>
          <p class="intro-sub">{{ detailCollege.tagline }}</p>
        </div>
      </div>
      <nav class="intro-tabs" aria-label="介绍分类">
        <button
          v-for="t in INTRO_TABS" :key="t.id"
          type="button"
          class="intro-tab"
          :class="{ 'intro-tab--on': activeTab === t.id }"
          @click="goTab(t.path)"
        >
          <span class="intro-tab__text intro-tab__text--full">{{ t.label }}</span>
          <span class="intro-tab__text intro-tab__text--short">{{ t.shortLabel }}</span>
        </button>
      </nav>
    </header>
    <header v-else-if="detailCampus" ref="introHeadRef" class="intro-head intro-head--detail intro-head--sticky">
      <div class="intro-head__veil" aria-hidden="true" />
      <div class="intro-head-top intro-head-top--detail">
        <div class="intro-brand intro-brand--detail">
          <p class="intro-eyebrow">{{ INTRO_SCHOOL }}</p>
          <h2 class="intro-title intro-title--sm">{{ detailCampus.name }}</h2>
          <p class="intro-sub">{{ detailCampus.address }}</p>
        </div>
      </div>
    </header>
    <div class="intro-body">
      <router-view :key="route.path" />
    </div>
  </div>
</template>

<style scoped>
.intro {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 100%;
  background: #fff;
}

.intro-head {
  position: relative;
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  align-items: center;
  gap: 32px;
  min-height: 106px;
  padding: 22px 30px 18px;
  border: none;
  border-bottom: 1px solid var(--intro-line, #dedee3);
  border-radius: 15px 15px 0 0;
  background: linear-gradient(180deg, #fafbfc 0%, #fff 72%);
}

.intro-head::before {
  display: none;
}

.intro--wiki .intro-head {
  border-bottom: 0;
}

.intro-head--detail {
  padding-bottom: 8px;
}

/* 认识牧院顶栏：PC 随内容滚动；移动端吸顶见 intro-mobile.css */
.intro-head--sticky {
  flex-shrink: 0;
  background: #fff;
}

.intro-head__veil {
  display: none;
}

.intro--clubs .intro-head--sticky {
  box-shadow: none;
}

.intro-brand {
  display: grid;
  grid-template-columns: max-content max-content;
  align-items: start;
  column-gap: 28px;
}

.intro-eyebrow {
  grid-column: 1;
  margin: 0 0 7px;
  font-size: 24px;
  line-height: 1.1;
  letter-spacing: 0;
  color: var(--intro-accent-strong, #b51f2d);
  font-weight: 800;
}

.intro-title {
  grid-column: 2;
  grid-row: 1;
  margin: 0;
  padding-left: 28px;
  border-left: 1px solid var(--intro-line, #dedee3);
  font-size: 24px;
  line-height: 1.1;
  font-weight: 800;
  color: var(--intro-ink, #15151a);
  font-family: inherit;
  letter-spacing: 0;
}

.intro-title--sm {
  font-size: 1.12rem;
}

.intro-sub {
  grid-column: 1;
  margin: 8px 0 0;
  font-size: 15px;
  color: var(--intro-faint, #777780);
  line-height: 1.45;
}

.intro-tabs {
  display: flex;
  flex-wrap: nowrap;
  justify-content: flex-end;
  gap: 18px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin-top: 0;
  padding-bottom: 0;
}

.intro--wiki .intro-tabs {
  margin-top: 8px;
}

.intro-tabs::-webkit-scrollbar {
  display: none;
}

.intro-tab {
  position: relative;
  flex-shrink: 0;
  width: 144px;
  height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  border: 1px solid var(--intro-line, #dedee3);
  background: #fff;
  color: var(--intro-muted, #4b4b52);
  font-size: 16px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.2s;
}

.intro-tab:hover {
  border-color: rgba(181, 31, 45, .42);
  color: var(--intro-accent, #b51f2d);
  transform: translateY(-1px);
}

.intro-tab:focus-visible {
  outline: 3px solid rgba(181, 31, 45, .22);
  outline-offset: 2px;
}

.intro-tab--on {
  background: var(--intro-accent, #b51f2d);
  border-color: var(--intro-accent, #b51f2d);
  color: #fff;
}

.intro-tab--on:hover {
  color: #fff;
}

.intro-tab__text--short {
  display: none;
}

.intro-body {
  flex: 1;
  min-height: 0;
}

@media (max-width: 768px) {
  .intro {
    gap: 0;
  }

  .intro-head {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    min-height: auto;
    padding: 12px 12px 10px;
    border-radius: 11px 11px 0 0;
    background: linear-gradient(180deg, #fafbfc 0%, #fff 100%);
  }

  .intro-head::before {
    display: none;
  }

  .intro-head-top {
    flex-shrink: 0;
  }

  .intro-brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .intro-brand--detail {
    gap: 4px;
  }

  .intro-eyebrow {
    display: none;
  }

  .intro-title {
    padding-left: 0;
    border-left: 0;
    font-size: 1.1rem;
    line-height: 1.3;
  }

  .intro-sub {
    margin: 0;
    font-size: 0.74rem;
    line-height: 1.45;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  /* 分段 Tab：三等分、短文案、不截断 */
  .intro-tab__text--full {
    display: none;
  }

  .intro-tab__text--short {
    display: inline;
  }

  .intro-tabs {
    flex-shrink: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0;
    width: 100%;
    margin: 0;
    padding: 3px;
    overflow: visible;
    background: #f4f4f6;
    border: 1px solid var(--intro-line, #dedee3);
    border-radius: 10px;
  }

  .intro-tab {
    width: 100%;
    min-width: 0;
    height: 34px;
    min-height: 34px;
    padding: 0 6px;
    border: 0;
    border-radius: 8px;
    background: transparent;
    color: var(--intro-muted, #4b4b52);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-tap-highlight-color: transparent;
    box-shadow: none;
  }

  .intro-tab--on {
    background: #fff;
    color: var(--intro-accent, #b51f2d);
    box-shadow: 0 1px 3px rgba(21, 21, 26, 0.08);
  }

  .intro-tab--on:hover {
    color: var(--intro-accent, #b51f2d);
  }

  .intro-tab:hover {
    transform: none;
  }

  .intro-head--detail {
    padding-bottom: 10px;
  }

  .intro-head--detail .intro-eyebrow {
    display: block;
    margin: 0;
    font-size: 0.68rem;
    font-weight: 700;
    line-height: 1.3;
  }

  .intro-head--detail .intro-title {
    font-size: 1rem;
    line-height: 1.35;
  }

  .intro-head--detail .intro-sub {
    -webkit-line-clamp: 2;
    font-size: 0.72rem;
  }
}

@media (max-width: 480px) {
  .intro-head {
    padding: 10px 10px 8px;
  }

  .intro-title {
    font-size: 1.05rem;
  }

  .intro-tab {
    height: 32px;
    min-height: 32px;
    font-size: 0.74rem;
  }
}
</style>
