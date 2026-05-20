<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Announcement { id: string; date: string; title: string; content: string }

const items = ref<Announcement[]>([])

const isAdmin = localStorage.getItem('student')
  ? JSON.parse(localStorage.getItem('student')!).role === 'admin'
  : false

function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('token')
  return t ? { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` } : {}
}

async function load() {
  try {
    const res = await fetch('/api/announcements')
    const d = await res.json()
    if (d.success) items.value = d.data
  } catch { /* */ }
}

async function handleDelete(id: string) {
  try {
    await fetch(`/api/admin/announcements/${id}`, { method: 'DELETE', headers: authHeaders() })
    await load()
  } catch { /* */ }
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
    <div v-for="item in items" :key="item.id" class="ann-item">
      <div class="ann-item-head">
        <span class="ann-date">{{ item.date }}</span>
        <h4 class="ann-title">{{ item.title }}</h4>
        <a v-if="isAdmin" class="ann-del" @click="handleDelete(item.id)">删除</a>
      </div>
      <p class="ann-content">{{ item.content }}</p>
    </div>

    <p v-if="items.length === 0" class="ann-empty">暂无公告</p>
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
.ann-del{font-size:.74rem;color:#c4b0a0;cursor:pointer;flex-shrink:0;opacity:0;transition:opacity .15s}
.ann-item:hover .ann-del{opacity:1}
.ann-del:hover{color:#b5343a}
.ann-content{font-size:.86rem;color:#5c5040;line-height:1.7}

.ann-empty{text-align:center;color:#b0a090;padding:16px 0;font-size:.84rem}

@media(max-width:480px){
  .ann-item{padding:12px}
  .ann-title{font-size:.88rem}
  .ann-content{font-size:.8rem}
}
</style>
