<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePreload } from '../composables/usePreload'
import { authHeaders, useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'

interface Announcement { id: string; date: string; title: string; content: string; category?: string }

const categoryText: Record<string, string> = {
  campus: '校园公告',
  guide: '报到须知',
  tips: '新生攻略',
}

const { announcements: cached } = usePreload()
const items = ref<Announcement[]>(cached.value.length ? cached.value : [])
const loading = ref(!cached.value.length)

const { isAdmin } = useAuth()

// 过滤掉报到须知类公告（在独立页面展示）
const displayItems = computed(() => items.value.filter(i => i.category !== 'guide' && i.category !== 'tips'))

// 编辑状态
const editingId = ref<string | null>(null)
const editForm = ref({ title: '', content: '', date: '', category: '' })
const saving = ref(false)
const saveMsg = ref('')

function startEdit(item: Announcement) {
  editingId.value = item.id
  editForm.value = { title: item.title, content: item.content, date: item.date || '', category: item.category || 'campus' }
  saveMsg.value = ''
}

function cancelEdit() { editingId.value = null }

async function saveEdit(id: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    const body: Record<string, string | null> = {}
    if (editForm.value.title) body.title = editForm.value.title
    if (editForm.value.content) body.content = editForm.value.content
    if (editForm.value.date) body.date = editForm.value.date
    body.category = editForm.value.category
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

async function load() {
  loading.value = true
  try {
    const res = await fetch('/api/announcements')
    const d = await res.json()
    if (d.success) items.value = d.data
  } catch { console.warn('加载公告列表失败') }
  finally { loading.value = false }
}

async function handleDelete(id: string) {
  try {
    await fetch(`/api/admin/announcements/${id}`, { method: 'DELETE', headers: authHeaders() })
    await load()
  } catch { console.warn('删除公告请求失败') }
}

onMounted(load)
</script>

<template>
  <div class="ann">
    <!-- 标题栏 -->
    <div class="ann-header">
      <h3 class="ann-head-title">校园公告</h3>
      <router-link v-if="isAdmin" to="/announcements/add" class="ann-add-btn">+ 发布公告</router-link>
    </div>
    <!-- 公告列表 -->
    <div v-for="item in displayItems" :key="item.id" class="ann-item">
      <!-- 编辑模式 -->
      <template v-if="editingId === item.id">
        <div class="ann-edit-row">
          <input v-model="editForm.date" type="date" class="ann-edit-date" />
          <input v-model="editForm.title" class="ann-edit-title" placeholder="标题" />
        </div>
        <select v-model="editForm.category" class="ann-edit-category">
          <option value="campus">校园公告</option>
          <option value="guide">报到须知</option>
          <option value="tips">新生攻略</option>
        </select>
        <textarea v-model="editForm.content" class="ann-edit-content" placeholder="内容" rows="4" />
        <div class="ann-edit-actions">
          <button class="ann-edit-save" :disabled="saving" @click="saveEdit(item.id)">{{ saving ? '保存中…' : '保存' }}</button>
          <button class="ann-edit-cancel" :disabled="saving" @click="cancelEdit">取消</button>
        </div>
        <Transition name="toast">
          <div v-if="saveMsg" class="ann-toast" :class="{ 'ann-toast--err': saveMsg !== '已保存' }">
            <svg v-if="saveMsg === '已保存'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>
            <span>{{ saveMsg }}</span>
          </div>
        </Transition>
      </template>
      <!-- 展示模式 -->
      <template v-else>
        <div class="ann-item-head">
          <span class="ann-date">{{ item.date }}</span>
          <h4 class="ann-title">{{ item.title }}</h4>
          <span v-if="item.category" class="ann-category">{{ categoryText[item.category] || item.category }}</span>
          <a v-if="isAdmin" class="ann-edit-btn" @click="startEdit(item)">编辑</a>
          <a v-if="isAdmin" class="ann-del" @click="handleDelete(item.id)">删除</a>
        </div>
        <p class="ann-content">{{ item.content }}</p>
      </template>
    </div>

    <div v-if="loading" class="ann-loading">
      <AppSpinner />
    </div>
    <p v-else-if="displayItems.length === 0 && !loading" class="ann-empty">暂无公告</p>
  </div>
</template>

<style scoped>
.ann { display: flex; flex-direction: column; gap: 12px }

.ann-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px }
.ann-head-title { font-size: 1.05rem; font-weight: 600; color: #2c2c2c; letter-spacing: .06em; margin: 0 }
.ann-add-btn {
  height: 30px; padding: 0 12px; border: 1px solid #c9a96e; border-radius: 6px;
  background: #fefcf9; color: #8b7b65; font-size: .76rem; cursor: pointer;
  font-family: inherit; text-decoration: none; display: inline-flex; align-items: center;
  transition: border-color .2s, color .2s;
}
.ann-add-btn:hover { border-color: #b5343a; color: #b5343a }

.ann-item{padding:16px;background:#fff;border-radius:10px;border:1px solid #f2ebe0}
.ann-item-head{display:flex;align-items:center;gap:12px;margin-bottom:8px}
.ann-date{font-size:.76rem;color:#b0a090;white-space:nowrap}
.ann-title{font-size:.95rem;color:#3c3028;font-weight:600;flex:1}
.ann-category{flex-shrink:0;padding:2px 8px;border-radius:999px;background:#edf6ef;color:#4a8c5c;font-size:.72rem}
.ann-edit-btn{font-size:.74rem;color:#c4b0a0;cursor:pointer;flex-shrink:0;opacity:0;transition:opacity .15s}
.ann-del{font-size:.74rem;color:#c4b0a0;cursor:pointer;flex-shrink:0;opacity:0;transition:opacity .15s}
@media (hover: hover) {
  .ann-item:hover .ann-edit-btn{opacity:1}
  .ann-item:hover .ann-del{opacity:1}
}
@media (hover: none) {
  .ann-edit-btn, .ann-del { opacity: 1; padding: 4px 6px; min-height: 32px; display: inline-flex; align-items: center }
}
.ann-edit-btn:hover{color:#4a8c5c}
.ann-del:hover{color:#b5343a}
.ann-content{font-size:.86rem;color:#5c5040;line-height:1.7}

/* 编辑模式 */
.ann-edit-row{display:flex;gap:10px;margin-bottom:10px}
.ann-edit-date{width:140px;height:34px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.8rem;color:#3c3028;font-family:inherit;outline:none}
.ann-edit-date:focus{border-color:#4a8c5c}
.ann-edit-title{flex:1;height:34px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.88rem;font-weight:600;color:#3c3028;font-family:inherit;outline:none}
.ann-edit-title:focus{border-color:#4a8c5c}
.ann-edit-category{width:100%;height:34px;margin-bottom:10px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.8rem;color:#3c3028;background:#fff;font-family:inherit;outline:none}
.ann-edit-category:focus{border-color:#4a8c5c}
.ann-edit-content{width:100%;padding:10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;font-family:inherit;resize:vertical;outline:none;line-height:1.6}
.ann-edit-content:focus{border-color:#4a8c5c}
.ann-edit-actions{display:flex;gap:8px;margin-top:10px;justify-content:flex-end}
.ann-edit-save{height:30px;padding:0 16px;border:none;border-radius:6px;background:#4a8c5c;color:#fff;font-size:.78rem;cursor:pointer;font-family:inherit;transition:opacity .2s}
.ann-edit-save:hover:not(:disabled){opacity:.9}
.ann-edit-save:disabled{opacity:.5;cursor:default}
.ann-edit-cancel{height:30px;padding:0 16px;border:1px solid #e5dbcc;border-radius:6px;background:#fff;color:#8b7b65;font-size:.78rem;cursor:pointer;font-family:inherit;transition:border-color .2s}
.ann-edit-cancel:hover:not(:disabled){border-color:#b0a090}
.ann-edit-cancel:disabled{opacity:.5;cursor:default}

/* ===== Toast 通知 ===== */
.ann-toast {
  position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 9999;
  display: flex; align-items: center; gap: 10px;
  padding: 12px 28px; border-radius: 10px;
  background: #4a8c5c; color: #fff;
  font-size: .92rem; font-weight: 600;
  box-shadow: 0 4px 24px rgba(74,140,92,.35);
  pointer-events: none;
}
.ann-toast--err { background: #b5343a; box-shadow: 0 4px 24px rgba(181,52,58,.35) }
.ann-toast svg { flex-shrink: 0 }

.toast-enter-active { animation: toastIn .35s cubic-bezier(.33,1,.68,1) both }
.toast-leave-active { animation: toastOut .3s ease-in both }
@keyframes toastIn { from { opacity: 0; transform: translateX(-50%) translateY(-16px) } to { opacity: 1; transform: translateX(-50%) translateY(0) } }
@keyframes toastOut { to { opacity: 0; transform: translateX(-50%) translateY(-12px) } }

.ann-empty{text-align:center;color:#b0a090;padding:16px 0;font-size:.84rem}
.ann-loading{display:flex;align-items:center;justify-content:center;padding:32px 0}

@media(max-width:768px){
  .ann-header { flex-wrap: wrap; gap: 10px }
  .ann-add-btn { min-height: 40px; padding: 0 14px; font-size: .8rem }
  .ann-item-head { flex-wrap: wrap; gap: 8px }
  .ann-edit-row { flex-direction: column }
  .ann-edit-date { width: 100%; min-height: 44px; font-size: 16px }
  .ann-edit-title, .ann-edit-category, .ann-edit-content {
    min-height: 44px; font-size: 16px;
  }
  .ann-edit-save, .ann-edit-cancel { min-height: 44px; padding: 0 18px }
}

@media(max-width:480px){
  .ann-item{padding:12px}
  .ann-title{font-size:.88rem}
  .ann-content{font-size:.8rem}
}
</style>
