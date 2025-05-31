<script setup>
import { computed } from 'vue'

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

// Emit logout event to parent
const emit = defineEmits(['logout'])
const handleLogout = () => {
  emit('logout')
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
  </nav>
</template>