<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToAdmin = () => {
  router.push('/admin/login') // Replace '/admin' with the actual admin route
}

const navigateToIntern = () => {
  router.push('/intern/login') // Replace '/intern' with the actual intern route
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen w-full text-center">
    <h1 class="text-3xl font-bold mb-8">UP-CIDS-DSPPP Internship Attendance</h1>
    <div class="flex gap-4">
      <button 
        @click="navigateToIntern" 
        class="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
      >
        Login as Intern
      </button>
      <button 
        @click="navigateToAdmin" 
        class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
      >
        Login as Admin
      </button>
    </div>
  </div>
</template>
