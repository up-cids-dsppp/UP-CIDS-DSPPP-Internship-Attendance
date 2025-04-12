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
const evaluationModal = ref(false) // Control evaluation modal visibility
const evaluationDuration = ref(0) // Evaluation duration
const evaluationRemarks = ref('') // Evaluation remarks
const maxDuration = ref(0) // Maximum duration
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

    // Ensure tasks exist before iterating
    if (attendanceLog.value.tasks && attendanceLog.value.tasks.length > 0) {
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
    } else {
      console.log('No tasks available for this attendance log.')
    }

    if (attendanceLog.value.time_in && attendanceLog.value.time_out) {
      const timeIn = new Date(attendanceLog.value.time_in)
      const timeOut = new Date(attendanceLog.value.time_out)
      maxDuration.value = (timeOut - timeIn) / 1000 // Convert to seconds
    }
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

// Submit evaluation
const submitEvaluation = async () => {
  errors.value = {} // Reset errors

  // Validate inputs
  if (evaluationDuration.value < 0 || evaluationDuration.value > maxDuration.value) {
    errors.value.duration = 'Duration must be between 0 and the maximum allowed.'
  }
  if (!evaluationRemarks.value.trim()) {
    errors.value.remarks = 'Remarks are required.'
  }

  if (Object.keys(errors.value).length > 0) {
    return
  }

  try {
    await axios.post(`/admin/interns/attendance/${logId}/evaluate`, {
      duration: evaluationDuration.value,
      remarks: evaluationRemarks.value,
    })
    alert('Attendance evaluated successfully!')
    evaluationModal.value = false // Close modal
    location.reload() // Refresh the page
  } catch (error) {
    console.error('Failed to evaluate attendance:', error)
    alert('Failed to evaluate attendance. Please try again.')
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

    <!-- Conditional Buttons Based on Status -->
    <div v-if="attendanceLog">
      <div v-if="attendanceLog.status === 'sent'" class="mb-4">
        <!-- "Send Feedback" Button -->
        <button 
          @click="showModal = true" 
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Send Feedback
        </button>
      </div>
      <div v-if="attendanceLog.status === 'flagged'" class="mb-4">
        <!-- "Evaluate" Button -->
        <button 
          @click="evaluationModal = true" 
          class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
        >
          Evaluate
        </button>
      </div>
      <!-- No button for "validated" status -->
    </div>

    <!-- Attendance Log Details -->
    <div v-if="attendanceLog">
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
      <p><strong>Work Duration: </strong>{{ (attendanceLog.work_duration || 0).toFixed(2) }} hours</p>
      <p><strong>Remarks: </strong>{{ attendanceLog.remarks || 'N/A' }}</p>

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

    <!-- Evaluation Modal -->
    <div 
      v-if="evaluationModal" 
      class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-[600px] relative">
        <button 
          @click="evaluationModal = false" 
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
        >
          &times;
        </button>
        <h2 class="text-xl font-bold mb-4">Evaluate Attendance</h2>
        <div class="mb-4">
          <label for="evaluationDuration" class="block mb-2">Duration (seconds):</label>
          <input 
            id="evaluationDuration"
            type="number"
            v-model="evaluationDuration"
            :max="maxDuration"
            :min="0"
            class="border rounded px-4 py-2 mb-4 w-full"
          />
          <input 
            type="range"
            v-model="evaluationDuration"
            :max="maxDuration"
            :min="0"
            class="w-full"
          />
          <p v-if="errors.duration" class="text-red-500 text-sm mt-1">{{ errors.duration }}</p>
        </div>
        <div class="mb-4">
          <label for="evaluationRemarks" class="block font-semibold mb-2">Remarks</label>
          <textarea 
            id="evaluationRemarks" 
            v-model="evaluationRemarks" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2"
            rows="6"
          ></textarea>
          <p v-if="errors.remarks" class="text-red-500 text-sm mt-1">{{ errors.remarks }}</p>
        </div>
        <div class="flex justify-end">
          <button 
            @click="submitEvaluation" 
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>