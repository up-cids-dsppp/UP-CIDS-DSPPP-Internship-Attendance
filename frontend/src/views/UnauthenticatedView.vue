<template>
  <div class="flex flex-col items-center justify-center h-screen w-full text-center bg-gray-100">
    <h1 class="text-3xl font-bold text-red-500 mb-6">Unauthorized Access</h1>
    <p class="text-lg text-gray-700 mb-4">
      You do not have permission to view this page.
    </p>
    <router-link 
      to="/" 
      class="text-blue-500 underline hover:text-blue-700 text-lg"
    >
      Go back
    </router-link>
  </div>
</template>

<script setup>
// No additional logic is needed for this simple view
</script>