<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import {useRouter} from 'vue-router'

const tasks = reactive([]) // Task descriptions
const internEmail = ref('') // Intern email


// Initialize tasks array with one empty task
tasks.push({ description: '' })

const router = useRouter()

const goBack = () => {
  router.back() // Navigates to the previous page
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
    <h1 class="text-2xl font-bold mb-4">Time Out</h1>

  </div>
</template>