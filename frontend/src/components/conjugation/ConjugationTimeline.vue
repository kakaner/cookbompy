<template>
  <div v-if="loading" class="loading">Loading conjugation highlights...</div>
  <div v-else-if="books.length === 0" class="empty-state">
    <p>No high conjugation reads yet. Read books around the same time to see this feature!</p>
  </div>
  <div v-else class="conjugation-list">
    <div
      v-for="book in books"
      :key="book.book_id"
      class="conjugation-card"
    >
      <div class="conjugation-header">
        <div>
          <div class="conjugation-title">{{ book.title }}</div>
          <div class="book-author-small">{{ book.author }}</div>
        </div>
        <div
          class="conjugation-score"
          :class="`score-${book.conjugation_score}`"
        >
          ● {{ book.conjugation_score.charAt(0).toUpperCase() + book.conjugation_score.slice(1) }} Conjugation
        </div>
      </div>

      <div class="timeline-viz">
        <div class="timeline-dates">
          <span>{{ formatDate(getEarliestDate(book.reading_periods)) }}</span>
          <span>{{ formatDate(getLatestDate(book.reading_periods)) }}</span>
        </div>
        <div class="reading-bars">
          <div
            v-for="(user, index) in book.users"
            :key="user.user_id"
            class="reading-bar-wrapper"
            :style="getBarPosition(book.reading_periods[user.username], book.reading_periods, index)"
          >
            <div
              class="reading-bar"
              :class="{ overlap: isOverlapping(book.reading_periods[user.username], book.overlap_dates) }"
              :style="getBarStyle(book.reading_periods[user.username], book.reading_periods)"
              :title="getBarTooltip(user, book.reading_periods[user.username])"
            >
              <span class="reader-label">{{ user.display_name }}</span>
              <span v-if="user.format" class="format-icon-small" :title="user.format">
                {{ getFormatIcon(user.format) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="overlap-summary">
        <strong>Overlap:</strong>
        <span v-if="book.overlap_dates && book.overlap_dates.length === 2">
          All readers finished within {{ getDaysDifference(book.finish_dates) }} days
          <span v-if="book.overlap_percentage > 0">
            • {{ book.overlap_percentage.toFixed(0) }}% reading period overlap
          </span>
        </span>
        <span v-else>
          All readers finished within {{ getDaysDifference(book.finish_dates) }} days
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getFormatIcon } from '../../utils/formats'

const props = defineProps({
  books: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const getEarliestDate = (readingPeriods) => {
  if (!readingPeriods || Object.keys(readingPeriods).length === 0) return null
  const dates = Object.values(readingPeriods).map(p => p.start_date)
  return dates.sort()[0]
}

const getLatestDate = (readingPeriods) => {
  if (!readingPeriods || Object.keys(readingPeriods).length === 0) return null
  const dates = Object.values(readingPeriods).map(p => p.end_date)
  return dates.sort().reverse()[0]
}

const getDaysDifference = (finishDates) => {
  if (!finishDates || Object.keys(finishDates).length < 2) return 0
  const dates = Object.values(finishDates).map(d => new Date(d))
  dates.sort((a, b) => a - b)
  return Math.ceil((dates[dates.length - 1] - dates[0]) / (1000 * 60 * 60 * 24))
}

const getBarPosition = (period, allPeriods, index) => {
  if (!period || !allPeriods) return {}
  
  const earliest = new Date(getEarliestDate(allPeriods))
  const latest = new Date(getLatestDate(allPeriods))
  const totalRange = latest - earliest
  
  if (totalRange === 0) return { top: `${index * 25}px` }
  
  const start = new Date(period.start_date)
  const leftPercent = ((start - earliest) / totalRange) * 100
  
  return {
    top: `${index * 25}px`,
    left: `${Math.max(0, leftPercent)}%`
  }
}

const getBarStyle = (period, allPeriods) => {
  if (!period || !allPeriods) return {}
  
  const earliest = new Date(getEarliestDate(allPeriods))
  const latest = new Date(getLatestDate(allPeriods))
  const totalRange = latest - earliest
  
  if (totalRange === 0) return { width: '100%' }
  
  const start = new Date(period.start_date)
  const end = new Date(period.end_date)
  const widthPercent = ((end - start) / totalRange) * 100
  
  return {
    width: `${Math.max(5, widthPercent)}%`
  }
}

const isOverlapping = (period, overlapDates) => {
  if (!period || !overlapDates || overlapDates.length !== 2) return false
  
  const periodStart = new Date(period.start_date)
  const periodEnd = new Date(period.end_date)
  const overlapStart = new Date(overlapDates[0])
  const overlapEnd = new Date(overlapDates[1])
  
  return (
    (periodStart <= overlapEnd && periodEnd >= overlapStart)
  )
}

const getBarTooltip = (user, period) => {
  if (!period) return user.display_name
  const start = formatDate(period.start_date)
  const end = formatDate(period.end_date)
  return `${user.display_name}: ${start} - ${end}`
}
</script>

<style scoped>
.conjugation-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.conjugation-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(44, 44, 44, 0.08);
}

.conjugation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.conjugation-title {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.book-author-small {
  font-size: 0.8rem;
  color: var(--color-secondary);
}

.conjugation-score {
  padding: 0.5rem 1rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid;
}

.conjugation-score.score-high {
  background: linear-gradient(135deg, rgba(81, 207, 102, 0.15) 0%, rgba(81, 207, 102, 0.1) 100%);
  color: #2B8A3E;
  border-color: rgba(81, 207, 102, 0.3);
}

.conjugation-score.score-medium {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.1) 100%);
  color: #B8860B;
  border-color: rgba(212, 175, 55, 0.3);
}

.conjugation-score.score-low {
  background: linear-gradient(135deg, rgba(155, 72, 25, 0.15) 0%, rgba(155, 72, 25, 0.1) 100%);
  color: #9B4819;
  border-color: rgba(155, 72, 25, 0.3);
}

.timeline-viz {
  position: relative;
  min-height: 120px;
  background: var(--color-background);
  border-radius: var(--radius-sm);
  padding: 1rem;
  overflow-x: auto;
}

.timeline-dates {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin-bottom: 0.75rem;
}

.reading-bars {
  position: relative;
  min-height: 60px;
  margin-top: 1.5rem;
}

.reading-bar-wrapper {
  position: absolute;
  height: 12px;
}

.reading-bar {
  position: relative;
  height: 12px;
  background: var(--color-primary);
  border-radius: 6px;
  opacity: 0.7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.5rem;
  transition: all 0.2s ease;
}

.reading-bar:hover {
  opacity: 1;
  transform: scaleY(1.2);
  z-index: 10;
}

.reading-bar.overlap {
  background: #D4AF37;
  opacity: 1;
  box-shadow: 0 2px 4px rgba(212, 175, 55, 0.3);
}

.reader-label {
  position: absolute;
  left: 0;
  top: -18px;
  font-size: 0.7rem;
  color: var(--color-secondary);
  font-weight: 600;
  white-space: nowrap;
}

.format-icon-small {
  font-size: 0.7rem;
  margin-left: auto;
}

.overlap-summary {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--color-secondary);
  line-height: 1.6;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .conjugation-card {
    padding: 1.5rem;
  }

  .conjugation-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .timeline-viz {
    padding: 0.75rem;
  }
}
</style>

