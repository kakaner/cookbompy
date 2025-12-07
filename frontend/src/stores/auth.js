import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { applyTheme } from '../utils/themes'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  // Set up axios interceptor for auth header on initialization
  if (accessToken.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  const login = async (identifier, password) => {
    // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    // Use URLSearchParams to create the form data
    const params = new URLSearchParams()
    params.append('username', identifier)  // Can be email or username
    params.append('password', password)
    
    // Send with proper Content-Type for form data
    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    
    // Store tokens
    localStorage.setItem('access_token', accessToken.value)
    localStorage.setItem('refresh_token', refreshToken.value)
    
    // Set auth header
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
    
    // Fetch user info
    await fetchUser()
    return response.data
  }

  const register = async (userData) => {
    // Clean the data - remove undefined values and ensure all required fields are present
    const cleanData = {
      email: userData.email,
      username: userData.username,
      password: userData.password
    }
    
    // Only include display_name if it's provided and not empty
    if (userData.display_name && userData.display_name.trim()) {
      cleanData.display_name = userData.display_name.trim()
    }
    
    // Log the data being sent for debugging
    console.log('Registering with data:', cleanData)
    
    // Send as JSON
    const response = await api.post('/auth/register', cleanData)
    
    // After registration, automatically log in
    // Use the identifier (email) that was registered
    try {
      await login(userData.email, userData.password)
    } catch (loginError) {
      // If auto-login fails, throw the original registration response
      // but log the login error for debugging
      console.error('Auto-login after registration failed:', loginError)
      // Still return the registration response - user can log in manually
    }
    
    return response.data
  }

  const fetchUser = async () => {
    try {
      // Fetch user profile and preferences from the users endpoint
      const response = await api.get('/users/me')
      user.value = response.data
      
      // Apply user's color theme if set
      if (user.value?.color_theme) {
        applyTheme(user.value.color_theme)
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
  }

  // Initialize user if token exists
  if (accessToken.value) {
    fetchUser()
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    login,
    register,
    fetchUser,
    logout
  }
})

