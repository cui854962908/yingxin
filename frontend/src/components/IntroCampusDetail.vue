<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getIntroCampus } from '../constants/intro'
import { useAppNavigate } from '../composables/useAppNavigate'
import { usePanelReveal } from '../composables/usePanelReveal'
import '../styles/intro-theme.css'
import '../styles/intro-campus-detail.css'
import '../styles/panel-enter.css'

const props = defineProps<{ campusId: string }>()

const router = useRouter()
const { appNavigate } = useAppNavigate()

const campus = computed(() => getIntroCampus(props.campusId))
const { ready: revealReady } = usePanelReveal()

watch(
  () => props.campusId,
  (id) => {
    if (!getIntroCampus(id)) router.replace('/intro/wiki')
  },
  { immediate: true },
)

function goBack() {
  appNavigate('/intro/wiki')
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div
    v-if="campus"
    class="campus-detail intro-page panel-reveal panel-reveal--intro"
    :class="{ 'panel-reveal--ready': revealReady }"
  >
    <button type="button" class="intro-back-btn" @click="goBack">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      返回牧院大百科
    </button>

    <header class="campus-hero panel-reveal__item">
      <img class="campus-hero__img" :src="campus.heroImage" :alt="campus.name" loading="eager" />
      <div class="campus-hero__shade" />
      <div class="campus-hero__copy">
        <span class="campus-hero__tag">{{ campus.tag }}</span>
        <h2>{{ campus.name }}</h2>
        <p class="campus-hero__tagline">{{ campus.tagline }}</p>
        <p class="campus-hero__addr">{{ campus.address }}</p>
      </div>
    </header>

    <div v-if="campus.stats.length" class="intro-stat-row campus-stats panel-reveal__item">
      <div v-for="(s, i) in campus.stats" :key="i" class="intro-stat-chip">
        <span class="intro-stat-chip__val">{{ s.value }}</span>
        <span class="intro-stat-chip__label">{{ s.label }}</span>
      </div>
    </div>

    <nav class="intro-pill-nav campus-anchors panel-reveal__item" aria-label="页面章节">
      <button type="button" @click="scrollTo('campus-overview')">校区概况</button>
      <button type="button" @click="scrollTo('campus-facilities')">校园设施</button>
      <button type="button" @click="scrollTo('campus-transport')">交通指引</button>
      <button type="button" @click="scrollTo('campus-gallery')">校园风光</button>
    </nav>

    <section id="campus-overview" class="campus-block panel-reveal__item">
      <span class="intro-section-label">校区概况</span>
      <h3 class="intro-section-title">{{ campus.name }}</h3>
      <p class="campus-lead">{{ campus.summary }}</p>
      <p class="campus-text">{{ campus.overview }}</p>
      <ul class="campus-features">
        <li v-for="(item, i) in campus.features" :key="i">{{ item }}</li>
      </ul>
    </section>

    <div class="campus-detail-rest panel-reveal__item">
    <section id="campus-facilities" class="campus-block">
      <span class="intro-section-label">校园设施</span>
      <h3 class="intro-section-title">主要设施</h3>
      <p class="intro-section-desc">设施名称供新生提前建立印象，具体位置与开放时间以到校后学院、后勤通知为准。</p>
      <div class="campus-facility-grid">
        <span v-for="(f, i) in campus.facilities" :key="i" class="campus-facility">{{ f }}</span>
      </div>
    </section>

    <section id="campus-transport" class="campus-block campus-block--warm">
      <span class="intro-section-label">交通指引</span>
      <h3 class="intro-section-title">如何到达</h3>
      <p class="campus-text">{{ campus.transport }}</p>
      <p class="campus-map-hint">
        <strong>详细地址</strong>
        {{ campus.address }}
      </p>
    </section>

    <section id="campus-gallery" class="campus-block">
      <span class="intro-section-label">校园风光</span>
      <h3 class="intro-section-title">实景一览</h3>
      <div class="campus-gallery">
        <figure v-for="(img, i) in campus.gallery" :key="i">
          <img :src="img.src" :alt="img.caption" loading="lazy" />
          <figcaption>{{ img.caption }}</figcaption>
        </figure>
      </div>
    </section>
    </div>
  </div>
</template>
