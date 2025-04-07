<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const router = useRouter()

const goBack = () => {
  router.back() // Navigates to the previous page
}
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen w-full text-center">
    <h1 class="text-2xl font-bold mb-6">Admin Login</h1>
    <form class="flex flex-col gap-4 w-80">
      <div>
        <label for="email" class="block text-left font-medium mb-1">Email</label>
        <input 
          id="email" 
          type="email" 
          v-model="email" 
          class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your email"
        />
      </div>
      <div>
        <label for="password" class="block text-left font-medium mb-1">Password</label>
        <div class="relative">
          <input 
            id="password" 
            :type="showPassword ? 'text' : 'password'" 
            v-model="password" 
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
          />
          <button 
            type="button" 
            @click="showPassword = !showPassword" 
            class="absolute inset-y-0 right-3 flex items-center text-sm text-gray-500"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
      </div>
      <button 
        type="button" 
        class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
      >
        Login
      </button>
    </form>
    <p 
      @click="goBack" 
      class="mt-4 text-gray-500 underline cursor-pointer hover:text-gray-700"
    >
      Go back
    </p>
  </div>
</template>