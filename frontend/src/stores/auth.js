import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const userType = ref(localStorage.getItem('userType') || null)
  const userEmail = ref(localStorage.getItem('userEmail') || null)
  const errorMessage = ref(null)
  const router = useRouter()
  let idleTimer = null
  let tokenExpirationTimer = null

  if (accessToken.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  const saveTokens = (access, refresh, type, email) => {
    accessToken.value = access
    refreshToken.value = refresh
    userType.value = type
    userEmail.value = email
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    localStorage.setItem('userType', type)
    localStorage.setItem('userEmail', email)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
    resetIdleTimer() // Reset the idle timer whenever tokens are saved
  }

  const intern_login = async (email, password) => {
    try {
      const response = await axios.post('/intern/login', { email, password })
      saveTokens(response.data.access, response.data.refresh, 'intern', email)
      errorMessage.value = null
      router.push('/intern/home') // Redirect to intern home
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Invalid login credentials'
    }
  }

  const admin_login = async (email, password) => {
    try {
      const response = await axios.post('/admin/login', { email, password })
      saveTokens(response.data.access, response.data.refresh, 'admin', email)
      errorMessage.value = null
      router.push('/admin/home') // Redirect to admin home
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Invalid admin credentials'
    }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    userType.value = null
    userEmail.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userType')
    localStorage.removeItem('userEmail')
    delete axios.defaults.headers.common['Authorization']
    clearTimeout(idleTimer) // Clear the idle timer
    clearTimeout(tokenExpirationTimer) // Clear the token expiration timer
    router.push('/') // Redirect to landing page
  }

  const refreshAccessToken = async () => {
    try {
      const response = await axios.post('/token/refresh/', { refresh: refreshToken.value })
      saveTokens(response.data.access, refreshToken.value, userType.value, userEmail.value)
    } catch (error) {
      logout() // Log the user out if the refresh token is invalid
    }
  }

  const resetIdleTimer = () => {
    clearTimeout(idleTimer) // Clear the existing idle timer
    clearTimeout(tokenExpirationTimer) // Clear the token expiration timer

    // Set a new idle timer for 1 hour
    tokenExpirationTimer = setTimeout(() => {
      logout() // Log the user out if idle for 1 hour
    }, 60 * 60 * 1000) // 1 hour in milliseconds
  }

  const trackUserActivity = () => {
    // Reset the idle timer on user activity
    window.addEventListener('keydown', resetIdleTimer)
    window.addEventListener('click', resetIdleTimer)
  }

  // Start tracking user activity when the store is initialized
  trackUserActivity()

  // Listen for changes in localStorage to synchronize state across tabs
  window.addEventListener('storage', (event) => {
    if (event.key === 'accessToken' || event.key === 'refreshToken' || event.key === 'userType' || event.key === 'userEmail') {
      accessToken.value = localStorage.getItem('accessToken')
      refreshToken.value = localStorage.getItem('refreshToken')
      userType.value = localStorage.getItem('userType')
      userEmail.value = localStorage.getItem('userEmail')

      if (accessToken.value) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      } else {
        delete axios.defaults.headers.common['Authorization']
      }
    }
  })

  return {
    accessToken,
    refreshToken,
    userType,
    userEmail,
    errorMessage,
    intern_login,
    admin_login,
    logout,
    refreshAccessToken,
    saveTokens,
  }
})

axios.interceptors.response.use(
  (response) => response, // Pass through successful responses
  async (error) => {
    const authStore = useAuthStore()

    // Check if the error is due to an expired access token
    if (error.response?.status === 401 && error.response?.data?.code === 'token_not_valid') {
      try {
        // Attempt to refresh the access token
        await authStore.refreshAccessToken()
        // Retry the original request with the new access token
        error.config.headers['Authorization'] = `Bearer ${authStore.accessToken}`
        return axios.request(error.config)
      } catch (refreshError) {
        // If refreshing fails, log the user out and redirect to the landing page
        authStore.logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error) // Pass through other errors
  }
)
