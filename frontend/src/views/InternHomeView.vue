<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { useTimeInOutStore } from '../stores/timeInOut'

const router = useRouter()
const timeInOutStore = useTimeInOutStore() // Use the Pinia store

// Intern details
const internDetails = ref({
  email: '',
  full_name: '',
  start_date: '',
  time_to_render: 0,
  time_rendered: 0,
  status: '',
})

// Attendance logs
const attendanceLogs = ref([]) // Array to store attendance logs
const mostRecentAttendance = ref(null) // Tracks the most recent attendance log

// Date and time
const currentDate = ref(new Date().toLocaleDateString())
const currentTime = ref(new Date().toLocaleTimeString())

// Update the clock every second
const updateClock = () => {
  currentTime.value = new Date().toLocaleTimeString()
}
setInterval(updateClock, 1000)

// Fetch intern details and attendance logs on component mount
onMounted(async () => {
  try {
    // Fetch intern profile with logs
    const profileResponse = await axios.get('/intern/profile') // Fetch from the combined endpoint
    const data = profileResponse.data

    // Set intern details
    internDetails.value = {
      email: data.email,
      full_name: data.full_name,
      start_date: data.start_date,
      time_to_render: data.time_to_render,
      time_rendered: data.time_rendered,
      status: data.status,
    }

    // Set attendance logs
    attendanceLogs.value = data.attendance_logs

    // Determine the most recent attendance
    if (attendanceLogs.value.length > 0) {
      mostRecentAttendance.value = attendanceLogs.value[0] // Most recent log is the first in the list

      // Update the store with the correct values
      timeInOutStore.setTimedIn(mostRecentAttendance.value.status === 'ongoing')

      // Compute tasks for the day from the tasks array
      const tasks = mostRecentAttendance.value.tasks || []
      timeInOutStore.setTasksForTheDay(Array.isArray(tasks) ? tasks.length : 0)
    } else {
      // Reset the store if no attendance logs are found
      timeInOutStore.setTimedIn(false)
      timeInOutStore.setTasksForTheDay(0)
    }
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Handle "Time In" button click
const handleTimeIn = async () => {
  router.push('/intern/in') // Redirect to the time-in page
}

// Redirect to the time-out page with the ongoing attendance log ID
const handleTimeOut = () => {
  const ongoingLogId = mostRecentAttendance.value.id // Get the ongoing attendance log ID
  router.push(`/intern/out/${ongoingLogId}`)
}

// Handle "View" link click
const viewAttendanceLog = (logId) => {
  router.push(`/intern/attendance/${logId}`) // Redirect to the attendance log details page
}
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="intern" :userEmail="internDetails.email" />

    <!-- Intern Content -->
    <div class="mt-8 px-6">
      <h2 class="text-xl font-bold">Welcome, {{ internDetails.full_name }}!</h2>
      <p class="mt-2"><strong>Email:</strong> {{ internDetails.email }}</p>
      <p class="mt-2"><strong>Start Date:</strong> {{ internDetails.start_date }}</p>
      <p class="mt-2"><strong>Time to be Rendered:</strong> {{ internDetails.time_to_render.toFixed(2) }} hours</p>
      <p class="mt-2"><strong>Time Rendered:</strong> {{ internDetails.time_rendered.toFixed(2) }} hours</p>
      <p class="mt-2"><strong>Status:</strong> {{ internDetails.status }}</p>

      <!-- Time In/Out Section -->
      <div
        :class="[
          'text-white p-4 mt-4 rounded-lg max-w-md',
          timeInOutStore.isTimedIn ? 'bg-red-500' : 'bg-green-500'
        ]"
      >
        <p class="text-lg font-semibold">Today's Date: {{ currentDate }}</p>
        <p class="text-lg font-semibold">Current Time: {{ currentTime }}</p>
        <p v-if="timeInOutStore.isTimedIn" class="text-lg font-semibold mt-2">
          Tasks to accomplish: {{ timeInOutStore.tasksForTheDay }}
        </p>
        <div class="flex justify-end mt-4">
          <button
            v-if="!timeInOutStore.isTimedIn"
            @click="handleTimeIn"
            class="bg-white text-green-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
          >
            Time In
          </button>
          <button
            v-else
            @click="handleTimeOut"
            class="bg-white text-red-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
          >
            Time Out
          </button>
        </div>
      </div>

      <!-- Attendance Logs Section -->
      <h2 class="text-xl font-bold mt-8">Attendance Logs</h2>
      <div v-if="attendanceLogs.length === 0" class="text-gray-500 mt-4 text-center">
        No attendance logs reported.
      </div>
      <table v-else class="table-auto w-full mt-4 border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-200">
            <th class="border border-gray-300 px-4 py-2">Date</th>
            <th class="border border-gray-300 px-4 py-2">Type</th>
            <th class="border border-gray-300 px-4 py-2">Time In</th>
            <th class="border border-gray-300 px-4 py-2">Time Out</th>
            <th class="border border-gray-300 px-4 py-2">Work Duration (hours)</th>
            <th class="border border-gray-300 px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="log in attendanceLogs"
            :key="log.id"
            :class="{
              'bg-green-100': log.status === 'validated',
              'bg-red-100': log.status === 'flagged',
              'bg-orange-100': log.status === 'sent',
              '': log.status === 'ongoing',
            }"
            class="text-center"
          >
            <td class="border border-gray-300 px-4 py-2">{{ log.date }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.type }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_in }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_out || 'N/A' }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ (log.work_duration || 0).toFixed(2) }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <button 
                @click="viewAttendanceLog(log.id)" 
                class="text-blue-500 hover:underline"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>