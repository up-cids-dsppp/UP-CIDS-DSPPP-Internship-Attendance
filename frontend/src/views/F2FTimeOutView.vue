<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const logId = route.params.log_id // Get the log ID from the route parameter
const internEmail = ref('') // Intern email
const attendanceLog = ref(null) // Store the attendance log details
const faceScreenshot = ref(null) // Face screenshot for the timeout task
const videoStream = ref(null) // Video stream for the camera
const showModal = ref(false) // Modal visibility for the camera
const showConfirmationModal = ref(false) // Modal visibility for confirmation

// Fetch attendance log details on component mount
onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile') // Replace with the correct endpoint
    internEmail.value = profileResponse.data.email

    // Fetch attendance log details
    const logResponse = await axios.get(`/intern/attendance/${logId}`) // Replace with the correct endpoint
    attendanceLog.value = logResponse.data
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Open the modal and start the camera
const openCameraModal = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    videoStream.value = stream
    showModal.value = true
  } catch (error) {
    console.error('Error accessing camera:', error)
    alert('Unable to access the camera.')
  }
}

// Close the modal and stop the camera
const closeCameraModal = () => {
  if (videoStream.value) {
    videoStream.value.getTracks().forEach(track => track.stop())
    videoStream.value = null
  }
  showModal.value = false
}

// Capture the image from the camera
const captureImage = () => {
  const video = document.querySelector('#cameraPreview')
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  faceScreenshot.value = canvas.toDataURL('image/png') // Save the captured image
  closeCameraModal() // Close the modal
}

// Show confirmation modal
const confirmSubmit = () => {
  showConfirmationModal.value = true // Show the confirmation modal
}

// Submit the timeout
const handleSubmit = async () => {
  showConfirmationModal.value = false // Hide the modal after confirmation

  try {
    if (attendanceLog.value.type === 'f2f') {
      if (!faceScreenshot.value) {
        alert('Please take a face screenshot for the timeout task.')
        return
      }

      // Submit face-to-face timeout
      await axios.post(`/intern/attendance/${logId}/submit/f2f`, {
        faceScreenshot: faceScreenshot.value,
      })
    } else if (attendanceLog.value.type === 'async') {
      for (const task of tasks) {
        if (task.images.length === 0) {
          alert(`Task "${task.description}" must have at least one image.`)
          return
        }
        if (!task.intern_remarks.trim()) {
          alert(`Task "${task.description}" must have remarks.`)
          return
        }
      }

      // Submit asynchronous timeout
      const formData = new FormData()
      tasks.forEach(task => {
        formData.append(`tasks[${task.id}][intern_remarks]`, task.intern_remarks)
        task.images.forEach((image, index) => {
          formData.append(`tasks[${task.id}][images][${index}]`, image)
        })
      })

      await axios.post(`/intern/attendance/${logId}/submit/async`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    // Set timed-out state in the store
    timeInOutStore.setTimedOutForTheDay(true)
    timeInOutStore.setTimedIn(false, null, null)

    alert('Timeout submitted successfully!')
    router.push('/intern/home')
  } catch (error) {
    console.error('Failed to submit timeout:', error)
    alert('Failed to submit timeout. Please try again.')
  }
}
</script>

<template>
  <!-- Navbar Component -->
  <NavBar userType="intern" :userEmail="internEmail" />
  <div class="p-6">
    <p 
      @click="() => router.push('/intern/home')" 
      class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    <div v-if="attendanceLog">
      <h1 class="text-2xl font-bold mb-4">Face-to-Face Timeout</h1>
      <p><strong>Date:</strong> {{ attendanceLog.date }}</p>
      <p><strong>Type:</strong> {{ attendanceLog.type }}</p>
      <p><strong>Time In:</strong> {{ attendanceLog.time_in }}</p>
      <p><strong>Time Out:</strong> {{ attendanceLog.time_out || 'N/A' }}</p>

      <!-- Face-to-Face Out Screenshot -->
      <div class="mt-4">
        <p><strong>Face Screenshot:</strong></p>
        <button
          @click="openCameraModal"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Take Screenshot
        </button>
        <div v-if="faceScreenshot" class="mt-4">
          <img :src="faceScreenshot" alt="Face Screenshot" class="rounded-md" style="max-height: 150px;" />
        </div>
      </div>

      <!-- Submit Button -->
      <div class="mt-6">
        <button
          @click="confirmSubmit"
          class="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition"
        >
          Submit
        </button>
      </div>
    </div>
    <div v-else class="text-gray-500">Loading attendance log details...</div>

    <!-- Camera Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h2 class="text-lg font-bold mb-4">Take Face Screenshot</h2>
        <video id="cameraPreview" autoplay playsinline :srcObject="videoStream" class="w-full rounded-md"></video>
        <div class="flex justify-end mt-4">
          <button
            @click="closeCameraModal"
            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mr-2"
          >
            Cancel
          </button>
          <button
            @click="captureImage"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Capture
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div
      v-if="showConfirmationModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h2 class="text-lg font-bold mb-4">Confirm Submission</h2>
        <p>Are you sure you want to time out?</p>
        <div class="flex justify-end mt-4">
          <button
            @click="() => (showConfirmationModal = false)"
            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mr-2"
          >
            Cancel
          </button>
          <button
            @click="handleSubmit"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>