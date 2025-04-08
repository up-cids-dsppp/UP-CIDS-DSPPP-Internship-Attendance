<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

// Helper function to get today's date in YYYY-MM-DD format
const getCurrentDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const router = useRouter()

// Form fields for the intern
const fullName = ref('')
const email = ref('')
const password = ref('')
const startDate = ref(getCurrentDate()) // Initialize with today's date
const timeToRender = ref('')

// Store the admin's email
const adminEmail = ref('')

// Fetch the admin's email when the component is mounted
onMounted(async () => {
  try {
    const response = await axios.get('/admin/profile') // Adjust endpoint if necessary
    adminEmail.value = response.data.email
  } catch (error) {
    console.error('Failed to fetch admin email:', error)
  }
})

// Submit the form
const handleSubmit = async () => {
  try {
    await axios.post('/admin/interns', {
      full_name: fullName.value,
      email: email.value,
      password: password.value,
      start_date: startDate.value,
      time_to_render: timeToRender.value,
    })
    router.push('/admin/home') // Redirect to admin home page
  } catch (error) {
    console.error('Failed to add intern:', error)
  }
}

// Navigate back to the admin home page
const goBack = () => {
  router.push('/admin/home')
}
</script>

<template>
  <div>
    <!-- Navbar -->
    <NavBar userType="admin" :userEmail="adminEmail" />

    <!-- Add Intern Form -->
    <div class="max-w-lg mx-auto mt-8 p-6 bg-white shadow-md rounded-lg">
      <h2 class="text-2xl font-bold mb-4">Add New Intern</h2>
      <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
        <div>
          <label for="fullName" class="block font-medium mb-1">Full Name</label>
          <input
            id="fullName"
            v-model="fullName"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter full name"
            required
          />
        </div>
        <div>
          <label for="email" class="block font-medium mb-1">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter email"
            required
          />
        </div>
        <div>
          <label for="password" class="block font-medium mb-1">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter password"
            required
          />
        </div>
        <div>
          <label for="startDate" class="block font-medium mb-1">Start Date</label>
          <input
            id="startDate"
            v-model="startDate"
            type="date"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label for="timeToRender" class="block font-medium mb-1">Time to Render (in hours)</label>
          <input
            id="timeToRender"
            v-model="timeToRender"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter time to render (in hours)"
            required
          />
        </div>
        <button
          type="submit"
          class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          Add Intern
        </button>
      </form>

      <!-- Back Button -->
      <p 
      @click="goBack" 
      class="mt-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    </div>
  </div>
</template>