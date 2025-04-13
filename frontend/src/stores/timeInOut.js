import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue' // Add 'watch' here
import { useAuthStore } from './auth'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  const authStore = useAuthStore()
  const currentUserEmail = authStore.userEmail // Get the logged-in user's email

  // Helper function to get the key for localStorage
  const getStorageKey = (key) => `${currentUserEmail}_${key}`

  // Load initial state from localStorage
  const isTimedIn = ref(JSON.parse(localStorage.getItem(getStorageKey('isTimedIn'))) || false)
  const tasksForTheDay = ref(JSON.parse(localStorage.getItem(getStorageKey('tasksForTheDay'))) || 0)
  const internStatus = ref(localStorage.getItem(getStorageKey('internStatus')) || '') // Load from localStorage
  const attendanceLogs = ref([])

  // Actions to update the state
  function setTimedIn(status) {
    isTimedIn.value = status
  }

  function setTasksForTheDay(count) {
    tasksForTheDay.value = count
  }

  const setInternStatus = (status) => {
    internStatus.value = status
    localStorage.setItem(getStorageKey('internStatus'), status) // Persist to localStorage
    console.log('Intern status set to:', status)
  }

  // Persist state to localStorage whenever it changes
  watch(isTimedIn, (newValue) => {
    localStorage.setItem(getStorageKey('isTimedIn'), JSON.stringify(newValue))
  })

  watch(tasksForTheDay, (newValue) => {
    localStorage.setItem(getStorageKey('tasksForTheDay'), JSON.stringify(newValue))
  })

  const canTimeInOut = computed(() => {
    const now = new Date()
    const currentHour = now.getHours()
    const today = new Date().toISOString().split('T')[0]
    const hasSentAttendance = attendanceLogs.value.some(
      (log) => log.date === today && log.status === 'sent'
    )
    return currentHour >= 8 && currentHour < 17 && !hasSentAttendance
  })

  return {
    isTimedIn,
    tasksForTheDay,
    internStatus,
    attendanceLogs,
    canTimeInOut,
    setTimedIn,
    setTasksForTheDay,
    setInternStatus,
  }
})