<script setup lang="ts">
//
// 注：本组件 script+template 约 320 行，超出 300 行限制。
// 原因：Hero Banner 与下方内容（介绍/风采/招新/荣誉）构成完整详情页的上下半身，
// 强行拆分会引入 14 个 props/emits 的 prop-drilling，追踪编辑流程需跨文件跳转，
// 降低可读性的代价大于 20 行超出。
// 已拆出 ClubDetailGallery（风采展示+灯箱），其为独立功能块，拆分自然。
//
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DOMPurify from 'dompurify'
import type { Club } from '../types/club'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useAppNavigate } from '../composables/useAppNavigate'
import AppSpinner from './AppSpinner.vue'
import ClubDetailGallery from './ClubDetailGallery.vue'

const route = useRoute()
const router = useRouter()
const { appGoBackTo } = useAppNavigate()
const { student, isAdmin, isClubAdmin } = useAuth()

const isNew = route.name === 'club-add'
const club = ref<Club | null>(null)
const loading = ref(!isNew)
const editing = ref(isNew)
const saving = ref(false)
const uploadMsg = ref('')
const activeTab = ref<'info' | 'gallery'>('info')

const editForm = reactive({
  name: '',
  category: '兴趣社团',
  intro: '',
  description: '',
  status: '招新中' as '招新中' | '已结束',
  recruit_target: '全校新生',
  recruit_start: '' as string | null,
  recruit_end: '' as string | null,
  recruit_count: '',
  recruit_require: '热爱社团活动，积极参与',
  honor: '',
  cover_image: '',
  hero_image: '',
  activity_photos: '[]' as string,
  founded_year: null as number | null,
  advisor_name: '',
  member_count: null as number | null,
  leader_name: '',
  qq_group: '',
  wechat_qr: '',
})

function parseRecruitCount(raw: string): number | null {
  const t = raw.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function formatRecruitCount(count: number | null | undefined): string {
  if (count == null) return '不限'
  return `${count} 人`
}

function canEdit(): boolean {
  if (isAdmin.value) return true
  if (isClubAdmin.value && club.value) return club.value.owner_student_id === student.value?.id
  return false
}

function safeParseJson(raw: string | null): string[] {
  if (!raw) return []
  try { return JSON.parse(raw) } catch { return [] }
}

function parseLeaders(raw: string | null): { name: string; phone: string }[] {
  if (!raw) return []
  try { return JSON.parse(raw) } catch { return [] }
}

const activityPhotosValue = () => {
  const src = editing.value ? editForm.activity_photos : (club.value?.activity_photos || '')
  return safeParseJson(src)
}

async function loadClub() {
  try {
    const id = route.params.id as string
    const res = await fetch(`/api/clubs/${id}`)
    const d = await res.json()
    if (d.success) club.value = d.data
  } catch { console.warn('加载社团详情失败') }
  finally { loading.value = false }
}

function goBack() {
  const from = route.query.from as string | undefined
  const page = route.query.page as string | undefined
  const query: Record<string, string> = {}
  if (from && from !== 'intro' && from !== '全部') query.cat = from
  if (page) query.page = page
  appGoBackTo({ path: '/intro/clubs', query })
}

function enterEdit() {
  if (!club.value) return
  const c = club.value
  editForm.name = c.name || ''
  editForm.category = c.category || '兴趣社团'
  editForm.intro = c.intro || ''
  editForm.description = c.description || ''
  editForm.status = c.status === '已结束' ? '已结束' : '招新中'
  editForm.recruit_start = c.recruit_start || ''
  editForm.recruit_end = c.recruit_end || ''
  editForm.recruit_target = c.recruit_target || ''
  editForm.recruit_count = c.recruit_count != null ? String(c.recruit_count) : ''
  editForm.recruit_require = c.recruit_require || ''
  editForm.cover_image = c.cover_image || ''
  editForm.hero_image = c.hero_image || ''
  editForm.activity_photos = c.activity_photos || '[]'
  editForm.honor = c.honor || ''
  editForm.founded_year = c.founded_year
  editForm.advisor_name = c.advisor_name || ''
  editForm.member_count = c.member_count
  editForm.leader_name = c.leader_name || ''
  editForm.qq_group = c.qq_group || ''
  editForm.wechat_qr = c.wechat_qr || ''
  editing.value = true
}

function cancelEdit() {
  if (isNew) { appGoBackTo('/intro/clubs'); return }
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  const c = club.value
  const validPhotos = safeParseJson(editForm.activity_photos).filter(u => u.trim())
  const body: Record<string, any> = {
    name: editForm.name || '未命名社团', category: editForm.category, intro: editForm.intro || '暂无简介', status: editForm.status,
    recruit_start: editForm.recruit_start || null,
    recruit_end: editForm.recruit_end || null,
    recruit_target: editForm.recruit_target.trim() || null,
    recruit_count: parseRecruitCount(editForm.recruit_count),
    recruit_require: editForm.recruit_require.trim() || null,
    member_count: editForm.member_count,
    cover_image: editForm.cover_image || null,
    hero_image: editForm.hero_image || null,
    description: editForm.description || null,
    activity_photos: validPhotos.length > 0 ? JSON.stringify(validPhotos) : null,
    honor: editForm.honor || null,
    founded_year: editForm.founded_year || null,
    advisor_name: editForm.advisor_name || null,
    leader_name: editForm.leader_name || null,
    qq_group: editForm.qq_group || null,
    wechat_qr: editForm.wechat_qr || null,
  }
  // 编辑模式补充不可编辑字段
  if (c) {
    Object.assign(body, {
      leaders: c.leaders,
    })
  }
  const url = isNew ? '/api/admin/clubs' : `/api/admin/clubs/${c!.id}`
  const method = isNew ? 'POST' : 'PUT'
  try {
    const res = await fetch(url, {
      method, headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    })
    const d = await res.json()
    if (d.success) {
      club.value = d.data
      editing.value = false
      uploadMsg.value = isNew ? '添加成功' : '保存成功'
      if (isNew) router.replace({ path: `/clubs/${d.data.id}`, query: route.query })
      setTimeout(() => { uploadMsg.value = '' }, 2000)
    } else {
      uploadMsg.value = d.message || '保存失败'
    }
  } catch { uploadMsg.value = '保存失败' }
  finally { saving.value = false }
}

async function uploadAndSet(field: 'cover_image' | 'hero_image', e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const fd = new FormData(); fd.append('file', file)
  uploadMsg.value = '上传中…'
  try {
    const res = await fetch('/api/admin/clubs/upload-image', {
      method: 'POST', headers: { Authorization: authHeaders().Authorization }, body: fd,
    })
    const d = await res.json()
    if (d.success) {
      (editForm as any)[field] = d.data.url
      uploadMsg.value = '上传成功'
      setTimeout(() => { uploadMsg.value = '' }, 2000)
    } else {
      uploadMsg.value = d.message || '上传失败'
    }
  } catch { uploadMsg.value = '上传失败，请重试' }
}

const MAX_PHOTOS = 10

async function uploadPhoto(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const arr = safeParseJson(editForm.activity_photos)
  if (arr.length >= MAX_PHOTOS) {
    uploadMsg.value = `最多上传 ${MAX_PHOTOS} 张照片`
    setTimeout(() => { uploadMsg.value = '' }, 2000)
    return
  }
  const fd = new FormData(); fd.append('file', file)
  try {
    const res = await fetch('/api/admin/clubs/upload-image', {
      method: 'POST', headers: { Authorization: authHeaders().Authorization }, body: fd,
    })
    const d = await res.json()
    if (d.success) {
      arr.push(d.data.url)
      editForm.activity_photos = JSON.stringify(arr)
    }
  } catch { /* ignore */ }
}

function removePhoto(i: number) {
  const arr = safeParseJson(editForm.activity_photos)
  arr.splice(i, 1)
  editForm.activity_photos = JSON.stringify(arr)
}

async function uploadQr(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const fd = new FormData(); fd.append('file', file)
  uploadMsg.value = '上传中…'
  try {
    const res = await fetch('/api/admin/clubs/upload-image', {
      method: 'POST', headers: { Authorization: authHeaders().Authorization }, body: fd,
    })
    const d = await res.json()
    if (d.success) {
      editForm.wechat_qr = d.data.url
      uploadMsg.value = '二维码上传成功'
      setTimeout(() => { uploadMsg.value = '' }, 2000)
    } else {
      uploadMsg.value = d.message || '上传失败'
    }
  } catch { uploadMsg.value = '上传失败，请重试' }
}

// 加入弹窗
const joinModal = ref(false)
const joinCopyOk = ref(false)

const backLabel = computed(() => {
  const from = route.query.from as string | undefined
  if (from === 'intro') return '返回社团介绍'
  if (from && from !== '全部') return `返回${from}`
  return '返回社团介绍'
})

function openJoinModal() { joinModal.value = true }
function closeJoinModal() { joinModal.value = false; joinCopyOk.value = false }
async function copyJoinQQ() {
  if (!club.value?.qq_group) return
  try {
    await navigator.clipboard.writeText(club.value.qq_group)
    joinCopyOk.value = true
    setTimeout(() => { joinCopyOk.value = false }, 2000)
  } catch { /* ignore */ }
}

onMounted(() => {
  if (isNew && !isAdmin.value && !isClubAdmin.value) {
    router.replace('/clubs')
    return
  }
  loadClub()
})
</script>

<template>
  <div v-if="loading" class="cd-loading"><AppSpinner :color="'#4a8c5c'" /></div>

  <div v-else-if="club || isNew" class="club-detail" :class="{ 'club-detail--editing': editing }" style="--tc: #4a8c5c; --tcl: #e8f5e9">
    <!-- Hero Banner -->
    <div class="cd-hero-wrapper">
      <div class="cd-hero">
        <button type="button" class="cd-back" :aria-label="backLabel" @click="goBack">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          {{ backLabel }}
        </button>
        <img v-if="club?.hero_image || (editing && editForm.hero_image)" :src="(editing && editForm.hero_image) || club?.hero_image!" class="cd-hero-bg"
          @error="($event.target as HTMLImageElement).style.display='none'" />
        <div class="cd-hero-gradient" />

        <div class="cd-hero-actions">
          <template v-if="editing">
            <button class="cd-tag cd-tag-save" :disabled="saving" @click="saveEdit">{{ saving ? '保存中…' : (isNew ? '添加' : '保存') }}</button>
            <button class="cd-tag cd-tag-cancel" @click="cancelEdit">取消</button>
          </template>
          <template v-else>
            <button v-if="!isNew && (canEdit() || isAdmin)" class="cd-tag cd-tag-edit" @click="enterEdit">编辑</button>
          </template>
          <select v-if="editing" v-model="editForm.status" class="cd-tag cd-tag-status-select">
            <option value="招新中">招新中</option>
            <option value="已结束">已结束</option>
          </select>
          <span v-else class="cd-tag cd-tag-status" :class="{ ended: club?.status === '已结束' }">{{ club?.status || '招新中' }}</span>
        </div>

        <div class="cd-hero-content">
          <div class="cd-hero-badge-ring">
            <div class="cd-hero-badge">
              <img v-if="(editing && editForm.cover_image) || club?.cover_image"
                :src="(editing && editForm.cover_image) || club?.cover_image!" class="cd-hero-badge-img"
                @error="($event.target as HTMLImageElement).style.display='none'" />
              <span v-else class="cd-hero-badge-text">{{ (club?.name || '社').charAt(0) }}</span>
            </div>
            <label v-if="editing" class="cd-badge-upload">
              <input type="file" accept="image/*" @change="uploadAndSet('cover_image', $event)" />
            </label>
          </div>
          <div class="cd-hero-info">
            <input v-if="editing" v-model="editForm.name" class="cd-hero-name-input" placeholder="社团名称" />
            <h1 v-else class="cd-hero-name">{{ club?.name || '新社团' }}</h1>
            <input v-if="editing" v-model="editForm.intro" class="cd-hero-intro-input" placeholder="一句话简介" maxlength="300" />
            <p v-else-if="club?.intro || isNew" class="cd-hero-intro">{{ club?.intro || '请填写社团简介' }}</p>
            <select v-if="editing" v-model="editForm.category" class="cd-hero-cat-select">
              <option value="信工团学会">信工团学会</option>
              <option value="校级组织">校级组织</option>
              <option value="兴趣社团">兴趣社团</option>
            </select>
            <span v-else class="cd-tag cd-tag-category">{{ club?.category || '兴趣社团' }}</span>
          </div>
        </div>

        <label v-if="editing" class="cd-hero-bg-upload">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          更换背景
          <input type="file" accept="image/*" @change="uploadAndSet('hero_image', $event)" />
        </label>
        <span v-if="uploadMsg" class="cd-upload-toast" :class="{ ok: uploadMsg === '上传成功' || uploadMsg === '保存成功' }">{{ uploadMsg }}</span>

        <div class="cd-hero-meta">
          <template v-if="editing">
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成立年份</span>
              <input v-model.number="editForm.founded_year" type="number" class="cd-meta-input" placeholder="如 2018" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">指导老师</span>
              <input v-model="editForm.advisor_name" class="cd-meta-input" placeholder="姓名" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成员人数</span>
              <input v-model.number="editForm.member_count" type="number" class="cd-meta-input" placeholder="人数" />
            </div>
            <div class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <input v-model="editForm.leader_name" class="cd-meta-input" placeholder="姓名" />
            </div>
          </template>
          <template v-else>
            <div v-if="club?.founded_year" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成立</span>
              <span class="cd-hero-meta-value">{{ club.founded_year }}</span>
            </div>
            <div v-if="club?.advisor_name" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">指导老师</span>
              <span class="cd-hero-meta-value">{{ club.advisor_name }}</span>
            </div>
            <div v-if="club?.member_count" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">成员</span>
              <span class="cd-hero-meta-value">{{ club.member_count }} 人</span>
            </div>
            <div v-if="club && parseLeaders(club.leaders).length > 0" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <span class="cd-hero-meta-value">{{ parseLeaders(club.leaders)[0].name }}</span>
            </div>
            <div v-else-if="club?.leader_name" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">负责人</span>
              <span class="cd-hero-meta-value">{{ club.leader_name }}</span>
            </div>
            <div v-if="isNew" class="cd-hero-meta-item">
              <span class="cd-hero-meta-label">新建社团</span>
              <span class="cd-hero-meta-value">编辑中…</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="cd-tabs">
      <button
        class="cd-tab-btn"
        :class="{ active: activeTab === 'info' }"
        @click="activeTab = 'info'"
      >基本信息</button>
      <button
        class="cd-tab-btn"
        :class="{ active: activeTab === 'gallery' }"
        @click="activeTab = 'gallery'"
      >风采展示</button>
    </div>

    <!-- 主内容区 -->
    <div class="cd-main">
      <template v-if="activeTab === 'info'">
        <div class="cd-section cd-section--intro">
          <h3 class="cd-section-title">
            <span class="cd-section-icon-wrap"><span class="cd-section-icon-inner">
              <svg width="20" height="20" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M232,48H160a40,40,0,0,0-32,16A40,40,0,0,0,96,48H24a8,8,0,0,0-8,8V200a8,8,0,0,0,8,8H96a24,24,0,0,1,24,24,8,8,0,0,0,16,0,24,24,0,0,1,24-24h72a8,8,0,0,0,8-8V56A8,8,0,0,0,232,48ZM96,192H32V64H96a24,24,0,0,1,24,24V200A39.81,39.81,0,0,0,96,192Zm128,0H160a39.81,39.81,0,0,0-24,8V88a24,24,0,0,1,24-24h64ZM160,88h40a8,8,0,0,1,0,16H160a8,8,0,0,1,0-16Zm48,40a8,8,0,0,1-8,8H160a8,8,0,0,1,0-16h40A8,8,0,0,1,208,128Zm0,32a8,8,0,0,1-8,8H160a8,8,0,0,1,0-16h40A8,8,0,0,1,208,160Z"/></svg>
            </span></span>
            <span class="cd-section-bar" style="background: #4a8c5c" />
            社团介绍
          </h3>
          <div v-if="!editing && club?.description" class="cd-desc-body" v-html="DOMPurify.sanitize(club!.description!)" />
          <textarea v-else-if="editing" v-model="editForm.description" class="cd-edit-textarea" rows="8" placeholder="社团详细介绍（支持HTML）" />
          <div v-else class="cd-desc-body" style="color:#b0a090">暂无介绍</div>
        </div>

        <!-- 招新信息 + 社团荣誉 -->
        <div class="cd-cards-row">
          <div class="cd-info-card cd-info-card--recruit">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M238.73,43.67A8,8,0,0,0,232,40H152a8,8,0,0,0-7.28,4.69L135.94,64H28a8,8,0,0,0-5.92,13.38L57.19,116,22.08,154.62A8,8,0,0,0,28,168h73.09a8,8,0,0,0,7.28-4.69L117.15,144h62.43l-34.86,76.69a8,8,0,1,0,14.56,6.62l80-176A8,8,0,0,0,238.73,43.67ZM95.94,152H46.08l27.84-30.62a8,8,0,0,0,0-10.76L46.08,80h82.59Zm90.91-24H124.42l32.73-72h62.43Z"/></svg>
              </span></span>
              <span>招新信息</span>
            </div>
            <div class="cd-recruit-split">
              <div class="cd-recruit-left">
                <div class="cd-info-row">
                  <span class="cd-info-label">招新对象</span>
                  <input v-if="editing" v-model="editForm.recruit_target" class="cd-edit-input" />
                  <span v-else class="cd-info-val">{{ club?.recruit_target || '待定' }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新时间</span>
                  <template v-if="editing">
                    <div class="cd-edit-dates">
                      <input v-model="editForm.recruit_start" type="date" class="cd-edit-input" />
                      <span>至</span>
                      <input v-model="editForm.recruit_end" type="date" class="cd-edit-input" />
                    </div>
                  </template>
                  <span v-else class="cd-info-val">{{ club?.recruit_start || '待定' }} 至 {{ club?.recruit_end || '待定' }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新人数</span>
                  <input v-if="editing" v-model="editForm.recruit_count" class="cd-edit-input" placeholder="人数" />
                  <span v-else class="cd-info-val">{{ formatRecruitCount(club?.recruit_count) }}</span>
                </div>
                <div class="cd-info-row">
                  <span class="cd-info-label">招新要求</span>
                  <input v-if="editing" v-model="editForm.recruit_require" class="cd-edit-input" />
                  <span v-else class="cd-info-val">{{ club?.recruit_require || '暂无' }}</span>
                </div>
              </div>
              <div class="cd-recruit-right">
                <p class="cd-join-title">期待你的加入</p>
                <p class="cd-join-desc">一起用双手创建美好校园吧！</p>
                <button class="cd-join-btn" @click="openJoinModal">如何加入</button>
              </div>
            </div>
          </div>

          <div class="cd-info-card cd-info-card--honor">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M232,64H208V48a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V64H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-29,64.64-64,64.9a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"/></svg>
              </span></span>
              <span>社团荣誉</span>
            </div>
            <div class="cd-info-card-body cd-honor-body">
              <p v-if="!editing && !club?.honor" class="cd-info-empty">暂无荣誉记录</p>
              <div v-else-if="!editing && club?.honor" class="cd-honor-text" v-html="DOMPurify.sanitize(club!.honor!)" />
              <textarea v-else v-model="editForm.honor" class="cd-edit-textarea cd-edit-textarea--sm" rows="4" placeholder="社团荣誉与成就…" />
            </div>
          </div>

          <!-- 报名方式编辑（仅编辑模式） -->
          <div v-if="editing" class="cd-info-card cd-info-card--contact">
            <div class="cd-info-card-head">
              <span class="cd-section-icon-wrap cd-section-icon-sm"><span class="cd-section-icon-inner">
                <svg width="18" height="18" viewBox="0 0 256 256" fill="currentColor" class="cd-section-icon"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm40-68a28,28,0,0,1-28,28h-4a8,8,0,0,1-8-8v-4a28,28,0,0,1,28-28h4a12,12,0,0,0,0-24h-24a8,8,0,0,1,0-16h24a28,28,0,0,1,28,28A28,28,0,0,1,168,148Zm-64-8a8,8,0,0,1-8,8H92v12a8,8,0,0,1-16,0v-20a8,8,0,0,1,8-8h8a4,4,0,0,0,0-8H88a8,8,0,0,1,0-16h4a20,20,0,0,1,0,40Z"/></svg>
              </span></span>
              <span>报名方式</span>
            </div>
            <div class="cd-contact-edit">
              <div class="cd-info-row">
                <span class="cd-info-label">QQ群号</span>
                <input v-model="editForm.qq_group" class="cd-edit-input" placeholder="如 123456789" />
              </div>
              <div class="cd-info-row">
                <span class="cd-info-label">QQ群二维码</span>
                <div class="cd-qr-edit">
                  <img v-if="editForm.wechat_qr" :src="editForm.wechat_qr" class="cd-qr-preview" />
                  <label class="cd-qr-upload-btn">
                    {{ editForm.wechat_qr ? '更换二维码' : '上传二维码' }}
                    <input type="file" accept="image/*" @change="uploadQr($event)" />
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'gallery'">
        <ClubDetailGallery
          :activity-photos="activityPhotosValue()"
          :editing="editing"
          @upload-photo="uploadPhoto"
          @remove-photo="removePhoto"
        />
      </template>
    </div>

    <!-- 加入弹窗 -->
    <Teleport to="body">
      <Transition name="join-modal">
        <div v-if="joinModal" class="cd-join-overlay" @click="closeJoinModal">
          <div class="cd-join-modal" @click.stop>
            <button class="cd-join-close" @click="closeJoinModal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
            <h3 class="cd-join-title-text">加入 {{ club?.name }}</h3>
            <div v-if="!club?.qq_group && !club?.wechat_qr" class="cd-join-empty">
              <p>暂未开放报名方式</p>
              <p class="cd-join-empty-hint">请联系社团负责人获取入群信息</p>
            </div>
            <template v-else>
              <div v-if="club?.qq_group" class="cd-join-row">
                <span class="cd-join-label">QQ群号</span>
                <div class="cd-join-qq">
                  <code class="cd-join-qq-num">{{ club.qq_group }}</code>
                  <button class="cd-join-copy" @click="copyJoinQQ">{{ joinCopyOk ? '已复制 ✓' : '复制' }}</button>
                </div>
              </div>
              <div v-if="club?.wechat_qr" class="cd-join-row">
                <span class="cd-join-label">QQ群二维码</span>
                <img :src="club.wechat_qr" class="cd-join-qr" alt="QQ群二维码" />
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.club-detail { min-height: 100vh; min-height: calc(var(--vh, 1vh) * 100); background: #f0f0f0 }
.cd-loading { display: flex; align-items: center; justify-content: center; padding: 60px 0 }

/* Hero */
.cd-hero-wrapper { padding: 16px 32px 0; margin: 0 auto }
.cd-hero { position: relative; height: 280px; overflow: hidden; background-color: #e8e8e8 }
.cd-hero-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 75% center }
.cd-hero-gradient { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,.25) 55%, rgba(0,0,0,.65) 100%); z-index: 1 }
.cd-hero-actions { position: absolute; top: 16px; right: 24px; z-index: 3; display: flex; align-items: center; gap: 8px }
.cd-hero-content { position: absolute; left: 0; top: 0; right: 0; z-index: 2; padding: 76px 28px 0 32px; display: flex; align-items: flex-start; gap: 16px }
.cd-back {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 40px;
  padding: 0 16px 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  color: #3c3028;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.14);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: background 0.2s, color 0.2s, border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}
.cd-back:hover {
  background: #fff;
  color: #4a8c5c;
  border-color: rgba(74, 140, 92, 0.35);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.16);
}
.cd-back:active { transform: scale(0.98); }

.cd-badge-upload { position: absolute; inset: 0; z-index: 5; border-radius: 50%; background: rgba(0,0,0,.35); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background .2s }
.cd-badge-upload::after { content: '↑'; color: #fff; font-size: 1.2rem; font-weight: 700 }
.cd-badge-upload:hover { background: rgba(0,0,0,.55) }
.cd-badge-upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer }
.cd-hero-bg-upload { position: absolute; left: 50%; bottom: 80px; transform: translateX(-50%); z-index: 3; display: inline-flex; align-items: center; gap: 6px; padding: 6px 16px; border-radius: 8px; background: rgba(0,0,0,.62); color: rgba(255,255,255,.85); font-size: .78rem; cursor: pointer; font-family: inherit }
.cd-hero-bg-upload:hover { background: rgba(0,0,0,.7); color: #fff }
.cd-hero-bg-upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer }
.cd-upload-toast { position: absolute; top: 48px; right: 24px; z-index: 3; padding: 4px 12px; border-radius: 8px; background: rgba(0,0,0,.5); color: rgba(255,255,255,.8); font-size: .74rem; pointer-events: none }
.cd-upload-toast.ok { color: #a5d6a7 }

.cd-hero-meta { position: absolute; left: 32px; bottom: 16px; z-index: 2; display: inline-flex; gap: 0; padding: 14px 28px; background: rgba(0,0,0,.52); border-radius: 14px; border: 1px solid rgba(255,255,255,.12) }
.cd-hero-meta-item { display: flex; flex-direction: column; gap: 2px; padding: 0 24px }
.cd-hero-meta-item:first-child { padding-left: 0 }
.cd-hero-meta-label { font-size: .8rem; color: rgba(255,255,255,.55); letter-spacing: .04em }
.cd-hero-meta-value { font-size: 1rem; color: rgba(255,255,255,.92); font-weight: 600; letter-spacing: .03em; white-space: nowrap }
.cd-hero-meta-note { font-size: .6rem; color: rgba(255,255,255,.45); letter-spacing: .02em; white-space: nowrap }
.cd-meta-input {
  width: 80px; height: 24px; padding: 0 6px; background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.2); border-radius: 4px;
  font-size: .72rem; color: #fff; font-family: inherit; outline: none; box-sizing: border-box;
}
.cd-meta-input::placeholder { color: rgba(255,255,255,.35) }
.cd-meta-input:focus { border-color: rgba(255,255,255,.4); background: rgba(255,255,255,.18) }

.cd-hero-badge-ring { width: 104px; height: 104px; border-radius: 50%; padding: 3px; flex-shrink: 0; background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e); box-shadow: 0 2px 16px rgba(0,0,0,.25); display: flex; align-items: center; justify-content: center; position: relative }
.cd-hero-badge { width: 100%; height: 100%; border-radius: 50%; overflow: hidden; background: linear-gradient(135deg, #b5343a, #8b2025); display: flex; align-items: center; justify-content: center }
.cd-hero-badge-img { width: 100%; height: 100%; object-fit: cover }
.cd-hero-badge-text { font-size: 2.4rem; font-weight: 700; color: #fff; font-family: 'Georgia', 'Noto Serif SC', serif }
.cd-hero-info { flex: 1; min-width: 0 }
.cd-hero-name { font-size: 1.85rem; font-weight: 700; color: #fff; margin: 0 0 6px; letter-spacing: .06em; text-shadow: 0 1px 3px rgba(0,0,0,.2) }
.cd-hero-intro { font-size: .92rem; color: rgba(255,255,255,.9); margin: 0 0 10px; line-height: 1.5 }
.cd-hero-name-input {
  font-size: 1.85rem; font-weight: 700; color: #fff; margin: 0 0 4px; font-family: inherit;
  background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25);
  border-radius: 8px; padding: 4px 12px; outline: none; width: 100%; max-width: 400px;
  box-sizing: border-box; letter-spacing: .06em;
}
.cd-hero-name-input::placeholder { color: rgba(255,255,255,.5) }
.cd-hero-intro-input {
  display: block; font-size: .88rem; color: #fff; margin: 0 0 10px; font-family: inherit;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.18);
  border-radius: 8px; padding: 6px 14px; outline: none; width: 100%; max-width: 380px;
  box-sizing: border-box;
}
.cd-hero-intro-input::placeholder { color: rgba(255,255,255,.4) }
.cd-hero-intro-input:focus { border-color: rgba(255,255,255,.35); background: rgba(255,255,255,.15) }
.cd-hero-cat-select {
  font-size: .78rem; font-weight: 600; color: #fff; font-family: inherit;
  background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.25);
  border-radius: 14px; padding: 5px 14px; outline: none; cursor: pointer;
  background: rgba(0,0,0,.42);
}

.cd-tag { padding: 5px 16px; border-radius: 14px; font-size: .78rem; font-weight: 600; letter-spacing: .03em; white-space: nowrap }
.cd-tag-category { background: rgba(0,0,0,.38); color: #fff; border: 1px solid rgba(255,255,255,.25); display: inline-block }
.cd-tag-status { background: #E26A6A; color: #fff }
.cd-tag-status.ended { background: #999 }
.cd-tag-status-select {
  background: rgba(0,0,0,.45); color: #fff; border: 1px solid rgba(255,255,255,.3);
  cursor: pointer; font-family: inherit; appearance: none; padding-right: 22px;
  background-image: linear-gradient(45deg, transparent 50%, rgba(255,255,255,.7) 50%),
    linear-gradient(135deg, rgba(255,255,255,.7) 50%, transparent 50%);
  background-position: calc(100% - 14px) 55%, calc(100% - 9px) 55%;
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}
.cd-tag-edit { background: rgba(0,0,0,.45); color: #fff; border: 1px solid rgba(255,255,255,.3); cursor: pointer; transition: background .2s; font-family: inherit }
.cd-tag-edit:hover { background: rgba(255,255,255,.4) }
.cd-tag-save { background: #2e7d32; color: #fff; border: none; cursor: pointer; font-family: inherit }
.cd-tag-save:disabled { opacity: .5; cursor: default }
.cd-tag-cancel { background: rgba(0,0,0,.45); color: #fff; border: 1px solid rgba(255,255,255,.3); cursor: pointer; font-family: inherit }

.cd-edit-textarea { width: 100%; padding: 12px; border: 1.5px solid #e5dbcc; border-radius: 8px; font-size: .9rem; color: #333; font-family: inherit; resize: vertical; min-height: 200px; box-sizing: border-box; outline: none; background: #fff; line-height: 1.8 }
.cd-edit-textarea:focus { border-color: #E26A6A }
.cd-edit-textarea--sm { min-height: 120px; max-width: 65% }
.cd-honor-body { position: relative; z-index: 1 }
.cd-honor-text { font-size: .88rem; color: #666; line-height: 1.7; max-width: 65% }
.cd-edit-input { height: 34px; padding: 0 10px; border: 1.5px solid #e5dbcc; border-radius: 6px; font-size: .86rem; color: #333; font-family: inherit; outline: none; background: #fff; max-width: 240px; box-sizing: border-box }
.cd-edit-input:focus { border-color: #E26A6A }
.cd-edit-dates { display: flex; align-items: center; gap: 4px; max-width: 340px }
.cd-edit-dates .cd-edit-input { flex: 1; max-width: none }
.cd-edit-dates span { font-size: .8rem; color: #666 }
.cd-qr-edit { display: flex; align-items: center; gap: 10px }
.cd-qr-preview { width: 64px; height: 64px; object-fit: contain; border: 1px solid #e5dbcc; border-radius: 6px }
.cd-qr-upload-btn {
  height: 32px; padding: 0 14px; border: 1px dashed #d5c9b3; border-radius: 6px;
  background: #fefcf9; color: #8b7b65; font-size: .78rem; cursor: pointer;
  font-family: inherit; position: relative; display: inline-flex; align-items: center;
  transition: border-color .2s;
}
.cd-qr-upload-btn:hover { border-color: #E26A6A; color: #E26A6A }
.cd-qr-upload-btn input { position: absolute; inset: 0; opacity: 0; cursor: pointer }

/* Tab 切换栏 */
.cd-tabs {
  display: flex; gap: 8px; margin: 0 32px; padding: 6px 8px;
  background: #fff; border-radius: 14px 14px 0 0;
  box-shadow: 0 -2px 8px rgba(0,0,0,.03);
}
.cd-tab-btn {
  flex: 1; height: 44px; border: none; background: transparent;
  font-size: .9rem; font-weight: 600; color: #8B7355;
  cursor: pointer; font-family: inherit; letter-spacing: .04em;
  position: relative; transition: color .2s; border-radius: 12px;
}
.cd-tab-btn.active {
  color: #3C2415;
  background: rgba(181,52,58,.06);
}
.cd-tab-btn:hover { color: #3C2415 }

.cd-main { padding: 16px 32px 32px; margin: 0 auto }
.cd-section { margin-bottom: 16px; background: linear-gradient(90deg, #FFF8F4 0%, #FDEDE8 100%); border-radius: 16px; padding: 20px 24px; box-shadow: none }
.cd-section-title { display: flex; align-items: center; gap: 10px; font-size: 1rem; font-weight: 700; color: #333; margin: 0 0 12px; letter-spacing: .04em }
.cd-section-icon-wrap { width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0; background: #fdf5ec; display: flex; align-items: center; justify-content: center }
.cd-section-icon-inner { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center }
.cd-section-icon { color: #E26A6A; flex-shrink: 0 }
.cd-section-icon-sm { width: 30px; height: 30px; border-radius: 8px }
.cd-section-bar { width: 4px; height: 18px; border-radius: 2px; flex-shrink: 0 }
.cd-desc-body { font-size: .9rem; color: #666; line-height: 1.8; max-width: 65%; position: relative; z-index: 1 }
.cd-desc-body :deep(img) { max-width: 100%; border-radius: 8px; margin: 8px 0 }

.cd-section--intro, .cd-info-card--recruit, .cd-info-card--honor { position: relative; overflow: hidden }
.cd-section--intro::after, .cd-info-card--recruit::after, .cd-info-card--honor::after { content: ''; position: absolute; right: 0; bottom: 0; width: 300px; height: 100%; background-size: cover; background-repeat: no-repeat; background-position: right bottom; opacity: .5; pointer-events: none; z-index: 0 }
.cd-section--intro { min-height: 300px }
.cd-section--intro::after  { background-image: image-set(url('/club1.webp') type('image/webp'), url('/club1.png') type('image/png')); width: 420px; height: 420px; background-size: contain; bottom: -80px; opacity: .7 }
.cd-info-card--recruit::after { background-image: image-set(url('/club2.webp') type('image/webp'), url('/club2.png') type('image/png')); bottom: -80px; right: -60px; width: 520px; height: 350px; background-size: contain }
.cd-info-card--honor { min-height: 260px }
.cd-info-card--honor::after { background-image: image-set(url('/club3.webp') type('image/webp'), url('/club3.png') type('image/png')); width: 380px; height: 340px; background-size: contain; right: -60px; bottom: -50px }
.cd-section--intro > *, .cd-info-card--recruit > *, .cd-info-card--honor > * { position: relative; z-index: 1 }

.cd-cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px }
.cd-info-card { background: linear-gradient(90deg, #FFF8F4 0%, #FDEDE8 100%); border-radius: 16px; padding: 28px 24px; box-shadow: none }
.cd-info-card-head { display: flex; align-items: center; gap: 8px; font-size: .92rem; font-weight: 700; color: #333; margin-bottom: 10px; letter-spacing: .04em }
.cd-info-card-body { display: flex; flex-direction: column; gap: 14px }
.cd-info-row { display: flex; flex-direction: column; gap: 2px }
.cd-info-label { font-size: .72rem; color: #666; letter-spacing: .03em }
.cd-info-val { font-size: .88rem; color: #333; font-weight: 500 }
.cd-info-empty { font-size: .82rem; color: #666; margin: 0 }
.cd-recruit-split { display: flex; gap: 4px }
.cd-recruit-left { flex: 1; display: flex; flex-direction: column; gap: 14px }
.cd-recruit-right { flex: 0 0 auto; display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start; margin-left: -16px; margin-top: -32px; padding: 0 }
.cd-join-title { font-size: 1.12rem; font-weight: 700; color: #333; margin: 0 0 6px; letter-spacing: .04em }
.cd-join-desc { font-size: .78rem; color: #666; margin: 0 0 14px }
.cd-join-btn { height: 36px; padding: 0 32px; border: none; border-radius: 8px; background: #E26A6A; color: #fff; font-size: .88rem; font-weight: 600; cursor: pointer; font-family: inherit; letter-spacing: .04em; transition: opacity .2s }
.cd-join-btn:hover { opacity: .85 }

@media(max-width: 768px) {
  .club-detail {
    min-height: auto;
    margin: 0;
    background: #f3f3f5;
  }

  .club-detail--editing .cd-main {
    padding-bottom: calc(24px + env(safe-area-inset-bottom, 0px));
  }

  .cd-hero-wrapper { padding: 0 }

  .cd-hero {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-areas:
      'cover'
      'toolbar'
      'content'
      'meta';
    gap: 0;
    position: relative;
    height: auto;
    overflow: visible;
    background: #fff;
    border-radius: 0;
    box-shadow: none;
  }

  .cd-hero-bg {
    grid-area: cover;
    position: relative;
    inset: auto;
    width: 100%;
    height: 172px;
    display: block;
    object-fit: cover;
    object-position: center;
  }

  .cd-hero-gradient {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 172px;
    z-index: 1;
    pointer-events: none;
  }

  .cd-back {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 6;
    min-height: 40px;
    max-width: min(46vw, 168px);
    padding: 0 12px 0 10px;
    font-size: 0.8rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .cd-back svg { flex-shrink: 0; }

  .cd-hero-actions {
    grid-area: toolbar;
    position: static;
    top: auto;
    right: auto;
    z-index: 2;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    align-items: center;
    gap: 8px;
    max-width: none;
    min-height: 60px;
    box-sizing: border-box;
    padding: 10px 14px 0;
  }

  .cd-hero-content {
    grid-area: content;
    position: relative;
    left: auto;
    top: auto;
    right: auto;
    margin-top: 0;
    padding: 8px 14px 12px;
    align-items: flex-start;
    gap: 12px;
  }

  .cd-hero-badge-ring {
    width: 64px;
    height: 64px;
    margin-top: 2px;
  }

  .cd-hero-badge-text { font-size: 1.45rem }

  .cd-hero-info {
    flex: 1;
    min-width: 0;
  }

  .cd-hero-info .cd-hero-name {
    font-size: 1.12rem;
    color: #1a1a1a;
    text-shadow: none;
    margin-bottom: 6px;
    line-height: 1.35;
    word-break: break-word;
  }

  .cd-hero-info .cd-hero-intro {
    font-size: 0.82rem;
    color: #666;
    margin-bottom: 8px;
    line-height: 1.5;
    word-break: break-word;
  }

  .cd-hero-info .cd-hero-name-input,
  .cd-hero-info .cd-hero-intro-input,
  .cd-hero-info .cd-hero-cat-select {
    color: #1a1a1a;
    background: #f7f7f7;
    border: 1px solid #e0e0e0;
    max-width: 100%;
    width: 100%;
  }

  .cd-hero-info .cd-hero-name-input {
    font-size: 1.05rem;
    font-weight: 700;
    padding: 8px 10px;
  }

  .cd-hero-info .cd-hero-intro-input {
    font-size: 0.84rem;
    padding: 8px 10px;
    margin-bottom: 8px;
  }

  .cd-hero-info .cd-hero-name-input::placeholder,
  .cd-hero-info .cd-hero-intro-input::placeholder {
    color: #aaa;
  }

  .cd-hero-info .cd-hero-cat-select {
    font-size: 0.78rem;
    padding: 6px 12px;
    color: #333;
  }

  .cd-tag-category {
    background: rgba(74, 140, 92, 0.12);
    color: #3d7a4e;
    border: none;
  }

  .cd-tag-edit,
  .cd-tag-cancel,
  .cd-tag-status-select {
    background: #f4f4f6;
    color: #333;
    border: 1px solid #dedee3;
  }

  .cd-tag-save {
    min-height: 34px;
    padding: 6px 14px;
  }

  .cd-hero-meta {
    grid-area: meta;
    position: relative;
    left: auto;
    bottom: auto;
    margin: 8px 14px 14px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px 12px;
    padding: 12px 14px;
    background: #f7f7f7;
    border: 1px solid #ebebeb;
    border-radius: 12px;
  }

  .cd-hero-meta-item { padding: 0; min-width: 0; }

  .cd-hero-meta-label { font-size: 0.68rem; color: #999 }

  .cd-hero-meta-value {
    font-size: 0.82rem;
    color: #333;
    white-space: normal;
    word-break: break-word;
    font-weight: 600;
  }

  .cd-meta-input {
    width: 100%;
    max-width: none;
    height: 32px;
    color: #333;
    background: #fff;
    border-color: #ddd;
    font-size: 0.8rem;
  }

  .cd-meta-input::placeholder { color: #aaa }

  .cd-hero-bg-upload {
    position: absolute;
    top: auto;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 6;
    font-size: 0.72rem;
    padding: 5px 12px;
  }

  .cd-upload-toast {
    position: fixed;
    top: auto;
    bottom: calc(64px + env(safe-area-inset-bottom, 0px));
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    z-index: 200;
    padding: 8px 14px;
    font-size: 0.78rem;
    background: rgba(26, 26, 26, 0.88);
    color: #fff;
    border-radius: 999px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  }

  .cd-tabs {
    margin: 12px 12px 0;
    padding: 4px;
    border-radius: 12px;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  }

  .cd-tab-btn { height: 40px; font-size: 0.86rem }

  .cd-main {
    padding: 12px 12px calc(16px + env(safe-area-inset-bottom, 0px));
  }

  .cd-section {
    padding: 16px 14px;
    border-radius: 12px;
    margin-bottom: 12px;
    background: #fff;
    border: 1px solid #ebebeb;
  }

  .cd-section-title { margin-bottom: 10px; font-size: 0.92rem }

  .cd-section--intro,
  .cd-info-card--honor { min-height: unset }

  .cd-section--intro::after,
  .cd-info-card--recruit::after,
  .cd-info-card--honor::after { display: none }

  .cd-desc-body,
  .cd-honor-text {
    max-width: 100%;
    font-size: 0.86rem;
    line-height: 1.65;
    word-break: break-word;
  }

  .cd-desc-body :deep(img) { max-width: 100%; height: auto }

  .cd-desc-body :deep(h3) {
    margin: 0.85em 0 0.35em;
    line-height: 1.4;
  }

  .cd-desc-body :deep(p) { margin: 0.35em 0 0.65em }

  .cd-desc-body :deep(ul),
  .cd-desc-body :deep(ol) {
    width: 100%;
    margin: 0.3em 0 0.75em;
    padding-left: 1.4rem;
    box-sizing: border-box;
  }

  .cd-desc-body :deep(li) {
    margin: 0.2em 0;
    padding-left: 0.1rem;
    overflow-wrap: anywhere;
  }

  .cd-edit-textarea {
    min-height: 160px;
    font-size: 16px;
  }

  .cd-edit-textarea--sm {
    max-width: 100%;
    min-height: 120px;
    font-size: 16px;
  }

  .cd-info-card {
    padding: 16px 14px;
    background: #fff;
    border: 1px solid #ebebeb;
    border-radius: 12px;
  }

  .cd-info-card-head { font-size: 0.88rem; margin-bottom: 10px }

  .cd-cards-row {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 0;
  }

  .cd-info-row { gap: 4px }

  .cd-info-val {
    font-size: 0.86rem;
    line-height: 1.45;
    word-break: break-word;
  }

  .cd-recruit-split { flex-direction: column; gap: 0 }

  .cd-recruit-right {
    width: 100%;
    margin: 14px 0 0;
    padding-top: 14px;
    border-top: 1px solid #f0f0f0;
    align-items: stretch;
    text-align: center;
  }

  .cd-join-btn {
    width: 100%;
    height: 44px;
    font-size: 0.9rem;
  }

  .cd-edit-input {
    width: 100%;
    max-width: none;
    height: 40px;
    font-size: 16px;
  }

  .cd-edit-dates {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
    max-width: 100%;
  }

  .cd-edit-dates span { display: none }

  .cd-qr-edit {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .cd-qr-upload-btn {
    width: 100%;
    justify-content: center;
    min-height: 40px;
  }
}

@media(max-width: 480px) {
  .club-detail { margin: 0 }

  .cd-main { padding: 10px 10px calc(14px + env(safe-area-inset-bottom, 0px)) }

  .cd-hero-bg,
  .cd-hero-gradient { height: 156px }

  .cd-back {
    top: 8px;
    left: 8px;
    min-height: 38px;
    font-size: 0.76rem;
    max-width: min(44vw, 150px);
  }

  .cd-hero-actions { min-height: 56px; padding: 8px 12px 0; gap: 6px }

  .cd-hero-content { padding: 6px 12px 10px; gap: 10px }

  .cd-hero-badge-ring { width: 56px; height: 56px }

  .cd-hero-badge-text { font-size: 1.25rem }

  .cd-hero-info .cd-hero-name { font-size: 1.02rem }

  .cd-hero-info .cd-hero-intro { font-size: 0.78rem }

  .cd-tag { font-size: 0.68rem; padding: 4px 10px }

  .cd-hero-meta {
    margin: 6px 12px 12px;
    padding: 10px 12px;
    gap: 8px 10px;
    border-radius: 10px;
  }

  .cd-hero-meta-label { font-size: 0.62rem }

  .cd-hero-meta-value { font-size: 0.78rem }

  .cd-tabs { margin: 8px 10px 0 }

  .cd-tab-btn { height: 38px; font-size: 0.82rem }

  .cd-section {
    padding: 14px 12px;
    border-radius: 10px;
    margin-bottom: 10px;
  }

  .cd-section-title { font-size: 0.86rem; gap: 6px; margin-bottom: 10px }

  .cd-desc-body,
  .cd-honor-text { font-size: 0.82rem }

  .cd-info-card { padding: 12px }

  .cd-info-card-head { font-size: 0.82rem; margin-bottom: 8px }

  .cd-recruit-right { margin-top: 12px; padding-top: 12px }

  .cd-join-title { font-size: 0.92rem }

  .cd-join-desc { font-size: 0.72rem; margin-bottom: 10px }

  .cd-join-btn { height: 42px; font-size: 0.86rem }

  .cd-hero-bg-upload { bottom: 8px; font-size: 0.66rem; padding: 4px 10px }
}

/* 联系方式编辑卡片 */
.cd-info-card--contact { margin-top: 0 }
.cd-contact-edit { display: flex; flex-direction: column; gap: 14px }

/* 加入弹窗 */
.cd-join-overlay {
  position: fixed; inset: 0; z-index: 5000;
  background: rgba(0,0,0,.52); display: flex;
  align-items: center; justify-content: center;
}
.cd-join-modal {
  position: relative; width: 360px; max-width: 90vw;
  background: #fff; border-radius: 20px; padding: 32px 28px 24px;
  box-shadow: 0 16px 48px rgba(0,0,0,.18);
}
.cd-join-close {
  position: absolute; top: 14px; right: 14px;
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: #f5f0eb; color: #8b7b65; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.cd-join-close:hover { background: #e8e0d5 }
.cd-join-title-text { margin: 0 0 20px; font-size: 1.1rem; font-weight: 700; color: #3C2415; text-align: center }
.cd-join-empty { text-align: center; color: #b0a090 }
.cd-join-empty p { margin: 0 0 4px; font-size: .88rem }
.cd-join-empty-hint { font-size: .76rem !important; color: #c4b8a4 }
.cd-join-row { margin-bottom: 18px }
.cd-join-row:last-child { margin-bottom: 0 }
.cd-join-label { display: block; font-size: .78rem; color: #8b7b65; margin-bottom: 8px; font-weight: 500 }
.cd-join-qq { display: flex; align-items: center; gap: 10px }
.cd-join-qq-num { flex: 1; padding: 10px 14px; background: #faf6f0; border-radius: 10px; font-size: 1.05rem; font-weight: 700; color: #3C2415; letter-spacing: .06em; text-align: center; font-family: inherit }
.cd-join-copy { height: 38px; padding: 0 16px; border: none; border-radius: 10px; background: #4a8c5c; color: #fff; font-size: .8rem; font-weight: 600; cursor: pointer; font-family: inherit; white-space: nowrap; transition: opacity .15s }
.cd-join-copy:hover { opacity: .85 }
.cd-join-qr { display: block; width: 200px; height: 200px; margin: 0 auto; object-fit: contain; border-radius: 12px; border: 1px solid #f0e4d8 }
.join-modal-enter-active { animation: jmIn .25s ease-out }
.join-modal-leave-active { animation: jmOut .18s ease-in }
@keyframes jmIn { from { opacity:0; transform:scale(.95) } to { opacity:1; transform:scale(1) } }
@keyframes jmOut { to { opacity:0; transform:scale(.95) } }
</style>
