<script setup lang="ts">
import { ref, onMounted } from 'vue'

function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('token')
  return t ? { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` } : { 'Content-Type': 'application/json' }
}

interface Student {
  name: string; student_id: string; class_name: string; dormitory: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

interface ClassGroup { name: string; students: Student[]; expanded: boolean }

const groups = ref<ClassGroup[]>([])
const searchQ = ref('')
const searchResult = ref<Student | null>(null)
const searchNotFound = ref(false)

// 表单状态
const showForm = ref(false)
const editingId = ref<string | null>(null)
const form = ref({
  name: '', student_id: '', class_name: '', dormitory: '',
  advisor_name: '', advisor_phone: '',
  class_teacher_name: '', class_teacher_phone: '',
  assistant_name: '', assistant_phone: '', assistant_class: '',
})
const formSaving = ref(false)

// 删除确认
const deleteTarget = ref<string | null>(null)

async function loadData() {
  try {
    const res = await fetch('/api/admin/students', { headers: authHeaders() })
    const d = await res.json()
    if (d.success) {
      groups.value = Object.entries(d.data as Record<string, Student[]>).map(([name, students]) => ({
        name, students, expanded: false,
      }))
    }
  } catch { /* */ }
}

async function doSearch() {
  const q = searchQ.value.trim()
  if (!q) { searchResult.value = null; searchNotFound.value = false; return }
  try {
    const res = await fetch(`/api/admin/students/search?q=${encodeURIComponent(q)}`, { headers: authHeaders() })
    const d = await res.json()
    if (d.success) { searchResult.value = d.data; searchNotFound.value = false }
    else { searchResult.value = null; searchNotFound.value = true }
  } catch { searchResult.value = null }
}

function toggleGroup(g: ClassGroup) { g.expanded = !g.expanded }

function openAdd() {
  editingId.value = null
  form.value = {
    name: '', student_id: '', class_name: '', dormitory: '',
    advisor_name: '', advisor_phone: '',
    class_teacher_name: '', class_teacher_phone: '',
    assistant_name: '', assistant_phone: '', assistant_class: '',
  }
  showForm.value = true
}

function openEdit(s: Student) {
  editingId.value = s.student_id
  form.value = {
    name: s.name, student_id: s.student_id, class_name: s.class_name, dormitory: s.dormitory,
    advisor_name: s.advisor.name, advisor_phone: s.advisor.phone,
    class_teacher_name: s.class_teacher.name, class_teacher_phone: s.class_teacher.phone,
    assistant_name: s.assistants[0]?.name || '', assistant_phone: s.assistants[0]?.phone || '', assistant_class: s.assistants[0]?.class_name || '',
  }
  showForm.value = true
}

async function saveForm() {
  formSaving.value = true
  const body = JSON.stringify({
    name: form.value.name,
    student_id: form.value.student_id,
    class_name: form.value.class_name,
    dormitory: form.value.dormitory,
    advisor: { name: form.value.advisor_name, phone: form.value.advisor_phone },
    class_teacher: { name: form.value.class_teacher_name, phone: form.value.class_teacher_phone },
    assistants: [{ name: form.value.assistant_name, phone: form.value.assistant_phone, class_name: form.value.assistant_class }],
  })
  const url = editingId.value
    ? `/api/admin/students/${editingId.value}`
    : '/api/admin/students'
  const method = editingId.value ? 'PUT' : 'POST'
  try {
    await fetch(url, { method, headers: authHeaders(), body })
    showForm.value = false
    await loadData()
  } catch { /* */ }
  formSaving.value = false
}

async function doDelete() {
  if (!deleteTarget.value) return
  await fetch(`/api/admin/students/${deleteTarget.value}`, { method: 'DELETE', headers: authHeaders() })
  deleteTarget.value = null
  searchResult.value = null
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="ap">
    <!-- 搜索栏 -->
    <div class="ap-toolbar">
      <div class="ap-search">
        <input
          v-model="searchQ" type="text" class="ap-search-input"
          placeholder="输入学号精准搜索..."
          @keyup.enter="doSearch"
        />
        <span v-if="searchNotFound" class="ap-search-none">未找到该学生</span>
      </div>
      <button class="ap-search-btn" @click="doSearch">搜索</button>
      <button class="ap-btn-add" @click="openAdd">+ 新增学生</button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResult" class="ap-search-result">
      <span class="ap-sr-label">搜索结果：</span>
      <table class="ap-table">
        <thead>
          <tr><th>姓名</th><th>学号</th><th>班级</th><th>宿舍</th><th>辅导员</th><th>班主任</th><th>代班</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ searchResult.name }}</td><td>{{ searchResult.student_id }}</td>
            <td>{{ searchResult.class_name }}</td><td>{{ searchResult.dormitory }}</td>
            <td>{{ searchResult.advisor.name }}</td>
            <td>{{ searchResult.class_teacher.name }}</td>
            <td>{{ searchResult.assistants.map(a => a.name).join(' / ') }}</td>
            <td class="ap-actions">
              <a class="ap-act ap-act--edit" @click="openEdit(searchResult)">编辑</a>
              <a class="ap-act ap-act--del" @click="deleteTarget = searchResult.student_id">删除</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 班级折叠列表 -->
    <div v-if="!searchResult" class="ap-groups">
      <div v-for="g in groups" :key="g.name" class="ap-group">
        <div class="ap-group-hd" @click="toggleGroup(g)">
          <span class="ap-group-arrow">{{ g.expanded ? '▼' : '▶' }}</span>
          <span class="ap-group-name">{{ g.name }}</span>
          <span class="ap-group-count">（{{ g.students.length }}人）</span>
        </div>
        <div v-if="g.expanded" class="ap-group-bd">
          <table class="ap-table">
            <thead>
              <tr><th>姓名</th><th>学号</th><th>宿舍</th><th>辅导员</th><th>班主任</th><th>代班</th><th>操作</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in g.students" :key="s.student_id">
                <td>{{ s.name }}</td><td>{{ s.student_id }}</td>
                <td>{{ s.dormitory }}</td><td>{{ s.advisor.name }}</td>
                <td>{{ s.class_teacher.name }}</td><td>{{ s.assistants.map(a => a.name).join(' / ') }}</td>
                <td class="ap-actions">
                  <a class="ap-act ap-act--edit" @click="openEdit(s)">编辑</a>
                  <a class="ap-act ap-act--del" @click="deleteTarget = s.student_id">删除</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <p v-if="groups.length === 0" class="ap-empty">暂无学生数据</p>
    </div>

    <!-- 弹窗：新增/编辑 -->
    <div v-if="showForm" class="ap-modal-mask" @click.self="showForm = false">
      <div class="ap-modal">
        <h3 class="ap-modal-title">{{ editingId ? '编辑学生' : '新增学生' }}</h3>
        <div class="ap-modal-body">
          <div class="ap-fields">
            <label><span>姓名</span><input v-model="form.name" /></label>
            <label><span>学号</span><input v-model="form.student_id" :disabled="!!editingId" /></label>
            <label><span>班级</span><input v-model="form.class_name" placeholder="如：物联网工程 2026-6班" /></label>
            <label><span>宿舍</span><input v-model="form.dormitory" placeholder="如：北苑 3号楼 412室" /></label>
          </div>
          <div class="ap-modal-divider">辅导员信息</div>
          <div class="ap-fields">
            <label><span>姓名</span><input v-model="form.advisor_name" /></label>
            <label><span>电话</span><input v-model="form.advisor_phone" /></label>
          </div>
          <div class="ap-modal-divider">班主任信息</div>
          <div class="ap-fields">
            <label><span>姓名</span><input v-model="form.class_teacher_name" /></label>
            <label><span>电话</span><input v-model="form.class_teacher_phone" /></label>
          </div>
          <div class="ap-modal-divider">代班信息</div>
          <div class="ap-fields">
            <label><span>姓名</span><input v-model="form.assistant_name" /></label>
            <label><span>电话</span><input v-model="form.assistant_phone" /></label>
            <label><span>班级</span><input v-model="form.assistant_class" /></label>
          </div>
        </div>
        <div class="ap-modal-foot">
          <button class="ap-btn-cancel" @click="showForm = false">取消</button>
          <button class="ap-btn-save" :disabled="formSaving" @click="saveForm">
            {{ formSaving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="deleteTarget" class="ap-modal-mask" @click.self="deleteTarget = null">
      <div class="ap-modal ap-modal--mini">
        <p class="ap-confirm-text">确认删除学号为 <strong>{{ deleteTarget }}</strong> 的学生？</p>
        <div class="ap-modal-foot">
          <button class="ap-btn-cancel" @click="deleteTarget = null">取消</button>
          <button class="ap-btn-save ap-btn-save--danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ap{display:flex;flex-direction:column;gap:16px}
.ap-toolbar{display:flex;gap:12px;align-items:flex-start}
.ap-search{flex:1;position:relative}
.ap-search-input{width:100%;height:38px;padding:0 14px;border:1.5px solid #e5dbcc;border-radius:8px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.ap-search-input:focus{border-color:#b5343a}
.ap-search-none{position:absolute;left:0;bottom:-18px;font-size:.74rem;color:#b5343a}
.ap-search-btn{height:38px;padding:0 16px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .2s}
.ap-search-btn:hover{opacity:.9}
.ap-btn-add{height:38px;padding:0 18px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;white-space:nowrap;font-family:inherit;transition:opacity .2s}
.ap-btn-add:hover{opacity:.9}
.ap-search-result{margin-top:4px}
.ap-sr-label{font-size:.78rem;color:#8b7b65}

.ap-group{border:1px solid #f0e8da;border-radius:10px;overflow:hidden}
.ap-group-hd{display:flex;align-items:center;gap:8px;padding:12px 16px;background:#fdfaf6;cursor:pointer;user-select:none;transition:background .15s}
.ap-group-hd:hover{background:#faf4ea}
.ap-group-arrow{font-size:.65rem;color:#b0a090;width:14px}
.ap-group-name{font-size:.88rem;color:#3c3028;font-weight:600}
.ap-group-count{font-size:.78rem;color:#b0a090}
.ap-group-bd{padding:0 8px 8px}

.ap-table{width:100%;border-collapse:collapse;font-size:.82rem}
.ap-table th{text-align:left;padding:8px 6px;color:#8b7b65;font-weight:500;border-bottom:1.5px solid #f0e8da;white-space:nowrap}
.ap-table td{padding:8px 6px;color:#3c3028;border-bottom:1px solid #faf3e8;white-space:nowrap}
.ap-table tbody tr:hover{background:#fefcfa}

.ap-actions{text-align:right}
.ap-act{font-size:.78rem;cursor:pointer;padding:2px 8px;border-radius:4px}
.ap-act--edit{color:#8b7b65}.ap-act--edit:hover{color:#b5343a}
.ap-act--del{color:#c4b0a0}.ap-act--del:hover{color:#b5343a;background:#fef5f5}
.ap-empty{text-align:center;color:#b0a090;padding:24px 0;font-size:.84rem}

.ap-modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.2);z-index:100;display:flex;align-items:center;justify-content:center}
.ap-modal{background:#fff;border-radius:14px;padding:28px 32px 24px;width:540px;max-width:93vw;max-height:85vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,.12)}
.ap-modal--mini{width:400px;padding:32px}
.ap-modal-title{font-size:1.1rem;font-weight:600;color:#2c2c2c;margin-bottom:20px}
.ap-modal-body{display:flex;flex-direction:column;gap:12px}
.ap-fields{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.ap-fields label{display:flex;flex-direction:column;gap:4px;font-size:.78rem;color:#8b7b65}
.ap-fields label span{letter-spacing:.04em}
.ap-fields input{height:36px;padding:0 10px;border:1.5px solid #e5dbcc;border-radius:6px;font-size:.84rem;color:#3c3028;background:#fefcf9;outline:none;font-family:inherit;transition:border-color .2s}
.ap-fields input:focus{border-color:#b5343a}
.ap-fields input:disabled{background:#f5f0e8;color:#b0a090}
.ap-modal-divider{font-size:.72rem;color:#b0a090;font-weight:500;letter-spacing:.04em;padding:4px 0;border-bottom:1px solid #f0e8da}
.ap-modal-foot{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.ap-btn-cancel{height:36px;padding:0 20px;border:1px solid #d4c8b0;border-radius:8px;background:#fff;color:#8b7b65;font-size:.84rem;cursor:pointer;font-family:inherit}
.ap-btn-save{height:36px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit}
.ap-btn-save--danger{background:#b5343a}.ap-btn-save:disabled{opacity:.5}
.ap-confirm-text{font-size:.92rem;color:#3c3028;text-align:center;line-height:1.6}
</style>
