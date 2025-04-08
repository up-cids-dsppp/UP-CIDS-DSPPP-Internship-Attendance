import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue' 
import InternLoginView from '../views/InternLoginView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminHomeView from '@/views/AdminHomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
    },
    {
      path: '/intern/login',
      name: 'intern_login',
      component: InternLoginView,
    },
    {
      path: '/admin/login',
      name: 'admin_login',
      component: AdminLoginView,
    },
    {
      path: '/admin/home',
      name: 'admin_home',
      component: AdminHomeView,
    }
  ],
})

export default router
