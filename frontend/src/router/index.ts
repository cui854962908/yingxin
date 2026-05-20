import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../components/HomePage.vue'),
      children: [
        { path: '', name: 'dashboard' },
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
          name: 'admin',
          component: () => import('../components/AdminPanel.vue'),
        },
      ],
    },
  ],
})

export default router
