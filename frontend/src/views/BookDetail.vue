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
        </div>
        <div class="detail-actions">
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
            <div class="cover-large">
              <img
                v-if="booksStore.currentBook.cover_image_url"
                :src="booksStore.currentBook.cover_image_url"
                :alt="booksStore.currentBook.title"
              />
              <div v-else class="cover-placeholder-large">
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

            <!-- Reading Sessions -->
            <div class="info-group" v-if="reads && reads.length > 0">
              <h3>Reading Sessions</h3>
              <div class="reads-list">
                <div
                  v-for="(read, index) in reads"
                  :key="read.id || index"
                  class="read-item"
                >
                  <div class="read-item-header">
                    <div>
                      <h4 class="read-item-title">
                        Read #{{ index + 1 }}
                        <span v-if="read.is_reread" class="reread-badge">Re-read</span>
                        <span v-if="read.is_memorable" class="memorable-badge-small">⭐</span>
                      </h4>
                      <div class="read-item-dates">
                        <span v-if="read.date_finished">Finished: {{ formatDate(read.date_finished) }}</span>
                        <span v-else-if="read.date_started">Started: {{ formatDate(read.date_started) }}</span>
                        <span class="read-status-badge" :class="`status-${read.read_status?.toLowerCase()}`">
                          {{ read.read_status || 'UNREAD' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="read.read_status === 'READ' && read.points" class="read-points">
                    <div class="points-row">
                      <span>Bompyallegory:</span>
                      <span class="points-value">{{ read.points.bompyallegory?.toFixed(2) || '0.00' }}</span>
                    </div>
                    <div class="points-row">
                      <span>Bompyreasonable:</span>
                      <span class="points-value">{{ read.points.bompyreasonable?.toFixed(2) || '0.00' }}</span>
                    </div>
                  </div>
                  
                  <div v-if="read.review" class="read-review">
                    <strong>Review:</strong>
                    <p>{{ read.review }}</p>
                  </div>
                  
                  <div v-if="read.read_vibe_photo_url" class="read-vibe-photo">
                    <img :src="read.read_vibe_photo_url" alt="Read vibe" />
                  </div>
                </div>
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
                  <div class="status-badge" :class="`status-${booksStore.currentBook.read_status.toLowerCase()}`">
                    {{ booksStore.currentBook.read_status }}
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
      </div>
    </div>

    <div v-else class="error">
      Boko not found
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { getFormatIcon, getFormatDisplayName } from '../utils/formats'

const route = useRoute()
const booksStore = useBooksStore()

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
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

onMounted(async () => {
  const bookId = parseInt(route.params.id)
  if (bookId) {
    await booksStore.fetchBook(bookId)
    // Load reads for this book
    try {
      const response = await api.get(`/reads/book/${bookId}`)
      reads.value = response.data || []
    } catch (err) {
      console.error('Error loading reads:', err)
      reads.value = []
    }
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
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--color-border);
}

.book-detail-title {
  font-family: var(--font-heading);
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.book-detail-author {
  font-size: 1.25rem;
  color: var(--color-text-light);
  font-family: var(--font-title);
  font-style: italic;
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
  grid-template-columns: 250px 1fr;
  gap: 2.5rem;
}

.cover-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cover-large {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-large {
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
  gap: 2rem;
}

.info-group h3 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-background);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
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

@media (max-width: 768px) {
  .detail-main {
    grid-template-columns: 1fr;
  }

  .cover-section {
    max-width: 200px;
    margin: 0 auto;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>

