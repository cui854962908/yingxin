<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getIntroCollege } from '../constants/intro'
import { useAppNavigate } from '../composables/useAppNavigate'
import IntroCollegeModule from './IntroCollegeModule.vue'
import IntroCollegeClubs from './IntroCollegeClubs.vue'
import '../styles/intro-theme.css'

const props = defineProps<{ id: string }>()

const router = useRouter()
const { appNavigate } = useAppNavigate()

const college = computed(() => getIntroCollege(props.id))

watch(
  () => props.id,
  (id) => {
    if (!getIntroCollege(id)) router.replace('/intro/colleges')
  },
  { immediate: true },
)

function goBack() {
  appNavigate('/intro/colleges')
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div v-if="college" class="college-detail intro-page">
    <button type="button" class="detail-back" @click="goBack">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
      返回学院列表
    </button>

    <div class="detail-hero-wrap">
      <header class="detail-hero">
        <img
          v-if="college.coverImage"
          class="detail-hero-img"
          :src="college.coverImage"
          :alt="college.college"
          loading="eager"
        />
        <div class="detail-hero-bg" />
        <div class="detail-hero-inner">
          <span class="detail-hero-badge">{{ college.shortName }}</span>
          <h2 class="detail-hero-title">{{ college.college }}</h2>
          <p class="detail-hero-tagline">{{ college.tagline }}</p>
        </div>
      </header>

      <div v-if="college.stats.length" class="intro-stat-row detail-stats-float">
        <div v-for="(s, i) in college.stats" :key="i" class="intro-stat-chip">
          <span class="intro-stat-chip__val">{{ s.value }}</span>
          <span class="intro-stat-chip__label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <nav class="intro-pill-nav detail-anchors" aria-label="页面章节">
      <button type="button" @click="scrollTo('section-overview')">学院简介</button>
      <button type="button" @click="scrollTo('section-faculty')">师资队伍</button>
      <button type="button" @click="scrollTo('section-clubs')">社团招新</button>
    </nav>

    <IntroCollegeModule
      :overview-category="college.overviewCategory"
      :faculty-category="college.facultyCategory"
      :overview-fallback="college.overviewFallback"
      :faculty-fallback="college.facultyFallback"
    />

    <IntroCollegeClubs
      :college-name="college.college"
      :club-filter="college.clubFilter"
    />
  </div>
</template>

<style scoped>
.college-detail {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0;
  border: none;
  background: none;
  color: var(--intro-faint, #8b7b65);
  font-size: 0.74rem;
  cursor: pointer;
  font-family: inherit;
}

.detail-back:hover {
  color: var(--intro-accent, #b5343a);
}

.detail-hero-wrap {
  position: relative;
  margin-bottom: 6px;
}

.detail-hero {
  position: relative;
  border-radius: var(--intro-radius, 14px);
  overflow: hidden;
  min-height: 132px;
  box-shadow: 0 6px 22px rgba(60, 48, 40, 0.12);
}

.detail-hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    115deg,
    rgba(45, 12, 15, 0.9) 0%,
    rgba(84, 11, 19, 0.55) 55%,
    rgba(45, 12, 15, 0.3) 100%
  );
}

.detail-hero-inner {
  position: relative;
  z-index: 1;
  padding: 18px 16px 20px;
  color: #f2e6d0;
}

.detail-hero-badge {
  display: inline-block;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 2px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.detail-hero-title {
  margin: 8px 0 4px;
  font-size: 1.22rem;
  font-weight: 700;
  font-family: 'Noto Serif SC', Georgia, serif;
  letter-spacing: 0.06em;
}

.detail-hero-tagline {
  margin: 0;
  font-size: 0.78rem;
  opacity: 0.9;
}

.detail-stats-float {
  margin: -18px 8px 0;
  position: relative;
  z-index: 2;
}

.detail-anchors {
  position: sticky;
  top: 0;
  z-index: 6;
  padding: 4px 0 6px;
  background: rgba(250, 247, 243, 0.96);
  backdrop-filter: blur(6px);
  margin: 0 -2px;
}

@media (max-width: 768px) {
  .college-detail {
    gap: 8px;
  }

  .detail-hero {
    min-height: 118px;
    border-radius: 12px;
  }

  .detail-hero-inner {
    padding: 14px 14px 16px;
  }

  .detail-hero-title {
    font-size: 1.08rem;
  }

  .detail-stats-float {
    margin: -14px 6px 0;
  }
}
</style>
