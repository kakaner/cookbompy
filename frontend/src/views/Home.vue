<template>
  <div class="container">
    <h2>Welcome to CookBomPy</h2>
    <p style="color: var(--color-text-light); font-size: 1.125rem;">
      A sophisticated book management and reading community platform.
    </p>
    
    <div v-if="!authStore.isAuthenticated" class="card" style="margin-top: 2rem;">
      <h3>Get Started</h3>
      <p>Please <router-link to="/login">log in</router-link> or <router-link to="/register">create an account</router-link> to start tracking your books.</p>
    </div>
    
    <div v-else class="card" style="margin-top: 2rem;">
      <h3>Welcome back, {{ authStore.user?.display_name || authStore.user?.username }}!</h3>
      <p>You're logged in and ready to start managing your library.</p>
      <p style="margin-top: 1rem;">
        <router-link to="/library" class="btn btn-primary" style="margin-right: 1rem;">Go to Library</router-link>
        <router-link to="/books/add" class="btn">Add Boko</router-link>
      </p>
    </div>
    
    <div class="card" style="margin-top: 2rem;">
      <h3>System Status</h3>
      <p>Testing backend connection...</p>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">
        Error: {{ error }}
      </div>
      <div v-else-if="healthStatus" class="success">
        Backend is healthy! Status: {{ healthStatus.status }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(true)
const error = ref(null)
const healthStatus = ref(null)

const checkHealth = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await api.get('/health')
    healthStatus.value = response.data
  } catch (err) {
    error.value = err.message || 'Failed to connect to backend'
    console.error('Health check error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkHealth()
  // Fetch user if authenticated
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser()
  }
})
</script>

