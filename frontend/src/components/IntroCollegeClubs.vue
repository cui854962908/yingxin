<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Club } from '../types/club'
import type { IntroClubFilter } from '../constants/intro'
import {
  filterClubsByIntroGroupId,
  resolveIntroClubGroups,
} from '../constants/intro'
import { useBreakpoint } from '../composables/useBreakpoint'
import { useRefreshOnActivate } from '../composables/useRefreshOnActivate'
import AppSpinner from './AppSpinner.vue'
import ClubCard from './ClubCard.vue'
import IntroOrgGroupCard from './IntroOrgGroupCard.vue'
import '../styles/intro-theme.css'

const PAGE_SIZE_DESKTOP = 10
const PAGE_SIZE_MOBILE = 6

const props = defineProps<{
  collegeName: string
  clubFilter: IntroClubFilter
}>()

const router = useRouter()
const { isMobile } = useBreakpoint()
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
  return filterClubsByIntroGroupId(clubs.value, expandedGroupId.value, props.clubFilter)
})

const pageSize = computed(() => (isMobile.value ? PAGE_SIZE_MOBILE : PAGE_SIZE_DESKTOP))

const totalPages = computed(() => Math.max(1, Math.ceil(visible.value.length / pageSize.value)))

const pagedClubs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return visible.value.slice(start, start + pageSize.value)
})

function clubCountForGroup(groupId: string): number {
  return filterClubsByIntroGroupId(clubs.value, groupId, props.clubFilter).length
}

watch([visible, pageSize], () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})

async function load(options: { silent?: boolean } = {}) {
  if (!options.silent) loading.value = true
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

useRefreshOnActivate(
  () => load(),
  (opts) => load(opts),
)
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
      <div class="intro-subnav" aria-label="组织导航">
        <button type="button" class="intro-back-btn intro-subnav__back" @click="backToGroups">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          返回全部组织
        </button>
        <h4 class="intro-subnav__title">{{ expandedGroup.label }}</h4>
      </div>
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
          <button type="button" class="intro-pagination__edge" :disabled="currentPage === 1" @click="prevPage">上一页</button>
          <div class="intro-pagination__pages" role="group" aria-label="页码">
            <button
              v-for="page in totalPages"
              :key="page"
              type="button"
              :class="{ active: page === currentPage }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button type="button" class="intro-pagination__edge" :disabled="currentPage === totalPages" @click="nextPage">下一页</button>
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
