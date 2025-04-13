<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth' // Import the auth store
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
const route = useRoute()
const internId = route.params.id
const authStore = useAuthStore() // Access the auth store

// Form fields for the intern
const fullName = ref('')
const email = ref('')
const password = ref('') // New password (optional)
const startDate = ref('')
const timeToRender = ref('')

// Store the admin's email
const adminEmail = ref('')

// Modal state
const showConfirmationModal = ref(false) // Control confirmation modal visibility

// Fetch the intern's details when the component is mounted
onMounted(async () => {
  try {
    const adminResponse = await axios.get('/admin/profile')
    adminEmail.value = adminResponse.data.email

    const internResponse = await axios.get(`/admin/interns/${internId}`)
    fullName.value = internResponse.data.full_name
    email.value = internResponse.data.email
    startDate.value = internResponse.data.start_date
    timeToRender.value = internResponse.data.time_to_render
  } catch (error) {
    console.error('Failed to fetch intern details:', error)
  }
})

const errors = ref({}) // Store validation errors

// Generate a strong password
const generatePassword = () => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
  let newPassword = ''
  for (let i = 0; i < 8; i++) {
    const randomIndex = Math.floor(Math.random() * characters.length)
    newPassword += characters[randomIndex]
  }
  password.value = newPassword // Set the generated password
}

// Submit the form
const handleSubmit = async () => {
  errors.value = {} // Reset errors

  // Validate inputs
  if (!fullName.value.trim()) {
    errors.value.fullName = 'Full name is required.'
  }
  if (!email.value.trim()) {
    errors.value.email = 'Email is required.'
  }
  if (!startDate.value.trim()) {
    errors.value.startDate = 'Start date is required.'
  }
  if (!timeToRender.value || timeToRender.value <= 0) {
    errors.value.timeToRender = 'Time to render must be greater than 0.'
  }

  // Check if there are any validation errors
  if (Object.keys(errors.value).length > 0) {
    return // Stop submission if there are errors
  }

  // Show the confirmation modal
  showConfirmationModal.value = true
}

// Confirm submission
const confirmSubmit = async () => {
  try {
    await axios.put(`/admin/interns/${internId}/`, {
      full_name: fullName.value,
      email: email.value,
      password: password.value || undefined, // Only send password if it's provided
      start_date: startDate.value,
      time_to_render: timeToRender.value,
    })
    alert('Intern details updated successfully!')
    showConfirmationModal.value = false // Close the modal
    router.push(`/admin/interns/${internId}`) // Redirect to the intern's profile
  } catch (error) {
    console.error('Failed to update intern details:', error)
    alert('Failed to update intern details. Please try again.')
    showConfirmationModal.value = false // Close the modal
  }
}

const goBack = () => {
  router.push(`/admin/interns/${internId}`) // Redirect to the intern's profile
}
</script>

<template>
  <div>
    <NavBar userType="admin" :userEmail="adminEmail" />

    <p 
      @click="goBack" 
      class="mt-4 ml-6 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    <div class="max-w-lg mx-auto mt-4 mb-10 p-6 bg-white shadow-md rounded-lg">
      <h2 class="text-2xl font-bold mb-4">Edit Intern</h2>
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
          <p v-if="errors.fullName" class="text-red-500 text-sm mt-1">{{ errors.fullName }}</p>
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
          <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email }}</p>
        </div>
        <div class="relative">
          <label for="password" class="block font-medium mb-1">New Password</label>
          <div class="flex items-center gap-2">
            <input
              id="password"
              v-model="password"
              type="text"
              class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Generated password"
              readonly
            />
            <button
              type="button"
              @click="generatePassword"
              class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
            >
              Generate
            </button>
          </div>
          <p class="text-gray-500 text-sm mt-1">Leave blank if you don't want to change the password.</p>
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
          <p v-if="errors.startDate" class="text-red-500 text-sm mt-1">{{ errors.startDate }}</p>
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
          <p v-if="errors.timeToRender" class="text-red-500 text-sm mt-1">{{ errors.timeToRender }}</p>
        </div>
        <button
          type="submit"
          class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          Save Changes
        </button>
      </form>
    </div>

    <!-- Confirmation Modal -->
    <div 
      v-if="showConfirmationModal" 
      class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-[400px] relative">
        <button 
          @click="showConfirmationModal = false" 
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
        >
          &times;
        </button>
        <h2 class="text-xl font-bold mb-4">Confirm Submission</h2>
        <p>Make sure the new password is saved.</p>
        <div class="flex justify-end mt-4">
          <button 
            @click="showConfirmationModal = false" 
            class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition mr-2"
          >
            Cancel
          </button>
          <button 
            @click="confirmSubmit" 
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>