<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'

const isMobile = ref(false)

onMounted(() => {
  // Simple mobile detection
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  isMobile.value = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase())
})
</script>

<template>
  <div>
    <div v-if="isMobile" class="flex items-center justify-center min-h-screen bg-gray-100">
      <div class="bg-white p-8 rounded shadow text-center max-w-xs mx-auto">
        <h1 class="text-2xl font-bold mb-4 text-red-600">Notice</h1>
        <p class="text-black">Please use a laptop or computer to access the attendance module.</p>
      </div>
    </div>
    <div v-else>
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
</style>
