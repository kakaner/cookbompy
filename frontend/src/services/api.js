console.log('[API] API service module loading...')

import axios from 'axios'
console.log('[API] Axios imported')

console.log('[API] Creating axios instance...')
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null // Use format=value1&format=value2 instead of format[]=value1&format[]=value2
  }
})
console.log('[API] Axios instance created with baseURL:', api.defaults.baseURL)

// Request interceptor to add auth token
console.log('[API] Setting up request interceptor...')
api.interceptors.request.use(
  (config) => {
    console.log('[API] Request interceptor triggered:', { method: config.method, url: config.url, baseURL: config.baseURL })
    
    // Ensure headers object exists
    if (!config.headers) {
      console.log('[API] Headers object missing, creating...')
      config.headers = {}
    }
    
    console.log('[API] Checking for access token in localStorage...')
    const token = localStorage.getItem('access_token')
    if (token) {
      console.log('[API] Token found, adding Authorization header')
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.log('[API] No token found in localStorage')
    }
    
    console.log('[API] Request config prepared:', { url: config.url, hasAuth: !!config.headers.Authorization })
    return config
  },
  (error) => {
    console.error('[API] Request interceptor error:', error)
    return Promise.reject(error)
  }
)
console.log('[API] Request interceptor registered')

// Response interceptor for error handling
console.log('[API] Setting up response interceptor...')
api.interceptors.response.use(
  (response) => {
    console.log('[API] Response interceptor (success):', { status: response.status, url: response.config.url, method: response.config.method })
    return response
  },
  (error) => {
    console.error('[API] Response interceptor (error):', { 
      message: error.message, 
      status: error.response?.status, 
      url: error.config?.url,
      method: error.config?.method 
    })
    
    if (error.response?.status === 401) {
      console.log('[API] 401 Unauthorized detected, clearing tokens...')
      // Token expired or invalid - clear tokens
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete api.defaults.headers.common['Authorization']
      console.log('[API] Tokens cleared')
      
      // Redirect to login if not already there
      const currentPath = window.location.pathname
      console.log('[API] Current path:', currentPath)
      if (currentPath !== '/login' && currentPath !== '/register') {
        console.log('[API] Redirecting to login...')
        window.location.href = '/login'
      } else {
        console.log('[API] Already on login/register page, skipping redirect')
      }
    }
    return Promise.reject(error)
  }
)
console.log('[API] Response interceptor registered')

console.log('[API] API service module loaded successfully')
export default api

