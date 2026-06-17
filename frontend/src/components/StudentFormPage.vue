<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authHeaders } from '../composables/useAuth'

const router = useRouter()

const classList = ref<string[]>([])
const showClassList = ref(false)
const filteredClasses = ref<string[]>([])

function filterClassList() {
  const q = form.value.class_name.trim().toLowerCase()
  filteredClasses.value = q
    ? classList.value.filter(c => c.toLowerCase().includes(q))
    : classList.value
  showClassList.value = true
}

function selectClass(name: string) {
  form.value.class_name = name
  showClassList.value = false
}

function onClassBlur() { setTimeout(() => { showClassList.value = false }, 150) }

async function loadClasses() {
  try {
    const res = await fetch('/api/admin/classes', { headers: authHeaders() })
    const d = await res.json()
    if (d.success) classList.value = d.data
  } catch { /* ignore */ }
}

const form = ref({
  name: '', student_id: '', id_number: '', class_name: '', dormitory: '',
  advisor_name: '', advisor_phone: '',
  class_teacher_name: '', class_teacher_phone: '',
  assistant_name: '', assistant_phone: '', assistant_class: '',
})
const formSaving = ref(false)
const toast = ref('')

async function saveForm() {
  formSaving.value = true
  const body = JSON.stringify({
    name: form.value.name, student_id: form.value.student_id,
    id_number: form.value.id_number, class_name: form.value.class_name,
    dormitory: form.value.dormitory,
    advisor_name: form.value.advisor_name, advisor_phone: form.value.advisor_phone,
    class_teacher_name: form.value.class_teacher_name, class_teacher_phone: form.value.class_teacher_phone,
    assistant_name: form.value.assistant_name, assistant_phone: form.value.assistant_phone,
    assistant_class_name: form.value.assistant_class,
  })
  try {
    const res = await fetch('/api/admin/students', { method: 'POST', headers: authHeaders(), body })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    toast.value = '添加成功'
    setTimeout(() => router.push('/admin'), 1000)
  } catch { toast.value = '保存失败' }
  formSaving.value = false
}

function goBack() { router.push('/admin') }

onMounted(loadClasses)
</script>

<template>
  <div class="sfp">
    <button class="sfp-back" @click="goBack">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
      返回学生管理
    </button>
    <h1 class="sfp-title">新增学生</h1>

    <div v-if="toast" class="sfp-toast" :class="{ ok: toast === '添加成功' }">{{ toast }}</div>

    <div class="sfp-card">
      <div class="sfp-body">
        <div class="sfp-section">
          <div class="sfp-section-title">基本信息</div>
          <div class="sfp-fields">
            <label><span>姓名</span><input v-model="form.name" placeholder="必填" /></label>
            <label><span>学号</span><input v-model="form.student_id" placeholder="必填" /></label>
            <label><span>身份证号</span><input v-model="form.id_number" placeholder="选填" /></label>
            <label class="sfp-combo-label"><span>班级</span>
              <div class="sfp-combo">
                <input v-model="form.class_name" placeholder="必填，输入关键词搜索" autocomplete="off"
                  @focus="filterClassList" @blur="onClassBlur" @input="filterClassList" />
                <div v-if="showClassList && filteredClasses.length" class="sfp-combo-drop">
                  <div v-for="c in filteredClasses" :key="c" class="sfp-combo-opt" @click.prevent="selectClass(c)">{{ c }}</div>
                </div>
              </div>
            </label>
            <label><span>宿舍</span><input v-model="form.dormitory" placeholder="如：12栋315" /></label>
          </div>
        </div>

        <div class="sfp-section">
          <div class="sfp-section-title">辅导员信息</div>
          <div class="sfp-fields">
            <label><span>姓名</span><input v-model="form.advisor_name" /></label>
            <label><span>电话</span><input v-model="form.advisor_phone" /></label>
          </div>
        </div>

        <div class="sfp-section">
          <div class="sfp-section-title">班主任信息</div>
          <div class="sfp-fields">
            <label><span>姓名</span><input v-model="form.class_teacher_name" /></label>
            <label><span>电话</span><input v-model="form.class_teacher_phone" /></label>
          </div>
        </div>

        <div class="sfp-section">
          <div class="sfp-section-title">代班信息</div>
          <div class="sfp-fields">
            <label><span>姓名</span><input v-model="form.assistant_name" /></label>
            <label><span>电话</span><input v-model="form.assistant_phone" /></label>
            <label><span>班级</span><input v-model="form.assistant_class" /></label>
          </div>
        </div>
      </div>

      <div class="sfp-foot">
        <button class="sfp-cancel" @click="goBack">取消</button>
        <button class="sfp-save" :disabled="!form.name || !form.student_id || !form.class_name || formSaving" @click="saveForm">
          {{ formSaving ? '保存中…' : '添加学生' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sfp { max-width: 680px; margin: 0 auto; padding-bottom: 48px }

.sfp-back {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 0; border: none;
  background: none; color: #8b7b65; font-size: .84rem; cursor: pointer;
  font-family: inherit; margin-bottom: 8px; transition: color .2s;
}
.sfp-back:hover { color: #b5343a }
.sfp-title { font-size: 1.4rem; font-weight: 700; color: #2c2c2c; margin: 0 0 24px; letter-spacing: .05em }

.sfp-toast {
  padding: 10px 20px; border-radius: 8px; margin-bottom: 16px;
  font-size: .84rem; background: #fef5f5; color: #b5343a; border: 1px solid #fce4e4;
}
.sfp-toast.ok { background: #eaf7ea; color: #2d6a2d; border-color: #c3e6c3 }

.sfp-card {
  background: #fefcf9; border-radius: 16px; border: 1px solid #f2ebe0;
  padding: 28px 32px 24px;
}
.sfp-body { display: flex; flex-direction: column; gap: 20px }
.sfp-section { display: flex; flex-direction: column; gap: 12px }
.sfp-section-title {
  font-size: .85rem; font-weight: 700; color: #3c3028;
  padding-bottom: 6px; border-bottom: 1px solid #f0e8da;
}
.sfp-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 14px }
.sfp-fields label { display: flex; flex-direction: column; gap: 4px; font-size: .78rem; color: #8b7b65 }
.sfp-fields label span { letter-spacing: .04em }
.sfp-fields input {
  height: 38px; padding: 0 10px; border: 1.5px solid #e5dbcc; border-radius: 8px;
  font-size: .86rem; color: #3c3028; background: #fff; outline: none;
  font-family: inherit; transition: border-color .2s;
}
.sfp-fields input:focus { border-color: #b5343a }

.sfp-combo-label { position: relative }
.sfp-combo { position: relative }
.sfp-combo input { width: 100%; box-sizing: border-box }
.sfp-combo-drop {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 200;
  max-height: 180px; overflow-y: auto;
  background: #fff; border: 1.5px solid #b5343a; border-top: none; border-radius: 0 0 8px 8px;
  box-shadow: 0 6px 20px rgba(0,0,0,.08);
}
.sfp-combo-opt {
  padding: 8px 12px; font-size: .82rem; color: #3c3028; cursor: pointer;
  border-bottom: 1px solid #faf3e8; transition: background .12s;
}
.sfp-combo-opt:last-child { border-bottom: none }
.sfp-combo-opt:hover { background: #fdf3f3; color: #b5343a }

.sfp-foot { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px }
.sfp-cancel {
  height: 40px; padding: 0 24px; border: 1px solid #e5dbcc; border-radius: 10px;
  background: #fff; color: #6b5e4e; font-size: .88rem; cursor: pointer; font-family: inherit;
}
.sfp-save {
  height: 40px; padding: 0 28px; border: none; border-radius: 10px;
  background: #b5343a; color: #fff; font-size: .88rem; font-weight: 600; cursor: pointer; font-family: inherit;
}
.sfp-save:disabled { opacity: .4; cursor: default }

@media (max-width: 480px) {
  .sfp-fields { grid-template-columns: 1fr }
  .sfp-card { padding: 20px 16px }
}
</style>
