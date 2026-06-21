<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { INTRO_SCHOOL, INTRO_TABS, getIntroCollege } from '../constants/intro'
import { PRODUCT_TAGLINE } from '../constants/product'
import '../styles/intro-theme.css'

const route = useRoute()
const router = useRouter()

const isDetailPage = computed(() => route.name === 'intro-college-detail')
const isWikiPage = computed(() => route.path.includes('/wiki'))
const detailCollege = computed(() => {
  const id = route.params.id as string
  return id ? getIntroCollege(id) : undefined
})

const activeTab = computed(() => {
  if (route.path.includes('/clubs')) return 'clubs'
  if (route.path.includes('/wiki')) return 'wiki'
  return 'colleges'
})

const subtitle = computed(() => {
  if (isDetailPage.value && detailCollege.value) {
    return `${detailCollege.value.college} · ${detailCollege.value.tagline}`
  }
  if (isWikiPage.value) return '学校概况 · 三校区 · 办学特色'
  if (route.path.includes('/colleges')) return '按学院了解师资、文化与社团'
  if (route.path.includes('/clubs')) return '全校社团招新信息'
  return PRODUCT_TAGLINE
})

function goTab(path: string) {
  if (route.path !== path) router.push(path)
}
</script>

<template>
  <div class="intro intro-page" :class="{ 'intro--detail': isDetailPage, 'intro--wiki': isWikiPage }">
    <header v-if="!isDetailPage" class="intro-head">
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
        >{{ t.label }}</button>
      </nav>
    </header>
    <header v-else-if="detailCollege" class="intro-head intro-head--detail">
      <p class="intro-eyebrow">{{ INTRO_SCHOOL }}</p>
      <h2 class="intro-title intro-title--sm">{{ detailCollege.college }}</h2>
      <p class="intro-sub">{{ detailCollege.tagline }}</p>
    </header>
    <div class="intro-body">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.intro {
  display: flex;
  flex-direction: column;
  gap: var(--intro-gap, 12px);
  min-height: 100%;
}

.intro-head {
  padding-bottom: 6px;
  border-bottom: 1px solid var(--intro-line, #f0e8dc);
}

.intro--wiki .intro-head {
  padding-bottom: 4px;
  border-bottom: none;
}

.intro-head--detail {
  padding-bottom: 8px;
}

.intro-eyebrow {
  margin: 0 0 2px;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  color: var(--intro-accent, #b5343a);
  font-weight: 600;
}

.intro-title {
  margin: 0;
  font-size: 1.22rem;
  font-weight: 700;
  color: var(--intro-ink, #3c3028);
  font-family: 'Noto Serif SC', Georgia, serif;
  letter-spacing: 0.06em;
}

.intro-title--sm {
  font-size: 1.12rem;
}

.intro-sub {
  margin: 4px 0 0;
  font-size: 0.76rem;
  color: var(--intro-faint, #8b7b65);
  line-height: 1.45;
}

.intro-tabs {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin-top: 10px;
  padding-bottom: 2px;
}

.intro--wiki .intro-tabs {
  margin-top: 8px;
}

.intro-tabs::-webkit-scrollbar {
  display: none;
}

.intro-tab {
  flex-shrink: 0;
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid #e5dbcc;
  background: #fefcf9;
  color: var(--intro-muted, #6b5e4e);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s, border-color 0.2s, color 0.2s, box-shadow 0.2s;
}

.intro-tab--on {
  background: linear-gradient(135deg, #75171d, #b5343a);
  border-color: #b5343a;
  color: #fff;
  box-shadow: 0 4px 12px rgba(181, 52, 58, 0.25);
}

.intro-body {
  flex: 1;
  min-height: 0;
}

@media (max-width: 768px) {
  .intro {
    gap: 8px;
  }

  .intro-head-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
  }

  .intro-title {
    font-size: 1.08rem;
  }

  .intro--wiki .intro-brand .intro-title,
  .intro--wiki .intro-brand .intro-eyebrow {
    display: none;
  }

  .intro-tab {
    min-height: 36px;
    padding: 0 16px;
    font-size: 0.8rem;
  }
}
</style>
