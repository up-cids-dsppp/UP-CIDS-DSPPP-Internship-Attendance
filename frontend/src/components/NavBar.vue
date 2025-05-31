<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  userType: {
    type: String,
    required: true,
  },
  userEmail: {
    type: String,
    required: true,
  },
})

const authStore = useAuthStore()
const showLogoutModal = ref(false)

const handleLogout = () => {
  showLogoutModal.value = true
}

const confirmLogout = () => {
  showLogoutModal.value = false
  authStore.logout()
}

const cancelLogout = () => {
  showLogoutModal.value = false
}

// Compute the navbar color based on the user type
const navbarColor = computed(() => {
  return props.userType === 'admin' ? 'bg-blue-500' : 'bg-green-500'
})
</script>

<template>
  <nav :class="`${navbarColor} w-full text-white px-6 py-4 flex justify-between items-center`">
    <h1 class="text-lg font-bold">
      Logged in with {{ userEmail }} as {{ userType === 'admin' ? 'Admin' : 'Intern' }}
    </h1>
    <button 
      @click="handleLogout" 
      class="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition"
    >
      Logout
    </button>

    <!-- Logout Confirmation Modal -->
    <div v-if="showLogoutModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div class="bg-white rounded-lg shadow-lg p-8 max-w-sm w-full">
        <h2 class="text-center text-lg font-bold mb-4 text-red-600">Confirm Logout</h2>
        <p class="mb-6 text-black">Are you sure you want to log out?</p>
        <div class="flex justify-end space-x-2">
          <button @click="cancelLogout" class="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">Cancel</button>
          <button @click="confirmLogout" class="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600">Logout</button>
        </div>
      </div>
    </div>
  </nav>
</template>