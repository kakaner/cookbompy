<template>
  <div id="app">
    <!-- Top Navigation Bar -->
    <header class="top-bar">
      <router-link to="/" class="logo">CookBomPy</router-link>
      <nav class="nav">
        <router-link to="/">Home</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/library">Library</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/semesters">Semesters</router-link>
        <router-link v-if="authStore.isAuthenticated" to="/profile">Profile</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/login">Log In</router-link>
        <router-link v-if="!authStore.isAuthenticated" to="/register">Sign Up</router-link>
        <a v-if="authStore.isAuthenticated" href="#" @click.prevent="handleLogout">Log Out</a>
        <div v-if="authStore.isAuthenticated && authStore.user" class="user-info">
          <div class="user-avatar" :style="avatarStyle">
            <img v-if="authStore.user.profile_photo_url" :src="authStore.user.profile_photo_url" alt="Profile" />
            <span v-else>{{ getUserInitials() }}</span>
          </div>
          <span>{{ authStore.user.display_name || authStore.user.username }}</span>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { initializeTheme, applyTheme } from './utils/themes'

const router = useRouter()
const authStore = useAuthStore()

// Initialize theme on app load
onMounted(() => {
  initializeTheme()
  
  // Apply user's saved theme if logged in
  if (authStore.user?.color_theme) {
    applyTheme(authStore.user.color_theme)
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const getUserInitials = () => {
  if (!authStore.user) return '?'
  const name = authStore.user.display_name || authStore.user.username
  return name.charAt(0).toUpperCase()
}

const avatarStyle = computed(() => {
  if (authStore.user?.profile_photo_url) {
    return {}
  }
  return {}
})
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

