<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Shareable Links</h3>
        <button @click="close" class="modal-close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>Loading links...</span>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="loadLinks" class="btn btn-primary">Try Again</button>
        </div>
        
        <div v-else class="links-content">
          <p class="links-description">
            Manage your shareable links for this book. Links expire after 7 days.
          </p>
          
          <!-- List of all links -->
          <div v-if="allLinks && allLinks.length > 0" class="links-list">
            <div
              v-for="link in allLinks"
              :key="link.id"
              class="link-card"
              :class="{ 'revoked': link.is_revoked, 'expired': isExpired(link) }"
            >
              <div class="link-card-header">
                <div class="link-status">
                  <span class="status-badge" :class="getStatusClass(link)">
                    {{ getStatusText(link) }}
                  </span>
                </div>
                <button
                  v-if="!link.is_revoked && !isExpired(link)"
                  @click="revokeLink(link.id)"
                  class="btn-revoke"
                  :disabled="revoking === link.id"
                >
                  {{ revoking === link.id ? 'Revoking...' : 'Revoke' }}
                </button>
              </div>
              
              <div class="link-display">
                <input
                  :value="link.share_url"
                  readonly
                  class="link-input"
                  :ref="el => { if (el) linkInputs[link.id] = el }"
                />
                <button @click="copyLink(link)" class="btn btn-primary copy-btn">
                  {{ copiedLinkId === link.id ? 'Copied!' : 'Copy' }}
                </button>
              </div>
              
              <div class="link-info-grid">
                <div class="info-item">
                  <span class="info-label">Created:</span>
                  <span class="info-value">{{ formatDate(link.created_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Expires:</span>
                  <span class="info-value">{{ formatExpirationDate(link.expires_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Views:</span>
                  <span class="info-value">{{ link.view_count }}</span>
                </div>
                <div v-if="link.revoked_at" class="info-item">
                  <span class="info-label">Revoked:</span>
                  <span class="info-value">{{ formatDate(link.revoked_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Empty state -->
          <div v-else class="no-links">
            <p>No shareable links yet. Generate one to share this book.</p>
          </div>
          
          <div class="modal-actions">
            <button @click="generateLink" class="btn btn-primary" :disabled="generating">
              {{ generating ? 'Generating...' : 'Generate New Link' }}
            </button>
            <button @click="close" class="btn btn-secondary">Done</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../services/api'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  bookId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref(null)
const allLinks = ref([])
const copiedLinkId = ref(null)
const revoking = ref(null)
const generating = ref(false)
const linkInputs = ref({})

const close = () => {
  emit('close')
}

const loadLinks = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.get(`/shareable-links/book/${props.bookId}/all`)
    allLinks.value = response.data || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load shareable links'
    console.error('Error loading links:', err)
  } finally {
    loading.value = false
  }
}

const generateLink = async () => {
  generating.value = true
  error.value = null
  
  try {
    await api.post('/shareable-links', {
      book_id: props.bookId
    })
    // Reload all links after generating
    await loadLinks()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to generate shareable link'
    console.error('Error generating link:', err)
  } finally {
    generating.value = false
  }
}

const copyLink = async (link) => {
  try {
    await navigator.clipboard.writeText(link.share_url)
    copiedLinkId.value = link.id
    setTimeout(() => {
      copiedLinkId.value = null
    }, 2000)
  } catch (err) {
    // Fallback for older browsers
    const input = linkInputs.value[link.id]
    if (input) {
      input.select()
      document.execCommand('copy')
      copiedLinkId.value = link.id
      setTimeout(() => {
        copiedLinkId.value = null
      }, 2000)
    }
  }
}

const revokeLink = async (linkId) => {
  if (!confirm('Are you sure you want to revoke this link? It will no longer be accessible.')) {
    return
  }
  
  revoking.value = linkId
  
  try {
    await api.delete(`/shareable-links/${linkId}`)
    // Reload all links after revoking
    await loadLinks()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to revoke link'
    console.error('Error revoking link:', err)
  } finally {
    revoking.value = null
  }
}

const isExpired = (link) => {
  if (link.is_revoked) return false
  const expiresAt = new Date(link.expires_at)
  return expiresAt < new Date()
}

const getStatusText = (link) => {
  if (link.is_revoked) return 'Revoked'
  if (isExpired(link)) return 'Expired'
  return 'Active'
}

const getStatusClass = (link) => {
  if (link.is_revoked) return 'status-revoked'
  if (isExpired(link)) return 'status-expired'
  return 'status-active'
}

const formatExpirationDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    allLinks.value = []
    error.value = null
    copiedLinkId.value = null
    loadLinks()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--color-background);
  border-radius: var(--radius-md);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  font-family: var(--font-heading);
  font-size: 1.25rem;
  color: var(--color-text);
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--color-text-light);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--color-surface);
  color: var(--color-text);
}

.modal-body {
  padding: 1.5rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state p {
  color: var(--color-error);
  margin-bottom: 1rem;
}

.links-description {
  color: var(--color-text);
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.link-card {
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.link-card.revoked {
  opacity: 0.6;
  background: rgba(139, 139, 139, 0.05);
}

.link-card.expired {
  opacity: 0.7;
  background: rgba(212, 175, 55, 0.05);
}

.link-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.link-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-active {
  background: rgba(10, 160, 0, 0.15);
  color: var(--color-success);
}

.status-expired {
  background: rgba(212, 175, 55, 0.15);
  color: var(--color-accent);
}

.status-revoked {
  background: rgba(139, 139, 139, 0.15);
  color: var(--color-text-light);
}

.btn-revoke {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-revoke:hover:not(:disabled) {
  background: var(--color-error);
  color: var(--color-background);
  border-color: var(--color-error);
}

.btn-revoke:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.link-display {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.link-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.9rem;
  background: var(--color-background);
  color: var(--color-text);
}

.copy-btn {
  white-space: nowrap;
  padding: 0.75rem 1rem;
}

.link-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  font-size: 0.875rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.no-links {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  font-style: italic;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .modal-content {
    max-width: 100%;
    margin: 1rem;
  }
  
  .link-display {
    flex-direction: column;
  }
  
  .link-info-grid {
    grid-template-columns: 1fr;
  }
  
  .link-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>

