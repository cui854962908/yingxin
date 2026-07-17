<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import DOMPurify from 'dompurify'
import {
  INTRO_SCHOOL,
  INTRO_WIKI_CAMPUSES,
  INTRO_WIKI_CATEGORY,
  INTRO_WIKI_FALLBACK,
  INTRO_WIKI_HIGHLIGHTS,
  INTRO_WIKI_HERO_IMAGE,
  INTRO_WIKI_OFFICIAL_URL,
  INTRO_WIKI_STATS,
  INTRO_WIKI_TAGLINE,
} from '../constants/intro'
import { usePanelReveal } from '../composables/usePanelReveal'
import '../styles/intro-theme.css'
import '../styles/panel-enter.css'
import '../styles/intro-school-wiki.css'
import '../styles/intro-school-wiki-responsive.css'
interface WikiBlock {
  id?: string
  title: string
  content: string
}

const blocks = ref<WikiBlock[]>([...INTRO_WIKI_FALLBACK])
const { ready: revealReady } = usePanelReveal()

const parsedBlocks = computed(() =>
  blocks.value.map((item) => {
    const { image, body } = splitBlockMedia(item.content)
    return { ...item, image, body }
  }),
)
const overviewBlock = computed(() => parsedBlocks.value[0])
const cultureBlock = computed(() => parsedBlocks.value[1])
const strengthBlock = computed(() => parsedBlocks.value[2])
const overviewBody = computed(() =>
  removeOfficialUrlEntry(overviewBlock.value?.body || overviewBlock.value?.content || ''),
)
const overviewBodySafe = computed(() => DOMPurify.sanitize(overviewBody.value))
const strengthBody = computed(() => strengthBlock.value?.body || strengthBlock.value?.content || '')
const strengthBodySafe = computed(() => DOMPurify.sanitize(strengthBody.value))
const strengthImage = computed(
  () => strengthBlock.value?.image || INTRO_WIKI_CAMPUSES[0].image,
)
const cultureImage = computed(() => cultureBlock.value?.image || '')
const cultureBodySafe = computed(() => DOMPurify.sanitize(cultureBlock.value?.body || overviewBlock.value?.body || ''))

function splitBlockMedia(html: string): { image: string; body: string } {
  const match = html.match(/<img[^>]+src=["']([^"']+)["'][^>]*>/i)
  if (!match) return { image: '', body: html }
  return { image: match[1], body: html.replace(match[0], '').trim() }
}

function removeOfficialUrlEntry(html: string): string {
  return html
    .replace(/[^<。！？.!?]{0,18}<a[^>]+hnuahe\.edu\.cn[^>]*>.*?<\/a>/gi, '')
    .replace(/<p>\s*<\/p>/gi, '')
}

async function load() {
  try {
    const res = await fetch(`/api/announcements?category=${encodeURIComponent(INTRO_WIKI_CATEGORY)}`)
    const data = await res.json()
    if (data.success && data.data?.length) {
      blocks.value = data.data.map((item: WikiBlock) => ({
        id: item.id,
        title: item.title,
        content: item.content,
      }))
    }
  } catch {
    blocks.value = [...INTRO_WIKI_FALLBACK]
  }
}

onMounted(load)
</script>

<template>
  <div
    class="school-wiki intro-page panel-reveal panel-reveal--intro"
    :class="{ 'panel-reveal--ready': revealReady }"
  >
    <section class="wiki-lead panel-reveal__item">
      <article class="wiki-hero">
        <img class="wiki-hero__img" :src="INTRO_WIKI_HERO_IMAGE" :alt="INTRO_SCHOOL" loading="eager" />
        <div class="wiki-hero__shade" />
        <div class="wiki-hero__copy">
          <h3>{{ INTRO_WIKI_TAGLINE }}</h3>
          <p>以牧业为特色，以经济为优势，农、经、管、工、文、法多学科协调发展；龙子湖主校区、英才智信校区、北林牧科校区各具分工，共同构成河南牧业经济学院的「一校三区」办学格局。</p>
          <a :href="INTRO_WIKI_OFFICIAL_URL" target="_blank" rel="noopener">了解更多</a>
        </div>
      </article>

      <aside class="wiki-overview">
        <span class="wiki-kicker">学校概况</span>
        <h3>{{ overviewBlock?.title || '学校概况' }}</h3>
        <div class="wiki-overview__text" v-html="overviewBodySafe" />
        <a class="wiki-official" :href="INTRO_WIKI_OFFICIAL_URL" target="_blank" rel="noopener">
          学校官网
          <strong>www.hnuahe.edu.cn</strong>
        </a>
      </aside>
    </section>

    <section class="wiki-stats panel-reveal__item" aria-label="学校关键数据">
      <article v-for="(stat, index) in INTRO_WIKI_STATS" :key="stat.label" class="wiki-stat">
        <span class="wiki-stat__index">{{ String(index + 1).padStart(2, '0') }}</span>
        <span class="wiki-stat__label">{{ stat.label }}</span>
        <strong>{{ stat.value }}</strong>
      </article>
    </section>

    <section class="wiki-section panel-reveal__item">
      <header class="wiki-section__head">
        <h3>三校区一览</h3>
        <span>点击卡片查看详情</span>
      </header>
      <div class="wiki-campus-grid">
        <RouterLink
          v-for="campus in INTRO_WIKI_CAMPUSES"
          :key="campus.id"
          :to="`/intro/campus/${campus.id}`"
          class="wiki-campus wiki-campus--link"
        >
          <div class="wiki-campus__image">
            <img :src="campus.image" :alt="campus.name" loading="lazy" />
            <span class="wiki-campus__tag">{{ campus.tag }}</span>
          </div>
          <div class="wiki-campus__body">
            <h4>{{ campus.name }}</h4>
            <p>{{ campus.address }}</p>
            <span class="wiki-campus__more">查看介绍 →</span>
          </div>
        </RouterLink>
      </div>
    </section>

    <section class="wiki-feature-grid panel-reveal__item">
      <article class="wiki-gallery-card">
        <div class="wiki-gallery-card__image">
          <img :src="cultureImage || INTRO_WIKI_CAMPUSES[1].image" alt="校园风光" loading="lazy" />
          <span>校园文化</span>
        </div>
        <footer>
          <p>「尚严崇实、善知敏行」——课堂教学、实验实训与学科竞赛并重</p>
          <b>{{ cultureBlock?.title || '校训与校风' }}</b>
        </footer>
      </article>

      <article class="wiki-text-card">
        <span class="wiki-kicker">{{ cultureBlock?.title || '校训与校风' }}</span>
        <h3>{{ cultureBlock?.title || '校训与校风' }}</h3>
        <div class="wiki-text-card__body" v-html="cultureBodySafe" />
        <a :href="INTRO_WIKI_OFFICIAL_URL" target="_blank" rel="noopener">了解更多学校信息</a>
        <div class="wiki-facts">
          <span>校庆日<br /><strong>9月19日</strong></span>
          <span>合并组建<br /><strong>2013年</strong></span>
          <span>校区布局<br /><strong>一校三区</strong></span>
        </div>
      </article>
    </section>

    <section class="wiki-strength panel-reveal__item">
      <div class="wiki-strength__copy">
        <span class="wiki-kicker">{{ strengthBlock?.title || '办学实力' }}</span>
        <h3>{{ strengthBlock?.title || '办学实力' }}</h3>
        <div class="wiki-strength__body" v-html="strengthBodySafe" />
      </div>
      <div class="wiki-strength__media">
        <img :src="strengthImage" :alt="strengthBlock?.title || '办学实力'" loading="lazy" />
        <span class="wiki-strength__badge">牧工商一体 · 应用型本科</span>
      </div>
    </section>

    <section class="wiki-highlights panel-reveal__item" aria-label="办学特色亮点">
      <header class="wiki-section__head">
        <h3>开放办学与服务</h3>
        <span>对接区域发展与行业需求</span>
      </header>
      <div class="wiki-highlight-grid">
        <article v-for="(item, index) in INTRO_WIKI_HIGHLIGHTS" :key="item.kicker" class="wiki-highlight-card">
          <span class="wiki-highlight-card__index">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="wiki-highlight-card__kicker">{{ item.kicker }}</span>
          <h4>{{ item.title }}</h4>
          <p>{{ item.body }}</p>
        </article>
      </div>
    </section>

  </div>
</template>
