<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const route = useRoute()

// Admin details
const adminEmail = ref('') // Admin email

// Intern details
const internDetails = ref({
  full_name: '',
  email: '',
  start_date: '',
  time_to_render: 0,
  time_rendered: 0,
  status: '',
}) // Intern details object

// Attendance logs
const attendanceLogs = ref([]) // Array to store attendance logs

// Fetch admin and intern details along with attendance logs on component mount
onMounted(async () => {
  try {
    // Fetch admin details
    const adminResponse = await axios.get('/admin/profile') // Admin profile endpoint
    adminEmail.value = adminResponse.data.email

    // Fetch intern details using the dynamic ID from the route
    const internId = route.params.id // Get the intern ID from the route
    const profileResponse = await axios.get(`/admin/interns/${internId}`) // New endpoint
    internDetails.value = {
      full_name: profileResponse.data.full_name,
      email: profileResponse.data.email,
      start_date: profileResponse.data.start_date,
      time_to_render: profileResponse.data.time_to_render,
      time_rendered: profileResponse.data.time_rendered,
      status: profileResponse.data.status,
    }

    // Fetch attendance logs for the specific intern
    attendanceLogs.value = profileResponse.data.attendance_logs // Assume the API returns an array of logs
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Handle "View" link click
const viewAttendanceLog = (logId) => {
  router.push(`/admin/intern/attendance/${logId}`) // Redirect to the attendance log details page
}

const goBack = () => {
  router.back() // Navigates to the previous page
}
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="admin" :userEmail="adminEmail" />
    <!-- Intern Content -->
    <div class="mt-8 px-6">
      <p 
      @click="goBack" 
      class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
      <h2 class="text-xl font-bold">Intern Profile</h2>
      <p class="mt-2"><strong>Full Name:</strong> {{ internDetails.full_name }}</p>
      <p class="mt-2"><strong>Email:</strong> {{ internDetails.email }}</p>
      <p class="mt-2"><strong>Start Date:</strong> {{ internDetails.start_date }}</p>
      <p class="mt-2"><strong>Time to be Rendered:</strong> {{ internDetails.time_to_render }} hours</p>
      <p class="mt-2"><strong>Time Rendered:</strong> {{ internDetails.time_rendered }} hours</p>
      <p class="mt-2"><strong>Status:</strong> {{ internDetails.status }}</p>

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
            <th class="border border-gray-300 px-4 py-2">Status</th>
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
            <td class="border border-gray-300 px-4 py-2">{{ log.status }}</td>
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