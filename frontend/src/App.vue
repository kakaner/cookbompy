<template>
  <div id="app" :class="{ 'public-mode': isPublicRoute }">
    <!-- Top Navigation Bar -->
    <header v-if="!isPublicRoute" class="top-bar">
      <router-link to="/" class="logo">CookBomPy</router-link>
      <nav class="nav">
        <router-link to="/">Home</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/library">Libbery</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/semesters">Semesters</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/statistics">Statistics</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/conjugation">Conjugation</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/login">Log In</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/register">Sign Up</router-link>
        <router-link v-if="authStore.isAuthenticated && authStore.user" to="/profile" class="user-info">
          <div class="user-avatar" :style="avatarStyle">
            <img v-if="authStore.user.profile_photo_url" :src="authStore.user.profile_photo_url" alt="Profile" />
            <span v-else>{{ getUserInitials() }}</span>
          </div>
          <span>{{ authStore.user.display_name || authStore.user.username }}</span>
        </router-link>
      </nav>
    </header>

    <!-- Main Content -->
    <main>
      <router-view />
    </main>
    
    <!-- Floating Action Button -->
    <FloatingActionButton v-if="!isPublicRoute" />
  </div>
</template>

<script setup>
console.log('[APP] App.vue script setup starting...')

import { onMounted, computed, watch } from 'vue'
console.log('[APP] Vue composables imported')

import { useRouter, useRoute } from 'vue-router'
console.log('[APP] Vue Router composables imported')

import { useAuthStore } from './stores/auth'
console.log('[APP] Auth store imported')

import { initializeTheme, applyTheme } from './utils/themes'
console.log('[APP] Theme utilities imported')

import FloatingActionButton from './components/FloatingActionButton.vue'
console.log('[APP] FloatingActionButton component imported')

console.log('[APP] Initializing router and route...')
const router = useRouter()
const route = useRoute()
console.log('[APP] Router and route initialized:', { currentPath: route.path, currentName: route.name })

console.log('[APP] Getting auth store instance...')
const authStore = useAuthStore()
console.log('[APP] Auth store instance obtained:', { 
  isAuthenticated: authStore.isAuthenticated, 
  hasUser: !!authStore.user,
  hasToken: !!authStore.accessToken 
})

const isPublicRoute = computed(() => {
  const result = route.meta.requiresAuth === false
  console.log('[APP] isPublicRoute computed:', { result, routeMeta: route.meta })
  return result
})

// Watch route changes
watch(() => route.path, (newPath, oldPath) => {
  console.log('[APP] Route changed:', { from: oldPath, to: newPath, name: route.name, meta: route.meta })
}, { immediate: true })

// Watch auth state
watch(() => authStore.isAuthenticated, (isAuth) => {
  console.log('[APP] Auth state changed:', { isAuthenticated: isAuth, hasUser: !!authStore.user })
}, { immediate: true })

// Watch user object
watch(() => authStore.user, (user) => {
  console.log('[APP] User object changed:', { hasUser: !!user, userId: user?.id, username: user?.username })
}, { immediate: true, deep: true })

// Initialize theme on app load
onMounted(() => {
  console.log('[APP] App component mounted')
  console.log('[APP] Initializing theme...')
  initializeTheme()
  console.log('[APP] Theme initialized')
  
  // Apply user's saved theme if logged in
  if (authStore.user?.color_theme) {
    console.log('[APP] Applying user theme:', authStore.user.color_theme)
    applyTheme(authStore.user.color_theme)
    console.log('[APP] User theme applied')
  } else {
    console.log('[APP] No user theme to apply')
  }
  console.log('[APP] onMounted completed')
})

const getUserInitials = () => {
  console.log('[APP] getUserInitials called')
  if (!authStore.user) {
    console.log('[APP] No user, returning ?')
    return '?'
  }
  const name = authStore.user.display_name || authStore.user.username
  const initial = name.charAt(0).toUpperCase()
  console.log('[APP] User initial:', initial)
  return initial
}

const avatarStyle = computed(() => {
  console.log('[APP] avatarStyle computed')
  if (authStore.user?.profile_photo_url) {
    console.log('[APP] User has profile photo')
    return {}
  }
  console.log('[APP] User has no profile photo')
  return {}
})

console.log('[APP] App.vue script setup completed')
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--color-surface);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: var(--color-background);
  font-weight: 600;
  font-size: 0.875rem;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
</style>

