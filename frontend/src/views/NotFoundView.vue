<!-- filepath: /Users/gabrielramos/Desktop/UP-CIDS-DSPP-Internship-Attendance/frontend/src/views/404View.vue -->
<template>
  <div class="flex flex-col items-center justify-center h-screen w-full text-center">
    <h1 class="text-4xl font-bold text-red-500 mb-6">404 - Page Not Found</h1>
    <p class="text-gray-700 mb-6">
      The page you are looking for does not exist or has been moved.
    </p>
    <p 
      @click="goBack" 
      class="mb-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back() // Navigates to the previous page
}
</script>