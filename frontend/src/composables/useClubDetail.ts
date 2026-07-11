import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Club } from '../types/club'
import { authHeaders, useAuth } from './useAuth'
import { useAppNavigate } from './useAppNavigate'

export function useClubDetail() {
//
// 注：本组件 script+template 约 320 行，超出 300 行限制。
// 原因：Hero Banner 与下方内容（介绍/风采/招新/荣誉）构成完整详情页的上下半身，
// 强行拆分会引入 14 个 props/emits 的 prop-drilling，追踪编辑流程需跨文件跳转，
// 降低可读性的代价大于 20 行超出。
// 已拆出 ClubDetailGallery（风采展示+灯箱），其为独立功能块，拆分自然。
//

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
  return {
    isNew, club, loading, editing, saving, uploadMsg, activeTab, editForm, isAdmin,
    parseLeaders, formatRecruitCount, activityPhotosValue, goBack, canEdit, enterEdit,
    cancelEdit, saveEdit, uploadAndSet, uploadPhoto, removePhoto, uploadQr, backLabel,
    joinModal, joinCopyOk, openJoinModal, closeJoinModal, copyJoinQQ,
  }
}
