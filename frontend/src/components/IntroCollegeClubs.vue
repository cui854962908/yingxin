<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Club } from '../types/club'
import type { IntroClubFilter } from '../constants/intro'
import {
  filterClubsByIntroGroup,
  resolveIntroClubGroups,
} from '../constants/intro'
import AppSpinner from './AppSpinner.vue'
import ClubCard from './ClubCard.vue'
import IntroOrgGroupCard from './IntroOrgGroupCard.vue'
import '../styles/intro-theme.css'

const PAGE_SIZE = 10

const props = defineProps<{
  collegeName: string
  clubFilter: IntroClubFilter
}>()

const router = useRouter()
const clubs = ref<Club[]>([])
const loading = ref(true)
const expandedGroupId = ref<string | null>(null)
const currentPage = ref(1)

const groups = computed(() => resolveIntroClubGroups(props.clubFilter))

const expandedGroup = computed(
  () => groups.value.find((group) => group.id === expandedGroupId.value) ?? null,
)

const visible = computed(() => {
  if (!expandedGroupId.value) return []
  return filterClubsByIntroGroup(clubs.value, props.clubFilter, expandedGroupId.value)
})

const totalPages = computed(() => Math.max(1, Math.ceil(visible.value.length / PAGE_SIZE)))

const pagedClubs = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return visible.value.slice(start, start + PAGE_SIZE)
})

function clubCountForGroup(groupId: string): number {
  return filterClubsByIntroGroup(clubs.value, props.clubFilter, groupId).length
}

watch(visible, () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})

async function load() {
  loading.value = true
  try {
    const res = await fetch('/api/clubs')
    const d = await res.json()
    if (d.success) clubs.value = d.data
  } catch {
    clubs.value = []
  } finally {
    loading.value = false
  }
}

function openGroup(groupId: string) {
  expandedGroupId.value = groupId
  currentPage.value = 1
}

function backToGroups() {
  expandedGroupId.value = null
  currentPage.value = 1
}

function goDetail(id: string) {
  router.push({ path: `/clubs/${id}`, query: { from: 'intro' } })
}

function goToPage(page: number) {
  currentPage.value = page
}

function prevPage() {
  if (currentPage.value > 1) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

onMounted(load)
</script>

<template>
  <section id="section-clubs" class="college-clubs">
    <header class="college-clubs-head">
      <span class="college-clubs-idx">社团</span>
      <h3 class="college-clubs-title">社团招新</h3>
      <p v-if="!expandedGroup" class="college-clubs-sub">
        选择学生组织，查看下属社团与招新信息
      </p>
    </header>

    <div v-if="loading" class="college-clubs-loading"><AppSpinner /></div>
    <p v-else-if="!groups.length" class="college-clubs-empty">
      暂无社团展示。管理员配置学院与社团隶属关系后将在此显示。
    </p>

    <div v-else-if="!expandedGroup" class="intro-org-list">
      <IntroOrgGroupCard
        v-for="group in groups"
        :key="group.id"
        :label="group.label"
        :subtitle="group.subtitle"
        :count="clubCountForGroup(group.id)"
        @click="openGroup(group.id)"
      />
    </div>

    <template v-else>
      <nav class="intro-org-crumb" aria-label="组织导航">
        <button type="button" @click="backToGroups">全部组织</button>
        <span class="intro-org-crumb__sep" aria-hidden="true">/</span>
        <span class="intro-org-crumb__current">{{ expandedGroup.label }}</span>
      </nav>
      <p v-if="visible.length === 0" class="college-clubs-empty">该组织下暂无社团展示。</p>
      <template v-else>
        <div class="college-clubs-grid">
          <ClubCard
            v-for="club in pagedClubs"
            :key="club.id"
            :club="club"
            :can-edit="false"
            :is-admin="false"
            :status-menu-open="false"
            @click="goDetail(club.id)"
          />
        </div>
        <nav v-if="totalPages > 1" class="intro-pagination" aria-label="社团分页">
          <button type="button" :disabled="currentPage === 1" @click="prevPage">上一页</button>
          <button
            v-for="page in totalPages"
            :key="page"
            type="button"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button type="button" :disabled="currentPage === totalPages" @click="nextPage">下一页</button>
        </nav>
      </template>
    </template>
  </section>
</template>

<style scoped>
.college-clubs {
  padding: 16px;
  border-radius: var(--intro-radius-sm, 12px);
  background: #fff;
  border: 1px solid var(--intro-line, #dedee3);
  box-shadow: 0 1px 3px rgba(21, 21, 26, 0.04);
}

.college-clubs-head {
  margin-bottom: 12px;
}

.college-clubs-idx {
  display: inline-block;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--intro-accent, #b51f2d);
  background: var(--intro-accent-soft, rgba(181, 31, 45, 0.08));
  padding: 3px 8px;
  border-radius: 6px;
}

.college-clubs-title {
  margin: 8px 0 4px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--intro-ink, #15151a);
  font-family: 'Noto Serif SC', Georgia, serif;
}

.college-clubs-sub {
  margin: 0;
  font-size: 0.74rem;
  color: var(--intro-faint, #777780);
  line-height: 1.5;
}

.college-clubs-loading {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.college-clubs-empty {
  margin: 0;
  text-align: center;
  font-size: 0.78rem;
  color: var(--intro-faint, #777780);
  padding: 16px 0;
}

.college-clubs-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 768px) {
  .college-clubs {
    padding: 14px 12px;
  }

  .college-clubs-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
</style>
