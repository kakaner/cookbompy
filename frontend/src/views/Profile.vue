<template>
  <div class="container">
    <h2>Profile</h2>
    
    <div class="profile-layout">
      <!-- Left Column: User Info -->
      <div class="card profile-card">
        <!-- Profile Photo Section -->
        <div class="photo-section">
          <div class="profile-photo-container">
            <img
              v-if="authStore.user?.profile_photo_url"
              :src="authStore.user.profile_photo_url"
              alt="Profile photo"
              class="profile-photo"
            />
            <div v-else class="profile-photo-placeholder">
              {{ getUserInitials() }}
            </div>
            <button @click="triggerPhotoUpload" class="photo-edit-btn" title="Change photo">
              📷
            </button>
          </div>
          <input
            type="file"
            ref="photoInput"
            accept="image/jpeg,image/png,image/webp"
            @change="handlePhotoUpload"
            style="display: none"
          />
          <button
            v-if="authStore.user?.profile_photo_url"
            @click="removePhoto"
            class="remove-photo-btn"
          >
            Remove Photo
          </button>
        </div>

        <div v-if="authStore.user" class="profile-info">
          <div class="profile-field">
            <label class="profile-label">Username</label>
            <div class="profile-value">{{ authStore.user.username }}</div>
          </div>
          
          <div class="profile-field">
            <label class="profile-label">Email</label>
            <div class="profile-value">{{ authStore.user.email }}</div>
          </div>
          
          <div class="profile-field">
            <label class="profile-label">Display Name</label>
            <div class="profile-value">{{ authStore.user.display_name || 'Not set' }}</div>
          </div>
          
          <div class="profile-field">
            <label class="profile-label">Account Status</label>
            <div class="profile-value">
              <span class="status-badge" :class="{ 'status-active': authStore.user.is_active }">
                {{ authStore.user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          
          <div class="profile-field">
            <label class="profile-label">Member Since</label>
            <div class="profile-value">{{ formatDate(authStore.user.created_at) }}</div>
          </div>
          
          <div class="profile-actions">
            <button @click="handleLogout" class="btn btn-primary">
              Log Out
            </button>
          </div>
        </div>
        
        <div v-else class="loading">
          Loading profile...
        </div>
      </div>

      <!-- Right Column: Preferences -->
      <div class="card preferences-card">
        <h3>Preferences</h3>
        
        <div v-if="saveMessage" :class="['save-message', saveMessage.type]">
          {{ saveMessage.text }}
        </div>

        <!-- Display Name -->
        <div class="preference-field">
          <label class="preference-label">Display Name</label>
          <input
            v-model="preferences.display_name"
            type="text"
            class="form-input"
            placeholder="Your display name"
            @change="savePreferences"
          />
        </div>

        <!-- Default Book Format -->
        <div class="preference-field">
          <label class="preference-label">Default Book Format</label>
          <p class="preference-hint">Auto-select this format when adding new books</p>
          <select v-model="preferences.default_book_format" class="form-select" @change="savePreferences">
            <option :value="null">No default</option>
            <option v-for="format in formatOptions" :key="format.value" :value="format.value">
              {{ format.icon }} {{ format.label }}
            </option>
          </select>
        </div>

        <!-- Color Theme -->
        <div class="preference-field">
          <label class="preference-label">Color Theme</label>
          <p class="preference-hint">Choose your preferred color scheme</p>
          <div class="theme-grid">
            <button
              v-for="theme in themeOptions"
              :key="theme.key"
              :class="['theme-swatch', { active: preferences.color_theme === theme.key }]"
              :style="{
                '--swatch-primary': theme.primary,
                '--swatch-secondary': theme.secondary
              }"
              @click="selectTheme(theme.key)"
              :title="theme.name"
            >
              <span class="swatch-primary"></span>
              <span class="swatch-secondary"></span>
              <span v-if="preferences.color_theme === theme.key" class="check-mark">✓</span>
            </button>
          </div>
        </div>

        <!-- Default Page Size -->
        <div class="preference-field">
          <label class="preference-label">Default Page Size</label>
          <p class="preference-hint">Bokos per page in Library view</p>
          <select v-model="preferences.default_page_size" class="form-select" @change="savePreferences">
            <option :value="25">25 bokos</option>
            <option :value="50">50 bokos</option>
            <option :value="75">75 bokos</option>
            <option :value="100">100 bokos</option>
            <option :value="200">200 bokos</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { themeList, applyTheme } from '../utils/themes'
import api from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const photoInput = ref(null)
const saveMessage = ref(null)

const preferences = ref({
  display_name: '',
  default_book_format: null,
  color_theme: 'terracotta',
  default_page_size: 50
})

const formatOptions = [
  { value: 'PAPERBACK', label: 'Paperback', icon: '📖' },
  { value: 'HARDCOVER', label: 'Hardcover', icon: '📚' },
  { value: 'EBOOK', label: 'E-book', icon: '📱' },
  { value: 'AUDIOBOOK', label: 'Audiobook', icon: '🎧' },
  { value: 'MAGAZINE', label: 'Magazine', icon: '📰' },
  { value: 'COMIC', label: 'Comic', icon: '🗯️' },
  { value: 'OTHER', label: 'Other', icon: '📄' }
]

const themeOptions = themeList

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const getUserInitials = () => {
  if (!authStore.user) return '?'
  const name = authStore.user.display_name || authStore.user.username
  return name.charAt(0).toUpperCase()
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const triggerPhotoUpload = () => {
  photoInput.value?.click()
}

const handlePhotoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    showMessage('error', 'Photo must be less than 5MB')
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/users/me/photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    // Update user in auth store
    authStore.user.profile_photo_url = response.data.profile_photo_url
    showMessage('success', 'Photo uploaded successfully')
  } catch (error) {
    console.error('Failed to upload photo:', error)
    showMessage('error', 'Failed to upload photo')
  }
}

const removePhoto = async () => {
  try {
    await api.delete('/users/me/photo')
    authStore.user.profile_photo_url = null
    showMessage('success', 'Photo removed')
  } catch (error) {
    console.error('Failed to remove photo:', error)
    showMessage('error', 'Failed to remove photo')
  }
}

const selectTheme = async (themeKey) => {
  preferences.value.color_theme = themeKey
  applyTheme(themeKey)
  await savePreferences()
}

const savePreferences = async () => {
  try {
    const response = await api.put('/users/me', {
      display_name: preferences.value.display_name || null,
      default_book_format: preferences.value.default_book_format || null,
      color_theme: preferences.value.color_theme,
      default_page_size: preferences.value.default_page_size
    })
    
    // Update auth store
    Object.assign(authStore.user, response.data)
    showMessage('success', 'Preferences saved')
  } catch (error) {
    console.error('Failed to save preferences:', error)
    showMessage('error', 'Failed to save preferences')
  }
}

const showMessage = (type, text) => {
  saveMessage.value = { type, text }
  setTimeout(() => {
    saveMessage.value = null
  }, 3000)
}

const loadPreferences = () => {
  if (authStore.user) {
    preferences.value = {
      display_name: authStore.user.display_name || '',
      default_book_format: authStore.user.default_book_format || null,
      color_theme: authStore.user.color_theme || 'terracotta',
      default_page_size: authStore.user.default_page_size || 50
    }
  }
}

onMounted(async () => {
  if (!authStore.user && authStore.isAuthenticated) {
    await authStore.fetchUser()
  }
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  loadPreferences()
})

watch(() => authStore.user, () => {
  loadPreferences()
}, { deep: true })
</script>

<style scoped>
.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;
  max-width: 1000px;
}

.profile-card {
  padding: 2rem;
}

.preferences-card {
  padding: 2rem;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.preferences-card h3 {
  margin-bottom: 1.5rem;
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-border);
}

.photo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
}

.profile-photo-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 1rem;
}

.profile-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid var(--color-primary);
}

.profile-photo-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 600;
  color: var(--color-background);
  font-family: var(--font-heading);
}

.photo-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.photo-edit-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.remove-photo-btn {
  background: none;
  border: none;
  color: var(--color-error);
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: underline;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.profile-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.profile-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile-value {
  font-size: 1rem;
  color: var(--color-text);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.status-active {
  background: rgba(81, 207, 102, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(81, 207, 102, 0.3);
}

.profile-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.preference-field {
  margin-bottom: 1.5rem;
}

.preference-label {
  display: block;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.preference-hint {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.theme-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.theme-swatch {
  position: relative;
  width: 60px;
  height: 40px;
  border-radius: var(--radius-sm);
  border: 3px solid var(--color-border);
  cursor: pointer;
  overflow: hidden;
  transition: all var(--transition-fast);
  display: flex;
}

.theme-swatch:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.theme-swatch.active {
  border-color: var(--color-text);
  box-shadow: 0 0 0 2px var(--color-background), 0 0 0 4px var(--color-text);
}

.swatch-primary {
  flex: 1;
  background: var(--swatch-primary);
}

.swatch-secondary {
  flex: 1;
  background: var(--swatch-secondary);
}

.check-mark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 1.25rem;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.save-message {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.save-message.success {
  background: rgba(81, 207, 102, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(81, 207, 102, 0.3);
}

.save-message.error {
  background: rgba(220, 53, 69, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(220, 53, 69, 0.3);
}

@media (max-width: 768px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}
</style>
