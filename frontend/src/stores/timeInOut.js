import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  const authStore = useAuthStore()
  const currentUserEmail = authStore.userEmail // Get the logged-in user's email

  const isTimedIn = ref(false)
  const timedInLogId = ref(null) // Store the ID of the current timed-in task
  const timedOutForTheDay = ref(false)
  const currentLogType = ref(null) // F2F or Async
  const tasksForTheDay = ref(0)
  const internStatus = ref('')
  const attendanceLogs = ref([])
  const mostRecentAttendance = ref(null) // Tracks the most recent attendance log
  const timedInLog = ref(null) // Tracks the timed-in log

  // Actions to update the state
  function setTimedIn(status, logId, logType) {
    isTimedIn.value = status
    timedInLogId.value = logId
    currentLogType.value = logType
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

  function setMostRecentAttendance(attendance) {
    mostRecentAttendance.value = attendance
  }

  function setTimedInLog(log) {
    timedInLog.value = log
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
    currentLogType,
    tasksForTheDay,
    internStatus,
    attendanceLogs,
    mostRecentAttendance,
    timedInLog,
    canTimeInOut,
    setTimedIn,
    setTasksForTheDay,
    setInternStatus,
    setTimedOutForTheDay,
    setMostRecentAttendance,
    setTimedInLog,
  }
}, {
  persist: true, // Enable persistence for this store
})