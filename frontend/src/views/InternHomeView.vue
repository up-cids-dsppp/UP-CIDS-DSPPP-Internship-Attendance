<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const router = useRouter()

// Intern details
const internEmail = ref('') // Intern email
const internFullName = ref('') // Intern full name

// Date and time
const currentDate = ref(new Date().toLocaleDateString())
const currentTime = ref(new Date().toLocaleTimeString())

// Attendance logs
const attendanceLogs = ref([]) // Array to store attendance logs

// Update the clock every second
const updateClock = () => {
  currentTime.value = new Date().toLocaleTimeString()
}
setInterval(updateClock, 1000)

// Fetch intern details and attendance logs on component mount
onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile') // Replace with the correct endpoint
    internEmail.value = profileResponse.data.email
    internFullName.value = profileResponse.data.full_name

    // Fetch attendance logs
    const logsResponse = await axios.get('/intern/attendance') // Replace with the correct endpoint
    attendanceLogs.value = logsResponse.data // Assume the API returns an array of logs
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Handle "Time In" button click
const handleTimeIn = async () => {
  router.push('/intern/in') // Redirect to the time-in page
}

// Handle "View" link click
const viewAttendanceLog = (logId) => {
  router.push(`/intern/attendance/${logId}`) // Redirect to the attendance log details page
}
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="intern" :userEmail="internEmail" />

    <!-- Intern Content -->
    <div class="mt-8 px-6">
      <h2 class="text-xl font-bold">Welcome, {{ internFullName }}!</h2>

      <!-- Green Div with Date, Time, and Time In Button -->
      <div class="bg-green-500 text-white p-4 mt-4 rounded-lg max-w-md">
        <p class="text-lg font-semibold">Today's Date: {{ currentDate }}</p>
        <p class="text-lg font-semibold">Current Time: {{ currentTime }}</p>
        <div class="flex justify-end mt-4">
          <button 
            @click="handleTimeIn" 
            class="bg-white text-green-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
          >
            Time In
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
            <th class="border border-gray-300 px-4 py-2">Type</th> <!-- Add Type Column -->
            <th class="border border-gray-300 px-4 py-2">Time In</th>
            <th class="border border-gray-300 px-4 py-2">Time Out</th>
            <th class="border border-gray-300 px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in attendanceLogs" :key="log.id" class="text-center">
            <td class="border border-gray-300 px-4 py-2">{{ log.date }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.type }}</td> <!-- Display Type -->
            <td class="border border-gray-300 px-4 py-2">{{ log.time_in }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_out || 'N/A' }}</td>
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