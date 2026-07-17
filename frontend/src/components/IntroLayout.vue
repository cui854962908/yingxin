<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch, KeepAlive } from 'vue'
import { useRoute, useRouter, type RouteLocationNormalizedLoaded } from 'vue-router'
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

const headTitle = computed(() => {
  if (isDetailPage.value && detailCollege.value) return detailCollege.value.college
  if (isCampusPage.value && detailCampus.value) return detailCampus.value.name
  return INTRO_TABS.find((t) => t.id === activeTab.value)?.label ?? '认识牧院'
})

/** 牧院内部三 Tab 缓存 key（详情页仍按 path 区分） */
function introChildKey(r: RouteLocationNormalizedLoaded): string {
  const path = r.path
  if (path === '/intro/wiki') return 'intro-wiki'
  if (path.startsWith('/intro/campus/')) return path
  if (path === '/intro/clubs') return 'intro-clubs'
  if (path === '/intro/colleges' || path.startsWith('/intro/sie')) return 'intro-colleges'
  if (r.name === 'intro-college-detail') return path
  return path
}

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
import '../styles/pages/intro-layout.css'
</script>

<template>
  <div
    ref="introRootRef"
    class="intro intro-page intro-choreo"
    :class="{
      'intro--detail': isDetailPage || isCampusPage,
      'intro--college-detail': isDetailPage,
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
          <h2 class="intro-title">{{ headTitle }}</h2>
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
      <router-view v-slot="{ Component, route: childRoute }">
        <KeepAlive :max="4">
          <component :is="Component" v-if="Component" :key="introChildKey(childRoute)" />
        </KeepAlive>
      </router-view>
    </div>
  </div>
</template>
