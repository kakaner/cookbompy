<template>
  <div class="container">
    <div class="page-header">
      <h2>Semesters</h2>
      <p class="page-subtitle">Your reading journey through time</p>
    </div>

    <!-- Current Semester Indicator -->
    <div v-if="semestersStore.currentSemester" class="current-semester-indicator">
      <span class="current-label">Current Semester:</span>
      <span class="current-number">{{ semestersStore.currentSemester }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="semestersStore.loading && semestersStore.semesters.length === 0" class="loading">
      Loading semesters...
    </div>

    <!-- Semesters Timeline -->
    <div v-else class="semesters-timeline">
      <div
        v-for="semester in semestersStore.semesters"
        :key="semester.semester_number"
        :class="['semester-card', { 'is-current': semester.is_current }]"
      >
        <!-- Timeline Line -->
        <div class="timeline-line"></div>
        <div class="timeline-dot" :class="{ 'is-current': semester.is_current }"></div>

        <!-- Semester Content -->
        <div class="semester-content">
          <!-- Header -->
          <div class="semester-header">
            <div class="semester-title-section">
              <div v-if="editingSemester === semester.semester_number" class="edit-name-form">
                <input
                  v-model="editName"
                  type="text"
                  class="edit-name-input"
                  placeholder="Custom name (e.g., 'Summer of Sci-Fi')"
                  @keydown.enter="saveCustomName(semester.semester_number)"
                  @keydown.escape="cancelEdit"
                  ref="editInput"
                />
                <div class="edit-actions">
                  <button @click="saveCustomName(semester.semester_number)" class="btn-save">Save</button>
                  <button @click="cancelEdit" class="btn-cancel">Cancel</button>
                </div>
              </div>
              <template v-else>
                <h3 class="semester-name" @click="startEdit(semester)">
                  {{ semester.display_name }}
                  <span class="edit-icon">✏️</span>
                </h3>
                <span class="semester-number-badge" v-if="semester.custom_name">
                  Semester {{ semester.semester_number }}
                </span>
              </template>
            </div>
            <span v-if="semester.is_current" class="current-badge">Current</span>
          </div>

          <!-- Date Range -->
          <p class="semester-dates">{{ semester.date_range_display }}</p>

          <!-- Stats Grid -->
          <div class="stats-grid" v-if="semester.stats">
            <div class="stat-item">
              <span class="stat-value">{{ semester.stats.books_read }}</span>
              <span class="stat-label">Books</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatNumber(semester.stats.total_pages) }}</span>
              <span class="stat-label">Pages</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ semester.stats.total_points_allegory.toFixed(1) }}</span>
              <span class="stat-label">Points</span>
            </div>
          </div>

          <!-- Book Previews -->
          <div v-if="semester.book_previews && semester.book_previews.length > 0" class="book-previews">
            <div class="preview-covers">
              <div
                v-for="book in semester.book_previews"
                :key="book.id"
                class="preview-cover"
                :class="{ 'memorable': book.is_memorable }"
                :title="book.title"
              >
                <img v-if="book.cover_image_url" :src="book.cover_image_url" :alt="book.title" />
                <div v-else class="preview-placeholder">
                  {{ book.title.charAt(0) }}
                </div>
                <span v-if="book.is_memorable" class="memorable-indicator">⭐</span>
              </div>
            </div>
          </div>

          <!-- View Details Link -->
          <router-link
            :to="`/semesters/${semester.semester_number}`"
            class="view-details-link"
          >
            View Details →
          </router-link>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="semestersStore.hasMore" class="load-more-container">
        <button
          @click="semestersStore.loadMore"
          class="btn load-more-btn"
          :disabled="semestersStore.loading"
        >
          {{ semestersStore.loading ? 'Loading...' : 'View More Semesters' }}
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="semestersStore.semesters.length === 0 && !semestersStore.loading" class="empty-state">
        <p>No semesters to display yet. Start adding books with "Date Finished" to see your reading timeline!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useSemestersStore } from '../stores/semesters'

const semestersStore = useSemestersStore()

const editingSemester = ref(null)
const editName = ref('')
const editInput = ref(null)

onMounted(async () => {
  await semestersStore.fetchSemesters(true)
})

const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString()
}

const startEdit = async (semester) => {
  editingSemester.value = semester.semester_number
  editName.value = semester.custom_name || ''
  await nextTick()
  if (editInput.value) {
    editInput.value.focus()
  }
}

const cancelEdit = () => {
  editingSemester.value = null
  editName.value = ''
}

const saveCustomName = async (semesterNumber) => {
  try {
    await semestersStore.updateSemesterName(semesterNumber, editName.value.trim() || null)
    editingSemester.value = null
    editName.value = ''
  } catch (error) {
    console.error('Failed to save custom name:', error)
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.page-subtitle {
  color: var(--color-text-light);
  margin-top: 0.5rem;
}

.current-semester-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  padding: 0.75rem 1.25rem;
  margin-bottom: 2rem;
}

.current-label {
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.current-number {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
}

.semesters-timeline {
  position: relative;
  padding-left: 2.5rem;
}

.semester-card {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-line {
  position: absolute;
  left: -2rem;
  top: 0;
  bottom: -2rem;
  width: 2px;
  background: var(--color-border);
}

.semester-card:last-child .timeline-line {
  bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: calc(-2rem - 6px);
  top: 1rem;
  width: 14px;
  height: 14px;
  background: var(--color-surface);
  border: 3px solid var(--color-border);
  border-radius: 50%;
  z-index: 1;
}

.timeline-dot.is-current {
  background: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px var(--color-primary-light);
}

.semester-content {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.semester-card.is-current .semester-content {
  border: 2px solid var(--color-primary);
}

.semester-content:hover {
  box-shadow: var(--shadow-md);
}

.semester-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.semester-title-section {
  flex: 1;
}

.semester-name {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.semester-name:hover {
  color: var(--color-primary);
}

.edit-icon {
  font-size: 0.875rem;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.semester-name:hover .edit-icon {
  opacity: 1;
}

.semester-number-badge {
  display: inline-block;
  font-size: 0.75rem;
  color: var(--color-text-light);
  background: var(--color-background);
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
  margin-top: 0.25rem;
}

.current-badge {
  background: var(--color-primary);
  color: var(--color-background);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.edit-name-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.edit-name-input {
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  font-family: var(--font-body);
  width: 100%;
  max-width: 300px;
}

.edit-name-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-save, .btn-cancel {
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.btn-save {
  background: var(--color-primary);
  color: var(--color-background);
}

.btn-cancel {
  background: var(--color-border);
  color: var(--color-text);
}

.semester-dates {
  color: var(--color-text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.stats-grid {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.view-details-link {
  display: inline-block;
  color: var(--color-primary);
  font-weight: 500;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.view-details-link:hover {
  color: var(--color-secondary);
  text-decoration: underline;
}

.load-more-container {
  text-align: center;
  padding: 2rem 0;
}

.load-more-btn {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  color: var(--color-text);
  padding: 0.875rem 2rem;
}

.load-more-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .semesters-timeline {
    padding-left: 1.5rem;
  }

  .timeline-line {
    left: -1rem;
  }

  .timeline-dot {
    left: calc(-1rem - 6px);
  }

  .stats-grid {
    gap: 1rem;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .preview-cover {
    width: 40px;
    height: 60px;
  }
}

.book-previews {
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.preview-covers {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.preview-cover {
  position: relative;
  width: 50px;
  height: 75px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.preview-cover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.preview-cover.memorable {
  border: 2px solid var(--color-accent);
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3);
}

.preview-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-border) 0%, #C5BFB5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-light);
  font-size: 1.25rem;
  font-weight: 600;
  font-family: var(--font-heading);
}

.memorable-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 0.75rem;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

