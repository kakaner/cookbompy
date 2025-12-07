import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Router guard for protected routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router

