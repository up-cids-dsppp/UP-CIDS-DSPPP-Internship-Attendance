import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import InternLoginView from '../views/InternLoginView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminHomeView from '@/views/AdminHomeView.vue'
import { useAuthStore } from '../stores/auth'
import InternHomeView from '@/views/InternHomeView.vue'
import AddInternView from '@/views/AddInternView.vue'
import UnauthenticatedView from '@/views/UnauthenticatedView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
    },
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: UnauthenticatedView,
    },
    {
      path: '/intern/login',
      name: 'intern_login',
      component: InternLoginView,
    },
    {
      path: '/intern/home',
      name: 'intern_home',
      component: InternHomeView, // Lazy-loaded
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
    },
    {
      path: '/admin/add_intern',
      name: 'admin_add_intern',
      component: AddInternView,
    },
  ],
})

// Add a global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Check if the user is logged in
  if (authStore.accessToken) {
    // Redirect to the appropriate home page based on user type
    if (to.path === '/' || to.path === '/landing') {
      if (authStore.userType === 'admin') {
        return next('/admin/home')
      } else if (authStore.userType === 'intern') {
        return next('/intern/home')
      }
    }

    // Allow access to admin-only routes for admins
    if (to.path.startsWith('/admin') && to.path !== '/admin/login' && authStore.userType !== 'admin') {
      return next('/unauthorized') // Redirect to unauthorized page
    }

    // Allow access to intern-only routes for interns
    if (to.path.startsWith('/intern') && to.path !== '/intern/login' && authStore.userType !== 'intern') {
      return next('/unauthorized') // Redirect to unauthorized page
    }

    // Allow navigation to the requested route
    return next()
  }

  // Allow unauthenticated users to access login pages
  if (to.path === '/admin/login' || to.path === '/intern/login') {
    return next()
  }

  // Redirect unauthenticated users to the login page
  if (to.path.startsWith('/admin')) {
    return next('/unauthorized')
  }
  if (to.path.startsWith('/intern')) {
    return next('/unauthorized')
  }

  // Allow navigation to public routes
  next()
})

export default router
