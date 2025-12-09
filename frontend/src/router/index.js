console.log('[ROUTER] Router module loading...')

import { createRouter, createWebHistory } from 'vue-router'
console.log('[ROUTER] Vue Router imported')

import { useAuthStore } from '../stores/auth'
console.log('[ROUTER] Auth store imported')

console.log('[ROUTER] Defining routes...')
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/library',
    name: 'Library',
    component: () => import('../views/Library.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/books/add',
    name: 'AddBook',
    component: () => import('../views/AddBook.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: () => import('../views/BookDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/books/:id/edit',
    name: 'EditBook',
    component: () => import('../views/EditBook.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/semesters',
    name: 'Semesters',
    component: () => import('../views/Semesters.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/semesters/:number',
    name: 'SemesterDetail',
    component: () => import('../views/SemesterDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/Statistics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/conjugation',
    name: 'Conjugation',
    component: () => import('../views/Conjugation.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/share/:token',
    name: 'ShareableView',
    component: () => import('../views/ShareableView.vue'),
    meta: { requiresAuth: false } // Public route, no auth required
  }
]

console.log('[ROUTER] Routes defined:', routes.length, 'routes')
routes.forEach((route, index) => {
  console.log(`[ROUTER] Route ${index + 1}:`, { path: route.path, name: route.name, requiresAuth: route.meta?.requiresAuth })
})

console.log('[ROUTER] Creating router instance...')
const router = createRouter({
  history: createWebHistory(),
  routes,
  // Ensure scroll behavior works correctly
  scrollBehavior(to, from, savedPosition) {
    console.log('[ROUTER] scrollBehavior called:', { to: to.path, from: from.path, hasSavedPosition: !!savedPosition })
    if (savedPosition) {
      console.log('[ROUTER] Returning saved position')
      return savedPosition
    } else {
      console.log('[ROUTER] Returning top: 0')
      return { top: 0 }
    }
  }
})
console.log('[ROUTER] Router instance created')

// Router guard for protected routes
console.log('[ROUTER] Setting up beforeEach navigation guard...')
router.beforeEach((to, from, next) => {
  console.log('[ROUTER] Navigation guard triggered:', { 
    from: from.path || 'initial', 
    to: to.path, 
    toName: to.name,
    requiresAuth: to.meta?.requiresAuth 
  })
  
  try {
    console.log('[ROUTER] Getting auth store...')
    const authStore = useAuthStore()
    console.log('[ROUTER] Auth store obtained:', { 
      isAuthenticated: authStore.isAuthenticated,
      hasUser: !!authStore.user 
    })
    
    // Check if route requires authentication
    // If requiresAuth is explicitly false, allow access (public routes)
    if (to.meta.requiresAuth === false) {
      console.log('[ROUTER] Route is public, allowing access')
      next()
      return
    }
    
    // If requiresAuth is true or undefined (default), check authentication
    if (to.meta.requiresAuth !== false) {
      console.log('[ROUTER] Route requires auth, checking authentication...')
      // Check authentication status
      if (!authStore.isAuthenticated) {
        console.log('[ROUTER] User not authenticated, redirecting to login')
        // Redirect to login, preserving the intended destination
        next({ 
          path: '/login', 
          query: { redirect: to.fullPath },
          replace: true 
        })
        return
      }
      console.log('[ROUTER] User is authenticated, allowing access')
    }
    
    // Allow navigation to proceed
    console.log('[ROUTER] Allowing navigation to proceed')
    next()
  } catch (error) {
    console.error('[ROUTER] Router guard error:', error)
    console.error('[ROUTER] Error stack:', error.stack)
    // If there's an error accessing the store, allow navigation to continue
    // This prevents the router from getting stuck
    console.log('[ROUTER] Allowing navigation despite error to prevent stuck state')
    next()
  }
})
console.log('[ROUTER] Navigation guard registered')

// Add afterEach hook for logging
router.afterEach((to, from) => {
  console.log('[ROUTER] Navigation completed:', { from: from.path || 'initial', to: to.path, toName: to.name })
})

console.log('[ROUTER] Router module loaded successfully')
export default router

