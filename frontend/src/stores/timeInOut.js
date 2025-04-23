import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  const authStore = useAuthStore()
  const currentUserEmail = authStore.userEmail // Get the logged-in user's email

  const isTimedIn = ref(false)
  const timedInLogId = ref(null) // Store the ID of the current timed-in task
  const timedOutForTheDay = ref(false)
  const currentTaskType = ref(null) // F2F or Async
  const tasksForTheDay = ref(0)
  const internStatus = ref('')
  const attendanceLogs = ref([])

  // Actions to update the state
  function setTimedIn(status, logId, taskType) {
    isTimedIn.value = status
    timedInLogId.value = logId
    currentTaskType.value = taskType
  }

  function setTasksForTheDay(count) {
    tasksForTheDay.value = count
  }

  const setInternStatus = (status) => {
    internStatus.value = status
    console.log('Intern status set to:', status)
  }

  function setTimedOutForTheDay(status) {
    timedOutForTheDay.value = status
  }

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
    timedInLogId,
    timedOutForTheDay,
    currentTaskType,
    tasksForTheDay,
    internStatus,
    attendanceLogs,
    canTimeInOut,
    setTimedIn,
    setTasksForTheDay,
    setInternStatus,
    setTimedOutForTheDay,
  }
}, {
  persist: true, // Enable persistence for this store
})