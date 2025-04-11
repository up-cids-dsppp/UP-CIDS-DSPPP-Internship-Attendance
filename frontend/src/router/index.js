import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import InternLoginView from '../views/InternLoginView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminHomeView from '@/views/AdminHomeView.vue'
import { useAuthStore } from '../stores/auth'
import InternHomeView from '@/views/InternHomeView.vue'
import AddInternView from '@/views/AddInternView.vue'
import UnauthenticatedView from '@/views/UnauthenticatedView.vue'
import InternAttendanceView from '@/views/InternAttendanceView.vue'
import TimeInView from '@/views/TimeInView.vue'
import TimeOutView from '@/views/TimeOutView.vue'
import AdminInternProfileView from '@/views/AdminInternProfileView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import { useTimeInOutStore } from '../stores/timeInOut'
import AdminInternAttendanceView from '@/views/AdminInternAttendanceView.vue'

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
      component: InternHomeView,
    },
    {
      path: '/intern/attendance/:id',
      name: 'attendance_log',
      component: InternAttendanceView,
    },
    {
      path: '/intern/in',
      name: 'intern_in',
      component: TimeInView,
    },
    {
      path: '/intern/out/:log_id',
      name: 'intern_out',
      component: TimeOutView,
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
    {
      path: '/admin/interns/:id',
      name: 'admin_intern_profile',
      component: AdminInternProfileView, // Correctly reference the imported component
    },
    {
      path: '/admin/interns/attendance/:id',
      name: 'admin_intern_attendance',
      component: AdminInternAttendanceView, // Correctly reference the imported component
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not_found',
      component: NotFoundView,
    },
  ],
})

// Add a global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const timeInOutStore = useTimeInOutStore() // Access the Pinia store

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

    // Restrict access to /intern/in and /intern/out based on isTimedIn state
    if (to.path === '/intern/in' && timeInOutStore.isTimedIn) {
      return next('/intern/home') // Redirect to intern home if already timed in
    }
    if (to.path === '/intern/out' && !timeInOutStore.isTimedIn) {
      return next('/intern/home') // Redirect to intern home if not timed in
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
