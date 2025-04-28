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
  <div class="flex h-screen w-full">
    <!-- Main Content -->
    <div class="flex flex-col items-center justify-center flex-grow text-center">
      <h1 class="text-5xl font-bold mb-8">UP-CIDS-DSPPP</h1>
      <h1 class="text-3xl font-bold mb-8">Internship Attendance</h1>
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

    <!-- Right Drawer -->
    <div class="w-1/5 bg-[#4a4a4a] text-white flex flex-col items-center justify-between p-4">
      <!-- Logos Section -->
      <div class="flex flex-col items-center">
        <img src="@/assets/University_of_The_Philippines_seal (2).svg" alt="UP Logo" class="h-50 mt-15 mb-15" />
        <img src="@/assets/UP CIDS Logo - clearer white.png" alt="UP Logo" class="h-24 mt-15 mb-15" />
        <img src="@/assets/DSPP 2021.png" alt="UP Logo" class="h-50 mt-15 mb-15" />

        <!-- Add more logos here if needed -->
      </div>

      <!-- Footer Section -->
      <div class="text-center text-sm mb-8">
        <p>Conceptualized by Lilian Jimenez-Marfil</p>
        <p>Developed by Gabriel Catadman Ramos</p>
      </div>
    </div>
  </div>
</template>
