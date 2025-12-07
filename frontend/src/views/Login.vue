<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">Log In</h2>
      <p class="auth-subtitle">Welcome back to CookBomPy.</p>
      
      <form @submit.prevent="handleLogin">
        <div v-if="error" class="error">
          {{ error }}
        </div>
        
        <div class="form-group">
          <label for="identifier">Email or Username *</label>
          <input
            id="identifier"
            v-model="formData.identifier"
            type="text"
            required
            placeholder="your@email.com or username"
            autocomplete="username"
            :disabled="loading"
          />
          <div class="field-hint">
            Enter your email address or username
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Password *</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            placeholder="Enter your password"
            autocomplete="current-password"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-weight: 400;">
            <input
              type="checkbox"
              v-model="formData.remember_me"
              :disabled="loading"
            />
            <span>Remember me</span>
          </label>
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading || !formData.identifier || !formData.password" style="width: 100%;">
          {{ loading ? 'Logging in...' : 'Log In' }}
        </button>
      </form>
      
      <p style="margin-top: 1.5rem; text-align: center; color: var(--color-text-light);">
        Don't have an account? <router-link to="/register">Create one</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  identifier: '',
  password: '',
  remember_me: false
})

const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null
  
  try {
    await authStore.login(formData.value.identifier, formData.value.password)
    
    // Redirect to home after successful login
    router.push('/')
  } catch (err) {
    console.error('Login error:', err)
    // Handle validation errors from FastAPI
    if (err.response?.data?.detail) {
      if (Array.isArray(err.response.data.detail)) {
        // Pydantic validation errors
        const errors = err.response.data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ')
        error.value = `Validation error: ${errors}`
      } else {
        // Single error message
        error.value = err.response.data.detail
      }
    } else {
      error.value = 'Login failed. Please check your credentials.'
    }
  } finally {
    loading.value = false
  }
}
</script>

