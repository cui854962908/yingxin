<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'login-success': [student: Record<string, any>, token: string]
}>()

const name = ref('')
const studentId = ref('')
const idNumber = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleSubmit() {
  errorMsg.value = ''
  if (!name.value.trim() || !studentId.value.trim() || !idNumber.value.trim()) {
    errorMsg.value = '请填写所有字段'
    return
  }
  loading.value = true
  try {
    const res = await fetch('/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value.trim(),
        student_id: studentId.value.trim(),
        id_number: idNumber.value.trim(),
      }),
    })
    const data = await res.json()
    if (data.success) {
      emit('login-success', data.data, data.token)
    } else {
      errorMsg.value = data.message
    }
  } catch {
    errorMsg.value = '网络异常，请检查后端服务是否已启动'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form class="form" @submit.prevent="handleSubmit">
    <div class="field">
      <label class="field-label" for="name">
        <span class="field-num">壹</span> 姓 名
      </label>
      <input
        id="name"
        v-model="name"
        type="text"
        class="field-input"
        placeholder="请输入你的姓名"
        autocomplete="name"
      />
    </div>

    <div class="field">
      <label class="field-label" for="studentId">
        <span class="field-num">贰</span> 学 号
      </label>
      <input
        id="studentId"
        v-model="studentId"
        type="text"
        class="field-input"
        placeholder="请输入你的学号"
        autocomplete="off"
      />
    </div>

    <div class="field">
      <label class="field-label" for="idNumber">
        <span class="field-num">叁</span> 身份证号
      </label>
      <input
        id="idNumber"
        v-model="idNumber"
        type="text"
        class="field-input"
        placeholder="请输入你的身份证号"
        autocomplete="off"
      />
    </div>

    <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

    <button type="submit" class="btn" :disabled="loading">
      <span v-if="loading" class="btn-spinner" />
      <span>{{ loading ? '验证中...' : '验 证 登 录' }}</span>
    </button>
  </form>
</template>

<style scoped>
.form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-label {
  font-size: 0.85rem;
  color: #5c5040;
  font-weight: 500;
  letter-spacing: 0.08em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.field-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: #f2ebe0;
  color: #b5343a;
  font-size: 0.7rem;
  font-weight: 700;
  font-family: 'Noto Serif SC', 'KaiTi', serif;
  flex-shrink: 0;
}

.field-input {
  width: 100%;
  height: 46px;
  padding: 0 16px;
  border: 1.5px solid #e5dbcc;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #2c2c2c;
  background: #fefcf9;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  font-family: inherit;
}

.field-input::placeholder {
  color: #c4b8a8;
  font-size: 0.9rem;
}

.field-input:focus {
  border-color: #b5343a;
  box-shadow: 0 0 0 3px rgba(181, 52, 58, 0.07);
  background: #fff;
}

.error-msg {
  color: #b5343a;
  font-size: 0.84rem;
  text-align: center;
  background: #fef5f5;
  border: 1px solid #fce4e4;
  border-radius: 8px;
  padding: 10px 14px;
  line-height: 1.5;
}

.btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #b5343a 0%, #9a2d32 100%);
  color: #fff;
  font-size: 1.02rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s, transform 0.1s, box-shadow 0.2s;
  font-family: inherit;
  margin-top: 6px;
  box-shadow: 0 2px 12px rgba(181, 52, 58, 0.25);
}

.btn:hover:not(:disabled) {
  opacity: 0.93;
  box-shadow: 0 4px 16px rgba(181, 52, 58, 0.35);
}

.btn:active:not(:disabled) {
  transform: scale(0.985);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
