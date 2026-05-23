<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const question = ref('')
const answer = ref('')
const saving = ref(false)

function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('token')
  return t ? { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` } : {}
}

function goBack() { router.push('/faq') }

async function handleSubmit() {
  if (!question.value.trim() || !answer.value.trim()) return
  saving.value = true
  try {
    await fetch('/api/admin/faq', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ question: question.value.trim(), answer: answer.value.trim() }),
    })
    goBack()
  } catch { console.warn('发布FAQ请求失败') }
  saving.value = false
}
</script>

<template>
  <div class="faf">
    <div class="faf-field">
      <label class="faf-label">问题标题</label>
      <input v-model="question" class="faf-input" placeholder="例如：学校快递站在哪里？" />
    </div>
    <div class="faf-field">
      <label class="faf-label">答案内容</label>
      <textarea v-model="answer" class="faf-textarea" placeholder="请输入详细的答案内容，支持换行分段..." rows="8" />
    </div>
    <div class="faf-actions">
      <button class="faf-cancel" @click="goBack">取消</button>
      <button class="faf-submit" :disabled="saving" @click="handleSubmit">
        {{ saving ? '提交中...' : '发布问题' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.faf{display:flex;flex-direction:column;gap:20px;width:100%}
.faf-field{display:flex;flex-direction:column;gap:8px}
.faf-label{font-size:.88rem;font-weight:500;color:#3c3028;letter-spacing:.04em}
.faf-input{height:44px;padding:0 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.9rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.faf-input:focus{border-color:#b5343a}
.faf-textarea{padding:12px 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.9rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;resize:vertical;line-height:1.7;transition:border-color .2s}
.faf-textarea:focus{border-color:#b5343a}
.faf-actions{display:flex;justify-content:flex-end;gap:10px}
.faf-cancel{height:38px;padding:0 24px;border:1px solid #d4c8b0;border-radius:8px;background:#fff;color:#8b7b65;font-size:.84rem;cursor:pointer;font-family:inherit}
.faf-submit{height:38px;padding:0 28px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit}
.faf-submit:disabled{opacity:.5}
</style>
