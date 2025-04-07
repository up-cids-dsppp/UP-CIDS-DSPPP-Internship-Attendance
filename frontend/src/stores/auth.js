import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null)
  const refreshToken = ref(null)
  const errorMessage = ref(null)
  const router = useRouter()

  const intern_login = async (email, password) => {
    try {
      const response = await axios.post('/intern/login', { email, password })
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      errorMessage.value = null
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      router.push('/intern/home') // Redirect to intern home
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Invalid login credentials'
    }
  }

  const admin_login = async (email, password) => {
    try {
      const response = await axios.post('/admin/login', { email, password })
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      errorMessage.value = null
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      router.push('/admin/home') // Redirect to admin home
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Invalid admin credentials'
    }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    delete axios.defaults.headers.common['Authorization']
    router.push('/intern/login') // Redirect to login page
  }

  return {
    accessToken,
    refreshToken,
    errorMessage,
    intern_login,
    admin_login,
    logout,
  }
})
