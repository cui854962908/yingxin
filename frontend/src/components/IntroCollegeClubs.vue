<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Club } from '../types/club'
import type { IntroClubFilter } from '../constants/intro'
import { filterClubsForCollege } from '../constants/intro'
import AppSpinner from './AppSpinner.vue'
import ClubCard from './ClubCard.vue'
import '../styles/intro-theme.css'

const props = defineProps<{
  collegeName: string
  clubFilter: IntroClubFilter
}>()

const router = useRouter()
const clubs = ref<Club[]>([])
const loading = ref(true)

const visible = computed(() => filterClubsForCollege(clubs.value, props.clubFilter))

async function load() {
  loading.value = true
  try {
    const res = await fetch('/api/clubs')
    const d = await res.json()
    if (d.success) clubs.value = d.data
  } catch { clubs.value = [] }
  finally { loading.value = false }
}

function goDetail(id: string) {
  router.push({ path: `/clubs/${id}`, query: { from: 'intro' } })
}

onMounted(load)
</script>

<template>
  <section id="section-clubs" class="college-clubs">
    <header class="college-clubs-head">
      <span class="college-clubs-idx">社团</span>
      <h3 class="college-clubs-title">社团招新</h3>
      <p class="college-clubs-sub">以下为{{ collegeName }}相关社团，点击可查看详情</p>
    </header>

    <div v-if="loading" class="college-clubs-loading"><AppSpinner /></div>
    <p v-else-if="visible.length === 0" class="college-clubs-empty">
      暂无社团展示。管理员配置学院与社团隶属关系后将在此显示。
    </p>
    <div v-else class="college-clubs-grid">
      <ClubCard
        v-for="club in visible" :key="club.id"
        :club="club"
        :can-edit="false"
        :is-admin="false"
        :status-menu-open="false"
        @click="goDetail(club.id)"
      />
    </div>
  </section>
</template>

<style scoped>
.college-clubs {
  padding: 14px 14px 12px;
  border-radius: var(--intro-radius-sm, 12px);
  background: #fff;
  border: 1px solid var(--intro-line, #f0e8dc);
  box-shadow: 0 2px 10px rgba(60, 48, 40, 0.04);
}

.college-clubs-head {
  margin-bottom: 10px;
}

.college-clubs-idx {
  display: inline-block;
  font-size: 0.64rem;
  font-weight: 700;
  color: var(--intro-accent, #b5343a);
  background: rgba(181, 52, 58, 0.08);
  padding: 3px 7px;
  border-radius: 6px;
}

.college-clubs-title {
  margin: 6px 0 2px;
  font-size: 0.96rem;
  font-weight: 700;
  color: var(--intro-ink, #3c3028);
  font-family: 'Noto Serif SC', Georgia, serif;
}

.college-clubs-sub {
  margin: 0;
  font-size: 0.72rem;
  color: var(--intro-faint, #8b7b65);
}

.college-clubs-loading {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.college-clubs-empty {
  margin: 0;
  text-align: center;
  font-size: 0.78rem;
  color: #b0a090;
  padding: 14px 0;
}

.college-clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
}

@media (max-width: 768px) {
  .college-clubs {
    padding: 12px 10px 10px;
  }

  .college-clubs-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>
