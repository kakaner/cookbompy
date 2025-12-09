<template>
  <router-link
    v-if="authStore.isAuthenticated"
    to="/books/add"
    class="fab"
    title="Add Boko"
  >
    <span class="fab-icon">+</span>
  </router-link>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  background: var(--color-primary);
  color: var(--color-background);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(155, 72, 25, 0.3);
  text-decoration: none;
  transition: all var(--transition-normal);
  z-index: 1000;
  cursor: pointer;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(155, 72, 25, 0.4);
  background: var(--color-primary-dark, #7a3a14);
}

.fab:active {
  transform: scale(0.95);
}

.fab-icon {
  font-size: 2rem;
  font-weight: 300;
  line-height: 1;
  user-select: none;
}

@media (max-width: 768px) {
  .fab {
    bottom: 1.5rem;
    right: 1.5rem;
    width: 52px;
    height: 52px;
  }
  
  .fab-icon {
    font-size: 1.75rem;
  }
}
</style>

