<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePreload } from '../composables/usePreload'
import { authHeaders, useAuth } from '../composables/useAuth'
import AppSpinner from './AppSpinner.vue'
import StudentFormModal from './StudentFormModal.vue'

const { adminStudents: cached } = usePreload()
const hasCache = ref(Array.isArray(cached.value) ? cached.value.length > 0 : Object.keys(cached.value).length > 0)
const loading = ref(!hasCache.value)

const router = useRouter()
const { isClubAdmin } = useAuth()

interface Student {
  name: string; student_id: string; id_number?: string; class_name: string; dormitory: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

interface ClassGroup { name: string; students: Student[]; expanded: boolean }

const groups = ref<ClassGroup[]>([])
const searchQ = ref('')
const searchResult = ref<Student[]>([])
const searchNotFound = ref(false)
function getAvailableGrades(): string[] {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth() + 1
  const newest = m >= 6 ? y : y - 1
  const grades: string[] = []
  for (let i = 0; i < 4; i++) {
    const g = newest - i
    if (m >= 9 && g + 4 <= y) continue
    grades.push(`${String(g).slice(-2)}级`)
  }
  return grades
}

const grades = getAvailableGrades()
const activeGrade = ref(grades[0])

const filteredGroups = computed(() => {
  const prefix = activeGrade.value.replace('级', '')
  return groups.value.filter(g => g.name.includes(prefix))
})

// Toast 提示
const toast = ref<{ text: string; type: 'success' | 'error' } | null>(null)
let toastTimer: ReturnType<typeof setTimeout> | null = null
function showToast(text: string, type: 'success' | 'error') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { text, type }
  toastTimer = setTimeout(() => { toast.value = null }, 3000)
}

// 表单弹窗
const showFormModal = ref(false)
const editStudentData = ref<Student | null>(null)

// 删除确认
const deleteTarget = ref<string | null>(null)

async function loadData() {
  if (hasCache.value) {
    // 缓存已预加载，直接用
    const data = cached.value as unknown as Record<string, Student[]>
    groups.value = Object.entries(data).map(([name, students]) => ({ name, students, expanded: false }))
    return
  }
  loading.value = true
  try {
    const res = await fetch('/api/admin/students', { headers: authHeaders() })
    const d = await res.json()
    if (d.success) {
      groups.value = Object.entries(d.data as Record<string, Student[]>).map(([name, students]) => ({
        name, students, expanded: false,
      }))
    }
  } catch { showToast('加载学生数据失败，请检查网络连接', 'error') }
  finally { loading.value = false }
}

async function doSearch() {
  const q = searchQ.value.trim()
  if (!q) { searchResult.value = []; searchNotFound.value = false; return }
  try {
    const res = await fetch(`/api/admin/students/search?q=${encodeURIComponent(q)}`, { headers: authHeaders() })
    const d = await res.json()
    if (d.success && d.data?.length) { searchResult.value = d.data; searchNotFound.value = false }
    else { searchResult.value = []; searchNotFound.value = true }
  } catch { searchResult.value = []; showToast('搜索失败，请稍后重试', 'error') }
}

function toggleGroup(g: ClassGroup) { g.expanded = !g.expanded }

function openAdd() {
  router.push('/admin/students/add')
}

function openEdit(s: Student) {
  editStudentData.value = s
  showFormModal.value = true
}

function onFormSaved() {
  showToast(editStudentData.value ? '学生信息已更新' : '学生已新增', 'success')
  loadData()
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    const res = await fetch(`/api/admin/students/${deleteTarget.value}`, { method: 'DELETE', headers: authHeaders() })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    deleteTarget.value = null
    searchResult.value = []
    showToast('学生已删除', 'success')
    await loadData()
  } catch { showToast('删除失败，请稍后重试', 'error') }
}

onMounted(loadData)
</script>

<template>
  <div class="ap">
    <!-- Toast 提示 -->
    <Transition name="toast">
      <div v-if="toast" :class="['ap-toast', `ap-toast--${toast.type}`]">{{ toast.text }}</div>
    </Transition>
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
      <button v-if="!isClubAdmin" class="ap-btn-add" @click="openAdd">+ 新增学生</button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResult.length" class="ap-search-result">
      <span class="ap-sr-label">搜索到 {{ searchResult.length }} 条结果：</span>
      <table class="ap-table ap-table--search">
        <thead>
          <tr><th>姓名</th><th>学号</th><th>班级</th><th>宿舍</th><th>辅导员</th><th v-if="activeGrade === '25级'">班主任</th><th v-if="!isClubAdmin">操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in searchResult" :key="s.student_id">
            <td>{{ s.name }}</td><td>{{ s.student_id }}</td>
            <td>{{ s.class_name }}</td><td>{{ s.dormitory }}</td>
            <td>{{ s.advisor.name }}</td>
            <td v-if="activeGrade === '25级'">{{ s.class_teacher.name }}</td>
            <td v-if="!isClubAdmin" class="ap-actions">
              <a class="ap-act ap-act--edit" @click="openEdit(s)">编辑</a>
              <a class="ap-act ap-act--del" @click="deleteTarget = s.student_id">删除</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 年级分类 -->
    <div v-if="!searchQ.trim()" class="ap-grades">
      <button
        v-for="g in grades" :key="g"
        class="ap-grade-btn" :class="{ active: activeGrade === g }"
        @click="activeGrade = g"
      >{{ g }}</button>
    </div>

    <!-- 班级折叠列表 -->
    <div v-if="!searchQ.trim()" class="ap-groups">
      <div v-for="g in filteredGroups" :key="g.name" class="ap-group">
        <div class="ap-group-hd" @click="toggleGroup(g)">
          <span class="ap-group-arrow">{{ g.expanded ? '▼' : '▶' }}</span>
          <span class="ap-group-name">{{ g.name }}</span>
          <span class="ap-group-count">（{{ g.students.length }}人）</span>
        </div>
        <div v-if="g.expanded" class="ap-group-bd">
          <table class="ap-table">
            <thead>
              <tr><th>姓名</th><th>学号</th><th>宿舍</th><th>辅导员</th><th v-if="activeGrade === '25级'">班主任</th><th v-if="!isClubAdmin">操作</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in g.students" :key="s.student_id">
                <td>{{ s.name }}</td><td>{{ s.student_id }}</td>
                <td>{{ s.dormitory }}</td><td>{{ s.advisor.name }}</td>
                <td v-if="activeGrade === '25级'">{{ s.class_teacher.name }}</td>
                <td v-if="!isClubAdmin" class="ap-actions">
                  <a class="ap-act ap-act--edit" @click="openEdit(s)">编辑</a>
                  <a class="ap-act ap-act--del" @click="deleteTarget = s.student_id">删除</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-if="loading" class="ap-loading">
        <AppSpinner />
      </div>
      <p v-else-if="filteredGroups.length === 0" class="ap-empty">暂无学生数据</p>
    </div>

    <!-- 弹窗：新增/编辑 -->
    <StudentFormModal
      v-model="showFormModal"
      :student-data="editStudentData"
      @saved="onFormSaved"
      @error="(msg: string) => showToast(msg, 'error')"
    />

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
.ap{display:flex;flex-direction:column;gap:16px;position:relative}

.ap-grades{display:flex;gap:8px;flex-wrap:wrap}
.ap-grade-btn{
  height:30px;padding:0 16px;border:1px solid #e5dbcc;border-radius:16px;
  background:#fefcf9;color:#6b5e4e;font-size:.8rem;cursor:pointer;
  font-family:inherit;transition:all .2s;
}
.ap-grade-btn:hover{border-color:#b5343a;color:#b5343a}
.ap-grade-btn.active{background:#b5343a;color:#fff;border-color:#b5343a}

/* Toast */
.ap-toast {
  position: fixed; top: 20px; right: 20px; z-index: 200;
  padding: 12px 24px; border-radius: 10px;
  font-size: .84rem; font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,.12);
  pointer-events: none;
}
.ap-toast--success { background: #eaf7ea; color: #2d6a2d; border: 1px solid #c3e6c3; }
.ap-toast--error { background: #fef5f5; color: #b5343a; border: 1px solid #fce4e4; }
.toast-enter-active { animation: toastIn .3s cubic-bezier(.16,1,.3,1); }
.toast-leave-active { animation: toastOut .25s ease-in; }
@keyframes toastIn { from { opacity: 0; transform: translateY(-12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes toastOut { to { opacity: 0; transform: translateY(-8px); } }
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
.ap-group-bd{padding:0 8px 8px;overflow-x:auto;-webkit-overflow-scrolling:touch}
.ap-table{min-width:640px}

.ap-table{width:100%;border-collapse:collapse;font-size:.82rem;table-layout:fixed}
.ap-table th{text-align:left;padding:8px 6px;color:#8b7b65;font-weight:500;border-bottom:1.5px solid #f0e8da;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ap-table th:last-child{text-align:right}
.ap-table td{padding:8px 6px;color:#3c3028;border-bottom:1px solid #faf3e8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* 列宽：动态列数，auto layout */
.ap-table tbody tr:hover{background:#fefcfa}

.ap-actions{text-align:right;min-width:80px;white-space:nowrap}
.ap-act{font-size:.78rem;cursor:pointer;padding:2px 8px;border-radius:4px}
.ap-act--edit{color:#8b7b65}.ap-act--edit:hover{color:#b5343a}
.ap-act--del{color:#c4b0a0}.ap-act--del:hover{color:#b5343a;background:#fef5f5}
.ap-empty{text-align:center;color:#b0a090;padding:24px 0;font-size:.84rem}
.ap-loading{display:flex;align-items:center;justify-content:center;padding:40px 0}

.ap-modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.2);z-index:100;display:flex;align-items:center;justify-content:center}
.ap-modal{background:#fff;border-radius:14px;padding:28px 32px 24px;width:540px;max-width:93vw;max-height:85vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,.12)}
.ap-modal--mini{width:400px;padding:32px}
.ap-modal-foot{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.ap-btn-cancel{height:36px;padding:0 20px;border:1px solid #d4c8b0;border-radius:8px;background:#fff;color:#8b7b65;font-size:.84rem;cursor:pointer;font-family:inherit}
.ap-btn-save{height:36px;padding:0 20px;border:none;border-radius:8px;background:#b5343a;color:#fff;font-size:.84rem;font-weight:500;cursor:pointer;font-family:inherit}
.ap-btn-save--danger{background:#b5343a}.ap-btn-save:disabled{opacity:.5}
.ap-confirm-text{font-size:.92rem;color:#3c3028;text-align:center;line-height:1.6}

@media(max-width:768px){
  .ap-toolbar{flex-wrap:wrap;gap:8px}
  .ap-search{flex:1;min-width:0}
  .ap-modal{padding:16px 14px 14px;border-radius:12px;max-height:70vh}
}
@media(max-width:480px){
  .ap-group-hd{padding:10px 12px}
  .ap-group-name{font-size:.78rem}
  .ap-table th,.ap-table td{padding:5px 3px;font-size:.72rem}
  .ap-btn-add{height:34px;font-size:.76rem;padding:0 10px}
  .ap-search-btn{height:34px;font-size:.76rem;padding:0 10px}
  .ap-search-input{height:34px;font-size:.8rem}
  .ap-act{padding:4px 6px;font-size:.74rem}
}
</style>
