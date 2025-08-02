import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/duenios',
      name: 'duenios',
      component: () => import('@/views/DueniosView.vue')
    },
    {
      path: '/turnos',
      name: 'turnos', 
      component: () => import('@/views/TurnosView.vue')
    },
    {
      path: '/calendario',
      name: 'calendario',
      component: () => import('@/views/CalendarioView.vue')
    }
  ]
})

export default router