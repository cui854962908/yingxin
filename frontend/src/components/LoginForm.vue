<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'login-success': [student: Record<string, any>, token: string, refreshToken?: string]
}>()

const name = ref('')
const studentId = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleSubmit() {
  errorMsg.value = ''
  if (!name.value.trim() || !studentId.value.trim() || !password.value) {
    errorMsg.value = '请填写姓名、学号和密码'
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
        password: password.value,
      }),
    })
    const data = await res.json()
    if (data.success) {
      emit('login-success', data.data, data.token, data.refresh_token)
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
        inputmode="numeric"
        class="field-input"
        placeholder="请输入你的学号"
        autocomplete="off"
      />
    </div>

    <div class="field">
      <label class="field-label" for="password">
        <span class="field-num">叁</span> 密 码
      </label>
      <input
        id="password"
        v-model="password"
        type="password"
        class="field-input"
        placeholder="请输入登录密码"
        autocomplete="current-password"
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
  color: #3d3224;
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
  transition: border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              background 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: inherit;
}

.field-input::placeholder {
  color: #8e7b68;
  font-size: 0.9rem;
}

.field-input:focus {
  border-color: #b5343a;
  box-shadow: 0 0 0 4px rgba(181, 52, 58, 0.1);
  background: #fff;
  outline: 2px solid rgba(181, 52, 58, 0.2);
  outline-offset: 1px;
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
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              background 0.25s ease;
  font-family: inherit;
  margin-top: 6px;
  box-shadow: 0 2px 8px rgba(181, 52, 58, 0.2);
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(181, 52, 58, 0.32);
}

.btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 1px 4px rgba(181, 52, 58, 0.15);
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

@media(max-width:480px){
  .form{
    gap:14px;
  }
  .field{
    gap:8px;
  }
  .field-label{
    font-size:.86rem;
    font-weight:700;
    color:#242a31;
    letter-spacing:.12em;
  }
  .field-num{
    display:none;
  }
  .field-input{
    height:50px;
    padding:0 16px;
    border:1.5px solid #ddd4cb;
    border-radius:13px;
    background:#fff;
    color:#29313a;
    font-size:16px;
    box-shadow:inset 0 1px 2px rgba(40,30,20,.03);
  }
  .field-input::placeholder{
    color:#9b9691;
    font-size:16px;
  }
  .field-input:focus{
    border-color:#a31522;
    box-shadow:0 0 0 4px rgba(163,21,34,.10);
    outline:none;
  }
  .btn{
    height:52px;
    margin-top:6px;
    border-radius:13px;
    background:linear-gradient(135deg,#bd1f2e 0%,#8f101c 100%);
    color:#fff;
    font-size:1rem;
    font-weight:800;
    letter-spacing:.22em;
    text-indent:.22em;
    box-shadow:0 10px 24px rgba(143,16,28,.28);
  }
  .error-msg{
    margin-top:-2px;
    border-radius:12px;
  }
}

@media(min-width:481px) and (max-width:768px){
  .form{
    gap:16px;
  }
  .field{
    gap:8px;
  }
  .field-label{
    font-size:.9rem;
    font-weight:700;
    color:#242a31;
    letter-spacing:.12em;
  }
  .field-num{
    display:none;
  }
  .field-input{
    height:54px;
    padding:0 18px;
    border:1.5px solid #ddd4cb;
    border-radius:13px;
    background:#fff;
    color:#29313a;
    font-size:16px;
  }
  .field-input::placeholder{
    color:#9b9691;
    font-size:16px;
  }
  .field-input:focus{
    border-color:#a31522;
    box-shadow:0 0 0 4px rgba(163,21,34,.10);
    outline:none;
  }
  .btn{
    height:54px;
    margin-top:6px;
    border-radius:13px;
    background:linear-gradient(135deg,#bd1f2e 0%,#8f101c 100%);
    color:#fff;
    font-size:1.04rem;
    font-weight:800;
    letter-spacing:.24em;
    text-indent:.24em;
    box-shadow:0 10px 24px rgba(143,16,28,.28);
  }
}
</style>
