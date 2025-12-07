<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 class="auth-title">Create Account</h2>
      <p class="auth-subtitle">Join CookBomPy to start tracking your reading journey.</p>
      
      <form @submit.prevent="handleRegister">
        <div v-if="error" class="error">
          {{ error }}
        </div>
        
        <div class="form-group">
          <label for="email">Email *</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            placeholder="your@email.com"
            autocomplete="email"
            :disabled="loading"
            @blur="validateEmail"
          />
          <div v-if="emailError" class="field-hint warning">
            {{ emailError }}
          </div>
        </div>
        
        <div class="form-group">
          <label for="username">Username *</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            required
            minlength="3"
            maxlength="30"
            placeholder="3-30 characters, letters, numbers, _, -"
            autocomplete="username"
            :disabled="loading"
            @blur="validateUsername"
          />
          <div v-if="usernameError" class="field-hint warning">
            {{ usernameError }}
          </div>
          <div v-else class="field-hint">
            Alphanumeric, underscores, and hyphens only
          </div>
        </div>
        
        <div class="form-group">
          <label for="display_name">Display Name (optional)</label>
          <input
            id="display_name"
            v-model="formData.display_name"
            type="text"
            maxlength="100"
            placeholder="How you want to be displayed"
            :disabled="loading"
          />
          <div class="field-hint">
            If not provided, your username will be used
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Password *</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            minlength="8"
            placeholder="At least 8 characters"
            autocomplete="new-password"
            :disabled="loading"
            @input="checkPasswordStrength"
          />
          <div v-if="passwordStrength" class="password-strength">
            <div :class="['password-strength-bar', passwordStrengthClass]"></div>
          </div>
          <div class="field-hint">
            Must include uppercase, lowercase, and number
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirm_password">Confirm Password *</label>
          <input
            id="confirm_password"
            v-model="formData.confirm_password"
            type="password"
            required
            placeholder="Re-enter your password"
            autocomplete="new-password"
            :disabled="loading"
          />
          <div v-if="formData.password && formData.confirm_password && formData.password !== formData.confirm_password" class="field-hint warning">
            Passwords do not match
          </div>
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading || !isFormValid" style="width: 100%;">
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>
      
      <p style="margin-top: 1.5rem; text-align: center; color: var(--color-text-light);">
        Already have an account? <router-link to="/login">Log in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  username: '',
  display_name: '',
  password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref(null)
const emailError = ref(null)
const usernameError = ref(null)
const passwordStrength = ref(null)

const passwordStrengthClass = computed(() => {
  if (!passwordStrength.value) return ''
  if (passwordStrength.value === 'weak') return 'password-strength-weak'
  if (passwordStrength.value === 'medium') return 'password-strength-medium'
  return 'password-strength-strong'
})

const validateEmail = () => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (formData.value.email && !emailRegex.test(formData.value.email)) {
    emailError.value = 'Please enter a valid email address'
  } else {
    emailError.value = null
  }
}

const validateUsername = () => {
  const username = formData.value.username
  if (!username) {
    usernameError.value = null
    return
  }
  
  if (username.length < 3 || username.length > 30) {
    usernameError.value = 'Username must be between 3 and 30 characters'
  } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    usernameError.value = 'Username can only contain letters, numbers, underscores, and hyphens'
  } else {
    usernameError.value = null
  }
}

const checkPasswordStrength = () => {
  const password = formData.value.password
  if (!password) {
    passwordStrength.value = null
    return
  }
  
  const hasUpper = /[A-Z]/.test(password)
  const hasLower = /[a-z]/.test(password)
  const hasNumber = /[0-9]/.test(password)
  const hasMinLength = password.length >= 8
  
  const strengthCount = [hasUpper, hasLower, hasNumber, hasMinLength].filter(Boolean).length
  
  if (strengthCount <= 2) {
    passwordStrength.value = 'weak'
  } else if (strengthCount === 3) {
    passwordStrength.value = 'medium'
  } else {
    passwordStrength.value = 'strong'
  }
}

const isFormValid = computed(() => {
  return (
    formData.value.email &&
    !emailError.value &&
    formData.value.username &&
    formData.value.username.length >= 3 &&
    formData.value.username.length <= 30 &&
    !usernameError.value &&
    formData.value.password &&
    formData.value.password.length >= 8 &&
    formData.value.password === formData.value.confirm_password &&
    /[A-Z]/.test(formData.value.password) &&
    /[a-z]/.test(formData.value.password) &&
    /[0-9]/.test(formData.value.password)
  )
})

const handleRegister = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields correctly'
    return
  }
  
  // Double-check that required fields are not empty
  if (!formData.value.email?.trim() || !formData.value.username?.trim() || !formData.value.password) {
    error.value = 'Please fill in all required fields'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    await authStore.register({
      email: formData.value.email.trim(),
      username: formData.value.username.trim(),
      display_name: formData.value.display_name?.trim() || null,
      password: formData.value.password
    })
    
    // Redirect to home after successful registration and login
    router.push('/')
  } catch (err) {
    console.error('Registration error:', err)
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
      error.value = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

