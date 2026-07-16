<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useAppNavigate } from '../composables/useAppNavigate'
import AppSpinner from './AppSpinner.vue'

const props = withDefaults(defineProps<{
  category: string
  pageTitle?: string
  pageSubtitle?: string
}>(), {
  pageTitle: '报到须知',
  pageSubtitle: '请仔细阅读以下内容，提前准备所需材料，按流程完成报到',
})

interface GuideItem { id: string; title: string; content: string; date: string }

const items = ref<GuideItem[]>([])
const loading = ref(true)

const { isAdmin } = useAuth()
const { appGoBackTo } = useAppNavigate()

function goBack() {
  appGoBackTo('/')
}

const editMode = ref(false)
const editingId = ref<string | null>(null)
const editForm = ref({ title: '', content: '' })
const saving = ref(false)
const saveMsg = ref('')

async function load() {
  loading.value = true
  try {
    const res = await fetch(`/api/announcements?category=${props.category}`)
    const d = await res.json()
    if (d.success) items.value = d.data
  } catch { console.warn('加载报到须知失败') }
  finally { loading.value = false }
}

function enterEditMode() {
  editMode.value = true
  editingId.value = null
  saveMsg.value = ''
}

function exitEditMode() {
  editMode.value = false
  editingId.value = null
  saveMsg.value = ''
}

function startEdit(item: GuideItem) {
  editingId.value = item.id
  editForm.value = { title: item.title, content: item.content }
  saveMsg.value = ''
}

function cancelEdit() {
  editingId.value = null
  saveMsg.value = ''
}

function onCardClick(item: GuideItem) {
  if (!editMode.value || editingId.value === item.id) return
  startEdit(item)
}

async function saveEdit(id: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    const body: Record<string, string> = {}
    if (editForm.value.title) body.title = editForm.value.title
    if (editForm.value.content) body.content = editForm.value.content
    const res = await fetch(`/api/admin/announcements/${id}`, {
      method: 'PATCH', headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error()
    saveMsg.value = '已保存'
    setTimeout(() => { editingId.value = null; saveMsg.value = ''; load() }, 1200)
  } catch {
    saveMsg.value = '保存失败，请重试'
  } finally { saving.value = false }
}

function contentUsesHtml(text: string): boolean {
  return /<[a-z][\s\S]*>/i.test(text)
}

onMounted(load)
</script>

<template>
  <div class="guide">
    <Transition name="toast">
      <div v-if="saveMsg" class="guide-toast" :class="{ 'guide-toast--err': saveMsg !== '已保存' }">
        <svg v-if="saveMsg === '已保存'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>
        <span>{{ saveMsg }}</span>
      </div>
    </Transition>

    <!-- 顶部：返回 + 管理员编辑 -->
    <div class="guide-topbar">
      <button type="button" class="guide-back" @click="goBack">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
        返回首页
      </button>
      <div v-if="isAdmin && !loading && items.length > 0" class="guide-topbar-actions">
        <button
          v-if="!editMode"
          type="button"
          class="guide-mode-btn"
          @click="enterEditMode"
        >
          编辑
        </button>
        <button
          v-else
          type="button"
          class="guide-mode-btn guide-mode-btn--active"
          @click="exitEditMode"
        >
          完成编辑
        </button>
      </div>
    </div>

    <div class="guide-hero">
      <div class="guide-hero-icon">
        <svg width="32" height="32" viewBox="0 0 256 256" fill="currentColor"><path d="M216,48H40a8,8,0,0,0-8,8V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V56A8,8,0,0,0,216,48Zm-8,160H48V64H208ZM184,96a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,96Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,128Zm-48,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h48A8,8,0,0,1,136,160Z"/></svg>
      </div>
      <h2 class="guide-title">{{ props.pageTitle }}</h2>
      <p class="guide-subtitle">{{ props.pageSubtitle }}</p>
    </div>

    <div v-if="loading" class="guide-loading">
      <AppSpinner />
    </div>

    <div v-else-if="items.length === 0" class="guide-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="guide-empty-icon"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>暂无{{ props.pageTitle }}内容</p>
      <p class="guide-empty-hint">管理员可通过公告系统发布{{ props.pageTitle }}</p>
    </div>

    <div v-else class="guide-list">
      <p v-if="editMode && !editingId" class="guide-edit-hint">点击要编辑的条目</p>
      <div
        v-for="(item, idx) in items"
        :key="item.id"
        class="guide-card"
        :class="{
          'guide-card--editing': editingId === item.id,
          'guide-card--pickable': editMode && editingId !== item.id,
        }"
        @click="onCardClick(item)"
      >
        <!-- 编辑模式：独立纵向面板，避免与展示态共用横向 flex -->
        <div v-if="editingId === item.id" class="guide-edit">
          <div class="guide-edit-head">
            <span class="guide-edit-badge">编辑中 · 第 {{ idx + 1 }} 条</span>
          </div>
          <div class="guide-edit-field">
            <label class="guide-edit-label" :for="`guide-title-${item.id}`">标题</label>
            <input
              :id="`guide-title-${item.id}`"
              v-model="editForm.title"
              class="guide-edit-title"
              placeholder="请输入标题"
            />
          </div>
          <div class="guide-edit-field">
            <label class="guide-edit-label" :for="`guide-content-${item.id}`">正文</label>
            <textarea
              :id="`guide-content-${item.id}`"
              v-model="editForm.content"
              class="guide-edit-content"
              placeholder="请输入正文，支持换行分段"
              rows="8"
            />
          </div>
          <div class="guide-edit-actions">
            <button class="guide-edit-save" :disabled="saving" @click.stop="saveEdit(item.id)">
              {{ saving ? '保存中…' : '保存' }}
            </button>
            <button class="guide-edit-cancel" :disabled="saving" @click.stop="cancelEdit">取消</button>
          </div>
        </div>

        <!-- 展示模式 -->
        <template v-else>
          <div class="guide-card-step">{{ idx + 1 }}</div>
          <div class="guide-card-body">
            <h3 class="guide-card-title">{{ item.title }}</h3>
            <div
              v-if="contentUsesHtml(item.content)"
              class="guide-card-content guide-card-content--html"
              v-html="item.content"
            />
            <p v-else class="guide-card-content">{{ item.content }}</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.guide { display: flex; flex-direction: column; gap: 20px; position: relative }

.guide-topbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; min-height: 36px;
}
.guide-back {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 12px 0 8px;
  border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; color: #6b5e4e;
  font-size: .82rem; font-weight: 500;
  cursor: pointer; font-family: inherit;
  transition: border-color .15s, color .15s, background .15s;
  flex-shrink: 0;
}
.guide-back:hover { border-color: #b5343a; color: #b5343a; background: #fff }
.guide-topbar-actions { display: flex; align-items: center; gap: 8px; margin-left: auto }
.guide-mode-btn {
  height: 32px; padding: 0 14px; border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; color: #6b5e4e; font-size: .78rem; font-weight: 500;
  cursor: pointer; font-family: inherit; transition: border-color .15s, color .15s, background .15s;
}
.guide-mode-btn:hover { border-color: #4a8c5c; color: #4a8c5c }
.guide-mode-btn--active {
  background: #e8f5e9; border-color: #4a8c5c; color: #3d7a4f; font-weight: 600;
}
.guide-edit-hint {
  margin: 0 0 4px; padding: 8px 12px; border-radius: 8px;
  background: #f5faf6; color: #4a8c5c; font-size: .78rem; text-align: center;
}

.guide-hero {
  text-align: center; padding: 28px 20px 20px;
  background: linear-gradient(180deg, #fdfaf6 0%, #fff 100%);
  border-radius: 14px; border: 1px solid #f2ebe0;
}
.guide-hero-icon {
  width: 56px; height: 56px; border-radius: 14px; margin: 0 auto 14px;
  background: linear-gradient(135deg, #fef3f3, #fdf0ea);
  border: 1px solid rgba(181,52,58,.08);
  color: #b5343a; display: flex; align-items: center; justify-content: center;
}
.guide-title { font-size: 1.3rem; font-weight: 700; color: #2c2c2c; letter-spacing: .08em; margin: 0 }
.guide-subtitle { font-size: .82rem; color: #b0a090; margin-top: 8px; line-height: 1.6 }

.guide-list { display: flex; flex-direction: column; gap: 12px }
.guide-card {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 20px 24px; background: #fff; border-radius: 12px;
  border: 1px solid #f2ebe0; position: relative;
  transition: border-color .2s, box-shadow .2s;
}
.guide-card:hover { border-color: #e5dbcc; box-shadow: 0 2px 12px rgba(0,0,0,.04) }
.guide-card--pickable { cursor: pointer; border-color: #d4e8d8 }
.guide-card--pickable:hover { border-color: #4a8c5c; background: #fafcf9 }
.guide-card--editing {
  display: block; padding: 0; border-color: #c5dcc9;
  background: #faf8f4; box-shadow: 0 2px 16px rgba(74,140,92,.08);
}
.guide-card-step {
  width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #b5343a, #8b2025);
  color: #fff; font-size: .88rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Georgia', serif;
}
.guide-card-body { flex: 1; min-width: 0 }
.guide-card-title { font-size: .95rem; font-weight: 600; color: #3c3028; margin: 0 0 6px; line-height: 1.45 }
.guide-card-content { font-size: .86rem; color: #5c5040; line-height: 1.7; white-space: pre-line; margin: 0 }
.guide-card-content--html { white-space: normal }
.guide-card-content--html :deep(p) { margin: 0 0 .65em }
.guide-card-content--html :deep(p:last-child) { margin-bottom: 0 }
.guide-card-content--html :deep(.guide-inline-img) {
  display: block;
  width: min(100%, 300px);
  height: auto;
  margin: 12px auto 0;
  border-radius: 16px;
  border: 1px solid #f2ebe0;
  box-shadow: 0 6px 24px rgba(60, 48, 40, 0.08);
  object-fit: contain;
}

/* 编辑面板 */
.guide-edit { padding: 18px 20px 20px; display: flex; flex-direction: column; gap: 16px }
.guide-edit-head { display: flex; align-items: center }
.guide-edit-badge {
  display: inline-flex; align-items: center;
  padding: 6px 12px; border-radius: 20px;
  background: #e8f5e9; color: #3d7a4f;
  font-size: .76rem; font-weight: 600; letter-spacing: .04em;
}
.guide-edit-field { display: flex; flex-direction: column; gap: 8px }
.guide-edit-label { font-size: .82rem; font-weight: 600; color: #6b5e4e; letter-spacing: .04em }
.guide-edit-title {
  width: 100%; height: 42px; padding: 0 14px;
  border: 1.5px solid #e5dbcc; border-radius: 10px;
  font-size: .92rem; font-weight: 600; color: #3c3028;
  background: #fff; font-family: inherit; outline: none; box-sizing: border-box;
  transition: border-color .2s, box-shadow .2s;
}
.guide-edit-title:focus { border-color: #4a8c5c; box-shadow: 0 0 0 3px rgba(74,140,92,.12) }
.guide-edit-content {
  width: 100%; min-height: 160px; padding: 14px;
  border: 1.5px solid #e5dbcc; border-radius: 10px;
  font-size: .88rem; color: #3c3028; background: #fff;
  font-family: inherit; resize: vertical; outline: none;
  line-height: 1.65; box-sizing: border-box;
  transition: border-color .2s, box-shadow .2s;
}
.guide-edit-content:focus { border-color: #4a8c5c; box-shadow: 0 0 0 3px rgba(74,140,92,.12) }
.guide-edit-actions {
  display: flex; gap: 10px; justify-content: flex-end;
  padding-top: 4px; border-top: 1px solid #ede6da;
}
.guide-edit-save {
  height: 38px; padding: 0 22px; border: none; border-radius: 10px;
  background: #4a8c5c; color: #fff; font-size: .84rem; font-weight: 600;
  cursor: pointer; font-family: inherit; transition: opacity .2s;
}
.guide-edit-save:hover:not(:disabled) { opacity: .9 }
.guide-edit-save:disabled { opacity: .5; cursor: default }
.guide-edit-cancel {
  height: 38px; padding: 0 22px; border: 1.5px solid #e5dbcc; border-radius: 10px;
  background: #fff; color: #8b7b65; font-size: .84rem;
  cursor: pointer; font-family: inherit; transition: border-color .2s;
}
.guide-edit-cancel:hover:not(:disabled) { border-color: #b0a090 }
.guide-edit-cancel:disabled { opacity: .5; cursor: default }

.guide-empty { text-align: center; padding: 48px 0; color: #b0a090 }
.guide-empty-icon { margin-bottom: 12px; opacity: .4 }
.guide-empty-hint { font-size: .78rem; margin-top: 6px; color: #d4c8b0 }
.guide-loading { display: flex; align-items: center; justify-content: center; padding: 48px 0 }

.guide-toast {
  position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 9999;
  display: flex; align-items: center; gap: 10px;
  padding: 12px 28px; border-radius: 10px;
  background: #4a8c5c; color: #fff;
  font-size: .92rem; font-weight: 600;
  box-shadow: 0 4px 24px rgba(74,140,92,.35);
  pointer-events: none;
}
.guide-toast--err { background: #b5343a; box-shadow: 0 4px 24px rgba(181,52,58,.35) }
.guide-toast svg { flex-shrink: 0 }
.toast-enter-active { animation: toastIn .35s cubic-bezier(.33,1,.68,1) both }
.toast-leave-active { animation: toastOut .3s ease-in both }
@keyframes toastIn { from { opacity: 0; transform: translateX(-50%) translateY(-16px) } to { opacity: 1; transform: translateX(-50%) translateY(0) } }
@keyframes toastOut { to { opacity: 0; transform: translateX(-50%) translateY(-12px) } }

@media (max-width: 768px) {
  .guide { gap: 14px }
  .guide-back { height: 40px; padding: 0 14px 0 10px; font-size: .86rem }
  .guide-mode-btn { height: 36px; padding: 0 16px; font-size: .82rem }
  .guide-hero { padding: 18px 14px 14px; border-radius: 12px }
  .guide-hero-icon { width: 48px; height: 48px; margin-bottom: 10px }
  .guide-title { font-size: 1.12rem }
  .guide-subtitle { font-size: .78rem; padding: 0 4px }

  .guide-card { padding: 14px; gap: 12px; border-radius: 10px }
  .guide-card-step { width: 28px; height: 28px; font-size: .76rem; border-radius: 8px }
  .guide-card-title { font-size: .9rem }
  .guide-card-content { font-size: .84rem }
  .guide-card-content--html :deep(.guide-inline-img) {
    width: min(100%, 260px);
    margin-top: 10px;
  }

  .guide-edit { padding: 14px; gap: 14px }
  .guide-edit-title,
  .guide-edit-content { font-size: 16px }
  .guide-edit-title { height: 44px }
  .guide-edit-content { min-height: 200px; padding: 12px 14px }
  .guide-edit-actions {
    flex-direction: column-reverse; gap: 10px;
    padding-top: 12px; margin-top: 2px;
  }
  .guide-edit-save,
  .guide-edit-cancel {
    width: 100%; height: 44px; font-size: .92rem;
  }
  .guide-toast {
    top: auto; bottom: calc(76px + env(safe-area-inset-bottom, 0px));
    left: 16px; right: 16px; transform: none;
    justify-content: center; padding: 14px 20px;
  }
  @keyframes toastIn { from { opacity: 0; transform: translateY(12px) } to { opacity: 1; transform: translateY(0) } }
  @keyframes toastOut { to { opacity: 0; transform: translateY(8px) } }
}
</style>
