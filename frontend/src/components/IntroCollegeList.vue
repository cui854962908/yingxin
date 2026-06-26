<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { INTRO_COLLEGES } from '../constants/intro'
import { usePanelReveal } from '../composables/usePanelReveal'
import '../styles/intro-theme.css'
import '../styles/panel-enter.css'

const router = useRouter()
const { ready: revealReady } = usePanelReveal()

/** 当前仅信工一个学院时直达详情，保留列表组件供日后扩展 */
onMounted(() => {
  if (INTRO_COLLEGES.length === 1) {
    router.replace(`/intro/${INTRO_COLLEGES[0].id}`)
  }
})

function openCollege(id: string) {
  router.push(`/intro/${id}`)
}
</script>

<template>
  <div
    class="college-list intro-page panel-reveal panel-reveal--intro"
    :class="{ 'panel-reveal--ready': revealReady }"
  >
    <p class="college-list-hint panel-reveal__item">点击进入学院详情，了解简介、师资与本院社团</p>
    <div class="college-grid panel-reveal__item">
      <button
        v-for="c in INTRO_COLLEGES" :key="c.id"
        type="button"
        class="college-card"
        @click="openCollege(c.id)"
      >
        <div class="college-card-cover">
          <img
            v-if="c.coverImage"
            :src="c.coverImage"
            :alt="c.college"
            loading="lazy"
          />
          <div v-else class="college-card-cover-fallback">
            <span class="college-card-badge">{{ c.shortName }}</span>
          </div>
          <div class="college-card-shade" />
          <span class="college-card-short">{{ c.shortName }}</span>
        </div>
        <div class="college-card-body">
          <h3 class="college-card-name">{{ c.college }}</h3>
          <p class="college-card-tagline">{{ c.tagline }}</p>
          <p class="college-card-summary">{{ c.summary }}</p>
          <span class="college-card-enter">查看详情</span>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.college-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.college-list-hint {
  margin: 0;
  font-size: 0.76rem;
  color: var(--intro-faint, #8b7b65);
  line-height: 1.45;
}

.college-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.college-card {
  display: flex;
  flex-direction: column;
  text-align: left;
  padding: 0;
  border: 1px solid var(--intro-line, #f0e8dc);
  border-radius: var(--intro-radius, 14px);
  background: #fff;
  cursor: pointer;
  font-family: inherit;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
  -webkit-tap-highlight-color: transparent;
  box-shadow: 0 2px 12px rgba(60, 48, 40, 0.05);
}

.college-card:active {
  transform: scale(0.985);
}

.college-card:hover {
  box-shadow: 0 8px 24px rgba(60, 48, 40, 0.1);
  transform: translateY(-2px);
}

.college-card-cover {
  position: relative;
  height: 108px;
  overflow: hidden;
  background: linear-gradient(135deg, #75171d, #b5343a);
}

.college-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.college-card-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 30%, rgba(45, 12, 15, 0.55) 100%);
}

.college-card-short {
  position: absolute;
  bottom: 8px;
  left: 10px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #f2e6d0;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(4px);
}

.college-card-cover-fallback {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.college-card-badge {
  font-size: 1.8rem;
  font-weight: 700;
  color: rgba(242, 230, 208, 0.9);
  font-family: 'Noto Serif SC', Georgia, serif;
}

.college-card-body {
  padding: 12px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.college-card-name {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 700;
  color: var(--intro-ink, #3c3028);
  font-family: 'Noto Serif SC', Georgia, serif;
}

.college-card-tagline {
  margin: 0;
  font-size: 0.68rem;
  color: var(--intro-accent, #b5343a);
}

.college-card-summary {
  margin: 2px 0 0;
  font-size: 0.76rem;
  line-height: 1.55;
  color: var(--intro-muted, #6b5e4e);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.college-card-enter {
  margin-top: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--intro-accent, #b5343a);
}

@media (max-width: 768px) {
  .college-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
