<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppNavigate } from '../composables/useAppNavigate'
import { authHeaders, useAuth } from '../composables/useAuth'

const { appGoBackTo } = useAppNavigate()
const { isAdmin } = useAuth()
const title = ref('')
const content = ref('')
const category = ref('')
const saving = ref(false)

function goBack() { appGoBackTo('/announcements') }

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim()) return
  saving.value = true
  try {
    const body: Record<string, string> = {
      title: title.value.trim(),
      content: content.value.trim(),
      category: category.value || 'campus',
    }
    const res = await fetch('/api/admin/announcements', {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) { console.warn('发布公告失败', res.status); saving.value = false; return }
    const d = await res.json()
    if (!d.success) { console.warn('发布公告失败', d.message); saving.value = false; return }
    goBack()
  } catch { console.warn('发布公告请求失败') }
  finally { saving.value = false }
}

onMounted(() => {
  if (!isAdmin.value) appGoBackTo('/announcements')
})
</script>

<template>
  <div class="aaf">
    <div class="aaf-field">
      <label class="aaf-label">公告标题</label>
      <input v-model="title" class="aaf-input" placeholder="例如：新生军训安排通知" />
    </div>
    <div class="aaf-field">
      <label class="aaf-label">分类</label>
      <select v-model="category" class="aaf-select">
        <option value="">校园公告</option>
        <option value="guide">报到须知</option>
        <option value="tips">新生攻略</option>
      </select>
    </div>
    <div class="aaf-field">
      <label class="aaf-label">公告内容</label>
      <textarea v-model="content" class="aaf-textarea" placeholder="请输入公告正文..." rows="6" />
    </div>
    <div class="aaf-actions">
      <button class="aaf-cancel" @click="goBack">取消</button>
      <button class="aaf-submit" :disabled="saving" @click="handleSubmit">
        {{ saving ? '发布中...' : '发布公告' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.aaf{display:flex;flex-direction:column;gap:20px;width:100%}
.aaf-field{display:flex;flex-direction:column;gap:8px}
.aaf-label{font-size:.88rem;font-weight:500;color:#3c3028;letter-spacing:.04em}
.aaf-input{height:44px;padding:0 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.9rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.aaf-input:focus{border-color:#b5343a}
.aaf-select{height:44px;padding:0 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.9rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;cursor:pointer;transition:border-color .2s}
.aaf-select:focus{border-color:#b5343a}
.aaf-textarea{padding:12px 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.9rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;resize:vertical;line-height:1.7;transition:border-color .2s}
.aaf-textarea:focus{border-color:#b5343a}
.aaf-actions{display:flex;justify-content:flex-end;gap:10px}
.aaf-cancel{height:38px;padding:0 24px;border:1px solid #d4c8b0;border-radius:8px;background:#fff;color:#8b7b65;font-size:.84rem;cursor:pointer;font-family:inherit}
.aaf-submit{height:38px;padding:0 28px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit}
.aaf-submit:disabled{opacity:.5}

@media(max-width:768px){
  .aaf-actions{flex-direction:column-reverse}
  .aaf-cancel,.aaf-submit{width:100%;height:44px;min-height:44px}
  .aaf-input,.aaf-select,.aaf-textarea{font-size:1rem}
}
</style>
