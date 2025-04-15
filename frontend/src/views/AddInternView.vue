<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
const authStore = useAuthStore() // Access the auth store

// Form fields for the intern
const fullName = ref('')
const email = ref('')
const password = ref('')
const startDate = ref(getCurrentDate()) // Initialize with today's date
const timeToRender = ref('')

// Store the admin's email
const adminEmail = ref('')

// Fetch the admin's email and generate a password when the component is mounted
onMounted(async () => {
  try {
    const response = await axios.get('/admin/profile') // Adjust endpoint if necessary
    adminEmail.value = response.data.email
  } catch (error) {
    console.error('Failed to fetch admin email:', error)
  }

  // Generate a password on mount
  generatePassword();
})

const errors = ref({}); // Store validation errors

// Submit the form
const handleSubmit = async () => {
  errors.value = {}; // Reset errors

  // Validate inputs
  if (!fullName.value.trim()) {
    errors.value.fullName = 'Full name is required.';
  }
  if (!email.value.trim()) {
    errors.value.email = 'Email is required.';
  }
  if (!password.value.trim()) {
    errors.value.password = 'Password is required.';
  }
  if (!startDate.value.trim()) {
    errors.value.startDate = 'Start date is required.';
  }
  if (!timeToRender.value || timeToRender.value <= 0) {
    errors.value.timeToRender = 'Time to render must be greater than 0.';
  }

  // Check if there are any validation errors
  if (Object.keys(errors.value).length > 0) {
    return; // Stop submission if there are errors
  }

  // Show the confirmation modal if all fields are valid
  showConfirmationModal.value = true;
};

const confirmSubmit = async () => {
  try {
    await axios.post('/admin/interns', {
      full_name: fullName.value,
      email: email.value,
      password: password.value,
      start_date: startDate.value,
      time_to_render: timeToRender.value,
    });
    showConfirmationModal.value = false; // Close the modal
    alert('Intern added successfully!'); // Success alert
    router.push('/admin/home'); // Redirect to admin home page
  } catch (error) {
    console.error('Failed to add intern:', error);
    showConfirmationModal.value = false; // Close the modal
    alert('Failed to add intern. Please try again.'); // Error alert
  }
};

// Add a loading state
const isGeneratingPassword = ref(false)

const generatePassword = async () => {
  isGeneratingPassword.value = true // Set loading state
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
  let newPassword = ''
  let isUnique = false

  try {
    while (!isUnique) {
      // Generate a random password
      newPassword = ''
      for (let i = 0; i < 8; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length)
        newPassword += characters[randomIndex]
      }

      // Hash the generated password
      const hashedPassword = await hashPassword(newPassword)

      // Check if the hashed password already exists in the database
      isUnique = await checkPasswordUniqueness(hashedPassword)
    }

    password.value = newPassword // Set the unique password
  } catch (error) {
    console.error('Error generating password:', error)
    alert('Failed to generate password. Please try again.')
  } finally {
    isGeneratingPassword.value = false // Reset loading state
  }
}

// Hash the password using the same algorithm as the backend
const hashPassword = async (plainPassword) => {
  try {
    const response = await axios.post('/admin/hash-password', { password: plainPassword })
    return response.data.hashed_password
  } catch (error) {
    console.error('Failed to hash password:', error)
    return null
  }
}

// Check if the hashed password is unique
const checkPasswordUniqueness = async (hashedPassword) => {
  try {
    const response = await axios.post('/admin/check-password-uniqueness', { hashed_password: hashedPassword })
    return response.data.is_unique
  } catch (error) {
    console.error('Failed to check password uniqueness:', error)
    return false
  }
}

// Navigate back to the appropriate page based on user type
const goBack = () => {
  router.push('/admin/home') // Redirect to admin home page
}

const showConfirmationModal = ref(false); // Control confirmation modal visibility
</script>

<template>
  <div>
    <!-- Navbar -->
    <NavBar userType="admin" :userEmail="adminEmail" />

    <!-- Add Intern Form -->
    <p 
      @click="goBack" 
      class="mt-4 ml-6 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
    <div class="max-w-lg mx-auto mt-4 mb-10 p-6 bg-white shadow-md rounded-lg">
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
          <label for="password" class="block font-medium mb-1">Password</label>
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
              :disabled="isGeneratingPassword"
              class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isGeneratingPassword">Generating...</span>
              <span v-else>Generate</span>
            </button>
          </div>
          <p class="text-gray-500 text-sm mt-1">Please record/save this password in an external file.</p>
          <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password }}</p>
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
          type="button"
          @click="handleSubmit"
          class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          Add Intern
        </button>
      </form>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div 
    v-if="showConfirmationModal" 
    class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg p-6 w-[400px] relative">
      <h2 class="text-xl font-bold mb-4">Confirm Submission</h2>
      <p>Are you sure you want to add this intern?</p>
      <p class="text-gray-700 mt-2">
        Make sure the password: <strong>{{ password }}</strong> is saved in a separate document.
      </p>
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
</template>