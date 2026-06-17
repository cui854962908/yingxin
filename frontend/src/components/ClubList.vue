<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Club } from '../types/club'
import { authHeaders, useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'
import ClubCard from './ClubCard.vue'

const router = useRouter()
const route = useRoute()
const clubs = ref<Club[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref((route.query.cat as string) || '信工团学会')
const statusMenuClubId = ref<string | null>(null)
const currentPage = ref(Number(route.query.page) || 1)
const perPage = 10

const categories = ['全部', '信工团学会', '校级组织', '兴趣社团']

const { isAdmin, isClubAdmin, student } = useAuth()
const isAnyAdmin = computed(() => isAdmin.value || isClubAdmin.value)

const filteredClubs = computed(() => {
  let result = clubs.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    // 搜索时忽略分类，全局匹配
    result = result.filter(c =>
      c.name.toLowerCase().includes(q)
      || (c.advisor_name && c.advisor_name.toLowerCase().startsWith(q)),
    )
  } else if (activeCategory.value !== '全部') {
    result = result.filter(c => c.category === activeCategory.value)
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredClubs.value.length / perPage)))
const pagedClubs = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredClubs.value.slice(start, start + perPage)
})
function goToPage(p: number) { currentPage.value = p }
function prevPage() { if (currentPage.value > 1) currentPage.value-- }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }

async function loadClubs() {
  loading.value = true
  try {
    const res = await fetch('/api/clubs')
    const d = await res.json()
    if (d.success) clubs.value = d.data
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

onMounted(loadClubs)
</script>

<template>
  <div class="clubs">
    <!-- 吸顶区：标题 + 搜索 + 分类 -->
    <div class="clubs-toolbar">
      <div class="clubs-header">
        <h3 class="clubs-title">社团介绍</h3>
        <button v-if="isAnyAdmin" class="clubs-add-btn" @click="goAdd">+ 添加社团</button>
      </div>
      <div class="clubs-search">
        <svg class="clubs-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input
          v-model="searchQuery"
          type="text"
          class="clubs-search-input"
          placeholder="搜索社团名称、介绍、指导老师…"
        />
      </div>
      <div class="clubs-categories">
        <button
          v-for="cat in categories" :key="cat"
          class="clubs-cat-btn" :class="{ active: activeCategory === cat }"
          @click="activeCategory = cat; currentPage = 1"
        >{{ cat }}</button>
      </div>
    </div>

    <div v-if="pagedClubs.length > 0" class="clubs-grid">
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

    <div v-if="totalPages > 1" class="clubs-pagination">
      <button :disabled="currentPage === 1" @click="prevPage">&lt;</button>
      <button
        v-for="p in totalPages" :key="p"
        :class="{ active: p === currentPage }"
        @click="goToPage(p)"
      >{{ p }}</button>
      <button :disabled="currentPage === totalPages" @click="nextPage">&gt;</button>
    </div>

    <div v-if="loading" class="clubs-loading">
      <AppSpinner />
    </div>
    <p v-else-if="clubs.length === 0" class="clubs-empty">暂无社团信息</p>
    <p v-else-if="pagedClubs.length === 0" class="clubs-empty">未找到匹配的社团</p>
  </div>
</template>

<style scoped>
.clubs { display: flex; flex-direction: column; gap: 16px }

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
.clubs-header { display: flex; align-items: center; justify-content: space-between }
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

.clubs-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px }

.clubs-empty { text-align: center; color: #b0a090; padding: 40px 0 24px; font-size: .88rem }
.clubs-loading { display: flex; align-items: center; justify-content: center; padding: 40px 0 }

.clubs-pagination { display: flex; justify-content: center; gap: 6px; padding: 8px 0 }
.clubs-pagination button {
  min-width: 36px; height: 36px; border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; color: #6b5e4e; font-size: .82rem; cursor: pointer;
  font-family: inherit; transition: all .2s;
}
.clubs-pagination button:hover:not(:disabled):not(.active) { border-color: #4a8c5c; color: #4a8c5c }
.clubs-pagination button.active { background: #4a8c5c; color: #fff; border-color: #4a8c5c }
.clubs-pagination button:disabled { opacity: .3; cursor: default }

@media(max-width: 1024px) {
  .clubs-grid { gap: 16px }
}
@media(max-width: 768px) {
  .clubs-toolbar { padding: 6px 14px 8px; margin: 0 -14px; gap: 8px; border-radius: 0 0 10px 10px; box-shadow: 0 1px 3px rgba(0,0,0,.06) }
  .clubs-toolbar::before { left: -14px; right: -14px }
  .clubs-grid { grid-template-columns: 1fr; gap: 16px }
}
@media(max-width: 480px) {
  .clubs-toolbar { padding: 6px 12px 8px; margin: 0 -12px }
  .clubs-toolbar::before { left: -12px; right: -12px }
  .clubs-search { max-width: 100% }
  .clubs-search-input { height: 38px; font-size: .84rem }
  .clubs-gr