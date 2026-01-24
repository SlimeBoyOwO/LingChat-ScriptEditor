import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/editor/:scriptId',
      name: 'editor',
      component: () => import('../views/EditorView.vue')
    }
  ],
})

export default router
