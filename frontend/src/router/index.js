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
import AdminInternProfileView from '@/views/AdminInternProfileView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import { useTimeInOutStore } from '../stores/timeInOut'
import AdminInternAttendanceView from '@/views/AdminInternAttendanceView.vue'
import F2FTimeOutView from '@/views/F2FTimeOutView.vue'
import AsyncTimeOutView from '@/views/AsyncTimeOutView.vue'

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
      path: '/intern/out/:log_id/f2f',
      name: 'intern_out_f2f',
      component: F2FTimeOutView,
    },
    {
      path: '/intern/out/:log_id/async',
      name: 'intern_out_async',
      component: AsyncTimeOutView,
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
      path: '/admin/interns/:internId/attendance/:logId',
      name: 'admin_intern_attendance',
      component: AdminInternAttendanceView, // Correctly reference the imported component
    },
    {
      path: '/admin/interns/:id/edit',
      name: 'admin_edit_intern',
      component: () => import('@/views/EditInternView.vue'), // Lazy load the component
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not_found',
      component: NotFoundView,
    },
  ],
})

// Add a global navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const timeInOutStore = useTimeInOutStore()

  console.log(timeInOutStore.isTimedIn, timeInOutStore.timedOutForTheDay, timeInOutStore.tasksForTheDay, timeInOutStore.currentLogType)


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

    if (timeInOutStore.timedOutForTheDay && (to.name === 'intern_in' || to.name === 'intern_out_f2f' || to.name === 'intern_out_async')) {
      console.error('Intern has already timed out for the day')
      return next('/unauthorized') // Redirect to unauthorized page
    }

    // Restrict access to /intern/in
    if (to.name === 'intern_in') {
      if (timeInOutStore.isTimedIn) {
        console.error('Intern is already timed in')
        return next('/unauthorized') // Redirect to unauthorized page
      }
    }

    // Restrict access to /intern/out/:log_id
    if (to.name === 'intern_out_f2f' || to.name === 'intern_out_async') {
      if (!timeInOutStore.isTimedIn) {
        console.error('Intern is not timed in')
        return next('/unauthorized') // Redirect to unauthorized page
      }

      // Ensure the log ID matches the currently timed-in task
      if (String(to.params.log_id) !== String(timeInOutStore.timedInLogId)) {
        console.log('Route log_id:', to.params.log_id, 'Store log_id:', timeInOutStore.timedInLogId)
        console.error('Log ID does not match the current timed-in task')
        return next('/unauthorized') // Redirect to unauthorized page
      }

      // Restrict access based on task type
      if (to.name === 'intern_out_f2f' && timeInOutStore.currentLogType !== 'f2f') {
        console.error('Task type does not match the current timed-in task')
        return next('/unauthorized') // Redirect to unauthorized page
      }
      if (to.name === 'intern_out_async' && timeInOutStore.currentLogType !== 'async') {
        console.error('Task type does not match the current timed-in task')
        return next('/unauthorized') // Redirect to unauthorized page
      }
    }

    return next() // Allow access to other routes
  }

  // Allow unauthenticated users to access login pages
  if (to.path === '/admin/login' || to.path === '/intern/login') {
    return next()
  }

  // Redirect unauthenticated users to the unauthorized page
  if (to.path.startsWith('/admin') || to.path.startsWith('/intern')) {
    return next('/unauthorized')
  }

  // Allow navigation to public routes
  next()
})

export default router
