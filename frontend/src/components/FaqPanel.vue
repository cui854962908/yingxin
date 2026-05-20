<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'

interface FaqItem { id: string; question: string; answer: string }

const allItems = ref<FaqItem[]>([])
const expanded = reactive<Record<string, boolean>>({})
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

function toggleExpand(id: string) { expanded[id] = !expanded[id] }

async function handleDelete(id: string) {
  try {
    await fetch(`/api/admin/faq/${id}`, { method: 'DELETE', headers: authHeaders() })
    await loadFaq()
  } catch { /* */ }
}

onMounted(loadFaq)

defineExpose({ refresh: loadFaq })
</script>

<template>
  <div class="faq">
    <!-- 标题栏 -->
    <div class="faq-header">
      <h3 class="faq-title">常见问题</h3>
      <router-link v-if="isAdmin" to="/faq/add" class="faq-add-btn">+ 添加问题</router-link>
    </div>
    <!-- 搜索栏 -->
    <div class="faq-search-bar">
      <input v-model="searchQ" type="text" class="faq-search-input" placeholder="搜索问题或答案关键词..." />
      <button class="faq-search-btn">搜索</button>
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
        <a v-if="isAdmin" class="faq-del" @click.stop="handleDelete(item.id)">删除</a>
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

.faq-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px }
.faq-title { font-size: 1.05rem; font-weight: 600; color: #2c2c2c; letter-spacing: .06em; margin: 0 }
.faq-add-btn {
  height: 30px; padding: 0 12px; border: 1px solid #c9a96e; border-radius: 6px;
  background: #fefcf9; color: #8b7b65; font-size: .76rem; cursor: pointer;
  font-family: inherit; text-decoration: none; display: inline-flex; align-items: center;
  transition: border-color .2s, color .2s;
}
.faq-add-btn:hover { border-color: #b5343a; color: #b5343a }

.faq-search-bar{display:flex;gap:8px;padding-bottom:12px;position:sticky;top:0;z-index:10;background:#fff;padding-top:4px}
.faq-search-input{flex:1;height:38px;padding:0 12px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.faq-search-input:focus{border-color:#b5343a}
.faq-search-btn{height:38px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .2s}
.faq-search-btn:hover{opacity:.9}

.faq-item{padding:14px 16px;background:#fff;border-radius:10px;border:1px solid #f2ebe0;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.faq-item:hover{border-color:#e5dbcc}
.faq-item--open{border-color:#e5dbcc;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.faq-q{display:flex;align-items:center;gap:10px}
.faq-q-num{width:24px;height:24px;border-radius:6px;background:#f2ebe0;color:#8b7b65;font-size:.72rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:'Georgia',serif}
.faq-q-text{flex:1;font-size:.92rem;color:#3c3028;font-weight:600;line-height:1.5}
.faq-q-arrow{font-size:.6rem;color:#c4b8a8;flex-shrink:0;transition:transform .2s}
.faq-del{font-size:.74rem;color:#c4b0a0;cursor:pointer;flex-shrink:0;opacity:0;transition:opacity .15s}
.faq-q:hover .faq-del{opacity:1}
.faq-del:hover{color:#b5343a}

.faq-a{margin-top:12px;padding-top:12px;border-top:1px solid #faf4ea}
.faq-a-text{font-size:.86rem;color:#5c5040;line-height:1.7;white-space:pre-line}

.faq-empty{text-align:center;color:#b0a090;padding:16px 0;font-size:.84rem}

@media(max-width:480px){
  .faq-search-bar{flex-wrap:nowrap}
  .faq-search-btn{flex:none;padding:0 16px}
  .faq-item{padding:12px}
  .faq-q-text{font-size:.84rem}
  .faq-q-num{width:20px;height:20px;font-size:.66rem}
}
</style>
