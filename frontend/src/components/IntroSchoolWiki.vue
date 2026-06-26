<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  INTRO_SCHOOL,
  INTRO_WIKI_CAMPUSES,
  INTRO_WIKI_CATEGORY,
  INTRO_WIKI_FALLBACK,
  INTRO_WIKI_HERO_IMAGE,
  INTRO_WIKI_OFFICIAL_URL,
  INTRO_WIKI_STATS,
  INTRO_WIKI_TAGLINE,
} from '../constants/intro'
import { useAuth } from '../composables/useAuth'
import { usePanelReveal } from '../composables/usePanelReveal'
import AppSpinner from './AppSpinner.vue'
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
const loading = ref(true)
const { isAdmin } = useAuth()
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
const sceneryImage = computed(
  () => strengthBlock.value?.image || cultureBlock.value?.image || INTRO_WIKI_CAMPUSES[0].image,
)

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
  loading.value = true
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
  } finally {
    loading.value = false
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
        <div class="wiki-overview__text" v-html="overviewBody" />
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
          <img :src="sceneryImage" alt="校园风光" loading="lazy" />
          <span>校园风光</span>
        </div>
        <footer>
          <p>绿树成荫的校园环境与「尚严崇实、善知敏行」的校训相得益彰</p>
          <b>校园风光</b>
        </footer>
      </article>

      <article class="wiki-text-card">
        <span class="wiki-kicker">{{ cultureBlock?.title || '学校简介' }}</span>
        <h3>学校简介</h3>
        <div class="wiki-text-card__body" v-html="cultureBlock?.body || overviewBlock?.body" />
        <a :href="INTRO_WIKI_OFFICIAL_URL" target="_blank" rel="noopener">了解更多学校信息</a>
        <div class="wiki-facts">
          <span>办学层次<br /><strong>本科</strong></span>
          <span>主管部门<br /><strong>河南省教育厅</strong></span>
          <span>学校类型<br /><strong>应用型</strong></span>
        </div>
      </article>
    </section>

    <div v-if="loading" class="wiki-loading" aria-label="正在加载认识牧院内容">
      <AppSpinner />
    </div>

    <p v-if="isAdmin" class="wiki-admin-hint">
      公告分类 <code>{{ INTRO_WIKI_CATEGORY }}</code>；正文内的首张图片会作为图文卡片图片。
    </p>
  </div>
</template>
