<template>
  <div class="statistics-summary">
    <div v-if="statisticsStore.loading && !statisticsStore.summary" class="loading">
      Loading statistics...
    </div>

    <div v-else-if="statisticsStore.summary" class="summary-content">
      <div class="compact-stats-line">
        <span class="stat-entry">
          <span class="stat-number">{{ statisticsStore.summary.total_reads }}</span>
          <span class="stat-text">reads</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ statisticsStore.summary.unique_books }}</span>
          <span class="stat-text">books</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ formatPoints(statisticsStore.summary.lifetime_points_allegory) }}</span>
          <span class="stat-text">points (allegory)</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ formatPoints(statisticsStore.summary.lifetime_points_reasonable) }}</span>
          <span class="stat-text">points (reasonable)</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ formatPercentage(statisticsStore.summary.viewner_rate) }}</span>
          <span class="stat-text">viewner rate</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ statisticsStore.summary.reads_in_common_count }}</span>
          <span class="stat-text">reads in common</span>
        </span>
        <span class="stat-separator">•</span>
        <span class="stat-entry">
          <span class="stat-number">{{ statisticsStore.summary.conjugation_highlights_count }}</span>
          <span class="stat-text">conjugation highlights</span>
        </span>
      </div>
    </div>

    <div v-else class="empty-state">
      No statistics available
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useStatisticsStore } from '../stores/statistics'

const statisticsStore = useStatisticsStore()

const formatPoints = (points) => {
  return points.toFixed(2)
}

const formatPercentage = (value) => {
  return `${value.toFixed(1)}%`
}

onMounted(async () => {
  if (!statisticsStore.summary) {
    await statisticsStore.fetchSummary()
  }
})
</script>

<style scoped>
.statistics-summary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
}

.loading {
  text-align: center;
  padding: 0.5rem;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 0.5rem;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.compact-stats-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.stat-entry {
  display: inline-flex;
  align-items: baseline;
  gap: 0.25rem;
}

.stat-number {
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--color-primary);
  font-size: 1.1em;
}

.stat-text {
  color: var(--color-text);
}

.stat-separator {
  color: var(--color-text-light);
  margin: 0 0.25rem;
}

@media (max-width: 768px) {
  .compact-stats-line {
    font-size: 0.85rem;
    gap: 0.375rem;
  }
  
  .stat-separator {
    margin: 0 0.125rem;
  }
}
</style>

