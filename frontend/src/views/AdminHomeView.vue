<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const interns = ref([])
const adminEmail = ref('') // Store the admin's email

// Fetch interns and admin email when the component is mounted
onMounted(async () => {
  try {
    const response = await axios.get('/admin/interns') // Adjust endpoint if necessary
    interns.value = response.data

    // Fetch admin email (adjust endpoint if necessary)
    const adminResponse = await axios.get('/admin/profile')
    adminEmail.value = adminResponse.data.email
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Navigate to add intern page
const goToAddIntern = () => {
  router.push('/admin/add_intern')
}

// Get row color based on intern status
const getRowClass = (status) => {
  if (status === 'completed') return 'bg-green-100'
  if (status === 'dropped') return 'bg-red-100'
  if (status === 'passed') return 'bg-orange-100'
  return '' // Default for ongoing (clear)
}
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="admin" :userEmail="adminEmail" />

    <!-- Interns Section -->
    <div class="mt-8 px-6">
      <div class="flex mb-6">
        <button 
          @click="goToAddIntern" 
          class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition"
        >
          Add new intern
        </button>
      </div>
      <h2 class="text-xl font-bold mb-4">Interns</h2>
      <div v-if="interns.length === 0" class="text-gray-500 text-center">
        No interns registered.
      </div>
      <table v-else class="w-full border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-100">
            <th class="border border-gray-300 px-4 py-2 text-left">Full Name</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Email</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Status</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="intern in interns" 
            :key="intern.id" 
            :class="getRowClass(intern.status)"
          >
            <td class="border border-gray-300 px-4 py-2">{{ intern.full_name }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ intern.email }}</td>
            <td class="border border-gray-300 px-4 py-2 capitalize">{{ intern.status }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <a 
                :href="`/admin/interns/${intern.id}`" 
                class="text-blue-500 underline hover:text-blue-700"
              >
                View
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>