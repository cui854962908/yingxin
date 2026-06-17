<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authHeaders, useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'

const props = withDefaults(defineProps<{
  category: string
  pageTitle?: string
  pageSubtitle?: string
}>(), {
  pageTitle: '报到须知',
  pageSubtitle: '请仔细阅读以下内容，提前准备所需材料，按流程完成报到',
})

interface GuideItem { id: string; title: string; content: string; date: string; category?: string }

const items = ref<GuideItem[]>([])
const loading = ref(true)

const { isAdmin } = useAuth()

// 编辑状态
const editingId = ref<string | null>(null)
const editForm = ref({ title: '', content: '', date: '' })
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

function startEdit(item: GuideItem) {
  editingId.value = item.id
  editForm.value = { title: item.title, content: item.content, date: item.date || '' }
  saveMsg.value = ''
}

function cancelEdit() { editingId.value = null }

async function saveEdit(id: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    const body: Record<string, string> = {}
    if (editForm.value.title) body.title = editForm.value.title
    if (editForm.value.content) body.content = editForm.value.content
    if (editForm.value.date) body.date = editForm.value.date
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

onMounted(load)
</script>

<template>
  <div class="guide">
    <!-- 顶部 Toast -->
    <Transition name="toast">
      <div v-if="saveMsg" class="guide-toast" :class="{ 'guide-toast--err': saveMsg !== '已保存' }">
        <svg v-if="saveMsg === '已保存'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>
        <span>{{ saveMsg }}</span>
      </div>
    </Transition>

    <!-- 页面头部 -->
    <div class="guide-hero">
      <div class="guide-hero-icon">
        <svg width="32" height="32" viewBox="0 0 256 256" fill="currentColor"><path d="M216,48H40a8,8,0,0,0-8,8V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V56A8,8,0,0,0,216,48Zm-8,160H48V64H208ZM184,96a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,96Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,128Zm-48,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h48A8,8,0,0,1,136,160Z"/></svg>
      </div>
      <h2 class="guide-title">{{ props.pageTitle }}</h2>
      <p class="guide-subtitle">{{ props.pageSubtitle }}</p>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="guide-loading">
      <AppSpinner />
    </div>

    <!-- 空状态 -->
    <div v-else-if="items.length === 0" class="guide-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" class="guide-empty-icon"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>暂无{{ props.pageTitle }}内容</p>
      <p class="guide-empty-hint">管理员可通过公告系统发布报到须知</p>
    </div>

    <!-- 内容列表 -->
    <div v-else class="guide-list">
      <div v-for="(item, idx) in items" :key="item.id" class="guide-card">
        <!-- 编辑模式 -->
        <template v-if="editingId === item.id">
          <input v-model="editForm.date" type="date" class="guide-edit-date" />
          <input v-model="editForm.title" class="guide-edit-title" placeholder="标题" />
          <textarea v-model="editForm.content" class="guide-edit-content" placeholder="内容" rows="5" />
          <div class="guide-edit-actions">
            <button class="guide-edit-save" :disabled="saving" @click="saveEdit(item.id)">{{ saving ? '保存中…' : '保存' }}</button>
            <button class="guide-edit-cancel" :disabled="saving" @click="cancelEdit">取消</button>
          </div>
        </template>
        <!-- 展示模式 -->
        <template v-else>
          <div class="guide-card-step">{{ idx + 1 }}</div>
          <div class="guide-card-body">
            <p v-if="item.date" class="guide-card-date">{{ item.date }}</p>
            <h3 class="guide-card-title">{{ item.title }}</h3>
            <p class="guide-card-content">{{ item.content }}</p>
          </div>
          <a v-if="isAdmin" class="guide-edit-btn" @click="startEdit(item)">编辑</a>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.guide { display: flex; flex-direction: column; gap: 20px; position: relative }

/* ===== 页面头部 ===== */
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
.guide-subtitle { font-size: .82rem; color: #b0a090; margin-top: 8px }

/* ===== 列表 ===== */
.guide-list { display: flex; flex-direction: column; gap: 12px }
.guide-card {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 20px 24px; background: #fff; border-radius: 12px;
  border: 1px solid #f2ebe0; position: relative;
  transition: border-color .2s, box-shadow .2s;
}
.guide-card:hover { border-color: #e5dbcc; box-shadow: 0 2px 12px rgba(0,0,0,.04) }
.guide-card-step {
  width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #b5343a, #8b2025);
  color: #fff; font-size: .88rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Georgia', serif;
}
.guide-card-body { flex: 1; min-width: 0 }
.guide-card-date { margin: 0 0 6px; font-size: .76rem; color: #b0a090 }
.guide-card-title { font-size: .95rem; font-weight: 600; color: #3c3028; margin: 0 0 6px }
.guide-card-content { font-size: .86rem; color: #5c5040; line-height: 1.7; white-space: pre-line; margin: 0 }
.guide-edit-btn {
  font-size: .74rem; color: #c4b0a0; cursor: pointer; flex-shrink: 0;
  opacity: 0; transition: opacity .15s; padding: 4px 0;
}
.guide-card:hover .guide-edit-btn { opacity: 1 }
.guide-edit-btn:hover { color: #4a8c5c }

/* ===== 编辑模式 ===== */
.guide-edit-title {
  width: 100%; height: 36px; padding: 0 12px; border: 1.5px solid #e5dbcc;
  border-radius: 6px; font-size: .9rem; font-weight: 600; color: #3c3028;
  font-family: inherit; outline: none; box-sizing: border-box;
}
.guide-edit-date {
  width: 180px; height: 36px; margin-bottom: 10px; padding: 0 12px; border: 1.5px solid #e5dbcc;
  border-radius: 6px; font-size: .84rem; color: #3c3028; font-family: inherit; outline: none; box-sizing: border-box;
}
.guide-edit-date:focus { border-color: #4a8c5c }
.guide-edit-title:focus { border-color: #4a8c5c }
.guide-edit-content {
  width: 100%; margin-top: 10px; padding: 10px 12px;
  border: 1.5px solid #e5dbcc; border-radius: 6px;
  font-size: .84rem; color: #3c3028; font-family: inherit;
  resize: vertical; outline: none; line-height: 1.6; box-sizing: border-box;
}
.guide-edit-content:focus { border-color: #4a8c5c }
.guide-edit-actions { display: flex; gap: 8px; margin-top: 10px; justify-content: flex-end }
.guide-edit-save {
  height: 30px; padding: 0 16px; border: none; border-radius: 6px;
  background: #4a8c5c; color: #fff; font-size: .78rem; cursor: pointer;
  font-family: inherit; transition: opacity .2s;
}
.guide-edit-save:hover:not(:disabled) { opacity: .9 }
.guide-edit-save:disabled { opacity: .5; cursor: default }
.guide-edit-cancel {
  height: 30px; padding: 0 16px; border: 1px solid #e5dbcc; border-radius: 6px;
  background: #fff; color: #8b7b65; font-size: .78rem; cursor: pointer;
  font-family: inherit; transition: border-color .2s;
}
.guide-edit-cancel:hover:not(:disabled) { border-color: #b0a090 }
.guide-edit-cancel:disabled { opacity: .5; cursor: default }

/* ===== 空/加载 ===== */
.guide-empty { text-align: center; padding: 48px 0; color: #b0a090 }
.guide-empty-icon { margin-bottom: 12px; opacity: .4 }
.guide-empty-hint { font-size: .78rem; margin-top: 6px; color: #d4c8b0 }
.guide-loading { display: flex; align-items: center; justify-content: center; padding: 48px 0 }

/* ===== Toast ===== */
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

@media(max-width:480px){
  .guide-hero { padding: 20px 14px 16px }
  .guide-card { padding: 16px; gap: 12px }
  .guide-card-step { width: 30px; height: 30px; font-size: .78rem }
}
</style>
