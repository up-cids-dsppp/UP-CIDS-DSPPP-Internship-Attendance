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

// State for image modal
const selectedImage = ref(null) // Store the currently selected image
const showImageModal = ref(false) // Control image modal visibility

const goBack = () => {
  router.push('/intern/home') // Navigates to the previous page
}

// Fetch the attendance log details when the component is mounted
onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile')
    internEmail.value = profileResponse.data.email

    // Fetch attendance log details
    const response = await axios.get(`/intern/attendance/${logId}`)
    attendanceLog.value = response.data
  } catch (error) {
    if (error.response && error.response.status === 403) {
      // Redirect to unauthorized page if access is forbidden
      router.push('/unauthorized')
    } else {
      console.error('Failed to fetch attendance log:', error)
    }
  }
})

// Function to determine the status color
const getStatusColor = (status) => {
  switch (status) {
    case 'validated':
      return 'text-green-500'
    case 'sent':
      return 'text-orange-500'
    case 'flagged':
      return 'text-red-500'
    case 'ongoing':
      return 'text-black'
    default:
      return 'text-gray-500'
  }
}

// Function to open the image modal
const openImageModal = (image) => {
  selectedImage.value = image
  showImageModal.value = true
}

// Function to close the image modal
const closeImageModal = () => {
  selectedImage.value = null
  showImageModal.value = false
}

// Function to download the image
const downloadImage = async () => {
  if (!selectedImage.value) return
  try {
    const response = await fetch(selectedImage.value)
    const blob = await response.blob()
    // Try to get a filename from the URL
    const urlParts = selectedImage.value.split('/')
    const filename = urlParts[urlParts.length - 1] || 'image.jpg'
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(link.href)
  } catch (e) {
    alert('Failed to download image.')
  }
}

const mediaBaseUrl = import.meta.env.VITE_MEDIA_BASE_URL
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
      <p><strong>Date: </strong>{{ attendanceLog.date }}</p>
      <p><strong>Type: </strong>{{ attendanceLog.type }}</p>
      <p><strong>Time In: </strong>{{ attendanceLog.time_in }}</p>
      <p><strong>Time Out: </strong>{{ attendanceLog.time_out || 'N/A' }}</p>
      <p><strong>Work Duration: </strong>{{ (attendanceLog.work_duration || 0).toFixed(2) }} hours</p>
      <br>
      <p><strong>Status: </strong> 
        <span :class="getStatusColor(attendanceLog.status)">
          {{ attendanceLog.status }}
        </span>
      </p>
      <p><strong>Admin Remarks: </strong><br>{{ attendanceLog.admin_remarks || 'N/A' }}</p>
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
                :src="`${mediaBaseUrl}${image.file}`"
                alt="Task Image"
                class="rounded-md cursor-pointer hover:opacity-80 transition"
                style="max-height: 150px;"
                @click="openImageModal(`${mediaBaseUrl}${image.file}`)"
              />
            </div>
          </div>
          <p class="mt-4"><strong>Remarks:</strong><br>{{ task.intern_remarks || 'N/A' }}</p>
        </div>
      </div>
      <div v-else class="text-gray-500">Loading tasks...</div>
    </div>
    <div v-else class="text-gray-500">Loading attendance log details...</div>

    <!-- Image Modal -->
    <div 
      v-if="showImageModal" 
      class="fixed inset-0 bg-black/30 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 relative max-w-7xl w-full flex flex-col items-center">
        <button 
          @click="closeImageModal" 
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-5xl"
        >
          &times;
        </button>
        <img 
          :src="selectedImage" 
          alt="Selected Image" 
          class="w-full h-auto max-h-[80vh] rounded-lg object-contain mb-4"
        />
        <button
          v-if="selectedImage"
          @click="downloadImage"
          class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
        >
          Download Image
        </button>
      </div>
    </div>
  </div>
</template>