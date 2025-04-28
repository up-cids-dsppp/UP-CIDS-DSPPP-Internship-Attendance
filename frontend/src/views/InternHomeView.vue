<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import NavBar from '../components/NavBar.vue'
import { useTimeInOutStore } from '../stores/timeInOut'

const router = useRouter()
const timeInOutStore = useTimeInOutStore() // Use the Pinia store

// Intern details
const internDetails = ref({
  email: '',
  full_name: '',
  start_date: '',
  time_to_render: 0,
  time_rendered: 0,
  status: '',
  admin_remarks: '',
})

// Sort and filter states for attendance logs
const sortOption = ref('date-asc') // Default sort option
const selectedStatuses = ref(['validated', 'flagged', 'sent', 'ongoing']) // Default status filter
const selectedTypes = ref(['f2f', 'async']) // Default type filter

// Date and time
const currentDate = ref(new Date().toLocaleDateString())
const currentTime = ref(new Date().toLocaleTimeString())

// Update the clock every second
const updateClock = () => {
  currentTime.value = new Date().toLocaleTimeString()
}
setInterval(updateClock, 1000)

// Fetch intern details and attendance logs on component mount
onMounted(async () => {
  try {
    // Fetch intern profile with logs
    const profileResponse = await axios.get('/intern/profile') // Fetch from the combined endpoint
    const data = profileResponse.data

    // Set intern details
    internDetails.value = {
      email: data.email,
      full_name: data.full_name,
      start_date: data.start_date,
      time_to_render: data.time_to_render,
      time_rendered: data.time_rendered,
      status: data.status,
      admin_remarks: data.admin_remarks,
    }

    // Save the intern's status in the timeInOutStore
    timeInOutStore.setInternStatus(data.status)

    // Set attendance logs
    timeInOutStore.attendanceLogs = data.attendance_logs

    // Determine the most recent attendance
    if (timeInOutStore.attendanceLogs.length > 0) {
      const mostRecent = timeInOutStore.attendanceLogs[0]
      timeInOutStore.setMostRecentAttendance(mostRecent)

      if (mostRecent.status === 'ongoing') {
        const timedInLog = await axios.get(`/intern/attendance/${mostRecent.id}`)
        timeInOutStore.setTimedIn(true, mostRecent.id, mostRecent.type)
        timeInOutStore.setTimedOutForTheDay(false)
        if (timedInLog.data.type == 'async') {
          timeInOutStore.setTasksForTheDay(timedInLog.data.tasks.length)
        } else {
          timeInOutStore.setTasksForTheDay(timedInLog.data.tasks.length - 1)
        }
        timeInOutStore.setTimedInLog(timedInLog.data)
      } else {
        // Check if the intern has already timed out today
        const today = new Date().toISOString().split('T')[0] // Get today's date in YYYY-MM-DD format
        const timedOutToday = timeInOutStore.attendanceLogs.some(
          (log) => log.date === today && log.time_out
        )
        if (timedOutToday) {
          timeInOutStore.setTimedOutForTheDay(true)
        } else {
          timeInOutStore.setTimedOutForTheDay(false)
        }
        timeInOutStore.setTimedIn(false, null, null)
        timeInOutStore.setTasksForTheDay(0)
      }
    } else {
      // Reset the store if no attendance logs are found
      timeInOutStore.setTimedIn(false, null, null)
      timeInOutStore.setTasksForTheDay(0)
      timeInOutStore.setTimedOutForTheDay(false)
    }
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
})

// Computed property for filtered and sorted attendance logs
const filteredAndSortedLogs = computed(() => {
  // Filter by selected statuses and types
  let filtered = timeInOutStore.attendanceLogs.filter(
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

// Computed property to check if there are flagged tasks
const hasFlaggedTasks = computed(() => {
  return timeInOutStore.attendanceLogs.some((log) => log.status === 'flagged')
})

// Computed property to check if the intern has timed out today
const hasTimedOutAttendanceToday = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return timeInOutStore.attendanceLogs.some(
    (log) => log.date === today && log.time_out
  )
})

// Computed property to check if the intern can time in or out
const canTimeInOut = computed(() => {
  const now = new Date()
  const currentHour = now.getHours()
  const today = new Date().toISOString().split('T')[0]
  const hasSentAttendance = timeInOutStore.attendanceLogs.some(
    (log) => log.date === today && log.status === 'sent'
  )
  return currentHour >= 8 && currentHour < 17 && !hasSentAttendance
})

// Handle "Time In" button click
const handleTimeIn = async () => {
  router.push('/intern/in') // Redirect to the time-in page
}

// Redirect to the time-out page with the ongoing attendance log ID
const handleTimeOut = () => {
  const ongoingLogId = timeInOutStore.timedInLog.id // Get the ongoing attendance log ID

  if (timeInOutStore.mostRecentAttendance.type === 'f2f') {
    router.push(`/intern/out/${ongoingLogId}/f2f`) // Redirect to the f2f time-out page
    return
  } else if (timeInOutStore.mostRecentAttendance.type === 'async') {
    router.push(`/intern/out/${ongoingLogId}/async`) // Redirect to the async time-out page
    return
  }
}

// Handle "View" link click
const viewAttendanceLog = (logId) => {
  router.push(`/intern/attendance/${logId}`) // Redirect to the attendance log details page
}

</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="intern" :userEmail="internDetails.email" />

    <!-- Intern Content -->
    <div class="mt-8 px-6">
    <!-- Flagged Tasks Warning -->
    <div v-if="hasFlaggedTasks" class="text-red-500 font-bold mb-4">
      You have flagged tasks! Please email admin for re-evaluation.
    </div>
      <h2 class="text-xl font-bold">Welcome, {{ internDetails.full_name }}!</h2>
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

      <!-- Status Section -->
      <div
        v-if="internDetails.status === 'completed'"
        class="text-white p-4 mt-4 rounded-lg max-w-md bg-green-500"
      >
        <p class="text-lg font-semibold">Status: Completed</p>
        <p class="mt-2"><strong>Admin Remarks:</strong><br>{{ internDetails.admin_remarks || 'No remarks provided.' }}</p>
      </div>

      <div
        v-else-if="internDetails.status === 'dropped'"
        class="text-white p-4 mt-4 rounded-lg max-w-md bg-red-500"
      >
        <p class="text-lg font-semibold">Status: Dropped</p>
        <p class="mt-2"><strong>Admin Remarks:</strong><br>{{ internDetails.admin_remarks || 'No remarks provided.' }}</p>
        <p class="text-lg"><br>Please email admin for re-evaluation.</p>
      </div>

      <div
        :class="[
          'text-white p-4 mt-4 rounded-lg max-w-md',
          hasTimedOutAttendanceToday
            ? 'bg-gray-500'
            : canTimeInOut
            ? timeInOutStore.isTimedIn
              ? 'bg-red-500'
              : 'bg-green-500'
            : 'bg-gray-500'
        ]"
      >
        <p class="text-lg font-semibold">Today's Date: {{ currentDate }}</p>
        <p class="text-lg font-semibold">Current Time: {{ currentTime }}</p>
        <p v-if="timeInOutStore.isTimedIn" class="text-lg font-semibold mt-2">
          Tasks to accomplish: {{ timeInOutStore.tasksForTheDay }}
        </p>
        <div class="flex justify-end mt-4">
          <template v-if="internDetails.status !== 'completed' && internDetails.status !== 'dropped'">
            <template v-if="canTimeInOut">
              <button
                v-if="!timeInOutStore.isTimedIn"
                @click="handleTimeIn"
                class="bg-white text-green-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
              >
                Time In
              </button>
              <button
                v-else
                @click="handleTimeOut"
                class="bg-white text-red-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
              >
                Time Out
              </button>
            </template>
            <template v-else>
              <p class="text-lg font-semibold">Cannot Time In/Out</p>
            </template>
          </template>
          <template v-else>
            <p class="text-lg font-semibold">Time In/Out is disabled for your status.</p>
          </template>
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
            <th class="border border-gray-300 px-4 py-2">Status</th>
            <th class="border border-gray-300 px-4 py-2">Time In</th>
            <th class="border border-gray-300 px-4 py-2">Time Out</th>
            <th class="border border-gray-300 px-4 py-2">Work Duration (hours)</th>
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
            <td class="border border-gray-300 px-4 py-2">{{ log.status }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_in }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ log.time_out || 'N/A' }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ (log.work_duration || 0).toFixed(2) }}</td>
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