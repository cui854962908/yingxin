import { createRouter, createWebHistory } from 'vue-router'
import { shouldMobileBackToHome } from '../composables/useAppNavigate'
import { MOBILE_MAX } from '../composables/useBreakpoint'

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
          path: 'admin',
          children: [
            { path: '', name: 'admin', component: () => import('../components/AdminPanel.vue') },
            { path: 'students/add', name: 'admin-student-add', component: () => import('../components/StudentFormPage.vue') },
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
          props: { category: 'tips', pageTitle: '新生攻略', pageSubtitle: '校园生活实用信息，帮你快速适应大学生活' },
        },
        {
          path: 'clubs',
          children: [
            { path: '', name: 'clubs', component: () => import('../components/ClubList.vue') },
            { path: 'add', name: 'club-add', component: () => import('../components/ClubDetail.vue') },
            { path: ':id', name: 'club-detail', component: () => import('../components/ClubDetail.vue') },
          ],
        },
      ],
    },
    {
      path: '/campus',
      name: 'campus',
      component: () => import('../components/CampusView.vue'),
    },
  ],
})

/** 小信聊天打开时，系统返回优先关聊天（由 XiaoXinAssistant 注册） */
let getChatOpen: () => boolean = () => false
export function registerMobileChatOpen(fn: () => boolean) {
  getChatOpen = fn
}

function isMobileViewport() {
  return window.innerWidth <= MOBILE_MAX
}

// 移动端：非首页模块按系统返回先回首页，在首页再按才退出站点
router.afterEach((to) => {
  if (!isMobileViewport() || !shouldMobileBackToHome(to.path)) return
  history.pushState({ yxMobileBack: true }, '')
})

window.addEventListener('popstate', () => {
  if (!isMobileViewport() || getChatOpen()) return
  const path = router.currentRoute.value.path
  if (!shouldMobileBackToHome(path)) return
  router.replace('/')
})

export default router
