<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Club } from '../types/club'
import { resolveIntroTabGroups, filterClubsByIntroGroupId } from '../constants/intro'
import type { IntroClubGroup } from '../constants/intro'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useBreakpoint } from '../composables/useBreakpoint'
import { usePanelReveal } from '../composables/usePanelReveal'
import { usePreload } from '../composables/usePreload'
import { useRefreshOnActivate } from '../composables/useRefreshOnActivate'
import AppSpinner from './AppSpinner.vue'
import ClubCard from './ClubCard.vue'
import IntroOrgGroupCard from './IntroOrgGroupCard.vue'
import '../styles/intro-theme.css'
import '../styles/panel-enter.css'

const props = withDefaults(
  defineProps<{ hideHeader?: boolean; perPage?: number }>(),
  { hideHeader: false, perPage: 10 },
)
const route = useRoute()
const router = useRouter()
const { clubs: cachedClubs } = usePreload()
const clubs = ref<Club[]>(cachedClubs.value.length ? [...cachedClubs.value] : [])
const loading = ref(!cachedClubs.value.length)
const searchQuery = ref('')
const activeCategory = ref(typeof route.query.cat === 'string' ? route.query.cat : '全部')
const statusMenuClubId = ref<string | null>(null)
const currentPage = ref(Number(route.query.page) || 1)

const categories = ['全部', '信工团学会', '校级组织', '兴趣社团']

const { isAdmin, isClubAdmin, student } = useAuth()
const { isMobile } = useBreakpoint()
const { ready: revealReady } = usePanelReveal()
const isAnyAdmin = computed(() => isAdmin.value || isClubAdmin.value)

const pageSize = computed(() => (isMobile.value ? 6 : props.perPage))

const introGroupMode = computed(
  () => props.hideHeader && !route.query.cat && !searchQuery.value.trim(),
)

const introGroups = computed(() =>
  resolveIntroTabGroups(clubs.value).map((group) => ({
    ...group,
    count:
      group.kind === 'club'
        ? 1
        : clubs.value.filter((club) => club.category === group.id).length,
  })),
)

const activeIntroGroup = computed(() => {
  const cat = route.query.cat
  if (typeof cat !== 'string' || !cat) return null
  return introGroups.value.find((group) => group.id === cat) ?? null
})

const filteredClubs = computed(() => {
  let result = clubs.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    result = result.filter(c =>
      c.name.toLowerCase().includes(q)
      || (c.advisor_name && c.advisor_name.toLowerCase().startsWith(q)),
    )
  } else if (props.hideHeader && route.query.cat) {
    result = filterClubsByIntroGroupId(result, String(route.query.cat))
  } else if (activeCategory.value !== '全部') {
    result = result.filter(c => c.category === activeCategory.value)
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredClubs.value.length / pageSize.value)))
const pagedClubs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredClubs.value.slice(start, start + pageSize.value)
})
function goToPage(p: number) { currentPage.value = p }
function prevPage() { if (currentPage.value > 1) currentPage.value-- }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }

watch([filteredClubs, pageSize], () => {
  if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
})
watch(searchQuery, () => { currentPage.value = 1 })

watch(
  () => route.query.cat,
  (cat) => {
    if (typeof cat === 'string' && categories.includes(cat)) {
      activeCategory.value = cat
      currentPage.value = 1
    } else if (!cat && props.hideHeader) {
      activeCategory.value = '全部'
    } else if (typeof cat === 'string' && cat === '校级组织' && props.hideHeader) {
      router.replace({ path: '/intro/clubs' })
    }
  },
  { immediate: true },
)

function openIntroGroup(group: IntroClubGroup & { count: number }) {
  if (group.kind === 'club') {
    goDetail(group.id.slice(5))
    return
  }
  router.replace({ path: '/intro/clubs', query: { cat: group.id } })
}

function backToIntroGroups() {
  router.replace({ path: '/intro/clubs' })
}

async function loadClubs(options: { silent?: boolean } = {}) {
  if (!options.silent) loading.value = true
  try {
    const res = await fetch('/api/clubs')
    const d = await res.json()
    if (d.success) {
      clubs.value = d.data
      cachedClubs.value = d.data
    }
  } catch { console.warn('加载社团列表失败') }
  finally { loading.value = false }
}

function goAdd() { router.push('/clubs/add') }
function goEdit(id: string) { router.push(`/clubs/${id}`) }
function goDetail(id: string) { router.push({ path: `/clubs/${id}`, query: { from: activeCategory.value, page: String(currentPage.value) } }) }

function canEdit(club: Club): boolean {
  if (isAdmin.value) return true
  if (isClubAdmin.value) return club.owner_student_id === student.value?.id
  return false
}

async function setStatus(clubId: string, status: string) {
  try {
    await fetch(`/api/admin/clubs/${clubId}/status`, {
      method: 'PATCH', headers: authHeaders(), body: JSON.stringify({ status }),
    })
    statusMenuClubId.value = null
    await loadClubs()
  } catch { /* ignore */ }
}

async function handleDelete(id: string) {
  if (!confirm('确定删除该社团吗？')) return
  try {
    await fetch(`/api/admin/clubs/${id}`, { method: 'DELETE', headers: authHeaders() })
    await loadClubs()
  } catch { console.warn('删除社团失败') }
}

useRefreshOnActivate(
  () => (cachedClubs.value.length ? loadClubs({ silent: true }) : loadClubs()),
  (opts) => loadClubs(opts),
)
</script>

<template>
  <div
    class="clubs"
    :class="{
      'clubs--intro-embed': hideHeader,
      'panel-reveal': hideHeader,
      'panel-reveal--intro': hideHeader,
      'panel-reveal--ready': hideHeader && revealReady,
    }"
  >
    <!-- 工具栏：添加 / 返回 / 搜索（Intro 顶栏单独吸顶，此处占文档流） -->
    <div class="clubs-toolbar panel-reveal__item" :class="{ 'clubs-toolbar--embed': hideHeader }">
      <div v-if="!hideHeader" class="clubs-header">
        <h3 class="clubs-title">社团介绍</h3>
        <button v-if="isAnyAdmin" class="clubs-add-btn" @click="goAdd">+ 添加社团</button>
      </div>
      <div v-else-if="isAnyAdmin" class="clubs-header clubs-header--compact">
        <button class="clubs-add-btn" @click="goAdd">+ 添加社团</button>
      </div>
      <div v-if="hideHeader && route.query.cat && activeIntroGroup" class="intro-subnav" aria-label="组织导航">
        <button type="button" class="intro-back-btn intro-subnav__back" @click="backToIntroGroups">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          返回全部组织
        </button>
        <h4 class="intro-subnav__title">{{ activeIntroGroup.label }}</h4>
      </div>
      <div v-if="!hideHeader || !route.query.cat" class="clubs-search">
        <svg class="clubs-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          class="clubs-search-input"
          placeholder="搜索社团名称、介绍、指导老师…"
        />
      </div>
      <div v-if="!hideHeader" class="clubs-categories">
        <button
          v-for="cat in categories" :key="cat"
          class="clubs-cat-btn" :class="{ active: activeCategory === cat }"
          @click="activeCategory = cat; currentPage = 1"
        >{{ cat }}</button>
      </div>
    </div>

    <div class="clubs-main panel-reveal__item">
    <div v-if="introGroupMode" class="intro-org-list">
      <IntroOrgGroupCard
        v-for="group in introGroups"
        :key="group.id"
        :label="group.label"
        :subtitle="group.subtitle"
        :count="group.count"
        :show-count="group.kind !== 'club'"
        @click="openIntroGroup(group)"
      />
    </div>

    <div v-else-if="pagedClubs.length > 0" class="clubs-grid">
      <ClubCard
        v-for="club in pagedClubs" :key="club.id"
        :club="club"
        :can-edit="canEdit(club)"
        :is-admin="isAdmin"
        :status-menu-open="statusMenuClubId === club.id"
        @click="goDetail(club.id)"
        @edit="goEdit(club.id)"
        @delete="handleDelete(club.id)"
        @update:status-menu-open="(v: boolean) => statusMenuClubId = v ? club.id : null"
        @status-change="(s: string) => setStatus(club.id, s)"
      />
    </div>

    <nav
      v-if="!introGroupMode && totalPages > 1"
      class="clubs-pagination"
      :class="{ 'intro-pagination': hideHeader }"
      aria-label="社团分页"
    >
      <button type="button" class="intro-pagination__edge" :disabled="currentPage === 1" @click="prevPage">上一页</button>
      <div class="intro-pagination__pages" role="group" aria-label="页码">
        <button
          v-for="p in totalPages"
          :key="p"
          type="button"
          :class="{ active: p === currentPage }"
          @click="goToPage(p)"
        >{{ p }}</button>
      </div>
      <button type="button" class="intro-pagination__edge" :disabled="currentPage === totalPages" @click="nextPage">下一页</button>
    </nav>

    <div v-if="loading" class="clubs-loading">
      <AppSpinner />
    </div>
    <p v-else-if="!introGroupMode && clubs.length === 0" class="clubs-empty">暂无社团信息</p>
    <p v-else-if="!introGroupMode && pagedClubs.length === 0" class="clubs-empty">未找到匹配的社团</p>
    </div>
  </div>
</template>

<style scoped>
.clubs { display: flex; flex-direction: column; gap: 16px }

.clubs--intro-embed {
  gap: 8px;
}
.clubs--intro-embed .clubs-main {
  gap: 14px;
}
.clubs--intro-embed .clubs-grid {
  padding-inline: 0;
}
.clubs--intro-embed .intro-org-list {
  gap: 12px;
}

.clubs-toolbar {
  display: flex; flex-direction: column; gap: 10px;
  position: sticky; top: 0; z-index: 20;
  background: #fff; padding: 8px 28px 12px;
  margin: 0 -28px;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.clubs-toolbar::before {
  content: ''; position: absolute; bottom: 100%; left: -28px; right: -28px;
  height: 50px; background: #fff;
  pointer-events: none;
}
.clubs-toolbar--embed {
  margin: 0;
  padding: 0;
  box-shadow: none;
  position: static;
  top: auto;
}
.clubs-toolbar--embed::before { display: none }
.clubs-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}
.clubs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}
.clubs-header--compact { justify-content: flex-start }
.clubs-header--compact .clubs-add-btn {
  margin-left: auto;
  margin-right: clamp(12px, 1.2vw, 20px);
}
.clubs-title { font-size: 1.15rem; font-weight: 700; color: #2c2c2c; letter-spacing: .06em; margin: 0 }
.clubs-add-btn {
  height: 32px; padding: 0 14px; border: 1px solid #c9a96e; border-radius: 8px;
  background: #fefcf9; color: #8b7b65; font-size: .78rem; cursor: pointer;
  font-family: inherit; transition: border-color .2s, color .2s;
}
.clubs-add-btn:hover { border-color: #4a8c5c; color: #4a8c5c }
.clubs-search {
  position: relative; max-width: 520px; width: 100%; margin: 0 auto;
}
.clubs-search-icon {
  position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
  color: #b0a090; pointer-events: none;
}
.clubs-search-input {
  width: 100%; height: 42px; padding: 0 16px 0 44px;
  border: 2px solid #e5dbcc; border-radius: 12px;
  font-size: .9rem; color: #3c3028; background: #fefcf9; outline: none;
  font-family: inherit; box-sizing: border-box; transition: border-color .2s, box-shadow .2s;
}
.clubs-search-input::placeholder { color: #c4b8a4 }
.clubs-search-input:focus {
  border-color: #4a8c5c;
  box-shadow: 0 0 0 3px rgba(74,140,92,.1);
}

.clubs-categories { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center }
.clubs-cat-btn {
  height: 30px; padding: 0 16px; border: 1px solid #e5dbcc; border-radius: 16px;
  background: #fefcf9; color: #6b5e4e; font-size: .8rem; cursor: pointer;
  font-family: inherit; transition: all .2s;
}
.clubs-cat-btn:hover { border-color: #4a8c5c; color: #4a8c5c }
.clubs-cat-btn.active { background: #4a8c5c; color: #fff; border-color: #4a8c5c }

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 0 clamp(12px, 1.2vw, 20px) 16px;
  box-sizing: border-box;
  gap: 18px;
}

.clubs-empty { text-align: center; color: #b0a090; padding: 40px 0 24px; font-size: .88rem }
.clubs-loading { display: flex; align-items: center; justify-content: center; padding: 40px 0 }

.clubs-pagination {
  display: grid;
  grid-template-columns: max-content minmax(0, 1fr) max-content;
  align-items: center;
  column-gap: 8px;
  padding: 8px 0;
  max-width: 100%;
  overflow: visible;
}

.clubs-pagination .intro-pagination__pages button {
  flex-shrink: 0;
  min-width: 36px;
  height: 36px;
  border: 1px solid #e5dbcc;
  border-radius: 8px;
  background: #fefcf9;
  color: #6b5e4e;
  font-size: 0.82rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.clubs-pagination .intro-pagination__pages button:hover:not(:disabled):not(.active) {
  border-color: #4a8c5c;
  color: #4a8c5c;
}

.clubs-pagination .intro-pagination__pages button.active {
  background: #4a8c5c;
  color: #fff;
  border-color: #4a8c5c;
}

@media(max-width: 1024px) {
  .clubs-grid { gap: 16px }
}
@media(max-width: 768px) {
  .clubs-toolbar:not(.clubs-toolbar--embed) {
    padding: 6px 14px 8px;
    margin: 0 -14px;
    gap: 8px;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }
  .clubs-toolbar:not(.clubs-toolbar--embed)::before { left: -14px; right: -14px }
  .clubs-grid { grid-template-columns: 1fr; gap: 16px; padding-inline: 12px }
}
@media(max-width:768px){
  .clubs-search { max-width: 100% }
  .clubs-search-input { height: 44px; font-size: 16px }
}
@media(max-width: 480px) {
  .clubs-toolbar:not(.clubs-toolbar--embed) { padding: 6px 12px 8px; margin: 0 -12px }
  .clubs-toolbar:not(.clubs-toolbar--embed)::before { left: -12px; right: -12px }
  .clubs-search { max-width: 100% }
  .clubs-search-input { height: 44px; font-size: 16px }
  .clubs-grid { grid-template-columns: 1fr; gap: 14px }
}
</style>
