<template>
  <div class="container">
    <div class="page-header">
      <h2 class="page-title">Conjugation</h2>
      <p class="page-subtitle">Shared discoveries and synchronized reading patterns</p>
    </div>


    <!-- Loading State -->
    <div v-if="conjugationStore.loading" class="loading">
      Loading conjugation data...
    </div>

    <!-- Summary Stats Cards -->
    <div v-else-if="conjugationStore.hasData" class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-label">Total Readers</div>
        <div class="stat-card-value">{{ conjugationStore.summaryStats.totalReaders }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-label">Books in Common</div>
        <div class="stat-card-value">{{ conjugationStore.summaryStats.booksInCommon }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-label">Total Comments</div>
        <div class="stat-card-value">{{ conjugationStore.summaryStats.totalComments }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-label">Avg Conjugation</div>
        <div class="stat-card-value">{{ conjugationStore.summaryStats.avgConjugation || 'N/A' }}</div>
      </div>
    </div>

    <!-- Reads in Common Section -->
    <section v-if="!conjugationStore.loading" class="section">
      <h3 class="section-title">Reads in Common</h3>
      <p class="section-description">Books that all readers have completed</p>
      <ReadsInCommon
        :books="conjugationStore.readsInCommon"
        :loading="conjugationStore.loading"
      />
    </section>

    <!-- Similar Sentiment Section -->
    <section v-if="!conjugationStore.loading" class="section">
      <h3 class="section-title">Reads with Similar Sentiment</h3>
      <p class="section-description">
        Books where everyone rated similarly (standard deviation ≤ 1.5 stars)
      </p>
      <SimilarSentiment
        :books="conjugationStore.similarSentiment"
        :loading="conjugationStore.loading"
      />
    </section>

    <!-- High Conjugation Reads Section -->
    <section v-if="!conjugationStore.loading" class="section">
      <h3 class="section-title">High Conjugation Reads</h3>
      <p class="section-description">
        Books read simultaneously or within days of each other
      </p>
      <ConjugationTimeline
        :books="conjugationStore.conjugationHighlights"
        :loading="conjugationStore.loading"
      />
    </section>

    <!-- Empty State -->
    <div v-if="!conjugationStore.loading && !conjugationStore.hasData" class="empty-state">
      <p>No conjugation data available yet. Start reading to discover shared patterns!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useConjugationStore } from '../stores/conjugation'
import ReadsInCommon from '../components/conjugation/ReadsInCommon.vue'
import SimilarSentiment from '../components/conjugation/SimilarSentiment.vue'
import ConjugationTimeline from '../components/conjugation/ConjugationTimeline.vue'

const conjugationStore = useConjugationStore()

onMounted(async () => {
  await conjugationStore.fetchCommunityStats(2, 10)
})
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 3rem 2.5rem;
}

.page-header {
  margin-bottom: 3rem;
}

.page-title {
  font-family: var(--font-heading);
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--color-text);
}

.page-subtitle {
  color: var(--color-secondary);
  font-size: 1rem;
  letter-spacing: 0.3px;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.95rem;
  background: var(--color-background);
  color: var(--color-text);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: var(--color-surface);
  padding: 1.5rem;
  border-radius: var(--radius-sm);
  box-shadow: 0 2px 8px rgba(44, 44, 44, 0.08);
  border-left: 4px solid var(--color-primary);
}

.stat-card-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-secondary);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.stat-card-value {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.section {
  margin-bottom: 3.5rem;
}

.section-title {
  font-family: var(--font-heading);
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.section-description {
  color: var(--color-secondary);
  margin-bottom: 1.75rem;
  line-height: 1.6;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text-light);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .container {
    padding: 2rem 1.25rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

