<script setup lang="ts">
import { ref } from 'vue'
import ProfileCard from './ProfileCard.vue'
import AdminPanel from './AdminPanel.vue'
import FaqPanel from './FaqPanel.vue'

interface Student {
  name: string; student_id: string; photo: string
  class_name: string; dormitory: string; role: string
  advisor: { name: string; phone: string }
  class_teacher: { name: string; phone: string }
  assistants: { name: string; phone: string; class_name: string }[]
}

const props = defineProps<{ student: Student }>()
const emit = defineEmits<{ logout: [] }>()

const isAdmin = props.student.role === 'admin'
const activeNav = ref('home')
const faqAddOpen = ref(false)

function toggleFaqAdd() { faqAddOpen.value = !faqAddOpen.value }

const navItems = [
  { key: 'home', label: '首页', icon: '🏠' },
  { key: 'notices', label: '校园公告', icon: '📋' },
  { key: 'faq', label: '问题答疑', icon: '💬' },
  ...(isAdmin ? [{ key: 'admin', label: '学生管理', icon: '⚙️' }] : []),
]

const notices = [
  { date: '2026-08-10', text: '新生入学教育安排通知' },
  { date: '2026-08-11', text: '关于 2026 级新生体检的通知' },
  { date: '2026-08-12', text: '关于新生军训服装领取的通知' },
]
</script>

<template>
  <div class="dashboard">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="sb-logo-wrap">
          <img src="/logo-1.png" alt="校徽" class="sb-logo" />
        </div>
        <p class="sb-school">河南牧业经济学院</p>
        <div class="sb-rule" />
        <div class="sb-avatar">{{ props.student.name.charAt(0) }}</div>
        <p class="sb-name">{{ props.student.name }}</p>
        <span class="sb-role" :class="{ 'sb-role--admin': isAdmin }">
          {{ isAdmin ? '管理员' : '2026 级新生' }}
        </span>
      </div>

      <nav class="sb-nav">
        <a v-for="item in navItems" :key="item.key"
          class="sb-nav-item" :class="{ active: activeNav === item.key }"
          @click="activeNav = item.key">
          <span class="sb-nav-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </a>
      </nav>

      <a class="sb-logout" @click="emit('logout')">退出登录</a>
    </aside>

    <!-- 右侧内容 -->
    <main class="main">
      <!-- 名片区（上 3/7） -->
      <section class="profile-section">
        <ProfileCard :student="props.student" />
      </section>

      <!-- 下半区（4/7） -->
      <section class="bottom-section">
        <!-- 首页：空白，预留给后续入口 -->
        <div v-if="activeNav === 'home'" class="section-card section-card--empty" />

        <div v-else-if="activeNav === 'faq'" class="section-card">
          <div class="section-header">
            <h3 class="section-title">常见问题</h3>
            <button v-if="isAdmin" class="section-header-btn" @click="toggleFaqAdd">
              {{ faqAddOpen ? '收起' : '+ 添加问题' }}
            </button>
          </div>
          <FaqPanel :show-add="faqAddOpen" @added="faqAddOpen = false" @cancelled="faqAddOpen = false" />
        </div>

        <div v-else-if="activeNav === 'admin' && isAdmin" class="section-card">
          <h3 class="section-title">学生管理</h3>
          <AdminPanel />
        </div>

        <div v-else class="section-card">
          <h3 class="section-title">校园公告</h3>
          <div v-for="n in notices" :key="n.date" class="notice-item">
            <span class="notice-date">{{ n.date }}&nbsp;</span>
            <span class="notice-text">{{ n.text }}</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 布局 */
.dashboard { display: flex; height: 100vh; background: #f5efe5 }

/* 侧边栏（固定不动） */
.sidebar {
  flex: 0 0 240px; height: 100vh; position: sticky; top: 0;
  background: linear-gradient(170deg, #3d1114 0%, #591a1e 30%, #4a1519 60%, #361012 100%);
  display: flex; flex-direction: column; align-items: center;
  padding: 32px 20px 20px; overflow: hidden;
}
.sidebar::after {
  content: '迎'; position: absolute; font-size: 14rem; font-weight: 900;
  color: rgba(255,255,255,.012); pointer-events: none; line-height: 1;
  top: 50%; left: 50%; transform: translate(-50%,-50%); font-family: 'Noto Serif SC', serif;
}
.sidebar-top { text-align: center; position: relative; z-index: 1; width: 100% }
.sb-logo-wrap {
  width: 56px; height: 56px; border-radius: 50%; padding: 2px; margin: 0 auto;
  background: linear-gradient(135deg, #c9a96e, #e8d5a8, #c9a96e);
}
.sb-logo { width: 100%; height: 100%; border-radius: 50%; object-fit: contain; background: #fff; display: block }
.sb-school { font-size: .75rem; color: rgba(242,230,208,.55); margin-top: 8px; letter-spacing: .03em }
.sb-rule { width: 30px; height: 1px; background: linear-gradient(90deg, transparent, rgba(201,169,110,.3), transparent); margin: 14px auto }
.sb-avatar {
  width: 56px; height: 56px; border-radius: 50%; margin: 0 auto;
  background: linear-gradient(135deg, #c9a96e, #d4b87a); color: #3d1114;
  font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; justify-content: center;
  font-family: 'Noto Serif SC', serif;
}
.sb-name { font-size: 1rem; color: #f2e6d0; font-weight: 600; margin-top: 8px; letter-spacing: .04em }
.sb-role { display: inline-block; margin-top: 4px; font-size: .68rem; padding: 2px 12px; border-radius: 8px; color: #c4a87e; border: 1px solid rgba(201,169,110,.25) }
.sb-role--admin { color: #e8d5a8; border-color: rgba(232,213,168,.4) }

.sb-nav { flex: 1; width: 100%; margin-top: 28px; position: relative; z-index: 1 }
.sb-nav-item {
  display: flex; align-items: center; gap: 10px; padding: 10px 16px;
  border-radius: 8px; font-size: .84rem; color: rgba(242,230,208,.5);
  cursor: pointer; transition: all .2s; margin-bottom: 2px;
}
.sb-nav-item:hover { color: rgba(242,230,208,.8); background: rgba(255,255,255,.04) }
.sb-nav-item.active { color: #f2e6d0; background: rgba(255,255,255,.08); font-weight: 500 }
.sb-nav-icon { font-size: 1rem; width: 22px; text-align: center }
.sb-logout { position: relative; z-index: 1; font-size: .75rem; color: rgba(242,230,208,.3); cursor: pointer; transition: color .2s }
.sb-logout:hover { color: rgba(242,230,208,.6) }

/* 右侧 */
.main { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 24px 32px 32px; gap: 24px }
.profile-section { flex: 0 0 42.8%; min-height: 0 }
.bottom-section { flex: 1; min-height: 0 }

.section-card {
  height: 100%; background: #fff; border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 6px 20px rgba(0,0,0,.05);
  padding: 24px 28px; overflow-y: auto;
}
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px }
.section-title { font-size: 1.05rem; font-weight: 600; color: #2c2c2c; letter-spacing: .06em; margin-bottom: 0 }
.section-header-btn { height: 30px; padding: 0 12px; border: 1px solid #c9a96e; border-radius: 6px; background: #fefcf9; color: #8b7b65; font-size: .76rem; cursor: pointer; font-family: inherit }
.section-header-btn:hover { border-color: #b5343a; color: #b5343a }
.section-card--empty { display: flex; align-items: center; justify-content: center }
.section-card--empty::after { content: '更多功能即将上线…'; font-size: .84rem; color: #c4b8a8 }

.notice-item { display: flex; padding: 12px 0; border-bottom: 1px solid #f2ebe0; font-size: .86rem; align-items: baseline }
.notice-date { color: #b0a090; white-space: nowrap; font-size: .8rem }
.notice-text { color: #3c3028 }

@media (max-width: 720px) {
  .dashboard { flex-direction: column }
  .sidebar { flex: 0 0 auto; flex-direction: row; padding: 14px 16px; align-items: center; gap: 8px }
  .sidebar::after { display: none }
  .sidebar-top { display: flex; align-items: center; gap: 8px; text-align: left }
  .sb-logo-wrap { width: 36px; height: 36px }
  .sb-school, .sb-rule, .sb-nav { display: none }
  .sb-avatar { width: 36px; height: 36px; font-size: 1rem }
  .sb-name { font-size: .85rem; margin-top: 0 }
  .sb-role { font-size: .62rem }
  .sb-logout { font-size: .7rem }
  .main { padding: 16px; gap: 16px }
  .profile-section, .bottom-section { flex: none }
}
</style>
