<script setup lang="ts">
import { ref, watch } from 'vue'
import { authHeaders } from '../composables/useAuth'

interface StudentData {
  name: string; student_id: string; id_number?: string; class_name: string; dormitory: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const props = defineProps<{
  modelValue: boolean
  studentData?: StudentData | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'saved': []
  'error': [message: string]
}>()

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

const editingId = ref<string | null>(null)
const form = ref({
  name: '', student_id: '', id_number: '', class_name: '', dormitory: '',
  advisor_name: '', advisor_phone: '',
  class_teacher_name: '', class_teacher_phone: '',
  assistant_name: '', assistant_phone: '', assistant_class: '',
})
const formSaving = ref(false)

// 打开时填充表单
watch(() => props.modelValue, (open) => {
  if (!open) return
  loadClasses()
  const s = props.studentData
  if (s) {
    editingId.value = s.student_id
    form.value = {
      name: s.name, student_id: s.student_id, id_number: s.id_number || '', class_name: s.class_name, dormitory: s.dormitory,
      advisor_name: s.advisor.name, advisor_phone: s.advisor.phone,
      class_teacher_name: s.class_teacher.name, class_teacher_phone: s.class_teacher.phone,
      assistant_name: s.assistants[0]?.name || '', assistant_phone: s.assistants[0]?.phone || '', assistant_class: s.assistants[0]?.class_name || '',
    }
  } else {
    editingId.value = null
    form.value = {
      name: '', student_id: '', id_number: '', class_name: '', dormitory: '',
      advisor_name: '', advisor_phone: '',
      class_teacher_name: '', class_teacher_phone: '',
      assistant_name: '', assistant_phone: '', assistant_class: '',
    }
  }
})

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
  const url = editingId.value
    ? `/api/admin/students/${editingId.value}`
    : '/api/admin/students'
  const method = editingId.value ? 'PUT' : 'POST'
  try {
    const res = await fetch(url, { method, headers: authHeaders(), body })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    close()
    emit('saved')
  } catch { emit('error', '保存失败，请检查网络连接') }
  formSaving.value = false
}

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <div v-if="modelValue" class="sfm-mask" @click.self="close">
    <div class="sfm-modal">
      <h3 class="sfm-title">{{ editingId ? '编辑学生' : '新增学生' }}</h3>
      <div class="sfm-body">
        <div class="sfm-fields">
          <label><span>姓名</span><input v-model="form.name" /></label>
          <label><span>学号</span><input v-model="form.student_id" :disabled="!!editingId" /></label>
          <label><span>身份证号</span><input v-model="form.id_number" /></label>
          <label class="sfm-combo-label"><span>班级</span>
            <div class="sfm-combo">
              <input v-model="form.class_name" placeholder="如：物联网工程 2026-6班" autocomplete="off"
                @focus="filterClassList" @blur="onClassBlur" @input="filterClassList" />
              <div v-if="showClassList && filteredClasses.length" class="sfm-combo-drop">
                <div v-for="c in filteredClasses" :key="c" class="sfm-combo-opt" @click.prevent="selectClass(c)">{{ c }}</div>
              </div>
            </div>
          </label>
          <label><span>宿舍</span><input v-model="form.dormitory" placeholder="如：北苑 3号楼 412室" /></label>
        </div>
        <div class="sfm-divider">辅导员信息</div>
        <div class="sfm-fields">
          <label><span>姓名</span><input v-model="form.advisor_name" /></label>
          <label><span>电话</span><input v-model="form.advisor_phone" /></label>
        </div>
        <div class="sfm-divider">班主任信息</div>
        <div class="sfm-fields">
          <label><span>姓名</span><input v-model="form.class_teacher_name" /></label>
          <label><span>电话</span><input v-model="form.class_teacher_phone" /></label>
        </div>
        <div class="sfm-divider">代班信息</div>
        <div class="sfm-fields">
          <label><span>姓名</span><input v-model="form.assistant_name" /></label>
          <label><span>电话</span><input v-model="form.assistant_phone" /></label>
          <label><span>班级</span><input v-model="form.assistant_class" /></label>
        </div>
      </div>
      <div class="sfm-foot">
        <button class="sfm-cancel" @click="close">取消</button>
        <button class="sfm-save" :disabled="formSaving" @click="saveForm">
          {{ formSaving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sfm-mask{position:fixed;inset:0;background:rgba(0,0,0,.2);z-index:100;display:flex;align-items:center;justify-content:center}
.sfm-modal{background:#fff;border-radius:14px;padding:28px 36px 24px;width:620px;max-width:95vw;max-height:85vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,.12)}
.sfm-title{font-size:1.1rem;font-weight:600;color:#2c2c2c;margin-bottom:20px}
.sfm-body{display:flex;flex-direction:column;gap:14px}
.sfm-fields{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.sfm-fields label{display:flex;flex-direction:column;gap:4px;font-size:.78rem;color:#8b7b65}
.sfm-fields label span{letter-spacing:.04em}
.sfm-fields input{height:36px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.sfm-fields input:focus{border-color:#b5343a}
.sfm-fields input:disabled{background:#f5f0e8;color:#b0a090}

/* 班级下拉面板 */
.sfm-combo-label{position:relative}
.sfm-combo{position:relative}
.sfm-combo input{width:100%;box-sizing:border-box}
.sfm-combo-drop{
  position:absolute;top:100%;left:0;right:0;z-index:200;
  max-height:180px;overflow-y:auto;
  background:#fff;border:1.5px solid #b5343a;border-top:none;border-radius:0 0 8px 8px;
  box-shadow:0 6px 20px rgba(0,0,0,.08);
}
.sfm-combo-opt{
  padding:8px 12px;font-size:.82rem;color:#3c3028;cursor:pointer;
  border-bottom:1px solid #faf3e8;transition:background .12s;
}
.sfm-combo-opt:last-child{border-bottom:none}
.sfm-combo-opt:hover{background:#fdf3f3;color:#b5343a}

.sfm-divider{font-size:.72rem;color:#b0a090;font-weight:500;letter-spacing:.04em;padding:4px 0;border-bottom:1px solid #f0e8da}
.sfm-foot{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.sfm-cancel{height:36px;padding:0 20px;border:1px solid #d4c8b0;border-radius:8px;background:#fff;color:#8b7b65;font-size:.84rem;cursor:pointer;font-family:inherit}
.sfm-save{height:36px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit}
.sfm-save:disabled{opacity:.5}

@media(max-width:768px){
  .sfm-fields{grid-template-columns:1fr}
  .sfm-modal{padding:16px 14px 14px;border-radius:12px;max-height:70vh}
  .sfm-cancel,.sfm-save{min-height:44px;height:44px}
}
</style>
