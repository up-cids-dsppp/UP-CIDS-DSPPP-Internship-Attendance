import { ref } from 'vue'

export const isTimedIn = ref(false) // Tracks if the intern is timed in
export const tasksForTheDay = ref(0) // Tracks the number of tasks for the day

export const timeIn = () => {
  isTimedIn.value = true
}

export const timeOut = () => {
  isTimedIn.value = false
}

export const setTasksForTheDay = (tasks) => {
  tasksForTheDay.value = tasks
}