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
          <span class="stat-value">{{ formatNumber(semester.stats.total_pages) }}</span>
          <span class="stat-label">Total Pages</span>
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

      <!-- Books Grid -->
      <div class="books-section">
        <h3>Books Read This Semester</h3>
        
        <div v-if="semester.books.length === 0" class="empty-books">
          <p>No books read in this semester yet.</p>
          <router-link to="/books/add" class="btn btn-primary">Add a Book</router-link>
        </div>

        <div v-else class="books-grid">
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
    </div>

    <div v-else class="error-state">
      <p>Semester not found.</p>
      <router-link to="/semesters" class="btn">Back to Semesters</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSemestersStore } from '../stores/semesters'

const route = useRoute()
const router = useRouter()
const semestersStore = useSemestersStore()

const semester = ref(null)
const loading = ref(true)

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

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
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

@media (max-width: 768px) {
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
  }

  .books-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

