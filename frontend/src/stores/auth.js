import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const userType = ref(localStorage.getItem('userType') || null) // Track the user type (admin or intern)
  const errorMessage = ref(null)
  const router = useRouter()

  if (accessToken.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  // Save tokens and user type to localStorage after login
  const saveTokens = (access, refresh, type) => {
    accessToken.value = access
    refreshToken.value = refresh
    userType.value = type
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
    localStorage.setItem('userType', type)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
  }

  const intern_login = async (email, password) => {
    try {
      const response = await axios.post('/intern/login', { email, password })
      saveTokens(response.data.access, response.data.refresh, 'intern')
      errorMessage.value = null
      router.push('/intern/home') // Redirect to intern home
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Invalid login credentials'
    }
  }

  const admin_login = async (email, password) => {
    try {
      const response = await axios.post('/admin/login', { email, password })
      saveTokens(response.data.access, response.data.refresh, 'admin')
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
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userType')
    delete axios.defaults.headers.common['Authorization']
    router.push('/') // Redirect to landing page
  }

  const refreshAccessToken = async () => {
    try {
      const response = await axios.post('/token/refresh/', { refresh: refreshToken.value })
      saveTokens(response.data.access, refreshToken.value, userType.value)
    } catch (error) {
      logout() // Log the user out if the refresh token is invalid
    }
  }

  return {
    accessToken,
    refreshToken,
    userType,
    errorMessage,
    intern_login,
    admin_login,
    logout,
    refreshAccessToken,
  }
})
