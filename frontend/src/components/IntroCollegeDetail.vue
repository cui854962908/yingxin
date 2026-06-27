<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getIntroCollege, getIntroCollegeTabPath, INTRO_COLLEGES } from '../constants/intro'
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
    if (!getIntroCollege(id)) router.replace(getIntroCollegeTabPath())
  },
  { immediate: true },
)

function goBack() {
  appNavigate(INTRO_COLLEGES.length > 1 ? '/intro/colleges' : '/intro/wiki')
}

</script>

<template>
  <div v-if="college" class="college-detail intro-page">
    <button type="button" class="intro-back-btn" @click="goBack">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
      返回{{ INTRO_COLLEGES.length > 1 ? '学院列表' : '牧院大百科' }}
    </button>

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
      </div>
    </header>

    <section class="detail-meta">
      <div v-if="college.stats.length" class="intro-stat-row detail-stats">
        <div v-for="(s, i) in college.stats" :key="i" class="intro-stat-chip">
          <span class="intro-stat-chip__val">{{ s.value }}</span>
          <span class="intro-stat-chip__label">{{ s.label }}</span>
        </div>
      </div>
    </section>

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
  padding: 4px 4px 0;
}

.detail-hero {
  position: relative;
  border-radius: var(--intro-radius, 14px);
  overflow: hidden;
  min-height: 88px;
  max-height: 112px;
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
  display: flex;
  align-items: flex-end;
  min-height: 88px;
  padding: 12px 14px;
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

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-stats {
  margin: 0;
}

.detail-stats .intro-stat-chip {
  min-width: 0;
}

.detail-stats .intro-stat-chip__val {
  font-size: 0.95rem;
  line-height: 1.25;
  word-break: keep-all;
}

@media (max-width: 768px) {
  .college-detail {
    gap: 10px;
    padding: 0;
  }

  .detail-hero {
    border-radius: 12px;
    min-height: 80px;
    max-height: 96px;
  }

  .detail-hero-inner {
    min-height: 80px;
    padding: 10px 12px;
  }

  .detail-stats .intro-stat-chip__val {
    font-size: 0.82rem;
  }

  .detail-stats .intro-stat-chip__label {
    font-size: 0.62rem;
    line-height: 1.3;
  }
}
</style>
