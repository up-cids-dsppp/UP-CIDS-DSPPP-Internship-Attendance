<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const logId = route.params.log_id // Get the log ID from the route parameter
const internEmail = ref('') // Intern email
const attendanceLog = ref(null) // Store the attendance log details
const tasks = reactive([]) // Task list with descriptions, images, and remarks
const showConfirmationModal = ref(false) // Modal visibility

// Fetch attendance log details and tasks on component mount
onMounted(async () => {
  try {
    const profileResponse = await axios.get('/intern/profile')
    internEmail.value = profileResponse.data.email

    const logResponse = await axios.get(`/intern/attendance/${logId}`)
    attendanceLog.value = logResponse.data

    tasks.push(...logResponse.data.tasks.map(task => ({
      id: task.id,
      description: task.description,
      images: [],
      imagePreviews: [],
      intern_remarks: ''
    })))
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Handle image upload for async tasks
const handleImageUpload = (task, event) => {
  const files = event.target.files
  for (const file of files) {
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      alert('Only JPG and PNG files are allowed.')
      continue
    }
    task.images.push(file)

    const reader = new FileReader()
    reader.onload = (e) => {
      task.imagePreviews.push(e.target.result)
    }
    reader.readAsDataURL(file)
  }
}

// Remove an image from the task
const removeImage = (task, index) => {
  task.images.splice(index, 1)
  task.imagePreviews.splice(index, 1)
}

// Submit the timeout
const handleSubmit = () => {
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
  showConfirmationModal.value = true
}

const confirmSubmit = async () => {
  showConfirmationModal.value = false // Hide the modal after confirmation

  try {

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

    alert('Timeout submitted successfully!')
    router.push('/intern/home')
  } catch (error) {
    console.error('Failed to submit timeout:', error)
    alert('Failed to submit timeout. Please try again.')
  }
}

// Go back to the previous page
const goBack = () => {
  router.push('/intern/home') // Navigates to the previous page
}
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
    <h1 class="text-2xl font-bold mb-4">Asynchronous Timeout</h1>

    <!-- Attendance Details -->
    <div v-if="attendanceLog" class="mb-6">
      <p><strong>Date:</strong> {{ attendanceLog.date }}</p>
      <p><strong>Type:</strong> {{ attendanceLog.type }}</p>
      <p><strong>Time In:</strong> {{ attendanceLog.time_in }}</p>
      <p><strong>Time Out:</strong> {{ attendanceLog.time_out || 'N/A' }}</p>
    </div>

    <div v-for="task in tasks" :key="task.id" class="bg-gray-100 p-4 rounded-lg mt-4">
      <p><strong>Description:</strong> {{ task.description }}</p>

      <!-- Image Upload -->
      <div class="mt-4">
        <label class="block mb-2 font-medium">Upload Images (JPG/PNG):</label>
        <input
          type="file"
          accept="image/jpeg, image/png"
          multiple
          @change="handleImageUpload(task, $event)"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <div
            v-for="(preview, index) in task.imagePreviews"
            :key="index"
            class="relative w-24 h-24"
          >
            <img :src="preview" alt="Preview" class="w-full h-full object-cover rounded-md" />
            <button
              @click="removeImage(task, index)"
              class="absolute top-0 right-0 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
            >
              &times;
            </button>
          </div>
        </div>
      </div>

<!-- Remarks -->
      <div class="mt-4">
        <label class="block mb-2 font-medium">Remarks:</label>
        <textarea
          v-model="task.intern_remarks"
          rows="3"
          class="w-full border rounded px-4 py-2"
          placeholder="Enter your remarks here..."
        ></textarea>
      </div>
    </div>

    <button
      @click="handleSubmit"
      class="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 mt-6"
    >
      Submit
    </button>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmationModal" class="fixed inset-0 bg-black/30 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <h2 class="text-lg font-bold mb-4">Confirm Submission</h2>
        <p>Are you sure you want to submit the timeout form?</p>
        <div class="mt-4 flex justify-end gap-2">
          <button
            @click="showConfirmationModal = false"
            class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            @click="confirmSubmit"
            class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>