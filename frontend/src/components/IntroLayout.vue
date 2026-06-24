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
  background: #fff;
}

.intro-head {
  position: relative;
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  align-items: center;
  gap: 32px;
  min-height: 106px;
  padding: 0 30px;
  border: 1px solid var(--intro-line, #dedee3);
  border-bottom: 0;
  background: #fff;
}

.intro-head::before {
  content: '';
  position: absolute;
  left: 30px;
  right: 30px;
  bottom: 0;
  height: 1px;
  background: var(--intro-line, #dedee3);
}

.intro--wiki .intro-head {
  border-bottom: 0;
}

.intro-head--detail {
  padding-bottom: 8px;
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

.intro-body {
  flex: 1;
  min-height: 0;
}

@media (max-width: 768px) {
  .intro {
    gap: 8px;
  }

  .intro-head {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 18px 16px;
    gap: 16px;
  }

  .intro-head::before {
    left: 16px;
    right: 16px;
  }

  .intro-head-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
  }

  .intro-title {
    font-size: 21px;
  }

  .intro-brand {
    grid-template-columns: 1fr;
  }

  .intro-title,
  .intro-sub,
  .intro-eyebrow {
    grid-column: 1;
    grid-row: auto;
  }

  .intro-title {
    padding-left: 0;
    border-left: 0;
  }

  .intro--wiki .intro-brand .intro-title,
  .intro--wiki .intro-brand .intro-eyebrow {
    display: block;
  }

  .intro-tab {
    width: auto;
    min-height: 38px;
    padding: 0 18px;
    font-size: 14px;
  }
}
</style>
