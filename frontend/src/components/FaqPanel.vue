<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { usePreload } from '../composables/usePreload'
import { authHeaders, useAuth } from '../composables/useAuth'
import { useFaqSort } from '../composables/useFaqSort'
import { faqMatchesSearch } from '../utils/faqSearch'
import AppSpinner from './AppSpinner.vue'

interface FaqItem { id: string; question: string; answer: string; keywords?: string; category?: string; sort_order?: number }

const { faqItems: cached } = usePreload()
const allItems = ref<FaqItem[]>(cached.value.length ? cached.value : [])
const loading = ref(!cached.value.length)
const expanded = reactive<Record<string, boolean>>({})
const searchQ = ref('')

// 分页（客户端）
const currentPage = ref(1)
const pageSize = 10

const searchedItems = computed(() => {
  const q = searchQ.value.trim()
  if (!q) return allItems.value
  return allItems.value.filter((i) => faqMatchesSearch(i, q))
})

watch(searchQ, () => {
  currentPage.value = 1
})

const totalPages = computed(() => Math.max(1, Math.ceil(searchedItems.value.length / pageSize)))

const displayItems = computed(() => {
  if (sortMode.value) return searchedItems.value // 排序模式显示全部
  const start = (currentPage.value - 1) * pageSize
  return searchedItems.value.slice(start, start + pageSize)
})

const { isAdmin } = useAuth()

// 编辑状态
const editMode = ref(false)
const editingId = ref<string | null>(null)
const editForm = ref({ question: '', answer: '', keywords: '', category: '', sort_order: 0 })
const saving = ref(false)
const saveMsg = ref('')

const {
  sortMode, dragIdx, dropIdx, enterSortMode: beginSort, exitSortMode, startDrag,
} = useFaqSort(allItems, displayItems)

function enterSortMode() {
  beginSort()
  editMode.value = false
  editingId.value = null
  searchQ.value = ''
  currentPage.value = 1
  Object.keys(expanded).forEach(k => delete expanded[k])
}

function enterEditMode() {
  editMode.value = true
  sortMode.value = false
  editingId.value = null
  Object.keys(expanded).forEach(k => delete expanded[k])
}

function exitEditMode() {
  editMode.value = false
  editingId.value = null
  saveMsg.value = ''
}

onMounted(() => { loadAllFaq() })

function startEdit(item: FaqItem) {
  editingId.value = item.id
  expanded[item.id] = true // 编辑时自动展开
  editForm.value = {
    question: item.question,
    answer: item.answer,
    keywords: item.keywords || '',
    category: item.category || '',
    sort_order: item.sort_order ?? 0,
  }
  saveMsg.value = ''
}

function cancelEdit() {
  editingId.value = null
  saveMsg.value = ''
}

function onItemClick(item: FaqItem) {
  if (sortMode.value) return
  if (editMode.value) {
    if (editingId.value !== item.id) startEdit(item)
    return
  }
  if (editingId.value === item.id) return
  toggleExpand(item.id)
}

async function saveEdit(id: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    const body: Record<string, string | number | null> = {}
    if (editForm.value.question) body.question = editForm.value.question
    if (editForm.value.answer) body.answer = editForm.value.answer
    body.keywords = editForm.value.keywords.trim() || null
    body.category = editForm.value.category.trim() || null
    body.sort_order = Number(editForm.value.sort_order)
    const res = await fetch(`/api/admin/faq/${id}`, {
      method: 'PATCH', headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error()
    saveMsg.value = '已保存'
    setTimeout(() => { editingId.value = null; saveMsg.value = ''; loadAllFaq() }, 1200)
  } catch {
    saveMsg.value = '保存失败，请重试'
  } finally { saving.value = false }
}

async function loadAllFaq() {
  loading.value = true
  try {
    const res = await fetch('/api/faq?page=1&page_size=200')
    const d = await res.json()
    if (d.success) {
      allItems.value = d.data.items
    }
  } catch { console.warn('加载FAQ失败') }
  finally { loading.value = false }
}

function goPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
}

function toggleExpand(id: string) {
  if (sortMode.value) return
  expanded[id] = !expanded[id]
}

async function handleDelete(id: string) {
  try {
    await fetch(`/api/admin/faq/${id}`, { method: 'DELETE', headers: authHeaders() })
    editingId.value = null
    await loadAllFaq()
  } catch { console.warn('删除FAQ请求失败') }
}

async function deleteFromEdit(id: string) {
  if (!confirm('确定删除这条问题？')) return
  await handleDelete(id)
}

defineExpose({ refresh: loadAllFaq })
</script>

<template>
  <div class="faq">
    <!-- 标题栏 -->
    <div class="faq-header">
      <h3 class="faq-title">常见问题</h3>
      <div class="faq-header-actions">
        <button v-if="isAdmin && !sortMode && !editMode" class="faq-sort-btn" @click="enterSortMode">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
          调整排序
        </button>
        <button v-if="isAdmin && sortMode" class="faq-sort-btn faq-sort-btn--active" @click="exitSortMode">完成排序</button>
        <button v-if="isAdmin && !sortMode && !editMode" class="faq-mode-btn" @click="enterEditMode">编辑</button>
        <router-link v-if="isAdmin && !sortMode && !editMode" to="/faq/add" class="faq-add-btn">+ 添加问题</router-link>
        <button v-if="isAdmin && editMode" class="faq-mode-btn faq-mode-btn--active" @click="exitEditMode">完成编辑</button>
      </div>
    </div>
    <!-- 搜索栏 -->
    <div v-if="!sortMode" class="faq-search-bar">
      <input v-model="searchQ" type="text" class="faq-search-input" placeholder="搜索问题标题或关键词…" />
      <button class="faq-search-btn">搜索</button>
    </div>

    <p v-if="editMode && !editingId" class="faq-edit-hint">点击任意问题开始编辑</p>

    <!-- FAQ 列表 -->
    <div
      v-for="(item, idx) in displayItems" :key="item.id"
      class="faq-item"
      :class="{
        'faq-item--open': expanded[item.id] || editingId === item.id,
        'faq-item--ghost': sortMode && dragIdx !== null && allItems[dragIdx]?.id === item.id,
        'faq-item--drop-before': sortMode && dropIdx === allItems.findIndex(i => i.id === item.id) && dragIdx !== null && dragIdx !== allItems.findIndex(i => i.id === item.id),
        'faq-item--sortable': sortMode,
        'faq-item--pickable': editMode && editingId !== item.id,
      }"
      @click="onItemClick(item)"
    >
      <!-- 编辑模式 -->
      <template v-if="editingId === item.id">
        <div class="faq-edit-row">
          <input v-model="editForm.question" class="faq-edit-question" placeholder="问题" @click.stop />
        </div>
        <textarea v-model="editForm.answer" class="faq-edit-answer" placeholder="答案" rows="4" @click.stop />
        <div class="faq-edit-meta">
          <input v-model="editForm.keywords" class="faq-edit-keywords" placeholder="关键词（逗号分隔）" @click.stop />
          <input v-model="editForm.category" class="faq-edit-category" placeholder="分类" @click.stop />
          <div class="faq-edit-sort">
            <label class="faq-edit-sort-label">排序</label>
            <input v-model.number="editForm.sort_order" type="number" min="0" class="faq-edit-sort-input" @click.stop />
          </div>
        </div>
        <div class="faq-edit-actions">
          <button class="faq-edit-delete" :disabled="saving" @click.stop="deleteFromEdit(item.id)">删除</button>
          <div class="faq-edit-actions-right">
            <button class="faq-edit-save" :disabled="saving" @click.stop="saveEdit(item.id)">{{ saving ? '保存中…' : '保存' }}</button>
            <button class="faq-edit-cancel" :disabled="saving" @click.stop="cancelEdit">取消</button>
          </div>
        </div>
        <Transition name="toast">
          <div v-if="saveMsg" class="faq-toast" :class="{ 'faq-toast--err': saveMsg !== '已保存' }">
            <svg v-if="saveMsg === '已保存'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>
            <span>{{ saveMsg }}</span>
          </div>
        </Transition>
      </template>
      <!-- 展示模式 -->
      <template v-else>
        <div class="faq-q">
          <span v-if="sortMode" class="faq-q-grip" @pointerdown.prevent.stop="startDrag(item.id, $event)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" opacity=".4"><circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/></svg>
          </span>
          <span v-else class="faq-q-num">{{ (currentPage - 1) * pageSize + idx + 1 }}</span>
          <span class="faq-q-text">{{ item.question }}</span>
          <span v-if="isAdmin && sortMode" class="faq-q-sort-tag">{{ item.sort_order ?? 0 }}</span>
          <span v-if="!sortMode && !editMode" class="faq-q-arrow">{{ expanded[item.id] ? '▲' : '▼' }}</span>
          <span v-if="editMode && editingId !== item.id" class="faq-q-edit-tag">点击编辑</span>
        </div>
        <div v-if="expanded[item.id]" class="faq-a">
          <span class="faq-a-text" v-text="item.answer" />
          <div v-if="item.category || item.keywords" class="faq-meta">
            <span v-if="item.category" class="faq-meta-tag faq-meta-tag--category">{{ item.category }}</span>
            <span v-if="item.keywords" class="faq-meta-tag">{{ item.keywords }}</span>
          </div>
        </div>
      </template>
    </div>

    <div v-if="loading" class="faq-loading">
      <AppSpinner />
    </div>
    <p v-else-if="displayItems.length === 0 && allItems.length > 0" class="faq-empty">未找到匹配的问题</p>
    <p v-else-if="allItems.length === 0" class="faq-empty">暂无常见问题</p>

    <!-- 分页（排序模式隐藏） -->
    <div v-if="!sortMode && totalPages > 1" class="faq-pager">
      <button :disabled="currentPage === 1" @click="goPage(currentPage - 1)">上一页</button>
      <span
        v-for="p in totalPages" :key="p"
        class="faq-page-num" :class="{ active: p === currentPage }"
        @click="goPage(p)"
      >{{ p }}</span>
      <button :disabled="currentPage === totalPages" @click="goPage(currentPage + 1)">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.faq { display: flex; flex-direction: column; gap: 10px }

.faq-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px }
.faq-title { font-size: 1.05rem; font-weight: 600; color: #2c2c2c; letter-spacing: .06em; margin: 0 }
.faq-header-actions { display: flex; align-items: center; gap: 8px }
.faq-sort-btn {
  height: 36px; min-height: 36px; padding: 0 12px; border: 1px solid #e5dbcc; border-radius: 6px;
  background: #fefcf9; color: #6b5e4e; font-size: .76rem; cursor: pointer;
  font-family: inherit; display: inline-flex; align-items: center; gap: 5px;
  transition: border-color .2s, color .2s;
}
.faq-sort-btn:hover { border-color: #4a8c5c; color: #4a8c5c }
.faq-sort-btn--active { background: #4a8c5c; color: #fff; border-color: #4a8c5c }
.faq-sort-btn--active:hover { background: #3d7a4d; color: #fff }
.faq-add-btn {
  height: 36px; min-height: 36px; padding: 0 12px; border: 1px solid #c9a96e; border-radius: 6px;
  background: #fefcf9; color: #8b7b65; font-size: .76rem; cursor: pointer;
  font-family: inherit; text-decoration: none; display: inline-flex; align-items: center;
  transition: border-color .2s, color .2s;
}
.faq-add-btn:hover { border-color: #b5343a; color: #b5343a }
.faq-mode-btn {
  height: 36px; min-height: 36px; padding: 0 12px; border: 1px solid #e5dbcc; border-radius: 6px;
  background: #fefcf9; color: #6b5e4e; font-size: .76rem; cursor: pointer;
  font-family: inherit; display: inline-flex; align-items: center;
  transition: border-color .2s, color .2s, background .2s;
}
.faq-mode-btn:hover { border-color: #4a8c5c; color: #4a8c5c }
.faq-mode-btn--active { background: #4a8c5c; color: #fff; border-color: #4a8c5c }
.faq-mode-btn--active:hover { background: #3d7a4d; color: #fff }

.faq-edit-hint {
  margin: 0; padding: 8px 12px; border-radius: 8px;
  background: #f5faf6; color: #4a8c5c; font-size: .78rem;
}

.faq-search-bar{display:flex;gap:8px;padding-bottom:12px;position:sticky;top:0;z-index:10;background:#fff;padding-top:4px}
.faq-search-input{flex:1;height:38px;padding:0 12px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.faq-search-input:focus{border-color:#b5343a}
.faq-search-btn{height:38px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .2s}
.faq-search-btn:hover{opacity:.9}

.faq-item{padding:14px 16px;background:#fff;border-radius:10px;border:1px solid #f2ebe0;cursor:pointer;transition:border-color .15s,box-shadow .15s,opacity .15s,margin-top .18s}
.faq-item:hover{border-color:#e5dbcc}
.faq-item--open{border-color:#e5dbcc;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.faq-item--sortable{cursor:grab;user-select:none}
.faq-item--sortable:active{cursor:grabbing}
/* 手动拖拽 */
.faq-item--ghost{opacity:.15; pointer-events:none}
.faq-item--drop-before{margin-top:58px; transition:margin-top .18s}
.faq-item--clone{transform:scale(1.04); box-shadow:0 12px 36px rgba(0,0,0,.18); border-radius:10px; background:#fff; cursor:grabbing}
.faq-q{display:flex;align-items:center;gap:10px}
.faq-q-grip{flex-shrink:0;display:flex;align-items:center;touch-action:none;cursor:grab;padding:4px 2px}
.faq-item--sortable{touch-action:pan-y}
.faq-item--sortable .faq-q-grip:active{cursor:grabbing}
.faq-q-num{width:24px;height:24px;border-radius:6px;background:#f2ebe0;color:#8b7b65;font-size:.72rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:'Georgia',serif}
.faq-q-text{flex:1;font-size:.92rem;color:#3c3028;font-weight:600;line-height:1.5}
.faq-q-sort-tag{flex-shrink:0;padding:2px 8px;border-radius:10px;background:#e8f5e9;color:#4a8c5c;font-size:.7rem;font-weight:600;letter-spacing:.03em}
.faq-q-arrow{font-size:.6rem;color:#c4b8a8;flex-shrink:0;transition:transform .2s}
.faq-q-edit-tag{font-size:.7rem;color:#4a8c5c;flex-shrink:0;opacity:.85}
.faq-item--pickable{cursor:pointer}
.faq-item--pickable:hover{border-color:#c5dcc9}

/* 编辑模式 */
.faq-edit-row{margin-bottom:8px}
.faq-edit-question{width:100%;height:34px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.88rem;font-weight:600;color:#3c3028;font-family:inherit;outline:none;box-sizing:border-box}
.faq-edit-question:focus{border-color:#4a8c5c}
.faq-edit-answer{width:100%;padding:10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;font-family:inherit;resize:vertical;outline:none;line-height:1.6;box-sizing:border-box}
.faq-edit-answer:focus{border-color:#4a8c5c}
.faq-edit-meta{display:flex;gap:10px;margin-top:8px}
.faq-edit-keywords{flex:1;height:32px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.78rem;color:#3c3028;font-family:inherit;outline:none;box-sizing:border-box}
.faq-edit-keywords:focus{border-color:#4a8c5c}
.faq-edit-category{width:120px;height:32px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.78rem;color:#3c3028;font-family:inherit;outline:none;box-sizing:border-box}
.faq-edit-category:focus{border-color:#4a8c5c}
.faq-edit-sort{display:flex;align-items:center;gap:6px;flex-shrink:0}
.faq-edit-sort-label{font-size:.72rem;color:#8b7b65;white-space:nowrap}
.faq-edit-sort-input{width:56px;height:32px;padding:0 8px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.78rem;color:#3c3028;font-family:inherit;outline:none;box-sizing:border-box;text-align:center}
.faq-edit-sort-input:focus{border-color:#4a8c5c}
.faq-edit-actions{display:flex;gap:8px;margin-top:10px;justify-content:space-between;align-items:center}
.faq-edit-actions-right{display:flex;gap:8px}
.faq-edit-delete{height:30px;padding:0 16px;border:1px solid #e5dbcc;border-radius:6px;background:#fff;color:#b5343a;font-size:.78rem;cursor:pointer;font-family:inherit;transition:border-color .2s,background .2s}
.faq-edit-delete:hover:not(:disabled){border-color:#b5343a;background:#fff5f5}
.faq-edit-delete:disabled{opacity:.5;cursor:default}
.faq-edit-save{height:30px;padding:0 16px;border:none;border-radius:6px;background:#4a8c5c;color:#fff;font-size:.78rem;cursor:pointer;font-family:inherit;transition:opacity .2s}
.faq-edit-save:hover:not(:disabled){opacity:.9}
.faq-edit-save:disabled{opacity:.5;cursor:default}
.faq-edit-cancel{height:30px;padding:0 16px;border:1px solid #e5dbcc;border-radius:6px;background:#fff;color:#8b7b65;font-size:.78rem;cursor:pointer;font-family:inherit;transition:border-color .2s}
.faq-edit-cancel:hover:not(:disabled){border-color:#b0a090}
.faq-edit-cancel:disabled{opacity:.5;cursor:default}

/* ===== Toast 通知 ===== */
.faq-toast {
  position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 9999;
  display: flex; align-items: center; gap: 10px;
  padding: 12px 28px; border-radius: 10px;
  background: #4a8c5c; color: #fff;
  font-size: .92rem; font-weight: 600;
  box-shadow: 0 4px 24px rgba(74,140,92,.35);
  pointer-events: none;
}
.faq-toast--err { background: #b5343a; box-shadow: 0 4px 24px rgba(181,52,58,.35) }
.faq-toast svg { flex-shrink: 0 }

.toast-enter-active { animation: toastIn .35s cubic-bezier(.33,1,.68,1) both }
.toast-leave-active { animation: toastOut .3s ease-in both }
@keyframes toastIn { from { opacity: 0; transform: translateX(-50%) translateY(-16px) } to { opacity: 1; transform: translateX(-50%) translateY(0) } }
@keyframes toastOut { to { opacity: 0; transform: translateX(-50%) translateY(-12px) } }

.faq-a{margin-top:12px;padding-top:12px;border-top:1px solid #faf4ea}
.faq-a-text{font-size:.86rem;color:#5c5040;line-height:1.7;white-space:pre-line}
.faq-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.faq-meta-tag{display:inline-flex;align-items:center;min-height:26px;padding:0 10px;border-radius:999px;background:#faf4ea;color:#8b7b65;font-size:.74rem}
.faq-meta-tag--category{background:#edf6ef;color:#4a8c5c}

.faq-empty{text-align:center;color:#b0a090;padding:16px 0;font-size:.84rem}
.faq-loading{display:flex;align-items:center;justify-content:center;padding:32px 0}

/* 分页 */
.faq-pager {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 16px 0 4px;
}
.faq-pager button {
  height: 40px; min-height: 40px; padding: 0 14px; border: 1px solid #e5dbcc; border-radius: 8px;
  background: #fefcf9; color: #6b5e4e; font-size: .8rem; cursor: pointer;
  font-family: inherit; transition: border-color .2s, color .2s;
}
.faq-pager button:hover:not(:disabled) { border-color: #b5343a; color: #b5343a }
.faq-pager button:disabled { opacity: .35; cursor: default }
.faq-page-num {
  width: 40px; height: 40px; border-radius: 8px; display: flex;
  align-items: center; justify-content: center; font-size: .8rem;
  color: #6b5e4e; cursor: pointer; transition: all .15s;
}
.faq-page-num:hover { background: #faf4ea }
.faq-page-num.active { background: #b5343a; color: #fff; font-weight: 600 }

@media(max-width:768px){
  .faq-header { flex-wrap: wrap; gap: 10px }
  .faq-header-actions { flex-wrap: wrap; gap: 8px }
  .faq-sort-btn, .faq-add-btn, .faq-mode-btn { min-height: 44px; padding: 0 14px; font-size: .8rem }
  .faq-search-bar { gap: 10px; padding-top: 8px }
  .faq-search-input { min-height: 44px; font-size: 16px }
  .faq-search-btn { min-height: 44px; padding: 0 18px }
  .faq-q { flex-wrap: wrap; gap: 8px }
  .faq-edit-meta { flex-direction: column }
  .faq-edit-category, .faq-edit-keywords { width: 100%; min-height: 44px; font-size: 16px }
  .faq-edit-question { min-height: 44px; font-size: 16px }
  .faq-edit-answer { font-size: 16px }
  .faq-edit-sort-input { min-height: 44px; font-size: 16px }
  .faq-edit-save, .faq-edit-cancel, .faq-edit-delete { min-height: 44px; padding: 0 18px }
  .faq-edit-actions { flex-wrap: wrap; gap: 10px }
  .faq-pager button { min-height: 44px }
  .faq-page-num { width: 44px; height: 44px }
}

@media(max-width:480px){
  .faq-search-input{font-size:16px}
  .faq-search-bar{flex-wrap:nowrap}
  .faq-search-btn{flex:none;padding:0 16px}
  .faq-item{padding:12px}
  .faq-q-text{font-size:.84rem}
  .faq-q-num{width:20px;height:20px;font-size:.66rem}
}
</style>
