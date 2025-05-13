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
  <div class="flex flex-col md:flex-row h-screen w-full">
    <!-- Left Drawer -->
    <div class="w-full md:w-1/5 bg-[#4a4a4a] text-white flex flex-col items-center justify-between p-4">
      <!-- Header  Section -->
      <div class="text-center text-sm mt-4 md:mt-0">
        <p>Property of UP CIDS - DSPPP</p>
      </div>

      <!-- Logos Section -->
      <div class="flex flex-col items-center space-y-6">
        <img 
          src="@/assets/University_of_The_Philippines_seal (2).svg" 
          alt="UP Logo" 
          class="w-auto max-w-[70%] h-auto"
        />
        <img 
          src="@/assets/UP CIDS Logo - clearer white.png" 
          alt="UP CIDS Logo" 
          class="w-auto max-w-[90%] h-auto"
        />
        <img 
          src="@/assets/DSPP 2021.png" 
          alt="DSPP Logo" 
          class="w-auto max-w-[70%] h-auto"
        />
      </div>

      <!-- Footer Section -->
      <div class="text-center text-sm mt-4 md:mt-0">
        <p>Conceptualized by Lilian Jimenez-Marfil</p>
        <p>Developed by Gabriel Catadman Ramos</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex flex-col items-center justify-center flex-grow text-center p-4">
      <h1 class="text-4xl md:text-5xl font-bold mb-6 md:mb-8">UP-CIDS-DSPPP</h1>
      <h1 class="text-2xl md:text-3xl font-bold mb-6 md:mb-8">Internship Attendance</h1>
      <div class="flex gap-4">
        <button 
          @click="navigateToIntern" 
          class="px-4 py-2 md:px-6 md:py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
        >
          Login as Intern
        </button>
        <button 
          @click="navigateToAdmin" 
          class="px-4 py-2 md:px-6 md:py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          Login as Admin
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Ensure the drawer and images are responsive */
img {
  height: auto;
  display: block;
}
</style>
