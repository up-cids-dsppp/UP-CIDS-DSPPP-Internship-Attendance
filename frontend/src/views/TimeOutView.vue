<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const logId = route.params.log_id // Get the log ID from the route parameter
const internEmail = ref('') // Intern email
const attendanceLog = ref(null) // Store the attendance log details
const tasks = reactive([]) // Task list with descriptions, images, and remarks

const objectURLs = new Set()

// Fetch attendance log details and tasks on component mount
onMounted(async () => {
  try {
    // Fetch intern details
    const profileResponse = await axios.get('/intern/profile') // Replace with the correct endpoint
    internEmail.value = profileResponse.data.email

    // Fetch attendance log details
    const logResponse = await axios.get(`/intern/attendance/log/${logId}`) // Replace with the correct endpoint
    attendanceLog.value = logResponse.data

    // Populate tasks with descriptions, images, remarks, and initialize imagePreviews
    tasks.push(...attendanceLog.value.tasks.map(task => ({
      id: task.id,
      description: task.description,
      images: [],
      remarks: '',
      imagePreviews: [], // Initialize imagePreviews as an empty array
    })))
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Handle file upload for a task
const handleFileUpload = (task, event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    // Store the actual file objects in the task.images array
    task.images = Array.from(files)

    // Generate blob URLs for preview
    task.imagePreviews = task.images.map(file => getImageURL(file))
  }
}

// Validate and submit the tasks
const handleSubmit = async () => {
  const formData = new FormData()
  tasks.forEach(task => {
    formData.append(`tasks[${task.id}][remarks]`, task.remarks)
    task.images.forEach((image, index) => {
      formData.append(`tasks[${task.id}][images][${index}]`, image) // Append the actual file objects
    })
  })

  try {
    await axios.post(`/intern/attendance/log/${logId}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    alert('Tasks submitted successfully!')
    router.push('/intern/home')
  } catch (error) {
    console.error('Failed to submit tasks:', error)
    alert('Failed to submit tasks. Please try again.')
  }
}

// Go back to the previous page
const goBack = () => {
  router.back()
}

// Get image URL
const getImageURL = (file) => {
  const url = URL.createObjectURL(file)
  objectURLs.add(url)
  return url
}

onUnmounted(() => {
  objectURLs.forEach((url) => URL.revokeObjectURL(url))
  objectURLs.clear()
  tasks.forEach((task) => {
    if (task.imagePreviews) {
      task.imagePreviews.forEach((image) => {
        URL.revokeObjectURL(image)
      })
    }
  })
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
    <div v-if="attendanceLog">
      <h1 class="text-2xl font-bold mb-4">Time Out</h1>
      <p><strong>Date:</strong> {{ attendanceLog.date }}</p>
      <p><strong>Type:</strong> {{ attendanceLog.type }}</p>
      <p><strong>Time In:</strong> {{ attendanceLog.time_in }}</p>
      <p><strong>Time Out:</strong> {{ attendanceLog.time_out || 'N/A' }}</p>

      <!-- Task List -->
      <h2 class="text-xl font-semibold mt-4">Tasks</h2>
      <form @submit.prevent="handleSubmit" enctype="multipart/form-data">
        <div v-for="task in tasks" :key="task.id" class="bg-gray-100 p-4 rounded-lg mt-4">
          <p><strong>Description:</strong> {{ task.description }}</p>
          
          <div class="mt-4">
            <p><strong>Images:</strong></p>
            <label class="block text-sm font-medium text-gray-700">Upload Images:</label>
            <input
              type="file"
              multiple
              accept=".jpg,.jpeg,.png"
              @change="(event) => handleFileUpload(task, event)"
              class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
            <div v-if="task.imagePreviews.length" class="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4">
              <img
                v-for="(image, index) in task.imagePreviews"
                :key="index"
                :src="image"
                alt="Uploaded Image"
                class="rounded-md"
                style="max-height: 150px;"
              />
            </div>
          </div>

          <div class="mt-4">
            <p><strong>Remarks:</strong></p>
            <textarea
              v-model="task.remarks"
              rows="3"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2"
              placeholder="Enter remarks for this task"
            ></textarea>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="mt-6">
          <button
            type="submit"
            class="bg-red-500 text-white px-6 py-2 rounded-lg hover:bg-red-600 transition"
          >
            Submit
          </button>
        </div>
      </form>
    </div>
    <div v-else class="text-gray-500">Loading attendance log details...</div>
  </div>
</template>