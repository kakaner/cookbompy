<template>
  <div class="book-card" @click="goToDetail">
    <div class="book-content">
      <div class="book-cover">
        <img v-if="book.cover_image_url" :src="book.cover_image_url" :alt="book.title" />
        <div v-else class="cover-placeholder">
          {{ book.title.charAt(0) }}
        </div>
      </div>
      <div class="book-info">
        <h3 class="book-title">{{ book.title }}</h3>
        <p class="book-author">{{ book.author }}</p>
        <div class="book-meta">
          <span v-if="publicationYear" class="publication-year">{{ publicationYear }}</span>
          <span v-if="book.has_review" class="viewner-badge">Viewnered</span>
        </div>
        <div v-if="uniqueReaders.length > 0" class="readers-list">
          <div
            v-for="reader in uniqueReaders"
            :key="reader.id"
            class="reader-avatar"
            :title="reader.display_name || reader.username"
          >
            <img v-if="reader.profile_photo_url" :src="reader.profile_photo_url" :alt="reader.display_name || reader.username" />
            <span v-else>{{ (reader.display_name || reader.username).charAt(0).toUpperCase() }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="card-badges">
      <span v-if="mostRecentReadSemester" class="semester-badge">
        {{ mostRecentReadSemester }}
      </span>
      <span v-if="mostRecentReadPoints !== null" class="points-badge" :title="mostRecentReadPointsBreakdown">
        {{ mostRecentReadPoints.toFixed(2) }} pts
      </span>
      <span class="format-icon" :title="getFormatDisplayName(book.format)">
        <img v-if="book.format === 'KINDLE'" src="/kindle-icon.svg" alt="Kindle" class="kindle-icon" />
        <span v-else>{{ getFormatIcon(book.format) }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getFormatIcon, getFormatDisplayName } from '../utils/formats'
import { calculateSemesterNumber, getSemesterDisplayName } from '../utils/semesters'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const goToDetail = () => {
  router.push(`/books/${props.book.id}`)
}

// Get most recent read and its semester
const mostRecentRead = computed(() => {
  if (!props.book.reads || props.book.reads.length === 0) return null
  // Get reads that are finished, sorted by date_finished desc
  const finishedReads = props.book.reads
    .filter(read => read.read_status === 'READ' && read.date_finished)
    .sort((a, b) => new Date(b.date_finished) - new Date(a.date_finished))
  return finishedReads[0] || null
})

const mostRecentReadSemester = computed(() => {
  if (!mostRecentRead.value || !mostRecentRead.value.date_finished) return null
  try {
    const semesterNum = calculateSemesterNumber(new Date(mostRecentRead.value.date_finished))
    return getSemesterDisplayName(semesterNum)
  } catch (e) {
    return null
  }
})

const mostRecentReadPoints = computed(() => {
  if (!mostRecentRead.value) return null
  // Points might be in different formats
  if (mostRecentRead.value.points?.bompyallegory) {
    return mostRecentRead.value.points.bompyallegory
  }
  if (mostRecentRead.value.calculated_points_allegory) {
    return mostRecentRead.value.calculated_points_allegory / 100.0 // Convert from integer
  }
  return null
})

const mostRecentReadPointsBreakdown = computed(() => {
  return mostRecentRead.value?.points?.breakdown || ''
})

const publicationYear = computed(() => {
  if (!props.book.publication_date) return null
  const date = new Date(props.book.publication_date)
  return date.getFullYear()
})

// Get unique users who have read this book
const uniqueReaders = computed(() => {
  if (!props.book.reads || props.book.reads.length === 0) return []
  
  // Get unique users from reads
  const userMap = new Map()
  props.book.reads.forEach(read => {
    if (read.user) {
      // Use user info from read if available
      if (!userMap.has(read.user.id)) {
        userMap.set(read.user.id, {
          id: read.user.id,
          username: read.user.username,
          display_name: read.user.display_name || read.user.username,
          profile_photo_url: read.user.profile_photo_url
        })
      }
    } else if (read.user_id) {
      // Fallback to user_id if user object not available
      if (!userMap.has(read.user_id)) {
        userMap.set(read.user_id, {
          id: read.user_id,
          username: `user${read.user_id}`,
          display_name: `User ${read.user_id}`,
          profile_photo_url: null
        })
      }
    }
  })
  
  return Array.from(userMap.values())
})
</script>

<style scoped>
.book-card {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 1.5rem;
  padding-bottom: 3rem;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  cursor: pointer;
  position: relative;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.book-content {
  display: flex;
  gap: 1rem;
}

.book-cover {
  width: 70px;
  min-width: 70px;
  height: 105px;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.book-cover img {
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
  font-size: 1.5rem;
  font-weight: 600;
  font-family: var(--font-heading);
}

.book-info {
  flex: 1;
  min-width: 0;
}

.book-title {
  font-family: var(--font-title);
  font-size: 1.05rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  line-height: 1.3;
  color: var(--color-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-badges {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.semester-badge {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.12) 0%, rgba(212, 175, 55, 0.08) 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  color: var(--color-primary);
  padding: 0.3rem 0.75rem;
  border-radius: 14px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
}

.review-badge {
  background: linear-gradient(135deg, rgba(107, 116, 86, 0.12) 0%, rgba(107, 116, 86, 0.08) 100%);
  border: 1px solid rgba(107, 116, 86, 0.3);
  color: var(--color-secondary);
  padding: 0.3rem 0.65rem;
  border-radius: 14px;
  font-size: 0.7rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.review-badge.reviewed {
  background: linear-gradient(135deg, rgba(155, 72, 25, 0.12) 0%, rgba(155, 72, 25, 0.08) 100%);
  border: 1px solid rgba(155, 72, 25, 0.3);
  color: var(--color-primary);
}

.points-badge {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.1) 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  color: var(--color-primary);
  padding: 0.3rem 0.75rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  backdrop-filter: blur(10px);
  cursor: help;
}

.format-icon {
  font-size: 1.2rem;
  cursor: help;
  display: inline-flex;
  align-items: center;
}

.kindle-icon {
  width: 1.2rem;
  height: 1.2rem;
  object-fit: contain;
}

.book-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.publication-year {
  font-weight: 500;
}

.viewner-badge {
  background: linear-gradient(135deg, rgba(155, 72, 25, 0.12) 0%, rgba(155, 72, 25, 0.08) 100%);
  border: 1px solid rgba(155, 72, 25, 0.3);
  color: var(--color-primary);
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.readers-list {
  display: flex;
  gap: 0.375rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.reader-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  overflow: hidden;
  border: 1.5px solid var(--color-background);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.reader-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>

