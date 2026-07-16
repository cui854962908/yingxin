<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAppNavigate } from '../composables/useAppNavigate'
import { authFetch } from '../composables/useAuthFetch'
import { hasAuthToken } from '../composables/useGuest'

const { appGoBackTo } = useAppNavigate()

const currentPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

function goBack() {
  appGoBackTo('/')
}

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  if (!currentPwd.value || !newPwd.value || !confirmPwd.value) {
    errorMsg.value = '请填写全部字段'
    return
  }
  if (newPwd.value.length < 8) {
    errorMsg.value = '新密码至少 8 位'
    return
  }
  if (newPwd.value !== confirmPwd.value) {
    errorMsg.value = '两次输入的新密码不一致'
    return
  }
  if (newPwd.value === currentPwd.value) {
    errorMsg.value = '新密码不能与当前密码相同'
    return
  }

  loading.value = true
  try {
    const res = await authFetch('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: currentPwd.value,
        new_password: newPwd.value,
      }),
    })
    const data = await res.json()
    if (data.success) {
      successMsg.value = '密码已更新，请妥善保管新密码'
      currentPwd.value = ''
      newPwd.value = ''
      confirmPwd.value = ''
    } else {
      errorMsg.value = data.message || '修改失败'
    }
  } catch {
    errorMsg.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!hasAuthToken()) appGoBackTo('/')
})
</script>

<template>
  <div class="pwd-page">
    <header class="pwd-header">
      <button type="button" class="pwd-back" @click="goBack">← 返回</button>
      <h1 class="pwd-title">修改密码</h1>
      <p class="pwd-desc">请先输入当前密码，再设置新密码（至少 8 位）</p>
    </header>

    <form class="pwd-form" @submit.prevent="handleSubmit">
      <div class="pwd-field">
        <label class="pwd-label" for="current-pwd">当前密码</label>
        <input
          id="current-pwd"
          v-model="currentPwd"
          type="password"
          class="pwd-input"
          autocomplete="current-password"
          placeholder="请输入当前登录密码"
        />
      </div>
      <div class="pwd-field">
        <label class="pwd-label" for="new-pwd">新密码</label>
        <input
          id="new-pwd"
          v-model="newPwd"
          type="password"
          class="pwd-input"
          autocomplete="new-password"
          placeholder="至少 8 位"
        />
      </div>
      <div class="pwd-field">
        <label class="pwd-label" for="confirm-pwd">确认新密码</label>
        <input
          id="confirm-pwd"
          v-model="confirmPwd"
          type="password"
          class="pwd-input"
          autocomplete="new-password"
          placeholder="再次输入新密码"
        />
      </div>

      <p v-if="errorMsg" class="pwd-error">{{ errorMsg }}</p>
      <p v-if="successMsg" class="pwd-success">{{ successMsg }}</p>

      <div class="pwd-actions">
        <button type="button" class="pwd-cancel" @click="goBack">取消</button>
        <button type="submit" class="pwd-submit" :disabled="loading">
          {{ loading ? '提交中…' : '确认修改' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.pwd-page {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: 8px 0 24px;
}
.pwd-header { margin-bottom: 28px }
.pwd-back {
  border: none;
  background: none;
  color: #8b7b65;
  font-size: .84rem;
  cursor: pointer;
  padding: 0;
  margin-bottom: 12px;
  font-family: inherit;
}
.pwd-back:hover { color: #b5343a }
.pwd-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c2c2c;
  letter-spacing: .08em;
}
.pwd-desc {
  margin-top: 8px;
  font-size: .86rem;
  color: #8b7b65;
  line-height: 1.55;
}
.pwd-form { display: flex; flex-direction: column; gap: 18px }
.pwd-field { display: flex; flex-direction: column; gap: 8px }
.pwd-label { font-size: .88rem; font-weight: 500; color: #3c3028 }
.pwd-input {
  height: 46px;
  padding: 0 14px;
  border: 1.5px solid #e5dbcc;
  border-radius: 10px;
  font-size: .92rem;
  color: #3c3028;
  background: #fefcf9;
  outline: none;
  font-family: inherit;
  transition: border-color .2s;
}
.pwd-input:focus { border-color: #b5343a }
.pwd-error {
  margin: 0;
  font-size: .84rem;
  color: #b5343a;
  background: #fef5f5;
  border: 1px solid #fce4e4;
  border-radius: 8px;
  padding: 10px 14px;
}
.pwd-success {
  margin: 0;
  font-size: .84rem;
  color: #2d7a4f;
  background: #f0faf4;
  border: 1px solid #d4edda;
  border-radius: 8px;
  padding: 10px 14px;
}
.pwd-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}
.pwd-cancel {
  height: 42px;
  padding: 0 22px;
  border: 1px solid #d4c8b0;
  border-radius: 10px;
  background: #fff;
  color: #8b7b65;
  font-size: .86rem;
  cursor: pointer;
  font-family: inherit;
}
.pwd-submit {
  height: 42px;
  padding: 0 28px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #b5343a, #9a2d32);
  color: #fff;
  font-size: .88rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.pwd-submit:disabled { opacity: .6; cursor: not-allowed }

@media (max-width: 768px) {
  .pwd-page { max-width: 100%; padding: 4px 0 16px }
  .pwd-title { font-size: 1.3rem }
}
</style>
