<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  INTRO_SCHOOL,
  INTRO_WIKI_CATEGORY,
  INTRO_WIKI_FALLBACK,
  INTRO_WIKI_TAGLINE,
  INTRO_WIKI_HERO_IMAGE,
  INTRO_WIKI_STATS,
  INTRO_WIKI_CAMPUSES,
  INTRO_WIKI_OFFICIAL_URL,
} from '../constants/intro'
import { useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'
import '../styles/intro-theme.css'

interface WikiBlock { id?: string; title: string; content: string }

const blocks = ref<WikiBlock[]>([])
const loading = ref(true)
const { isAdmin } = useAuth()

const parsedBlocks = computed(() =>
  blocks.value.map((item) => {
    const { image, body } = splitBlockMedia(item.content)
    return { ...item, image, body }
  }),
)

function splitBlockMedia(html: string): { image: string; body: string } {
  const m = html.match(/<img[^>]+src=["']([^"']+)["'][^>]*>/i)
  if (!m) return { image: '', body: html }
  return { image: m[1], body: html.replace(m[0], '').trim() }
}

async function load() {
  loading.value = true
  try {
    const res = await fetch(`/api/announcements?category=${encodeURIComponent(INTRO_WIKI_CATEGORY)}`)
    const d = await res.json()
    blocks.value = d.success && d.data?.length
      ? d.data.map((x: WikiBlock) => ({ id: x.id, title: x.title, content: x.content }))
      : INTRO_WIKI_FALLBACK
  } catch {
    blocks.value = INTRO_WIKI_FALLBACK
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="school-wiki intro-page">
    <div class="wiki-hero-wrap">
      <header class="wiki-hero">
        <img class="wiki-hero-img" :src="INTRO_WIKI_HERO_IMAGE" :alt="INTRO_SCHOOL" loading="eager" />
        <div class="wiki-hero-shade" />
        <div class="wiki-hero-body">
          <div class="wiki-hero-logo">
            <img src="/logo-1.webp" alt="校徽" width="48" height="48" decoding="async" />
          </div>
          <p class="wiki-hero-eyebrow">牧院大百科</p>
          <h3 class="wiki-hero-title">{{ INTRO_SCHOOL }}</h3>
          <p class="wiki-hero-motto">{{ INTRO_WIKI_TAGLINE }}</p>
          <a class="wiki-hero-link" :href="INTRO_WIKI_OFFICIAL_URL" target="_blank" rel="noopener">官网 →</a>
        </div>
      </header>

      <div class="intro-stat-row wiki-stats-float">
        <div v-for="(s, i) in INTRO_WIKI_STATS" :key="i" class="intro-stat-chip">
          <span class="intro-stat-chip__val">{{ s.value }}</span>
          <span class="intro-stat-chip__label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <section class="wiki-panel">
      <span class="intro-section-label">校区</span>
      <h4 class="intro-section-title">三校区一览</h4>
      <p class="intro-section-desc">地址摘自学校章程</p>
      <div class="wiki-campus-scroll">
        <article v-for="c in INTRO_WIKI_CAMPUSES" :key="c.id" class="wiki-campus-card">
          <div class="wiki-campus-photo">
            <img :src="c.image" :alt="c.name" loading="lazy" />
            <span class="wiki-campus-tag">{{ c.tag }}</span>
          </div>
          <div class="wiki-campus-info">
            <h5 class="wiki-campus-name">{{ c.name }}</h5>
            <p class="wiki-campus-addr">{{ c.address }}</p>
          </div>
        </article>
      </div>
    </section>

    <div v-if="loading" class="wiki-loading"><AppSpinner /></div>
    <template v-else>
      <section class="wiki-panel wiki-panel--blocks">
        <span class="intro-section-label">百科</span>
        <h4 class="intro-section-title">了解更多</h4>
      </section>

      <div class="wiki-blocks">
        <article
          v-for="(item, i) in parsedBlocks" :key="item.id ?? i"
          class="wiki-block"
          :class="{ 'wiki-block--reverse': i % 2 === 1, 'wiki-block--text': !item.image }"
        >
          <div v-if="item.image" class="wiki-block-media">
            <img :src="item.image" :alt="item.title" loading="lazy" />
          </div>
          <div class="wiki-block-text">
            <h4 class="wiki-block-title">{{ item.title }}</h4>
            <div class="wiki-block-body" v-html="item.image ? item.body : item.content" />
          </div>
        </article>
      </div>

      <p v-if="isAdmin" class="wiki-admin-hint">
        公告分类 <code>{{ INTRO_WIKI_CATEGORY }}</code> · 正文含 <code>&lt;img&gt;</code> 可图文并排
      </p>
    </template>
  </div>
</template>

<style scoped>
.school-wiki {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0 -2px;
}

.wiki-hero-wrap {
  position: relative;
  margin-bottom: 8px;
}

.wiki-hero {
  position: relative;
  border-radius: var(--intro-radius, 14px);
  overflow: hidden;
  min-height: 168px;
  box-shadow: 0 8px 28px rgba(60, 48, 40, 0.14);
}

.wiki-hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 35%;
}

.wiki-hero-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    115deg,
    rgba(45, 12, 15, 0.92) 0%,
    rgba(84, 11, 19, 0.62) 50%,
    rgba(45, 12, 15, 0.35) 100%
  );
}

.wiki-hero-body {
  position: relative;
  z-index: 1;
  padding: 18px 16px 22px;
  color: #f2e6d0;
}

.wiki-hero-logo {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  padding: 3px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
  margin-bottom: 8px;
}

.wiki-hero-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 50%;
}

.wiki-hero-eyebrow {
  margin: 0 0 4px;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: rgba(242, 230, 208, 0.8);
}

.wiki-hero-title {
  margin: 0 0 4px;
  font-size: 1.28rem;
  font-weight: 700;
  font-family: 'Noto Serif SC', Georgia, serif;
  letter-spacing: 0.06em;
  line-height: 1.3;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.wiki-hero-motto {
  margin: 0 0 10px;
  font-size: 0.82rem;
  opacity: 0.92;
  letter-spacing: 0.08em;
}

.wiki-hero-link {
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 600;
  color: #f2e6d0;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(242, 230, 208, 0.35);
  background: rgba(255, 255, 255, 0.12);
  text-decoration: none;
}

.wiki-stats-float {
  position: relative;
  z-index: 2;
  margin: -20px 8px 0;
}

.wiki-panel {
  padding: 12px 12px 10px;
  border-radius: var(--intro-radius-sm, 12px);
  background: var(--intro-warm-bg, #faf7f3);
  border: 1px solid var(--intro-line, #f0e8dc);
}

.wiki-panel--blocks {
  padding-bottom: 6px;
  background: transparent;
  border: none;
  padding-left: 2px;
  padding-right: 2px;
}

.wiki-campus-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin-top: 10px;
  padding-bottom: 2px;
}

.wiki-campus-scroll::-webkit-scrollbar {
  display: none;
}

.wiki-campus-card {
  flex: 0 0 min(78vw, 240px);
  scroll-snap-align: start;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--intro-line, #f0e8dc);
  box-shadow: 0 3px 12px rgba(60, 48, 40, 0.06);
}

.wiki-campus-photo {
  position: relative;
  height: 88px;
  overflow: hidden;
}

.wiki-campus-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.wiki-campus-tag {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 0.58rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(61, 17, 20, 0.78);
  color: #f2e6d0;
}

.wiki-campus-info {
  padding: 10px 11px 11px;
}

.wiki-campus-name {
  margin: 0 0 4px;
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--intro-ink, #3c3028);
}

.wiki-campus-addr {
  margin: 0;
  font-size: 0.68rem;
  line-height: 1.5;
  color: var(--intro-faint, #8b7b65);
}

.wiki-loading {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.wiki-blocks {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wiki-block {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  border-radius: var(--intro-radius, 14px);
  overflow: hidden;
  border: 1px solid var(--intro-line, #f0e8dc);
  background: #fff;
  box-shadow: 0 2px 14px rgba(60, 48, 40, 0.05);
}

.wiki-block--reverse {
  direction: rtl;
}

.wiki-block--reverse > * {
  direction: ltr;
}

.wiki-block--text {
  grid-template-columns: 1fr;
}

.wiki-block-media {
  min-height: 140px;
  background: #f0ebe3;
}

.wiki-block-media img {
  width: 100%;
  height: 100%;
  min-height: 140px;
  object-fit: cover;
  display: block;
}

.wiki-block-text {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.wiki-block-title {
  margin: 0 0 8px;
  font-size: 0.94rem;
  font-weight: 700;
  color: var(--intro-ink, #3c3028);
  font-family: 'Noto Serif SC', Georgia, serif;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--intro-line, #f0e8dc);
}

.wiki-block-body {
  font-size: 0.82rem;
  line-height: 1.65;
  color: var(--intro-muted, #5a4e42);
}

.wiki-block-body :deep(p) {
  margin: 0 0 0.55em;
}

.wiki-block-body :deep(p:last-child) {
  margin-bottom: 0;
}

.wiki-block-body :deep(strong) {
  color: var(--intro-ink, #3c3028);
}

.wiki-block-body :deep(a) {
  color: var(--intro-accent, #b5343a);
  text-decoration: none;
}

.wiki-admin-hint {
  margin: 0;
  font-size: 0.68rem;
  color: #b0a090;
  line-height: 1.5;
  padding: 8px 10px;
  border-radius: 8px;
  background: #fefcf9;
  border: 1px dashed #e5dbcc;
}

.wiki-admin-hint code {
  font-size: 0.64rem;
  background: #f5f0ea;
  padding: 1px 4px;
  border-radius: 3px;
}

@media (min-width: 769px) {
  .wiki-campus-scroll {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    overflow: visible;
  }

  .wiki-campus-card {
    flex: none;
  }

  .wiki-campus-photo {
    height: 96px;
  }

  .wiki-hero {
    min-height: 188px;
  }
}

@media (max-width: 768px) {
  .school-wiki {
    gap: 8px;
    margin: 0 -4px;
  }

  .wiki-hero {
    border-radius: 12px;
    min-height: 152px;
  }

  .wiki-hero-body {
    padding: 14px 14px 18px;
  }

  .wiki-hero-title {
    font-size: 1.12rem;
  }

  .wiki-stats-float {
    margin: -16px 6px 0;
  }

  .wiki-panel {
    padding: 10px 10px 8px;
  }

  .wiki-block,
  .wiki-block--reverse {
    grid-template-columns: 1fr;
    direction: ltr;
  }

  .wiki-block-media {
    min-height: 130px;
  }

  .wiki-block-media img {
    min-height: 130px;
  }

  .wiki-block-text {
    padding: 12px 14px;
  }
}
</style>
