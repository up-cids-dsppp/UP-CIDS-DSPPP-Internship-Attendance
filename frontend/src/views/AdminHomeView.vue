<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const interns = ref([])
const adminEmail = ref('') // Store the admin's email
const sortOption = ref('name-asc') // Default sort option
const selectedStatuses = ref(['ongoing', 'dropped', 'completed', 'passed']) // Default filter

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
  if (status === 'passed') return 'bg-green-100'
  if (status === 'dropped') return 'bg-red-100'
  if (status === 'completed') return 'bg-orange-100'
  return '' // Default for ongoing (clear)
}

// Computed property for filtered and sorted interns
const filteredAndSortedInterns = computed(() => {
  // Filter by selected statuses
  let filtered = interns.value.filter((intern) =>
    selectedStatuses.value.includes(intern.status)
  )

  // Sort based on the selected sort option
  if (sortOption.value === 'name-asc') {
    filtered.sort((a, b) => a.full_name.localeCompare(b.full_name))
  } else if (sortOption.value === 'name-desc') {
    filtered.sort((a, b) => b.full_name.localeCompare(a.full_name))
  } else if (sortOption.value === 'startdate-asc') {
    filtered.sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
  } else if (sortOption.value === 'startdate-desc') {
    filtered.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
  }

  return filtered
})

// Export interns to CSV
const exportInternsToCSV = async () => {
  try {
    const response = await axios.get('/admin/export/interns', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'interns.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to export interns:', error)
  }
}

// Export attendance to CSV
const exportAttendanceToCSV = async () => {
  try {
    const response = await axios.get('/admin/export/attendance', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'attendance.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to export attendance:', error)
  }
}
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="admin" :userEmail="adminEmail" />

    <!-- Interns Section -->
    <div class="mt-8 px-6">
      <div class="flex mb-6 items-center space-x-4">
        <!-- Add Intern Button -->
        <button 
          @click="goToAddIntern" 
          class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition"
        >
          Add new intern
        </button>

        <!-- Export Interns to CSV Button -->
        <button 
          @click="exportInternsToCSV" 
          class="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition"
        >
          Export Interns to CSV
        </button>

        <!-- Export Attendance to CSV Button -->
        <button 
          @click="exportAttendanceToCSV" 
          class="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition"
        >
          Export Attendance to CSV
        </button>
      </div>

      <h2 class="text-xl font-bold mb-4">Interns</h2>

      <!-- Sort and Filter Section -->
      <div class="mb-6 space-y-4">
        <!-- Sort Dropdown -->
        <div>
          <label for="sort" class="block text-sm font-medium text-gray-700">Sort By:</label>
          <select 
            id="sort" 
            v-model="sortOption" 
            class="mt-1 block w-64 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="startdate-asc">Start Date (Earliest-Latest)</option>
            <option value="startdate-desc">Start Date (Latest-Earliest)</option>
          </select>
        </div>

        <!-- Filter Checkboxes -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Filter By Status:</label>
          <div class="mt-1 space-y-1">
            <div v-for="status in ['ongoing', 'dropped', 'completed', 'passed']" :key="status">
              <label class="inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="selectedStatuses" 
                  :value="status" 
                  class="form-checkbox text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span class="ml-2 capitalize">{{ status }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Interns Table -->
      <div v-if="filteredAndSortedInterns.length === 0" class="text-gray-500 text-center">
        No interns match the selected criteria.
      </div>
      <table v-else class="w-full border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-100">
            <th class="border border-gray-300 px-4 py-2 text-left">Full Name</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Email</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Status</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Start Date</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="intern in filteredAndSortedInterns" 
            :key="intern.id" 
            :class="getRowClass(intern.status)"
          >
            <td class="border border-gray-300 px-4 py-2">{{ intern.full_name }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ intern.email }}</td>
            <td class="border border-gray-300 px-4 py-2 capitalize">{{ intern.status }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ intern.start_date }}</td>
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