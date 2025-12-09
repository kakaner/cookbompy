<template>
  <div class="shareable-view public-view">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading book...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2>Link Not Available</h2>
      <p>{{ error }}</p>
      <router-link to="/" class="btn btn-primary">Go to Home</router-link>
    </div>
    
    <div v-else-if="book" class="shared-book-container">
      <!-- Header -->
      <div class="shared-header">
        <div class="shared-badge">Shared Book</div>
        <p class="shared-by">
          Shared by 
          <span class="sharing-user">
            <img 
              v-if="book.sharing_user.profile_photo_url" 
              :src="book.sharing_user.profile_photo_url" 
              :alt="book.sharing_user.display_name || book.sharing_user.username"
              class="user-avatar-small"
            />
            <span v-else class="user-avatar-placeholder">
              {{ (book.sharing_user.display_name || book.sharing_user.username).charAt(0).toUpperCase() }}
            </span>
            {{ book.sharing_user.display_name || book.sharing_user.username }}
          </span>
        </p>
      </div>
      
      <!-- Book Content -->
      <div class="shared-book-content">
        <!-- Cover and Basic Info -->
        <div class="shared-cover-section">
          <div class="shared-cover">
            <img
              v-if="book.cover_image_url"
              :src="book.cover_image_url"
              :alt="book.title"
            />
            <div v-else class="cover-placeholder">
              {{ book.title.charAt(0) }}
            </div>
          </div>
        </div>
        
        <div class="shared-info-section">
          <h1 class="shared-title">{{ book.title }}</h1>
          <p class="shared-author">by {{ book.author }}</p>
          
          <!-- Format -->
          <div v-if="book.format" class="shared-format">
            <span class="format-icon">{{ getFormatIcon(book.format) }}</span>
            <span>{{ getFormatDisplayName(book.format) }}</span>
          </div>
          
          <!-- Basic Metadata -->
          <div class="shared-metadata">
            <div v-if="book.publication_date" class="metadata-item">
              <span class="metadata-label">Published:</span>
              <span class="metadata-value">{{ formatDate(book.publication_date) }}</span>
            </div>
            <div v-if="book.publisher" class="metadata-item">
              <span class="metadata-label">Publisher:</span>
              <span class="metadata-value">{{ book.publisher }}</span>
            </div>
            <div v-if="book.page_count" class="metadata-item">
              <span class="metadata-label">Pages:</span>
              <span class="metadata-value">{{ book.page_count }}</span>
            </div>
            <div v-if="book.language" class="metadata-item">
              <span class="metadata-label">Language:</span>
              <span class="metadata-value">{{ book.language.toUpperCase() }}</span>
            </div>
            <div v-if="book.book_type" class="metadata-item">
              <span class="metadata-label">Type:</span>
              <span class="metadata-value">{{ book.book_type }}</span>
            </div>
          </div>
          
          <!-- Genres -->
          <div v-if="book.genres && book.genres.length > 0" class="shared-genres">
            <div
              v-for="genre in book.genres"
              :key="genre"
              class="genre-tag"
            >
              {{ genre }}
            </div>
          </div>
          
          <!-- Synopsis -->
          <div v-if="book.description" class="shared-synopsis">
            <h3>Synopsis</h3>
            <p>{{ book.description }}</p>
            <div v-if="book.description_source" class="synopsis-source">
              <span class="source-icon">{{ getSourceIcon(book.description_source) }}</span>
              <span>Synopsis from {{ book.description_source }}</span>
            </div>
          </div>
          
          <!-- Sharing User's Review -->
          <div v-if="book.sharing_user_review || book.sharing_user_rating || book.sharing_user_date_read" class="shared-review-section">
            <h3>
              Review by {{ book.sharing_user.display_name || book.sharing_user.username }}
            </h3>
            
            <!-- Date Read -->
            <div v-if="book.sharing_user_date_read" class="shared-date-read">
              <span class="date-label">Read on:</span>
              <span class="date-value">{{ formatDate(book.sharing_user_date_read) }}</span>
            </div>
            
            <!-- Rating -->
            <div v-if="book.sharing_user_rating" class="shared-rating">
              <span class="rating-label">Rating:</span>
              <div class="rating-display">
                <span class="rating-stars">{{ formatRating(book.sharing_user_rating) }}</span>
                <span class="rating-value">{{ book.sharing_user_rating }}/10</span>
              </div>
            </div>
            
            <!-- Review Content -->
            <div v-if="book.sharing_user_review" class="review-content">{{ book.sharing_user_review }}</div>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="shared-footer">
        <p class="footer-text">
          This is a shared view. To see more and manage your own library, 
          <router-link to="/register">create an account</router-link> or 
          <router-link to="/login">log in</router-link>.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { getFormatIcon, getFormatDisplayName } from '../utils/formats'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const book = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return null
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatRating = (rating) => {
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  return '⭐'.repeat(fullStars) + (hasHalfStar ? '½' : '')
}

const getSourceIcon = (source) => {
  const icons = {
    'GOODREADS': '📚',
    'GOOGLE_BOOKS': '🔍',
    'AMAZON': '📦',
    'WIKIPEDIA': '🌐',
    'MANUAL': '✍️'
  }
  return icons[source] || '📄'
}

onMounted(async () => {
  const token = route.params.token
  
  try {
    const response = await api.get(`/shareable-links/token/${token}`)
    book.value = response.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'This shareable link was not found.'
    } else if (err.response?.status === 410) {
      error.value = 'This shareable link has expired or been revoked.'
    } else {
      error.value = 'Unable to load this shared book. The link may be invalid or expired.'
    }
    console.error('Error loading shared book:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.shareable-view {
  min-height: 100vh;
  background: var(--color-background);
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-container h2 {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.error-container p {
  color: var(--color-text-light);
  margin-bottom: 1.5rem;
}

.shared-book-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.shared-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--color-border);
}

.shared-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: var(--color-background);
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.shared-by {
  color: var(--color-text-light);
  font-size: 0.95rem;
}

.sharing-user {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text);
  font-weight: 500;
}

.user-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.shared-book-content {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.shared-cover {
  width: 200px;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.shared-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-border) 0%, #C5BFB5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-light);
  font-size: 4rem;
  font-weight: 600;
  font-family: var(--font-heading);
}

.shared-info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.shared-title {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  line-height: 1.2;
}

.shared-author {
  font-size: 1.25rem;
  color: var(--color-text-light);
  margin: 0;
}

.shared-format {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--color-text);
}

.format-icon {
  font-size: 1.5rem;
}

.shared-metadata {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.metadata-value {
  font-size: 0.95rem;
  color: var(--color-text);
  font-weight: 500;
}

.shared-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  font-size: 0.875rem;
  color: var(--color-text);
}

.shared-synopsis {
  margin-top: 1rem;
}

.shared-synopsis h3 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
  color: var(--color-text);
}

.shared-synopsis p {
  color: var(--color-text);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.synopsis-source {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-top: 0.5rem;
}

.source-icon {
  font-size: 1rem;
}

.shared-review-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.shared-review-section h3 {
  font-family: var(--font-heading);
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.shared-date-read {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.date-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.date-value {
  font-size: 0.95rem;
  color: var(--color-text);
  font-weight: 500;
}

.shared-rating {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.rating-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.review-content {
  color: var(--color-text);
  line-height: 1.6;
  white-space: pre-wrap;
}

.rating-stars {
  font-size: 1.5rem;
}

.rating-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-primary);
}

.shared-footer {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid var(--color-border);
  text-align: center;
}

.footer-text {
  color: var(--color-text-light);
  font-size: 0.95rem;
}

.footer-text a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.footer-text a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .shared-book-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .shared-cover {
    width: 150px;
    height: 225px;
    margin: 0 auto;
  }
  
  .shared-title {
    font-size: 1.5rem;
    text-align: center;
  }
  
  .shared-author {
    text-align: center;
  }
  
  .shared-metadata {
    grid-template-columns: 1fr;
  }
}
</style>

