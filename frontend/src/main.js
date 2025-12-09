console.log('[MAIN] Starting application initialization...')

import { createApp } from 'vue'
console.log('[MAIN] Vue imported successfully')

import { createPinia } from 'pinia'
console.log('[MAIN] Pinia imported successfully')

import App from './App.vue'
console.log('[MAIN] App component imported successfully')

import router from './router'
console.log('[MAIN] Router imported successfully')

import './style.css'
console.log('[MAIN] Styles imported successfully')

console.log('[MAIN] Creating Vue app instance...')
const app = createApp(App)
console.log('[MAIN] Vue app instance created')

console.log('[MAIN] Creating Pinia store...')
const pinia = createPinia()
console.log('[MAIN] Pinia store created')

console.log('[MAIN] Registering Pinia plugin...')
app.use(pinia)
console.log('[MAIN] Pinia plugin registered')

console.log('[MAIN] Registering router plugin...')
app.use(router)
console.log('[MAIN] Router plugin registered')

console.log('[MAIN] Mounting app to #app element...')
app.mount('#app')
console.log('[MAIN] App mounted successfully!')

