<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const attendanceType = ref(null) // Dropdown value
const faceScreenshot = ref(null) // Captured face screenshot
const numberOfTasks = ref(1) // Number of tasks for asynchronous
const tasks = reactive([]) // Task descriptions
const internEmail = ref('') // Intern email

// Initialize tasks array with one empty task
tasks.push({ description: '' })

// Handle webcam capture
const captureFace = async () => {
  const video = document.createElement('video')
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.srcObject = stream
    await video.play()

    // Capture the frame
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    context.drawImage(video, 0, 0, canvas.width, canvas.height)
    faceScreenshot.value = canvas.toDataURL('image/png')

    // Stop the webcam
    stream.getTracks().forEach((track) => track.stop())
  } catch (error) {
    console.error('Error accessing webcam:', error)
  }
}

// Handle form submission
const submitForm = async () => {
  try {
    // Check if attendance type is selected
    if (!attendanceType.value) {
      alert('Please select an attendance type.')
      return
    }

    // Check for Face-to-Face attendance
    if (attendanceType.value === 'Face-to-Face') {
      if (!faceScreenshot.value) {
        alert('Please take a face screenshot.')
        return
      }

      // Submit face-to-face attendance
      await axios.post('/intern/attendance/f2f', {
        type: 'f2f',
        faceScreenshot: faceScreenshot.value,
        remarks: 'present',
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
      await axios.post('/intern/attendance/async', {
        type: 'async',
        tasks: tasks.map((task) => ({ description: task.description })),
      })
    }

    alert('Attendance logged successfully!')
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
        @click="captureFace"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Take Face Screenshot
      </button>
      <div v-if="faceScreenshot" class="mt-4">
        <h2 class="font-bold">Captured Image:</h2>
        <img :src="faceScreenshot" alt="Face Screenshot" class="mt-2 border rounded" />
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
      @click="submitForm"
      class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
    >
      Submit
    </button>
  </div>
</template>