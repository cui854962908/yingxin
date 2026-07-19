import { ref } from 'vue'
import { MOBILE_MAX } from './useBreakpoint'
import { optionalAuthFetch } from './useAuthFetch'
import type { ForumPostBrief } from '../types/forum'

// 全局缓存：登录后预加载，切换模块时数据已就绪，消除空白闪烁
interface Announcement { id: string; date: string; title: string; content: string }
interface FaqItem { id: string; question: string; answer: string }

const announcements = ref<Announcement[]>([])
const faqItems = ref<FaqItem[]>([])
const faqTotal = ref(0)
const clubs = ref<any[]>([])
const forumPosts = ref<ForumPostBrief[]>([])
const forumTotal = ref(0)

let preloaded = false
let mobileTabsPrefetched = false

async function loadForumPreview() {
  try {
    const res = await optionalAuthFetch('/api/forum/posts?page=1&page_size=4&sort=latest')
    const data = await res.json()
    if (data.success) {
      forumPosts.value = data.data.items
      forumTotal.value = data.data.total
    }
  } catch { /* 新生说非首屏必需 */ }
}

/** 移动端底栏 Tab：预拉组件 chunk，减少切 Tab 白屏 */
export function prefetchMobileTabChunks() {
  if (mobileTabsPrefetched || window.innerWidth > MOBILE_MAX) return
  mobileTabsPrefetched = true
  void import('../components/ForumPanel.vue')
  void import('../components/IntroLayout.vue')
  void import('../components/IntroSchoolWiki.vue')
  void import('../components/IntroCollegeList.vue')
  void import('../components/ClubList.vue')
}

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

    if (isMobile) {
      prefetchMobileTabChunks()
      setTimeout(loadForumPreview, 200)
      setTimeout(loadClubs, 400)
    } else {
      await loadClubs()
    }
  } catch { preloaded = false }
}

export function usePreload() {
  return {
    announcements,
    faqItems,
    faqTotal,
    clubs,
    forumPosts,
    forumTotal,
    preload,
    prefetchMobileTabChunks,
  }
}
