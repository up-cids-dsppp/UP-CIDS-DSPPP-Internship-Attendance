<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const route = useRoute()
const internId = route.params.id

// Admin details
const adminEmail = ref('')

// Intern details
const internDetails = ref({
  full_name: '',
  email: '',
  start_date: '',
  time_to_render: 0,
  time_rendered: 0,
  status: '',
})

// Attendance logs
const attendanceLogs = ref([])

// Sort and filter states for attendance logs
const sortOption = ref('date-asc') // Default sort option
const selectedStatuses = ref(['validated', 'flagged', 'sent', 'ongoing']) // Default status filter
const selectedTypes = ref(['f2f', 'async']) // Default type filter

// Modal states
const showEvaluationModal = ref(false)
const showEvaluationConfirmationModal = ref(false) // New confirmation modal state
const showUndropModal = ref(false)
const showDeleteModal = ref(false)
const evaluationType = ref('')
const evaluationRemarks = ref('')
const errors = ref({})
const previousStatus = ref('') // Store the previous status for "Undrop"

// Fetch admin and intern details along with attendance logs on component mount
onMounted(async () => {
  try {
    const adminResponse = await axios.get('/admin/profile')
    adminEmail.value = adminResponse.data.email

    const profileResponse = await axios.get(`/admin/interns/${internId}`)
    internDetails.value = {
      full_name: profileResponse.data.full_name,
      email: profileResponse.data.email,
      start_date: profileResponse.data.start_date,
      time_to_render: profileResponse.data.time_to_render,
      time_rendered: profileResponse.data.time_rendered,
      status: profileResponse.data.status,
    }

    attendanceLogs.value = profileResponse.data.attendance_logs
    previousStatus.value = profileResponse.data.previous_status || 'ongoing' // Default to "ongoing"
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Computed property for filtered and sorted attendance logs
const filteredAndSortedLogs = computed(() => {
  // Filter by selected statuses and types
  let filtered = attendanceLogs.value.filter(
    (log) =>
      selectedStatuses.value.includes(log.status) &&
      selectedTypes.value.includes(log.type)
  )

  // Sort based on the selected sort option
  if (sortOption.value === 'date-asc') {
    filtered.sort((a, b) => new Date(a.date) - new Date(b.date))
  } else if (sortOption.value === 'date-desc') {
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
  } else if (sortOption.value === 'duration-asc') {
    filtered.sort((a, b) => (a.work_duration || 0) - (b.work_duration || 0))
  } else if (sortOption.value === 'duration-desc') {
    filtered.sort((a, b) => (b.work_duration || 0) - (a.work_duration || 0))
  }

  return filtered
})

const viewAttendanceLog = (logId) => {
  router.push(`/admin/interns/${internId}/attendance/${logId}`)
}

// Handle "Evaluate Intern" form submission
const submitEvaluation = async () => {
  errors.value = {}

  // Check if the evaluation type is "completed" and the intern's status is not "passed"
  if (evaluationType.value === 'completed' && internDetails.value.status !== 'passed') {
    alert('A "completed" evaluation can only be submitted if the intern has a status of "passed".')
    return
  }

  // Validate inputs
  if (!evaluationType.value) {
    errors.value.type = 'Evaluation type is required.'
  }
  if (!evaluationRemarks.value.trim()) {
    errors.value.remarks = 'Remarks are required.'
  }

  if (Object.keys(errors.value).length > 0) {
    return
  }

  // Show confirmation modal
  showEvaluationConfirmationModal.value = true
}

const confirmEvaluation = async () => {
  try {
    const internId = route.params.id
    await axios.post(`/admin/interns/${internId}/evaluate`, {
      evaluation_type: evaluationType.value,
      admin_remarks: evaluationRemarks.value,
    })
    alert('Intern evaluated successfully!')
    showEvaluationModal.value = false
    showEvaluationConfirmationModal.value = false
    evaluationType.value = ''
    evaluationRemarks.value = ''
    location.reload()
  } catch (error) {
    console.error('Failed to evaluate intern:', error)
    alert('Failed to evaluate intern. Please try again.')
  }
}

// Handle "Undrop" action
const undropIntern = async () => {
  try {
    const internId = route.params.id
    await axios.post(`/admin/interns/${internId}/undrop`, {
      previous_status: previousStatus.value,
    })
    alert('Intern status updated successfully!')
    showUndropModal.value = false
    location.reload()
  } catch (error) {
    console.error('Failed to update intern status:', error)
    alert('Failed to update intern status. Please try again.')
  }
}

const deleteIntern = async () => {
  try {
    const internId = route.params.id
    await axios.delete(`/admin/interns/${internId}/`) // Ensure trailing slash
    alert('Intern deleted successfully!')
    router.push('/admin/home') // Redirect to the interns list page
  } catch (error) {
    console.error('Failed to delete intern:', error)
    alert('Failed to delete intern. Please try again.')
  }
}

const goBack = () => {
  router.push('/admin/home') // Redirect to the interns list page
}
</script>

<template>
  <div>
    <NavBar userType="admin" :userEmail="adminEmail" />
    <div class="mt-8 px-6">
      <p 
        @click="goBack" 
        class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
      >
        Go back
      </p>

      <!-- Conditional Buttons -->
      <div class="mb-6">
        <button 
          v-if="internDetails.status === 'ongoing' || internDetails.status === 'passed'" 
          @click="showEvaluationModal = true" 
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Evaluate Intern
        </button>
        <button 
          v-if="internDetails.status === 'dropped'" 
          @click="showUndropModal = true" 
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Undrop
        </button>
      </div>

      <!-- Delete Intern Button -->
      <div class="mb-6">
        <button 
          v-if="internDetails.status === 'dropped' || internDetails.status === 'completed'" 
          @click="showDeleteModal = true" 
          class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
        >
          Delete Intern
        </button>
      </div>

      <!-- Delete Confirmation Modal -->
      <div 
        v-if="showDeleteModal" 
        class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-lg p-6 w-[400px] relative">
          <button 
            @click="showDeleteModal = false" 
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
          <h2 class="text-xl font-bold mb-4">Confirm Delete</h2>
          <p>Are you sure you want to delete this intern? This action cannot be undone.</p>
          <div class="flex justify-end mt-6">
            <button 
              @click="showDeleteModal = false" 
              class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition mr-2"
            >
              No
            </button>
            <button 
              @click="deleteIntern" 
              class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
            >
              Yes
            </button>
          </div>
        </div>
      </div>

      <h2 class="text-xl font-bold">Intern Profile</h2>
      <p class="mt-2"><strong>Full Name:</strong> {{ internDetails.full_name }}</p>
      <p class="mt-2"><strong>Email:</strong> {{ internDetails.email }}</p>
      <p class="mt-2"><strong>Start Date:</strong> {{ internDetails.start_date }}</p>
      <p class="mt-2"><strong>Time to be Rendered:</strong> {{ internDetails.time_to_render.toFixed(2) }} hours</p>
      <p class="mt-2"><strong>Time Rendered:</strong> {{ internDetails.time_rendered.toFixed(2) }} hours</p>
      <p class="mt-2">
        <strong>Status: </strong> 
        <span 
          :class="{
            'text-green-500': internDetails.status === 'completed',
            'text-black': internDetails.status === 'ongoing',
            'text-red-500': internDetails.status === 'dropped',
            'text-orange-500': internDetails.status === 'passed',
          }"
        >
          {{ internDetails.status }}
        </span>
      </p>

      <!-- Evaluation Modal -->
      <div 
        v-if="showEvaluationModal" 
        class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-lg p-6 w-[600px] relative">
          <button 
            @click="showEvaluationModal = false" 
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
          <h2 class="text-xl font-bold mb-4">Evaluate Intern</h2>
          <div class="mb-4">
            <label for="evaluationType" class="block mb-2">Select Evaluation Type:</label>
            <select
              id="evaluationType"
              v-model="evaluationType"
              class="border rounded px-4 py-2 mb-4 w-full"
            >
              <option disabled value="">-- Select --</option>
              <option value="dropped">Drop</option>
              <option value="completed">Complete</option>
            </select>
            <p v-if="errors.type" class="text-red-500 text-sm mt-1">{{ errors.type }}</p>
          </div>
          <div class="mb-4">
            <label for="evaluationRemarks" class="block font-semibold mb-2">Remarks</label>
            <textarea 
              id="evaluationRemarks" 
              v-model="evaluationRemarks" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2"
              rows="6"
            ></textarea>
            <p v-if="errors.remarks" class="text-red-500 text-sm mt-1">{{ errors.remarks }}</p>
          </div>
          <div class="flex justify-end">
            <button 
              @click="submitEvaluation" 
              class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Submit
            </button>
          </div>
        </div>
      </div>

      <!-- Evaluation Confirmation Modal -->
      <div 
        v-if="showEvaluationConfirmationModal" 
        class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-lg p-6 w-[400px] relative">
          <button 
            @click="showEvaluationConfirmationModal = false" 
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
          <h2 class="text-xl font-bold mb-4">Confirm Evaluation</h2>
          <p>Are you sure you want to evaluate this intern with the following details?</p>
          <ul class="mt-4">
            <li><strong>Evaluation Type:</strong> {{ evaluationType }}</li>
            <li><strong>Remarks:</strong> {{ evaluationRemarks }}</li>
          </ul>
          <div class="flex justify-end mt-6">
            <button 
              @click="showEvaluationConfirmationModal = false" 
              class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition mr-2"
            >
              No
            </button>
            <button 
              @click="confirmEvaluation" 
              class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Yes
            </button>
          </div>
        </div>
      </div>

      <!-- Undrop Confirmation Modal -->
      <div 
        v-if="showUndropModal" 
        class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-lg p-6 w-[400px] relative">
          <button 
            @click="showUndropModal = false" 
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
          <h2 class="text-xl font-bold mb-4">Confirm Undrop</h2>
          <p>Are you sure you want to restore the intern's status to "{{ previousStatus }}"?</p>
          <div class="flex justify-end mt-6">
            <button 
              @click="showUndropModal = false" 
              class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition mr-2"
            >
              No
            </button>
            <button 
              @click="undropIntern" 
              class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
            >
              Yes
            </button>
          </div>
        </div>
      </div>

      <!-- Attendance Logs Section -->
      <h2 class="text-xl font-bold mt-8">Attendance Logs</h2>

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
            <option value="date-asc">Date (Earliest-Latest)</option>
            <option value="date-desc">Date (Latest-Earliest)</option>
            <option value="duration-asc">Work Duration (Shortest-Longest)</option>
            <option value="duration-desc">Work Duration (Longest-Shortest)</option>
          </select>
        </div>

        <!-- Filter Checkboxes -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Filter By Status:</label>
          <div class="mt-1 space-y-1">
            <div v-for="status in ['validated', 'flagged', 'sent', 'ongoing']" :key="status">
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

        <div>
          <label class="block text-sm font-medium text-gray-700">Filter By Type:</label>
          <div class="mt-1 space-y-1">
            <div v-for="type in ['f2f', 'async']" :key="type">
              <label class="inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="selectedTypes" 
                  :value="type" 
                  class="form-checkbox text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span class="ml-2 capitalize">{{ type }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Attendance Logs Table -->
      <div v-if="filteredAndSortedLogs.length === 0" class="text-gray-500 mt-4 mb-20 text-center">
        No attendance logs match the selected criteria.
      </div>
      <table v-else class="table-auto w-full mt-4 mb-20 border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-200">
            <th class="border border-gray-300 px-4 py-2">Date</th>
            <th class="border border-gray-300 px-4 py-2">Type</th>
            <th class="border border-gray-300 px-4 py-2">Time In</th>
            <th class="border border-gray-300 px-4 py-2">Time Out</th>
            <th class="border border-gray-300 px-4 py-2">Work Duration (hours)</th>
            <th class="border border-gray-300 px-4 py-2">Status</th>
            <th class="border border-gray-300 px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="log in filteredAndSortedLogs"
            :key="log.id"
            :class="{
              'bg-green-100': log.status === 'validated',
              'bg-red-100': log.status === 'flagged',
              'bg-orange-100': log.status === 'sent',
              '': log.status === 'ongoing',
            }"
            class="text-center"
          >
            <td class="border border-gray-300 px-4 py-2">{{ log.date }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.type }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_in }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_out || 'N/A' }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ (log.work_duration || 0).toFixed(2) }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.status }}</td>
            <td class="border border-gray-300 px-4 py-2">
              <button 
                @click="viewAttendanceLog(log.id)" 
                class="text-blue-500 hover:underline"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>