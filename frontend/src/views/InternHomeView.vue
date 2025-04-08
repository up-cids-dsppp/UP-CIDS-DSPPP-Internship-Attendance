<script setup>
import NavBar from '../components/NavBar.vue'
import { ref } from 'vue'

const internEmail = ref('intern@example.com') // Replace with actual email fetching logic
</script>

<template>
  <div>
    <!-- Navbar Component -->
    <NavBar userType="intern" :userEmail="internEmail" />

    <!-- Intern Content -->
    <div class="mt-8 px-6">
      <h2 class="text-xl font-bold">Welcome, Intern!</h2>
      <p class="text-gray-700">This is your dashboard.</p>
    </div>
  </div>
</template>