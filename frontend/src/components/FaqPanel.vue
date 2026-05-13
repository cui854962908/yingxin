<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'

interface FaqItem { id: string; question: string; answer: string }

const props = defineProps<{ showAdd: boolean }>()
const emit = defineEmits<{ added: []; cancelled: [] }>()

const allItems = ref<FaqItem[]>([])
const expanded = reactive<Record<string, boolean>>({})
const newQ = ref('')
const newA = ref('')
const saving = ref(false)
const searchQ = ref('')

const items = computed(() => {
  const q = searchQ.value.trim().toLowerCase()
  if (!q) return allItems.value
  return allItems.value.filter(
    i => i.question.toLowerCase().includes(q) || i.answer.toLowerCase().includes(q),
  )
})

const isAdmin = localStorage.getItem('student')
  ? JSON.parse(localStorage.getItem('student')!).role === 'admin'
  : false

function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('token')
  return t ? { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` } : {}
}

async function loadFaq() {
  try {
    const res = await fetch('/api/faq')
    const d = await res.json()
    if (d.success) allItems.value = d.data
  } catch { /* */ }
}

function toggleExpand(id: string) {
  expanded[id] = !expanded[id]
}

async function handleAdd() {
  if (!newQ.value.trim() || !newA.value.trim()) return
  saving.value = true
  try {
    await fetch('/api/admin/faq', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ question: newQ.value.trim(), answer: newA.value.trim() }),
    })
    newQ.value = ''; newA.value = ''
    emit('added')
    await loadFaq()
  } catch { /* */ }
  saving.value = false
}

async function handleDelete(id: string) {
  try {
    await fetch(`/api/admin/faq/${id}`, { method: 'DELETE', headers: authHeaders() })
    await loadFaq()
  } catch { /* */ }
}

function doSearch() { /* computed auto-reacts */ }

onMounted(loadFaq)
</script>

<template>
  <div class="faq">
    <!-- 搜索栏 -->
    <div class="faq-search-bar">
      <input
        v-model="searchQ" type="text" class="faq-search-input"
        placeholder="搜索问题或答案关键词..."
        @keyup.enter="doSearch"
      />
      <button class="faq-search-btn" @click="doSearch">搜索</button>
    </div>

    <!-- 添加表单 -->
    <div v-if="props.showAdd" class="faq-add-form">
      <input v-model="newQ" class="faq-add-input" placeholder="问题标题..." />
      <textarea v-model="newA" class="faq-add-textarea" placeholder="答案内容（支持换行）..." rows="4" />
      <div class="faq-add-foot">
        <button class="faq-add-cancel" @click="emit('cancelled')">取消</button>
        <button class="faq-add-submit" :disabled="saving" @click="handleAdd">
          {{ saving ? '提交中...' : '提交' }}
        </button>
      </div>
    </div>

    <!-- FAQ 列表 -->
    <div
      v-for="(item, idx) in items" :key="item.id"
      class="faq-item" :class="{ 'faq-item--open': expanded[item.id] }"
      @click="toggleExpand(item.id)"
    >
      <div class="faq-q">
        <span class="faq-q-num">{{ idx + 1 }}</span>
        <span class="faq-q-text">{{ item.question }}</span>
        <span class="faq-q-arrow">{{ expanded[item.id] ? '▲' : '▼' }}</span>
        <a
          v-if="isAdmin" class="faq-del"
          @click.stop="handleDelete(item.id)"
        >删除</a>
      </div>
      <div v-if="expanded[item.id]" class="faq-a">
        <span class="faq-a-text" v-text="item.answer" />
      </div>
    </div>

    <p v-if="items.length === 0 && allItems.length > 0" class="faq-empty">未找到匹配的问题</p>
    <p v-else-if="allItems.length === 0" class="faq-empty">暂无常见问题</p>
  </div>
</template>

<style scoped>
.faq { display: flex; flex-direction: column; gap: 10px }

/* 搜索 */
.faq-search-bar{display:flex;gap:8px;position:sticky;top:0;z-index:10;background:#fff;padding-bottom:12px}
.faq-search-input{flex:1;height:38px;padding:0 12px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.faq-search-input:focus{border-color:#b5343a}
.faq-search-btn{height:38px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .2s}
.faq-search-btn:hover{opacity:.9}

/* 添加表单 */
.faq-add-form{display:flex;flex-direction:column;gap:10px;padding:16px;background:#fdfaf6;border-radius:10px;border:1px solid #f0e8da}
.faq-add-input{height:38px;padding:0 12px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;background:#fff;outline:none;font-family:inherit}
.faq-add-input:focus{border-color:#b5343a}
.faq-add-textarea{padding:10px 12px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;background:#fff;outline:none;font-family:inherit;resize:vertical}
.faq-add-textarea:focus{border-color:#b5343a}
.faq-add-foot{display:flex;justify-content:flex-end;gap:8px}
.faq-add-cancel{height:32px;padding:0 16px;border:1px solid #d4c8b0;border-radius:6px;background:#fff;color:#8b7b65;font-size:.8rem;cursor:pointer;font-family:inherit}
.faq-add-submit{height:32px;padding:0 16px;border:none;border-radius:6px;background:#b5343a;color:#fff;font-size:.8rem;font-weight:500;cursor:pointer;font-family:inherit}
.faq-add-submit:disabled{opacity:.5}

/* 条目 */
.faq-item{padding:14px 16px;background:#fff;border-radius:10px;border:1px solid #f2ebe0;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.faq-item:hover{border-color:#e5dbcc}
.faq-item--open{border-color:#e5dbcc;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.faq-q{display:flex;align-items:center;gap:10px}
.faq-q-num{
  width:24px;height:24px;border-radius:6px;background:#f2ebe0;color:#8b7b65;
  font-size:.72rem;font-weight:700;display:flex;align-items:center;justify-content:center;
  flex-shrink:0;font-family:'Georgia',serif;
}
.faq-q-text{flex:1;font-size:.92rem;color:#3c3028;font-weight:600;line-height:1.5}
.faq-q-arrow{font-size:.6rem;color:#c4b8a8;flex-shrink:0;transition:transform .2s}
.faq-del{font-size:.74rem;color:#c4b0a0;cursor:pointer;flex-shrink:0;opacity:0;transition:opacity .15s}
.faq-q:hover .faq-del{opacity:1}
.faq-del:hover{color:#b5343a}

.faq-a{margin-top:12px;padding-top:12px;border-top:1px solid #faf4ea}
.faq-a-text{font-size:.86rem;color:#5c5040;line-height:1.7;white-space:pre-line}

.faq-empty{text-align:center;color:#b0a090;padding:16px 0;font-size:.84rem}
</style>
