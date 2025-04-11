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
const adminEmail = ref('') // Admin email

const goBack = () => {
  router.back() // Navigates to the previous page
}

// Fetch the attendance log details when the component is mounted
onMounted(async () => {
  try {
    // Fetch admin details
    const profileResponse = await axios.get('/admin/profile')
    adminEmail.value = profileResponse.data.email

    // Fetch attendance log details
    const response = await axios.get(`/admin/interns/attendance/${logId}/`)
    attendanceLog.value = response.data

    // Log each task and its images for debugging
    attendanceLog.value.tasks.forEach(task => {
      console.log(`Task ID: ${task.id}, Description: ${task.description}`)
      if (task.images && task.images.length > 0) {
        task.images.forEach(image => {
          console.log(`Image ID: ${image.id}, File URL: ${image.file}`)
        })
      } else {
        console.log(`Task ID: ${task.id} has no images.`)
      }
    })
  } catch (error) {
    console.error('Failed to fetch attendance log:', error)
  }
})
</script>

<template>
  <NavBar userType="admin" :userEmail="adminEmail" />
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
      <h2 class="text-xl font-semibold mt-4">Tasks</h2>
      <div v-if="attendanceLog.tasks.length">
        <div v-for="task in attendanceLog.tasks" :key="task.id" class="bg-gray-100 p-4 rounded-lg mt-4">
          <p><strong>Description:</strong> {{ task.description }}</p>
          <p class="mt-4"><strong>Images:</strong></p>
          <div v-if="task.images && task.images.length" class="mt-2">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <img
                v-for="image in task.images"
                :key="image.id"
                :src="`${'http://localhost:8000/media/'}${image.file}`"
                alt="Task Image"
                class="rounded-md"
                style="max-height: 150px;"
              />
            </div>
          </div>
          <p class="mt-4"><strong>Remarks:</strong> {{ task.remarks || 'N/A' }}</p>
        </div>
      </div>
      <div v-else class="text-gray-500">No tasks available.</div>
    </div>
    <div v-else class="text-gray-500">Loading attendance log details...</div>
  </div>
</template>