import { createRouter, createWebHistory } from 'vue-router'
import { shouldMobileBackToHome } from '../composables/useAppNavigate'
import { MOBILE_MAX } from '../composables/useBreakpoint'
import { getAccessToken } from '../composables/useAuthFetch'

function getStoredRole(): string | null {
  try {
    const raw = localStorage.getItem('student')
    if (!raw) return null
    return JSON.parse(raw).role ?? null
  } catch {
    return null
  }
}

function isClubManager(): boolean {
  const role = getStoredRole()
  return role === 'admin' || role === 'club_admin'
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../components/HomePage.vue'),
      children: [
        { path: '', name: 'dashboard', component: () => import('../components/HomePanel.vue') },
        {
          path: 'account/password',
          name: 'account-password',
          component: () => import('../components/ChangePasswordPage.vue'),
        },
        {
          path: 'announcements',
          children: [
            { path: '', name: 'announcements', component: () => import('../components/AnnouncementPanel.vue') },
            { path: 'add', name: 'announcements-add', component: () => import('../components/AnnAddForm.vue') },
          ],
        },
        {
          path: 'faq',
          children: [
            { path: '', name: 'faq', component: () => import('../components/FaqPanel.vue') },
            { path: 'add', name: 'faq-add', component: () => import('../components/FaqAddForm.vue') },
          ],
        },
        {
          path: 'guide',
          name: 'guide',
          component: () => import('../components/RegistrationGuide.vue'),
          props: { category: 'guide', pageTitle: '报到须知', pageSubtitle: '请仔细阅读以下内容，提前准备所需材料，按流程完成报到' },
        },
        {
          path: 'tips',
          name: 'tips',
          component: () => import('../components/RegistrationGuide.vue'),
          props: { category: 'tips', pageTitle: '新生攻略', pageSubtitle: '在校常用 App 图标，建议提前下载熟悉' },
        },
        {
          path: 'wall',
          children: [
            { path: '', name: 'wall', component: () => import('../components/ForumPanel.vue') },
            { path: 'new', name: 'wall-new', component: () => import('../components/ForumCompose.vue') },
            { path: ':id', name: 'wall-detail', component: () => import('../components/ForumDetail.vue') },
          ],
        },
        {
          path: 'intro',
          component: () => import('../components/IntroLayout.vue'),
          children: [
            { path: '', redirect: '/intro/wiki' },
            {
              path: 'wiki',
              name: 'intro-wiki',
              component: () => import('../components/IntroSchoolWiki.vue'),
            },
            {
              path: 'colleges',
              name: 'intro-colleges',
              component: () => import('../components/IntroCollegeList.vue'),
            },
            {
              path: 'clubs',
              name: 'intro-clubs',
              component: () => import('../components/ClubList.vue'),
              props: { hideHeader: true },
            },
            {
              path: 'campus/:campusId',
              name: 'intro-campus-detail',
              component: () => import('../components/IntroCampusDetail.vue'),
              props: true,
            },
            {
              path: ':id',
              name: 'intro-college-detail',
              component: () => import('../components/IntroCollegeDetail.vue'),
              props: true,
            },
          ],
        },
        { path: 'intro/sie/overview', redirect: '/intro/sie' },
        { path: 'intro/sie/clubs', redirect: '/intro/clubs' },
        { path: 'intro/sie/faculty', redirect: '/intro/sie' },
        {
          path: 'clubs',
          children: [
            { path: '', redirect: '/intro/clubs' },
            { path: 'add', name: 'club-add', component: () => import('../components/ClubDetail.vue') },
            { path: ':id', name: 'club-detail', component: () => import('../components/ClubDetail.vue') },
          ],
        },
      ],
    },
    {
      path: '/campus',
      name: 'campus',
      component: () => import('../components/CampusModeSelect.vue'),
    },
    {
      path: '/campus/2d',
      name: 'campus-2d',
      component: () => import('../components/CampusMap2D.vue'),
    },
    {
      path: '/campus/3d',
      name: 'campus-3d',
      component: () => import('../components/CampusView.vue'),
    },
  ],
})

function hasToken(): boolean {
  return !!(getAccessToken() || localStorage.getItem('token'))
}

router.beforeEach((to) => {
  const path = to.path
  const role = getStoredRole()

  if ((path === '/faq/add' || path === '/announcements/add') && role !== 'admin') {
    return path === '/faq/add' ? '/faq' : '/announcements'
  }
  if (path === '/clubs/add' && !isClubManager()) {
    return '/clubs'
  }
  if (path === '/wall/new' && !hasToken()) {
    return '/wall'
  }
  if (path === '/account/password' && !hasToken()) {
    return '/'
  }
})

/** 小信聊天打开时，系统返回优先关聊天（由 XiaoXinAssistant 注册） */
let getChatOpen: () => boolean = () => false
export function registerMobileChatOpen(fn: () => boolean) {
  getChatOpen = fn
}

function isMobileViewport() {
  return window.innerWidth <= MOBILE_MAX
}

/** 勿在 afterEach 里 pushState — 会冲掉 Vue Router 的 history.state，移动端无法再 router.push */

/** 记录最近一次导航的来源路径，用于 popstate 判断用户是否从子页面返回 */
let lastRoutePath = '/'
router.afterEach((_to, from) => {
  lastRoutePath = from.path
})

window.addEventListener('popstate', () => {
  if (!isMobileViewport() || getChatOpen()) return
  queueMicrotask(() => {
    if (getChatOpen()) return
    const path = router.currentRoute.value.path
    if (path === '/') return
    // 从子页面（如 /wall/123）返回其父级时，走正常浏览器后退，不拦截
    if (!shouldMobileBackToHome(lastRoutePath)) return
    if (shouldMobileBackToHome(path)) {
      router.replace('/')
    }
  })
})

export default router
