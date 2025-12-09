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
console.log('[HOME] Home.vue script setup starting...')

import { ref, onMounted, watch } from 'vue'
console.log('[HOME] Vue composables imported')

import { useRouter } from 'vue-router'
console.log('[HOME] Vue Router imported')

import api from '../services/api'
console.log('[HOME] API service imported')

import { useAuthStore } from '../stores/auth'
console.log('[HOME] Auth store imported')

console.log('[HOME] Initializing component state...')
const router = useRouter()
console.log('[HOME] Router instance obtained')

const authStore = useAuthStore()
console.log('[HOME] Auth store instance obtained:', { 
  isAuthenticated: authStore.isAuthenticated, 
  hasUser: !!authStore.user 
})

const loading = ref(true)
const error = ref(null)
const healthStatus = ref(null)
console.log('[HOME] Component state initialized')

// Watch auth state changes
watch(() => authStore.isAuthenticated, (isAuth) => {
  console.log('[HOME] Auth state changed:', { isAuthenticated: isAuth })
})

watch(() => authStore.user, (user) => {
  console.log('[HOME] User object changed:', { hasUser: !!user, userId: user?.id })
}, { deep: true })

const checkHealth = async () => {
  console.log('[HOME] checkHealth called')
  try {
    console.log('[HOME] Setting loading to true')
    loading.value = true
    error.value = null
    console.log('[HOME] Making health check API call...')
    const response = await api.get('/health')
    console.log('[HOME] Health check response received:', response.data)
    healthStatus.value = response.data
    console.log('[HOME] Health status set successfully')
  } catch (err) {
    console.error('[HOME] Health check error:', err)
    error.value = err.message || 'Failed to connect to backend'
    console.log('[HOME] Error set:', error.value)
  } finally {
    console.log('[HOME] Setting loading to false')
    loading.value = false
    console.log('[HOME] checkHealth completed')
  }
}

onMounted(async () => {
  console.log('[HOME] Home component mounted')
  console.log('[HOME] Starting onMounted operations...')
  
  console.log('[HOME] Calling checkHealth...')
  checkHealth()
  console.log('[HOME] checkHealth called (async)')
  
  // Fetch user if authenticated
  console.log('[HOME] Checking authentication status...')
  if (authStore.isAuthenticated) {
    console.log('[HOME] User is authenticated')
    console.log('[HOME] Checking if user data exists...')
    if (!authStore.user) {
      console.log('[HOME] User data not found, fetching user...')
      try {
        await authStore.fetchUser()
        console.log('[HOME] User fetch completed:', { hasUser: !!authStore.user })
      } catch (fetchError) {
        console.error('[HOME] Error fetching user:', fetchError)
      }
    } else {
      console.log('[HOME] User data already exists:', { userId: authStore.user.id, username: authStore.user.username })
    }
    
    // Redirect to default home page if user is authenticated
    console.log('[HOME] Checking default home page preference...')
    const defaultHome = authStore.user?.default_home_page || 'library'
    console.log('[HOME] Default home page:', defaultHome)
    
    if (defaultHome !== 'home') {
      console.log('[HOME] Default home is not "home", redirecting to:', `/${defaultHome}`)
      router.replace(`/${defaultHome}`)
      console.log('[HOME] Redirect initiated')
    } else {
      console.log('[HOME] Default home is "home", staying on home page')
    }
  } else {
    console.log('[HOME] User is not authenticated, staying on home page')
  }
  
  console.log('[HOME] onMounted completed')
})

console.log('[HOME] Home.vue script setup completed')
</script>

