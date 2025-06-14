import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export const useTimeInOutStore = defineStore('timeInOut', () => {
  const authStore = useAuthStore()

  const isTimedIn = ref(false)
  const timedInLogId = ref(null) // Store the ID of the current timed-in task
  const timedOutForTheDay = ref(false)
  const currentLogType = ref(null) // F2F or Async
  const tasksForTheDay = ref(0)
  const internStatus = ref('')
  const attendanceLogs = ref([])
  const mostRecentAttendance = ref(null) // Tracks the most recent attendance log
  const timedInLog = ref(null) // Tracks the timed-in log
  const internStartDate = ref(null) // Add this line

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
    // Prevent time in/out if start date is in the future
    if (!internStartDate.value) return false
    if (today < internStartDate.value) return false
    return currentHour >= 8 && currentHour < 19 && !hasSentAttendance
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
    internStartDate, // Add this to the return object
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