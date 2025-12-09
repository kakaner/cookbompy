console.log('[AUTH-STORE] Auth store module loading...')

import { defineStore } from 'pinia'
console.log('[AUTH-STORE] Pinia imported')

import { ref, computed } from 'vue'
console.log('[AUTH-STORE] Vue composables imported')

import api from '../services/api'
console.log('[AUTH-STORE] API service imported')

import { applyTheme } from '../utils/themes'
console.log('[AUTH-STORE] Theme utilities imported')

console.log('[AUTH-STORE] Creating auth store...')
export const useAuthStore = defineStore('auth', () => {
  console.log('[AUTH-STORE] Store function executing...')
  
  console.log('[AUTH-STORE] Reading tokens from localStorage...')
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  console.log('[AUTH-STORE] Tokens read:', { hasAccessToken: !!accessToken.value, hasRefreshToken: !!refreshToken.value })
  
  const user = ref(null)
  console.log('[AUTH-STORE] User ref initialized')

  const isAuthenticated = computed(() => {
    const result = !!accessToken.value
    console.log('[AUTH-STORE] isAuthenticated computed:', result)
    return result
  })
  console.log('[AUTH-STORE] isAuthenticated computed created')

  // Set up axios interceptor for auth header on initialization
  console.log('[AUTH-STORE] Setting up axios interceptor...')
  if (accessToken.value) {
    console.log('[AUTH-STORE] Access token found, setting Authorization header')
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
    console.log('[AUTH-STORE] Authorization header set')
  } else {
    console.log('[AUTH-STORE] No access token found, skipping Authorization header')
  }

  const login = async (identifier, password) => {
    console.log('[AUTH-STORE] login called:', { identifier: identifier ? '***' : null, hasPassword: !!password })
    // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    // Use URLSearchParams to create the form data
    console.log('[AUTH-STORE] Creating login params...')
    const params = new URLSearchParams()
    params.append('username', identifier)  // Can be email or username
    params.append('password', password)
    console.log('[AUTH-STORE] Login params created')
    
    // Send with proper Content-Type for form data
    console.log('[AUTH-STORE] Sending login request...')
    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    console.log('[AUTH-STORE] Login response received:', { hasAccessToken: !!response.data.access_token, hasRefreshToken: !!response.data.refresh_token })
    
    console.log('[AUTH-STORE] Setting tokens...')
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    console.log('[AUTH-STORE] Tokens set in store')
    
    // Store tokens
    console.log('[AUTH-STORE] Storing tokens in localStorage...')
    localStorage.setItem('access_token', accessToken.value)
    localStorage.setItem('refresh_token', refreshToken.value)
    console.log('[AUTH-STORE] Tokens stored in localStorage')
    
    // Set auth header
    console.log('[AUTH-STORE] Setting Authorization header...')
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
    console.log('[AUTH-STORE] Authorization header set')
    
    // Fetch user info
    console.log('[AUTH-STORE] Fetching user info...')
    await fetchUser()
    console.log('[AUTH-STORE] User info fetched')
    console.log('[AUTH-STORE] Login completed successfully')
    return response.data
  }

  const register = async (userData) => {
    console.log('[AUTH-STORE] register called:', { email: userData.email, username: userData.username, hasPassword: !!userData.password })
    
    // Clean the data - remove undefined values and ensure all required fields are present
    console.log('[AUTH-STORE] Cleaning registration data...')
    const cleanData = {
      email: userData.email,
      username: userData.username,
      password: userData.password
    }
    
    // Only include display_name if it's provided and not empty
    if (userData.display_name && userData.display_name.trim()) {
      cleanData.display_name = userData.display_name.trim()
      console.log('[AUTH-STORE] Display name included:', cleanData.display_name)
    } else {
      console.log('[AUTH-STORE] No display name provided')
    }
    
    // Log the data being sent for debugging
    console.log('[AUTH-STORE] Registering with data:', cleanData)
    
    // Send as JSON
    console.log('[AUTH-STORE] Sending registration request...')
    const response = await api.post('/auth/register', cleanData)
    console.log('[AUTH-STORE] Registration response received')
    
    // After registration, automatically log in
    // Use the identifier (email) that was registered
    console.log('[AUTH-STORE] Attempting auto-login after registration...')
    try {
      await login(userData.email, userData.password)
      console.log('[AUTH-STORE] Auto-login successful')
    } catch (loginError) {
      // If auto-login fails, throw the original registration response
      // but log the login error for debugging
      console.error('[AUTH-STORE] Auto-login after registration failed:', loginError)
      // Still return the registration response - user can log in manually
    }
    
    console.log('[AUTH-STORE] Registration completed')
    return response.data
  }

  const fetchUser = async () => {
    console.log('[AUTH-STORE] fetchUser called')
    try {
      // Fetch user profile and preferences from the users endpoint
      console.log('[AUTH-STORE] Fetching user from /users/me...')
      const response = await api.get('/users/me')
      console.log('[AUTH-STORE] User response received:', { userId: response.data?.id, username: response.data?.username })
      
      console.log('[AUTH-STORE] Setting user value...')
      user.value = response.data
      console.log('[AUTH-STORE] User value set:', { userId: user.value?.id, username: user.value?.username })
      
      // Apply user's color theme if set
      if (user.value?.color_theme) {
        console.log('[AUTH-STORE] Applying user theme:', user.value.color_theme)
        applyTheme(user.value.color_theme)
        console.log('[AUTH-STORE] User theme applied')
      } else {
        console.log('[AUTH-STORE] No user theme to apply')
      }
      console.log('[AUTH-STORE] fetchUser completed successfully')
    } catch (error) {
      console.error('[AUTH-STORE] Failed to fetch user:', error)
      console.error('[AUTH-STORE] Error details:', { message: error.message, response: error.response?.data, status: error.response?.status })
      console.log('[AUTH-STORE] Calling logout due to fetch error...')
      logout()
      console.log('[AUTH-STORE] Logout completed')
    }
  }

  const logout = () => {
    console.log('[AUTH-STORE] logout called')
    console.log('[AUTH-STORE] Clearing tokens and user...')
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    console.log('[AUTH-STORE] Tokens and user cleared in store')
    
    console.log('[AUTH-STORE] Removing tokens from localStorage...')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    console.log('[AUTH-STORE] Tokens removed from localStorage')
    
    console.log('[AUTH-STORE] Removing Authorization header...')
    delete api.defaults.headers.common['Authorization']
    console.log('[AUTH-STORE] Authorization header removed')
    console.log('[AUTH-STORE] Logout completed')
  }

  console.log('[AUTH-STORE] Returning store methods and state...')
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

console.log('[AUTH-STORE] Auth store created successfully')

