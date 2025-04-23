<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { useRouter } from 'vue-router'

const attendanceType = ref(null)
const faceScreenshot = ref(null)
const numberOfTasks = ref(1)
const tasks = reactive([])
const internEmail = ref('')
const showModal = ref(false)
const videoStream = ref(null)
const showConfirmationModal = ref(false) // Modal visibility for confirmation
const errorMessage = ref('') // Error message for the modal

tasks.push({ description: '' })

const router = useRouter()

const goBack = () => {
  router.push('/intern/home') // Navigates to the previous page
}

// Open the modal and start the camera
const openCameraModal = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    videoStream.value = stream
    showModal.value = true
  } catch (error) {
    console.error('Error accessing camera:', error)
    alert('Unable to access the camera. Please check your permissions.')
  }
}

// Close the modal and stop the camera
const closeCameraModal = () => {
  if (videoStream.value) {
    videoStream.value.getTracks().forEach((track) => track.stop())
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
  // Reset the error message before showing the confirmation modal
  errorMessage.value = ''

  // Always show the confirmation modal for both attendance types
  showConfirmationModal.value = true
}

// Reset the modal state
const resetModal = () => {
  showConfirmationModal.value = false
  errorMessage.value = ''
}

// Handle form submission
const submitForm = async () => {
  showConfirmationModal.value = false // Hide the modal after confirmation

  try {
    // Check if attendance type is selected
    if (!attendanceType.value) {
      alert('Please select an attendance type.')
      return
    }

    // Check for Face-to-Face attendance
    if (attendanceType.value === 'Face-to-Face') {
      // Validate time for Face-to-Face attendance
      const now = new Date()
      const currentHour = now.getHours()
      if (currentHour < 8 || currentHour >= 17) {
        errorMessage.value = 'You can only submit a Face-to-Face attendance from 8 AM to 5 PM.'
        showConfirmationModal.value = true // Reopen the modal with the error message
        return
      }

      if (!faceScreenshot.value) {
        alert('Please take a face screenshot.')
        return
      }

      // Submit face-to-face attendance
      const response = await axios.post('/intern/attendance/f2f', {
        faceScreenshot: faceScreenshot.value,
      })

    }

    // Check for Asynchronous attendance
    if (attendanceType.value === 'Asynchronous') {
      if (numberOfTasks.value < 1) {
        alert('Please specify at least one task.')
        return
      }

      for (const task of tasks) {
        if (!task.description.trim()) {
          alert('Please fill out all task descriptions.')
          return
        }
      }

      // Submit asynchronous attendance with tasks
      const response = await axios.post('/intern/attendance/async', {
        type: 'async',
        tasks: tasks.map((task) => ({ description: task.description })),
      })
    }

    alert('Attendance logged successfully!')
    router.push('/intern/home') // Redirect to home page
  } catch (error) {
    console.error('Error submitting attendance:', error)
    alert('Failed to log attendance.')
  }
}

// Update tasks array when number of tasks changes
const updateTasks = () => {
  while (tasks.length < numberOfTasks.value) {
    tasks.push({ description: '' })
  }
  while (tasks.length > numberOfTasks.value) {
    tasks.pop()
  }
}

onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile') // Replace with the correct endpoint
    internEmail.value = profileResponse.data.email
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})
</script>

<template>
  <!-- Navbar Component -->
  <NavBar userType="intern" :userEmail="internEmail" />
  <div class="p-6">
    <p 
      @click="goBack" 
      class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    <h1 class="text-2xl font-bold mb-4">Time In</h1>

    <!-- Attendance Type Dropdown -->
    <label for="attendanceType" class="block mb-2">Select Attendance Type:</label>
    <select
      id="attendanceType"
      v-model="attendanceType"
      class="border rounded px-4 py-2 mb-4 w-full"
    >
      <option disabled value="">-- Select --</option>
      <option value="Face-to-Face">Face-to-Face</option>
      <option value="Asynchronous">Asynchronous</option>
    </select>

    <!-- Face-to-Face Section -->
    <div v-if="attendanceType === 'Face-to-Face'" class="mb-4">
      <button
        @click="openCameraModal"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Take Face Screenshot
      </button>

      <div v-if="faceScreenshot" class="mt-4">
        <h2 class="font-bold">Captured Image:</h2>
        <img :src="faceScreenshot" alt="Face Screenshot" class="mt-2 border rounded" />
      </div>
    </div>

    <!-- Modal for Camera Preview -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-4 rounded shadow-lg w-96">
        <h2 class="text-lg font-bold mb-4">Camera Preview</h2>
        <video id="cameraPreview" autoplay playsinline class="w-full rounded" :srcObject="videoStream"></video>
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

    <!-- Asynchronous Section -->
    <div v-if="attendanceType === 'Asynchronous'" class="mb-4">
      <label for="numberOfTasks" class="block mb-2">Number of Tasks:</label>
      <input
        id="numberOfTasks"
        type="number"
        v-model="numberOfTasks"
        @input="updateTasks"
        class="border rounded px-4 py-2 mb-4 w-full"
        min="1"
      />

      <div v-for="(task, index) in tasks" :key="index" class="mb-2">
        <label :for="'task-' + index" class="block">Task {{ index + 1 }}:</label>
        <input
          :id="'task-' + index"
          v-model="task.description"
          type="text"
          class="border rounded px-4 py-2 w-full"
        />
      </div>
    </div>

    <!-- Submit Button -->
    <button
      @click="confirmSubmit"
      class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
    >
      Submit
    </button>

    <!-- Confirmation Modal -->
    <div
      v-if="showConfirmationModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
    >
      <div class="bg-white p-6 rounded shadow-lg w-96">
        <h2 class="text-lg font-bold mb-4">Confirm Submission</h2>
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <p v-else>Are you sure you want to time in?</p>
        <div class="flex justify-end mt-4">
          <button
            @click="resetModal"
            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mr-2"
          >
            Cancel
          </button>
          <button
            v-if="!errorMessage"
            @click="submitForm"
            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>