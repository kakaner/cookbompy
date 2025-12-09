<template>
  <div class="container">
    <div v-if="loading" class="loading">
      Loading semester...
    </div>

    <div v-else-if="semester">
      <!-- Header -->
      <div class="page-header">
        <router-link to="/semesters" class="back-link">← Back to Semesters</router-link>
        <div class="semester-header-content">
          <div class="semester-title-row">
            <h2>{{ semester.display_name }}</h2>
            <span v-if="semester.is_current" class="current-badge">Current</span>
          </div>
          <p class="semester-dates">{{ semester.date_range_display }}</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-bar" v-if="semester.stats">
        <div class="stat-card">
          <span class="stat-value">{{ semester.stats.books_read }}</span>
          <span class="stat-label">Books Read</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ semester.stats.total_unviewnered }}</span>
          <span class="stat-label">Unviewnered</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ semester.stats.commented }}</span>
          <span class="stat-label">Commented</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ semester.stats.total_points_allegory.toFixed(2) }}</span>
          <span class="stat-label">Points (bompyallegory)</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ semester.stats.total_points_reasonable.toFixed(2) }}</span>
          <span class="stat-label">Points (bompyreasonable)</span>
        </div>
      </div>

      <!-- Semester Comments -->
      <div class="semester-comments-section">
        <CommentSection
          :semester-id="semester.id"
          :semester-author-id="semester.user_id"
        />
      </div>

      <!-- Books Section - Horizontal Scrollable -->
      <div class="books-section">
        <h3>Books Read This Semester</h3>
        
        <div v-if="semester.books.length === 0" class="empty-books">
          <p>No books read in this semester yet.</p>
          <router-link to="/books/add" class="btn btn-primary">Add a Book</router-link>
        </div>

        <div v-else class="books-scroll">
          <div
            v-for="book in semester.books"
            :key="book.id"
            class="book-card"
            :class="{ 'memorable': book.is_memorable }"
            @click="goToBook(book.id)"
          >
            <div class="book-cover">
              <img v-if="book.cover_image_url" :src="book.cover_image_url" :alt="book.title" />
              <div v-else class="cover-placeholder">
                {{ book.title.charAt(0) }}
              </div>
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ book.title }}</h4>
              <p class="book-author">{{ book.author }}</p>
              <div class="book-meta">
                <span v-if="book.date_finished" class="finish-date">
                  {{ formatDate(book.date_finished) }}
                </span>
                <span v-if="book.calculated_points_allegory" class="points-badge">
                  {{ book.calculated_points_allegory.toFixed(1) }} pts
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reads Timeline -->
      <div v-if="semester.books.length > 0" class="reads-timeline-section">
        <div class="timeline-header">
          <h3>Reading Timeline</h3>
          <div class="timeline-controls">
            <input
              v-model="timelineSearch"
              type="text"
              class="timeline-search"
              placeholder="Search reads by title, author..."
              @input="filterTimeline"
            />
            <select v-model="timelineSort" @change="filterTimeline" class="timeline-sort">
              <option value="date_desc">Most Recent First</option>
              <option value="date_asc">Oldest First</option>
              <option value="title_asc">Title (A-Z)</option>
              <option value="title_desc">Title (Z-A)</option>
              <option value="author_asc">Author (A-Z)</option>
              <option value="author_desc">Author (Z-A)</option>
            </select>
          </div>
        </div>
        <div class="reads-timeline">
          <div
            v-for="(book, index) in sortedBooks"
            :key="book.read_id"
            class="read-timeline-item"
          >
            <!-- Timeline connector -->
            <div v-if="index < sortedBooks.length - 1" class="timeline-connector"></div>
            <div class="timeline-dot-small"></div>
            
            <!-- Read card -->
            <div class="read-card">
              <div class="read-card-header">
                <div class="read-cover-thumbnail">
                  <img v-if="book.cover_image_url" :src="book.cover_image_url" :alt="book.title" />
                  <div v-else class="cover-thumbnail-placeholder">
                    {{ book.title.charAt(0) }}
                  </div>
                </div>
                <div class="read-card-info">
                  <div class="read-date">{{ formatFullDate(book.date_finished) }}</div>
                  <h4 class="read-title">{{ book.title }}</h4>
                  <p class="read-author">{{ book.author }}</p>
                  <div class="read-meta-tags">
                    <span v-if="book.book_type" class="meta-tag">{{ book.book_type }}</span>
                    <span v-if="book.format" class="meta-tag">{{ getFormatDisplayName(book.format) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Review (Viewner) -->
              <div v-if="book.review" class="read-viewner">
                <h5 class="viewner-title">Viewner</h5>
                <div class="viewner-content">{{ book.review }}</div>
              </div>
              
              <!-- Comments Section -->
              <div class="read-comments">
                <CommentSection
                  :read-id="book.read_id"
                  :read-author-id="semester.user_id"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <p>Semester not found.</p>
      <router-link to="/semesters" class="btn">Back to Semesters</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSemestersStore } from '../stores/semesters'
import { getFormatDisplayName } from '../utils/formats'
import CommentSection from '../components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const semestersStore = useSemestersStore()

const semester = ref(null)
const loading = ref(true)
const timelineSearch = ref('')
const timelineSort = ref('date_desc')

// Sort and filter books
const sortedBooks = computed(() => {
  if (!semester.value || !semester.value.books) return []
  
  let books = [...semester.value.books]
  
  // Apply search filter
  if (timelineSearch.value) {
    const searchLower = timelineSearch.value.toLowerCase()
    books = books.filter(book => 
      book.title.toLowerCase().includes(searchLower) ||
      book.author.toLowerCase().includes(searchLower)
    )
  }
  
  // Apply sorting
  if (timelineSort.value === 'date_desc') {
    books.sort((a, b) => {
      const dateA = a.date_finished ? new Date(a.date_finished) : new Date(0)
      const dateB = b.date_finished ? new Date(b.date_finished) : new Date(0)
      return dateB - dateA
    })
  } else if (timelineSort.value === 'date_asc') {
    books.sort((a, b) => {
      const dateA = a.date_finished ? new Date(a.date_finished) : new Date(0)
      const dateB = b.date_finished ? new Date(b.date_finished) : new Date(0)
      return dateA - dateB
    })
  } else if (timelineSort.value === 'title_asc') {
    books.sort((a, b) => a.title.localeCompare(b.title))
  } else if (timelineSort.value === 'title_desc') {
    books.sort((a, b) => b.title.localeCompare(a.title))
  } else if (timelineSort.value === 'author_asc') {
    books.sort((a, b) => a.author.localeCompare(b.author))
  } else if (timelineSort.value === 'author_desc') {
    books.sort((a, b) => b.author.localeCompare(a.author))
  }
  
  return books
})

const filterTimeline = () => {
  // The computed property will automatically update
}

const fetchSemesterData = async () => {
  loading.value = true
  try {
    const semesterNumber = parseInt(route.params.number)
    semester.value = await semestersStore.fetchSemester(semesterNumber)
  } catch (error) {
    console.error('Failed to fetch semester:', error)
    semester.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSemesterData()
})

watch(() => route.params.number, () => {
  fetchSemesterData()
})

const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatFullDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric',
    month: 'long', 
    day: 'numeric' 
  })
}

const goToBook = (bookId) => {
  router.push(`/books/${bookId}`)
}
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-block;
  color: var(--color-text-light);
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.back-link:hover {
  color: var(--color-primary);
}

.semester-header-content {
  margin-bottom: 1.5rem;
}

.semester-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.semester-title-row h2 {
  margin: 0;
}

.current-badge {
  background: var(--color-primary);
  color: var(--color-background);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.semester-dates {
  color: var(--color-text-light);
  margin-top: 0.5rem;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 1.25rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.stat-value {
  display: block;
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 0.25rem;
}

.books-section h3 {
  margin-bottom: 1.5rem;
  font-family: var(--font-heading);
}

.empty-books {
  text-align: center;
  padding: 3rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  color: var(--color-text-light);
}

.empty-books .btn {
  margin-top: 1rem;
}

.books-scroll {
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 1rem;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}

.books-scroll::-webkit-scrollbar {
  height: 8px;
}

.books-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.books-scroll::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.books-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-light);
}

.book-card {
  min-width: 180px;
  max-width: 180px;
  flex-shrink: 0;
}

.book-card {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.book-card.memorable {
  border: 2px solid var(--color-accent);
  box-shadow: 0 2px 12px rgba(212, 175, 55, 0.2);
  position: relative;
}

.book-card.memorable::before {
  content: '⭐';
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 1rem;
  background: rgba(212, 175, 55, 0.9);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.book-cover {
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: var(--color-border);
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-border) 0%, #C5BFB5 100%);
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--color-text-light);
  font-family: var(--font-heading);
}

.book-info {
  padding: 1rem;
}

.book-title {
  font-family: var(--font-title);
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.finish-date {
  color: var(--color-text-light);
}

.points-badge {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  font-weight: 600;
}

.error-state {
  text-align: center;
  padding: 3rem;
}

/* Reads Timeline Section */
.reads-timeline-section {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid var(--color-border);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.timeline-header h3 {
  font-family: var(--font-heading);
  margin: 0;
}

.timeline-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.timeline-search {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.9rem;
  min-width: 200px;
}

.timeline-search:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.timeline-sort {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.9rem;
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
}

.timeline-sort:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.reads-timeline-section h3 {
  margin-bottom: 2rem;
  font-family: var(--font-heading);
}

.reads-timeline {
  position: relative;
  padding-left: 2rem;
}

.read-timeline-item {
  position: relative;
  margin-bottom: 3rem;
  padding-left: 2rem;
}

.timeline-connector {
  position: absolute;
  left: 0.5rem;
  top: 4rem;
  bottom: -3rem;
  width: 2px;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-secondary) 100%);
}

.timeline-dot-small {
  position: absolute;
  left: -0.5rem;
  top: 1rem;
  width: 12px;
  height: 12px;
  background: var(--color-primary);
  border: 3px solid var(--color-background);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-primary);
  z-index: 1;
}

.read-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.read-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.read-card-header {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.read-cover-thumbnail {
  width: 80px;
  height: 120px;
  min-width: 80px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.read-cover-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-border) 0%, #C5BFB5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-light);
  font-size: 1.5rem;
  font-weight: 600;
  font-family: var(--font-heading);
}

.read-card-info {
  flex: 1;
  min-width: 0;
}

.read-date {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.read-title {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.read-author {
  font-size: 0.95rem;
  color: var(--color-text-light);
  margin-bottom: 0.75rem;
  font-style: italic;
}

.read-meta-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.meta-tag {
  padding: 0.25rem 0.75rem;
  background: rgba(155, 72, 25, 0.1);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(155, 72, 25, 0.2);
}

.read-viewner {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.viewner-title {
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.75rem;
}

.viewner-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
}

.read-comments {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
  }

  .book-card {
    min-width: 150px;
    max-width: 150px;
  }

  .read-card-header {
    flex-direction: column;
  }

  .read-cover-thumbnail {
    width: 60px;
    height: 90px;
    align-self: flex-start;
  }

  .reads-timeline {
    padding-left: 1.5rem;
  }

  .read-timeline-item {
    padding-left: 1.5rem;
  }

  .timeline-dot-small {
    left: -0.75rem;
  }
}
</style>

