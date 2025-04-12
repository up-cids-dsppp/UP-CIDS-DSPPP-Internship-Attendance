import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useAuthStore } from './auth'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  const authStore = useAuthStore()
  const currentUserEmail = authStore.userEmail // Get the logged-in user's email

  // Helper function to get the key for localStorage
  const getStorageKey = (key) => `${currentUserEmail}_${key}`

  // Load initial state from localStorage
  const isTimedIn = ref(JSON.parse(localStorage.getItem(getStorageKey('isTimedIn'))) || false)
  const tasksForTheDay = ref(JSON.parse(localStorage.getItem(getStorageKey('tasksForTheDay'))) || 0)

  // Actions to update the state
  function setTimedIn(status) {
    isTimedIn.value = status
  }

  function setTasksForTheDay(count) {
    tasksForTheDay.value = count
  }

  // Persist state to localStorage whenever it changes
  watch(isTimedIn, (newValue) => {
    localStorage.setItem(getStorageKey('isTimedIn'), JSON.stringify(newValue))
  })

  watch(tasksForTheDay, (newValue) => {
    localStorage.setItem(getStorageKey('tasksForTheDay'), JSON.stringify(newValue))
  })

  return {
    isTimedIn,
    tasksForTheDay,
    setTimedIn,
    setTasksForTheDay,
  }
})