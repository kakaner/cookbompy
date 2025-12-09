<template>
  <div class="container">
    <div v-if="booksStore.loading && !booksStore.currentBook" class="loading">
      Loading boko...
    </div>

    <div v-else-if="booksStore.currentBook" class="book-detail">
      <!-- Header with Actions -->
      <div class="detail-header">
        <div>
          <h2 class="book-detail-title">{{ booksStore.currentBook.title }}</h2>
          <p class="book-detail-author">by {{ booksStore.currentBook.author }}</p>
          <div v-if="filteredReads && filteredReads.length > 0" class="read-count-badge">
            {{ filteredReads.length }} reading session{{ filteredReads.length !== 1 ? 's' : '' }}
          </div>
        </div>
        <div class="detail-actions">
          <button
            @click="showShareModal = true"
            class="btn btn-secondary"
          >
            Share Book Page
          </button>
          <router-link
            :to="`/books/${booksStore.currentBook.id}/edit`"
            class="btn btn-primary"
          >
            Edit
          </router-link>
        </div>
      </div>

      <!-- Main Content -->
      <div class="detail-content">
        <!-- Cover and Basic Info -->
        <div class="detail-main">
          <div class="cover-section">
            <div class="cover-compact">
              <img
                v-if="booksStore.currentBook.cover_image_url"
                :src="booksStore.currentBook.cover_image_url"
                :alt="booksStore.currentBook.title"
              />
              <div v-else class="cover-placeholder-compact">
                {{ booksStore.currentBook.title.charAt(0) }}
              </div>
            </div>
            <div class="format-display">
              <span class="format-icon-large">{{ getFormatIcon(booksStore.currentBook.format) }}</span>
              <span class="format-name">{{ getFormatDisplayName(booksStore.currentBook.format) }}</span>
            </div>
          </div>

          <div class="info-section">
            <!-- Core Info -->
            <div class="info-group">
              <h3>Boko Information</h3>
              <div class="info-grid">
                <div class="info-item" v-if="booksStore.currentBook.isbn_13">
                  <label>ISBN-13</label>
                  <div>{{ booksStore.currentBook.isbn_13 }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.isbn_10">
                  <label>ISBN-10</label>
                  <div>{{ booksStore.currentBook.isbn_10 }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.publication_date">
                  <label>Publication Date</label>
                  <div>{{ formatDate(booksStore.currentBook.publication_date) }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.publisher">
                  <label>Publisher</label>
                  <div>{{ booksStore.currentBook.publisher }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.page_count">
                  <label>Page Count</label>
                  <div>{{ booksStore.currentBook.page_count }} pages</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.language">
                  <label>Language</label>
                  <div>{{ booksStore.currentBook.language.toUpperCase() }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.book_type">
                  <label>Boko Type</label>
                  <div>{{ booksStore.currentBook.book_type }}</div>
                </div>
              </div>
            </div>

            <!-- Genres -->
            <div class="info-group" v-if="booksStore.currentBook.genres && booksStore.currentBook.genres.length > 0">
              <h3>Genres</h3>
              <div class="genre-tags">
                <span
                  v-for="genre in booksStore.currentBook.genres"
                  :key="genre"
                  class="genre-tag"
                >
                  {{ genre }}
                </span>
              </div>
            </div>

            <!-- Legacy Points Display (for backwards compatibility, remove if not needed) -->
            <div class="info-group" v-if="booksStore.currentBook.points && booksStore.currentBook.read_status === 'READ'">
              <h3>Points</h3>
              <div class="points-display">
                <div class="points-main">
                  <span class="points-value">{{ booksStore.currentBook.points.bompyallegory?.toFixed(2) }}</span>
                  <span class="points-label">bompyallegory</span>
                </div>
                <div class="points-secondary">
                  <span class="points-value">{{ booksStore.currentBook.points.bompyreasonable.toFixed(2) }}</span>
                  <span class="points-label">bompyreasonable</span>
                </div>
                <div class="points-breakdown">
                  {{ booksStore.currentBook.points.breakdown }}
                </div>
              </div>
            </div>

            <!-- Reading Status -->
            <div class="info-group">
              <h3>Reading Status</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Status</label>
                  <div class="status-badge" :class="`status-${(booksStore.currentBook.read_status || 'UNREAD').toLowerCase()}`">
                    {{ booksStore.currentBook.read_status || 'UNREAD' }}
                  </div>
                </div>
                <div class="info-item">
                  <label>Viewner Status</label>
                  <div class="viewner-status" :class="{ 'has-viewner': hasViewner }">
                    {{ hasViewner ? 'Yes' : 'No' }}
                  </div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.date_started">
                  <label>Date Started</label>
                  <div>{{ formatDate(booksStore.currentBook.date_started) }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.date_finished">
                  <label>Date Finished</label>
                  <div>{{ formatDate(booksStore.currentBook.date_finished) }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.is_reread">
                  <label>Re-read</label>
                  <div>Yes</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.is_memorable">
                  <label>Memorable</label>
                  <div class="memorable-badge">
                    <span class="star-icon">⭐</span>
                    Featured in semester timeline
                  </div>
                </div>
              </div>
            </div>

            <!-- Additional Details -->
            <div
              class="info-group"
              v-if="booksStore.currentBook.series || booksStore.currentBook.original_title || booksStore.currentBook.translator"
            >
              <h3>Additional Details</h3>
              <div class="info-grid">
                <div class="info-item" v-if="booksStore.currentBook.series">
                  <label>Series</label>
                  <div>
                    {{ booksStore.currentBook.series }}
                    <span v-if="booksStore.currentBook.series_number"> (#{{ booksStore.currentBook.series_number }})</span>
                  </div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.original_title">
                  <label>Original Title</label>
                  <div>{{ booksStore.currentBook.original_title }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.translator">
                  <label>Translator</label>
                  <div>{{ booksStore.currentBook.translator }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.illustrator">
                  <label>Illustrator</label>
                  <div>{{ booksStore.currentBook.illustrator }}</div>
                </div>
                <div class="info-item" v-if="booksStore.currentBook.awards">
                  <label>Awards</label>
                  <div>{{ booksStore.currentBook.awards }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Synopsis -->
        <div class="synopsis-section" v-if="booksStore.currentBook.description">
          <h3>Synopsis</h3>
          <p class="synopsis-text">{{ booksStore.currentBook.description }}</p>
          <div v-if="booksStore.currentBook.description_source" class="synopsis-source">
            <span class="source-icon">{{ getSourceIcon(booksStore.currentBook.description_source) }}</span>
            <span>Synopsis from {{ booksStore.currentBook.description_source }}</span>
          </div>
        </div>

        <!-- Reading Sessions -->
        <div class="reading-sessions-section">
          <div class="sessions-header">
            <h3 class="sessions-title">Reading Sessions</h3>
            <div class="filter-toggle">
              <button
                @click="showOnlyMyReads = !showOnlyMyReads"
                class="filter-toggle-btn"
                :class="{ 'active': showOnlyMyReads }"
              >
                <span v-if="showOnlyMyReads">My Reads Only</span>
                <span v-else>All Community Reads</span>
              </button>
            </div>
          </div>
          
          <!-- Loading state -->
          <div v-if="loadingReads" class="reads-loading">
            <div class="loading-spinner"></div>
            <span>Loading reading sessions...</span>
          </div>
          
          <!-- Empty state -->
          <div v-else-if="!filteredReads || filteredReads.length === 0" class="reads-empty">
            <div class="empty-illustration">📚</div>
            <p class="empty-message">{{ currentEmptyMessage }}</p>
          </div>
          
          <!-- Reads list -->
          <div v-else class="reads-list reads-timeline">
            <div
              v-for="(read, index) in filteredReads"
              :key="read.id || index"
              class="read-item"
              :data-read-number="index + 1"
            >
              <div class="read-item-header">
                <div class="read-item-meta">
                  <div class="read-item-user-info">
                    <div v-if="read.user" class="user-info">
                      <img
                        v-if="read.user.profile_photo_url"
                        :src="read.user.profile_photo_url"
                        :alt="read.user.display_name || read.user.username"
                        class="user-avatar-small"
                      />
                      <div v-else class="user-avatar-small user-avatar-placeholder">
                        {{ (read.user.display_name || read.user.username || '?').charAt(0).toUpperCase() }}
                      </div>
                      <span class="user-name">{{ read.user.display_name || read.user.username }}</span>
                    </div>
                    <div class="read-item-badges">
                      <span v-if="read.is_reread" class="reread-badge">Re-read</span>
                      <span v-if="read.is_memorable" class="memorable-badge-small">⭐</span>
                    </div>
                  </div>
                  <div class="read-item-dates">
                    <span v-if="read.date_finished" class="date-label">
                      <span class="date-icon">📅</span>
                      Finished {{ formatDate(read.date_finished) }}
                      <span class="time-ago">({{ getTimeAgo(read.date_finished) }})</span>
                    </span>
                    <span v-else-if="read.date_started" class="date-label">
                      <span class="date-icon">📅</span>
                      Started {{ formatDate(read.date_started) }}
                    </span>
                  </div>
                  <div v-if="read.comment_count > 0" class="comment-count-header">
                    <span class="comment-count-badge-header">{{ read.comment_count }} comment{{ read.comment_count !== 1 ? 's' : '' }}</span>
                  </div>
                </div>
                <!-- Vibe photo thumbnail -->
                <div v-if="read.read_vibe_photo_url" class="read-vibe-thumbnail">
                  <img :src="read.read_vibe_photo_url" alt="Read vibe" />
                </div>
              </div>
              
              <div v-if="read.read_status === 'READ' && read.points" class="read-points">
                <div class="points-container">
                  <div class="points-item">
                    <span class="points-label">bompyallegory</span>
                    <span class="points-value">{{ read.points.bompyallegory?.toFixed(2) || '0.00' }}</span>
                  </div>
                  <div class="points-item">
                    <span class="points-label">bompyreasonable</span>
                    <span class="points-value">{{ read.points.bompyreasonable?.toFixed(2) || '0.00' }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="read.review" class="read-review">
                <h5 class="review-title">Viewner</h5>
                <div class="review-content">{{ read.review }}</div>
              </div>
              
              <!-- Comments Section -->
              <CommentSection
                :read-id="read.id"
                :read-author-id="read.user_id"
                :collapsed="true"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error">
      Boko not found
    </div>
    
    <!-- Share Modal -->
    <ShareModal
      :show="showShareModal"
      :book-id="booksStore.currentBook?.id"
      @close="showShareModal = false"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { useAuthStore } from '../stores/auth'
import { getFormatIcon, getFormatDisplayName } from '../utils/formats'
import CommentSection from '../components/CommentSection.vue'
import ShareModal from '../components/ShareModal.vue'
import api from '../services/api'

const route = useRoute()
const booksStore = useBooksStore()
const authStore = useAuthStore()
const allReads = ref([])
const loadingReads = ref(false)
const showShareModal = ref(false)
const showOnlyMyReads = ref(false)

// Filter reads based on toggle
const filteredReads = computed(() => {
  if (!allReads.value || allReads.value.length === 0) return []
  
  if (showOnlyMyReads.value && authStore.user) {
    return allReads.value.filter(read => read.user_id === authStore.user.id)
  }
  
  return allReads.value
})

// Check if any read has a review (viewner)
const hasViewner = computed(() => {
  if (!filteredReads.value || filteredReads.value.length === 0) return false
  return filteredReads.value.some(read => read.review && read.review.trim().length > 0)
})

const emptyMessages = [
  "Pick up this boko to read it! Feed the kagua monaster.",
  "This boko awaits your reading journey. Time to feed the kagua monaster!",
  "A new reading adventure awaits. Pick up this boko and feed the kagua monaster!",
  "The kagua monaster hungers for your reading. Pick up this boko!",
  "Start your reading session and feed the kagua monaster with this boko!"
]

const currentEmptyMessage = ref(emptyMessages[0])

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getTimeAgo = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  const diffWeeks = Math.floor(diffDays / 7)
  const diffMonths = Math.floor(diffDays / 30)
  const diffYears = Math.floor(diffDays / 365)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  if (diffWeeks < 4) return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`
  if (diffMonths < 12) return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`
  return `${diffYears} year${diffYears !== 1 ? 's' : ''} ago`
}

const getSourceIcon = (source) => {
  const icons = {
    'GOODREADS': 'G',
    'GOOGLE_BOOKS': 'GB',
    'AMAZON': 'A',
    'WIKIPEDIA': 'W',
    'MANUAL': 'M'
  }
  return icons[source] || '?'
}

const loadReads = async (bookId) => {
  loadingReads.value = true
  try {
    // Load community reads (all users)
    const response = await api.get(`/reads/book/${bookId}/community`)
    allReads.value = response.data || []
    console.log('Loaded community reads:', allReads.value)
  } catch (err) {
    console.error('Error loading reads:', err)
    allReads.value = []
  } finally {
    loadingReads.value = false
  }
}

onMounted(async () => {
  const bookId = parseInt(route.params.id)
  if (bookId) {
    await booksStore.fetchBook(bookId)
    // Load reads for this book
    await loadReads(bookId)
  }
})

// Rotate empty messages
let messageInterval = null
watch(() => filteredReads.value, (newReads) => {
  if (messageInterval) {
    clearInterval(messageInterval)
    messageInterval = null
  }
  if (!newReads || newReads.length === 0) {
    let messageIndex = 0
    messageInterval = setInterval(() => {
      messageIndex = (messageIndex + 1) % emptyMessages.length
      currentEmptyMessage.value = emptyMessages[messageIndex]
    }, 3000)
  }
}, { immediate: true })

// Reload reads when route changes (e.g., navigating between books)
watch(() => route.params.id, async (newId) => {
  if (newId) {
    const bookId = parseInt(newId)
    await booksStore.fetchBook(bookId)
    await loadReads(bookId)
  }
})
</script>

<style scoped>
.book-detail {
  max-width: 1200px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--color-border);
}

.book-detail-title {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.book-detail-author {
  font-size: 1rem;
  color: var(--color-text-light);
  font-family: var(--font-title);
  font-style: italic;
  margin-bottom: 0.5rem;
}

.read-count-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(155, 72, 25, 0.1);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid rgba(155, 72, 25, 0.2);
}

.detail-actions {
  display: flex;
  gap: 1rem;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-main {
  display: grid;
  grid-template-columns: 125px 1fr;
  gap: 1.5rem;
}

.cover-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cover-compact {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.cover-compact img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-compact {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-border) 0%, #C5BFB5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-light);
  font-size: 2rem;
  font-weight: 600;
  font-family: var(--font-heading);
}

.format-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-background);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.format-icon-large {
  font-size: 1.5rem;
}

.format-name {
  font-weight: 500;
  color: var(--color-text);
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-group h3 {
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.75rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--color-border);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item div {
  font-size: 1rem;
  color: var(--color-text);
}

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.viewner-status {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: 500;
  background: rgba(139, 139, 139, 0.1);
  color: #8b8b8b;
}

.viewner-status.has-viewner {
  background: rgba(10, 160, 0, 0.1);
  color: var(--color-success);
}

.memorable-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.08) 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: var(--radius-full);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.star-icon {
  font-size: 1rem;
}

.status-unread {
  background: rgba(139, 139, 139, 0.1);
  color: #8b8b8b;
}

.status-reading {
  background: rgba(212, 175, 55, 0.1);
  color: var(--color-accent);
}

.status-read {
  background: rgba(10, 160, 0, 0.1);
  color: var(--color-success);
}

.status-dnf {
  background: rgba(204, 0, 0, 0.1);
  color: var(--color-error);
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: var(--color-background);
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.synopsis-section {
  padding: 2rem;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.synopsis-section h3 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 1rem;
}

.synopsis-text {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
  margin-bottom: 1rem;
}

.synopsis-source {
  font-size: 0.8rem;
  color: var(--color-secondary);
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.source-icon {
  width: 16px;
  height: 16px;
  background: var(--color-secondary);
  color: var(--color-background);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
}

.points-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.points-main,
.points-secondary {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.points-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
  font-family: var(--font-heading);
}

.points-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  text-transform: lowercase;
  font-style: italic;
}

.points-breakdown {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-style: italic;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

/* Reading Sessions Styling */
.reading-sessions-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid var(--color-border);
}

.sessions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-border);
}

.sessions-title {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: 0;
}

.filter-toggle {
  display: flex;
  align-items: center;
}

.filter-toggle-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-toggle-btn:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-toggle-btn.active {
  background: var(--color-primary);
  color: var(--color-background);
  border-color: var(--color-primary);
}

.reads-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 2rem;
  color: var(--color-text-light);
}

.reads-loading .loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.reads-empty {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--color-text-light);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
}

.empty-illustration {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-message {
  font-size: 1.1rem;
  font-style: italic;
  color: var(--color-text);
  line-height: 1.6;
  min-height: 3rem;
  transition: opacity 0.5s ease;
}

.reads-list {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  margin-top: 1rem;
}

.reads-timeline {
  position: relative;
  padding: 0 2rem;
  margin: 0;
}

.reads-timeline::before {
  content: '';
  position: absolute;
  left: 3rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  border-radius: 2px;
}

.reads-timeline .read-item {
  position: relative;
  margin-left: 4rem;
  margin-right: 0;
  margin-bottom: 0;
}

.reads-timeline .read-item::before {
  content: attr(data-read-number);
  position: absolute;
  left: -4.5rem;
  top: 1.5rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  border: 3px solid var(--color-background);
  box-shadow: 0 0 0 2px var(--color-primary);
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-background);
  font-family: var(--font-heading);
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1;
}

.reads-timeline .read-item::after {
  display: none;
}

.read-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  position: relative;
  margin: 0;
}

.read-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* Only show left border gradient for non-timeline items */
.reads-list:not(.reads-timeline) .read-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  border-radius: var(--radius-sm) 0 0 var(--radius-sm);
}

.read-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.read-item-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.read-item-user-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
}

.user-avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: var(--color-background);
  font-weight: 600;
  font-size: 0.875rem;
}

.user-name {
  font-weight: 500;
  color: var(--color-text);
  font-size: 0.95rem;
}

.read-item-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.reread-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  background: rgba(107, 116, 86, 0.15);
  color: var(--color-secondary);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid rgba(107, 116, 86, 0.3);
}

.memorable-badge-small {
  font-size: 1.25rem;
  filter: drop-shadow(0 2px 4px rgba(212, 175, 55, 0.3));
}

.read-item-dates {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text);
  font-weight: 500;
  flex-wrap: wrap;
}

.date-icon {
  font-size: 1rem;
  opacity: 0.7;
}

.time-ago {
  color: var(--color-text-light);
  font-size: 0.85rem;
  font-weight: 400;
  font-style: italic;
}

.comment-count-header {
  margin-top: 0.5rem;
}

.comment-count-badge-header {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  background: var(--color-primary);
  color: var(--color-background);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
}

.read-points {
  margin: 1.5rem 0;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(155, 72, 25, 0.05) 0%, rgba(107, 116, 86, 0.05) 100%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(155, 72, 25, 0.1);
}

.points-container {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.points-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.points-item .points-label {
  font-size: 0.8rem;
  color: var(--color-text-light);
  text-transform: lowercase;
  font-style: italic;
  letter-spacing: 0.5px;
}

.points-item .points-value {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-primary);
  line-height: 1;
}

.read-review {
  margin: 1.5rem 0;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.review-title {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.75rem;
}

.review-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
}

.read-vibe-thumbnail {
  width: 100px;
  height: 100px;
  min-width: 100px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  border: 3px solid var(--color-background);
  position: relative;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  flex-shrink: 0;
}

.read-vibe-thumbnail::before {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: var(--radius-md);
  padding: 3px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: -1;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.read-item:hover .read-vibe-thumbnail::before {
  opacity: 1;
}

.read-vibe-thumbnail:hover {
  transform: scale(1.05) rotate(2deg);
  box-shadow: var(--shadow-lg);
  z-index: 10;
}

.read-vibe-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

@media (max-width: 768px) {
  .detail-main {
    grid-template-columns: 100px 1fr;
    gap: 1rem;
  }

  .cover-section {
    max-width: 100px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .detail-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .reading-sessions-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
  }
  
  .sessions-title {
    font-size: 1.5rem;
  }
  
  .read-item {
    padding: 1rem;
  }
  
  .points-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .points-item {
    min-width: auto;
  }
  
  .read-item-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .read-vibe-thumbnail {
    width: 80px;
    height: 80px;
    min-width: 80px;
    align-self: flex-end;
    margin-top: 0.5rem;
  }
  
  .sessions-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .reads-list {
    gap: 2rem;
  }
  
  .reads-timeline {
    padding: 0 1.5rem;
  }
  
  .reads-timeline::before {
    left: 2.5rem;
  }
  
  .reads-timeline .read-item {
    margin-left: 3rem;
  }
  
  .reads-timeline .read-item::before {
    left: -3.5rem;
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
  
  .read-item {
    padding: 1.25rem;
  }
}
</style>

