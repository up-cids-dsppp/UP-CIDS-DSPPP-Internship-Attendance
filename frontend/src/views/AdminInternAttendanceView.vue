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
const showModal = ref(false) // Control modal visibility
const feedbackType = ref('') // Dropdown value
const feedbackRemarks = ref('') // Text area value
const errors = ref({}) // Validation errors

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

// Submit feedback
const submitFeedback = async () => {
  errors.value = {} // Reset errors

  // Validate inputs
  if (!feedbackType.value) {
    errors.value.type = 'Feedback type is required.'
  }
  if (!feedbackRemarks.value.trim()) {
    errors.value.remarks = 'Remarks are required.'
  }

  if (Object.keys(errors.value).length > 0) {
    return
  }

  try {
    await axios.post(`/admin/interns/attendance/${logId}/feedback`, {
      type: feedbackType.value,
      remarks: feedbackRemarks.value,
    })
    alert('Feedback submitted successfully!')
    showModal.value = false // Close modal
    feedbackType.value = '' // Reset dropdown
    feedbackRemarks.value = '' // Reset text area
    location.reload() // Refresh the page
  } catch (error) {
    console.error('Failed to submit feedback:', error)
    alert('Failed to submit feedback. Please try again.')
  }
}

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
    <!-- "Send Feedback" Button -->
    <div class="mb-4">
        <button 
          @click="showModal = true" 
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Send Feedback
        </button>
      </div>
    <div v-if="attendanceLog">
      <!-- Header with "Attendance Log Details" -->
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">Attendance Log Details</h1>
      </div>
      <p><strong>Date: </strong>{{ attendanceLog.date }}</p>
      <p><strong>Type: </strong>{{ attendanceLog.type }}</p>
      <p><strong>Status: </strong> 
        <span :class="getStatusColor(attendanceLog.status)">
          {{ attendanceLog.status }}
        </span>
      </p>
      <p><strong>Time In: </strong>{{ attendanceLog.time_in }}</p>
      <p><strong>Time Out: </strong>{{ attendanceLog.time_out || 'N/A' }}</p>

      <!-- Tasks Header -->
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

    <!-- Feedback Modal -->
    <div 
      v-if="showModal" 
      class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-[600px] relative">
        <button 
          @click="showModal = false" 
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
        >
          &times;
        </button>
        <h2 class="text-xl font-bold mb-4">Send Feedback</h2>
        <div class="mb-4">
          <label for="feedbackType" class="block mb-2">Select Feedback Type:</label>
          <select
            id="feedbackType"
            v-model="feedbackType"
            class="border rounded px-4 py-2 mb-4 w-full"
          >
            <option disabled value="">-- Select --</option>
            <option value="Flag">Flag</option>
            <option value="Validate">Validate</option>
          </select>
          <p v-if="errors.type" class="text-red-500 text-sm mt-1">{{ errors.type }}</p>
        </div>
        <div class="mb-4">
          <label for="feedbackRemarks" class="block font-semibold mb-2">Remarks</label>
          <textarea 
            id="feedbackRemarks" 
            v-model="feedbackRemarks" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
            rows="6"
          ></textarea>
          <p v-if="errors.remarks" class="text-red-500 text-sm mt-1">{{ errors.remarks }}</p>
        </div>
        <div class="flex justify-end">
          <button 
            @click="submitFeedback" 
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>