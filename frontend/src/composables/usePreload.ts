import { ref } from 'vue'
import { authHeaders } from './useAuth'
import { MOBILE_MAX } from './useBreakpoint'

// 全局缓存：登录后预加载，切换模块时数据已就绪，消除空白闪烁
interface Announcement { id: string; date: string; title: string; content: string }
interface FaqItem { id: string; question: string; answer: string }

const announcements = ref<Announcement[]>([])
const faqItems = ref<FaqItem[]>([])
const faqTotal = ref(0)
const clubs = ref<any[]>([])
const adminStudents = ref<any[]>([])

let preloaded = false

async function preload() {
  if (preloaded) return
  preloaded = true
  try {
    const isMobile = window.innerWidth <= MOBILE_MAX
    const [aRes, fRes] = await Promise.all([
      fetch('/api/announcements'),
      fetch('/api/faq?page=1&page_size=10'),
    ])
    const [aData, fData] = await Promise.all([aRes.json(), fRes.json()])
    if (aData.success) announcements.value = aData.data
    if (fData.success) {
      faqItems.value = fData.data.items
      faqTotal.value = fData.data.total
    }

    const loadClubs = async () => {
      try {
        const cRes = await fetch('/api/clubs')
        const cData = await cRes.json()
        if (cData.success) clubs.value = cData.data
      } catch { /* 社团列表非首屏必需 */ }
    }
    if (isMobile) setTimeout(loadClubs, 400)
    else await loadClubs()

    // 管理员/班助预加载学生数据
    const student = JSON.parse(localStorage.getItem('student') || '{}')
    if (student.role === 'admin' || student.role === 'assistant') {
      try {
        const sRes = await fetch('/api/admin/students', { headers: authHeaders() })
        const sData = await sRes.json()
        if (sData.success) adminStudents.value = sData.data
      } catch { /* 非管理员静默失败 */ }
    }
  } catch { preloaded = false }
}

export function usePreload() {
  return { announcements, faqItems, faqTotal, clubs, adminStudents, preload }
}
