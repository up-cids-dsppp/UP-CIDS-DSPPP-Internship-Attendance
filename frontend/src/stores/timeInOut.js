import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  // Load initial state from localStorage
  const isTimedIn = ref(JSON.parse(localStorage.getItem('isTimedIn')) || false) // Tracks if the intern is timed in
  const tasksForTheDay = ref(JSON.parse(localStorage.getItem('tasksForTheDay')) || 0) // Tracks the number of tasks for the day

  // Actions to update the state
  function setTimedIn(status) {
    isTimedIn.value = status
  }

  function setTasksForTheDay(count) {
    tasksForTheDay.value = count
  }

  // Persist state to localStorage whenever it changes
  watch(isTimedIn, (newValue) => {
    localStorage.setItem('isTimedIn', JSON.stringify(newValue))
  })

  watch(tasksForTheDay, (newValue) => {
    localStorage.setItem('tasksForTheDay', JSON.stringify(newValue))
  })

  return {
    isTimedIn,
    tasksForTheDay,
    setTimedIn,
    setTasksForTheDay,
  }
})