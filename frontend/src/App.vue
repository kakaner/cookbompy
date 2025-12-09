<template>
  <div id="app" :class="{ 'public-mode': isPublicRoute }">
    <!-- Top Navigation Bar -->
    <header v-if="!isPublicRoute" class="top-bar">
      <router-link to="/" class="logo">CookBomPy</router-link>
      <nav class="nav">
        <router-link v-if="authStore.isAuthenticated" to="/library">Libbery</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/semesters">Semesters</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/statistics">Statistics</router-link>
        <div v-if="authStore.isAuthenticated" class="dropdown" :class="{ 'dropdown-open': isDropdownOpen }" ref="dropdownRef">
          <span class="dropdown-trigger" @click.stop="toggleDropdown">YOIYOIYOIS</span>
          <div class="dropdown-menu" v-show="isDropdownOpen">
            <router-link to="/conjugation" @click="closeDropdown">Conjugation</router-link>
            <router-link to="/completionist" @click="closeDropdown">Completionist</router-link>
          </div>
        </div>
        <router-link v-if="!authStore.isAuthenticated" to="/login">Log In</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/register">Sign Up</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/profile" class="user-info">
          <div class="user-avatar" :style="avatarStyle">
            <img v-if="authStore.user?.profile_photo_url" :src="authStore.user.profile_photo_url" alt="Profile" />
            <span v-else>{{ getUserInitials() }}</span>
          </div>
          <span v-if="authStore.user">{{ authStore.user.display_name || authStore.user.username }}</span>
          <span v-else>Loading...</span>
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

import { onMounted, computed, watch, ref, onUnmounted } from 'vue'
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

// Dropdown state
const isDropdownOpen = ref(false)
const dropdownRef = ref(null)

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

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
onMounted(async () => {
  console.log('[APP] App component mounted')
  console.log('[APP] Initializing theme...')
  initializeTheme()
  console.log('[APP] Theme initialized')
  
  // Fetch user if authenticated but user not loaded yet
  if (authStore.isAuthenticated && !authStore.user) {
    console.log('[APP] User is authenticated but user object not loaded, fetching user...')
    try {
      await authStore.fetchUser()
      console.log('[APP] User fetched successfully')
    } catch (error) {
      console.error('[APP] Failed to fetch user:', error)
    }
  }
  
  // Apply user's saved theme if logged in
  if (authStore.user?.color_theme) {
    console.log('[APP] Applying user theme:', authStore.user.color_theme)
    applyTheme(authStore.user.color_theme)
    console.log('[APP] User theme applied')
  } else {
    console.log('[APP] No user theme to apply')
  }
  
  // Add click outside listener for dropdown
  document.addEventListener('click', handleClickOutside)
  
  console.log('[APP] onMounted completed')
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
  display: flex !important;
  align-items: center;
  gap: 0.875rem;
  color: var(--color-background) !important;
  font-size: 0.875rem;
  text-decoration: none;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-background) !important;
}

.user-info span {
  color: inherit;
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

/* YOIYOIYOIS Dropdown */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  color: var(--color-background);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--transition-fast);
  padding: 0;
  user-select: none;
}

.dropdown-trigger:hover {
  opacity: 0.8;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: var(--color-surface);
  min-width: 180px;
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-sm);
  margin-top: 0.5rem;
  padding: 0.5rem 0;
  z-index: 1000;
}

.dropdown-open .dropdown-menu {
  display: block;
}

.dropdown-menu a {
  display: block;
  padding: 0.75rem 1.25rem;
  color: var(--color-text);
  text-decoration: none;
  transition: background var(--transition-fast);
  font-size: 0.9rem;
}

.dropdown-menu a:hover {
  background: var(--color-background);
  color: var(--color-primary);
}

.dropdown-menu a.router-link-active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}
</style>

