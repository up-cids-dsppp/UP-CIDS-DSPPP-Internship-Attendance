<!-- filepath: /Users/gabrielramos/Desktop/UP-CIDS-DSPP-Internship-Attendance/frontend/src/views/AttendanceLogView.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const logId = route.params.id // Get the log ID from the route parameter
const attendanceLog = ref(null) // Store the attendance log details
const internEmail = ref('') // Intern email

const goBack = () => {
  router.back() // Navigates to the previous page
}

// Fetch the attendance log details when the component is mounted
onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile')
    internEmail.value = profileResponse.data.email

    // Fetch attendance log details
    const response = await axios.get(`/intern/attendance/log/${logId}`)
    attendanceLog.value = response.data
  } catch (error) {
    console.error('Failed to fetch attendance log:', error)
  }
})
</script>

<template>
  <NavBar userType="intern" :userEmail="internEmail" />
  <div class="p-6">
    <p 
    @click="goBack" 
    class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    <div v-if="attendanceLog">
      <h1 class="text-2xl font-bold mb-4">Attendance Log Details</h1>
      <p><strong>Date:</strong> {{ attendanceLog.date }}</p>
      <p><strong>Type:</strong> {{ attendanceLog.type }}</p>
      <p><strong>Time In:</strong> {{ attendanceLog.time_in }}</p>
      <p><strong>Time Out:</strong> {{ attendanceLog.time_out || 'N/A' }}</p>
      <p><strong>Remarks:</strong> {{ attendanceLog.remarks || 'N/A' }}</p>
      <div v-if="attendanceLog.tasks.length" class="mt-4">
        <h2 class="text-xl font-semibold">Tasks</h2>
        <div v-for="task in attendanceLog.tasks" :key="task.id" class="bg-gray-100 p-4 rounded-lg mt-4">
          <p><strong>Description:</strong> {{ task.description }}</p>
          <p><strong>Images:</strong></p>
          <div v-if="task.images && task.images.length" class="mt-2">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <img v-for="image in task.images" :key="image.id" :src="image.file" alt="Task Image" class="rounded-md" style="max-height: 150px;">
            </div>
          </div>
          <p><strong>Remarks:</strong> {{ task.remarks || 'N/A' }}</p>
        </div>
      </div>
    </div>
    <div v-else class="text-gray-500">Loading attendance log details...</div>
  </div>
</template>