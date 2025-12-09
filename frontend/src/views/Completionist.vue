<template>
  <div class="container">
    <div class="page-header">
      <h2 class="page-title">📚 Completionist</h2>
      <p class="page-subtitle">Track your journey to completing your favorite authors' complete works</p>
    </div>

    <!-- Loading State -->
    <div v-if="completionistStore.loading" class="loading">
      Loading completionist data...
    </div>

    <!-- Summary Stats -->
    <div v-else class="stats-bar">
      <div class="stat-item">
        <div class="stat-number">{{ completionistStore.computedStats.authors_100_percent }}</div>
        <div class="stat-label">Authors 100% Complete</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ completionistStore.computedStats.authors_75_plus }}</div>
        <div class="stat-label">Authors 75%+ Complete</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ completionistStore.computedStats.total_tracked }}</div>
        <div class="stat-label">Total Authors Tracked</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ Math.round(completionistStore.computedStats.overall_completion_rate * 100) }}%</div>
        <div class="stat-label">Overall Completion Rate</div>
      </div>
    </div>

    <!-- Controls -->
    <div v-if="!completionistStore.loading" class="controls">
      <div class="sort-group">
        <button 
          v-for="option in sortOptions" 
          :key="option.value"
          :class="['sort-btn', { active: currentSort === option.value }]"
          @click="currentSort = option.value; fetchData()"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <!-- Author Cards -->
    <div v-if="!completionistStore.loading" class="authors-list">
      <div v-for="author in completionistStore.authors" :key="author.author_canon_id" class="author-card">
        <div class="author-header">
          <div class="author-info">
            <h3 class="author-name">{{ author.author_name }}</h3>
            <div class="author-meta">
              {{ author.books_read }} of {{ author.books_total }} books read
            </div>
            <div v-if="author.achievements && author.achievements.length > 0" class="achievement-badges">
              <span v-for="achievement in author.achievements" :key="achievement" class="achievement-badge">
                {{ getAchievementLabel(achievement) }}
              </span>
            </div>
          </div>
          <div class="completion-badge" :class="getCompletionClass(author.completion_percentage)">
            {{ Math.round(author.completion_percentage) }}%
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-bar-container">
            <div 
              class="progress-bar" 
              :style="{ width: author.completion_percentage + '%' }"
            ></div>
          </div>
          <div class="progress-text">
            {{ author.books_read }} of {{ author.books_total }} books read • {{ author.books_total - author.books_read }} remaining
          </div>
        </div>

        <div v-if="author.missing_titles && author.missing_titles.length > 0" class="missing-section">
          <div class="missing-title">🎯 Missing from Your Collection:</div>
          <div class="missing-list">{{ author.missing_titles.join(' • ') }}</div>
        </div>

        <div class="actions">
          <router-link 
            :to="`/completionist/${author.author_canon_id}`" 
            class="action-btn primary"
          >
            📖 View Complete Timeline
          </router-link>
          <button 
            v-if="!author.is_goal"
            @click="setGoal(author.author_canon_id)"
            class="action-btn secondary"
          >
            ⭐ Mark as Goal
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!completionistStore.loading && completionistStore.authors.length === 0" class="empty-state">
      <p>No author progress data yet. Start adding books to track your completionist journey!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCompletionistStore } from '../stores/completionist'

const completionistStore = useCompletionistStore()
const currentSort = ref('books_read')

const sortOptions = [
  { value: 'books_read', label: '📚 Most Read' },
  { value: 'completion_pct', label: '📊 Completion %' },
  { value: 'recent', label: '🆕 Recent' },
  { value: 'alphabetical', label: '🔤 A-Z' },
  { value: 'almost_there', label: '⭐ Almost There (80%+)' }
]

const fetchData = async () => {
  await completionistStore.fetchAuthorProgress({
    sort: currentSort.value,
    page: 1,
    page_size: 50
  })
}

const setGoal = async (authorCanonId) => {
  try {
    await completionistStore.setGoal(authorCanonId, null, false)
    await fetchData()
  } catch (error) {
    console.error('Error setting goal:', error)
  }
}

const getAchievementLabel = (achievement) => {
  const labels = {
    'canon_complete': '🏆 Canon Complete',
    'nearly_there': '⭐ Nearly There',
    'deep_dive': '📚 Deep Dive'
  }
  return labels[achievement] || achievement
}

const getCompletionClass = (percentage) => {
  if (percentage >= 100) return 'complete'
  if (percentage >= 90) return 'almost'
  if (percentage >= 75) return 'started'
  return 'in-progress'
}

onMounted(async () => {
  await fetchData()
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

.stats-bar {
  background: var(--color-surface);
  padding: 1.5rem 2rem;
  border-radius: var(--radius-md);
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  gap: 3rem;
  flex-wrap: wrap;
  justify-content: center;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
  font-family: var(--font-heading);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 0.25rem;
}

.controls {
  margin-bottom: 2rem;
}

.sort-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sort-btn {
  padding: 0.625rem 1.25rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
  font-size: 0.9rem;
}

.sort-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-background);
}

.sort-btn.active {
  background: var(--color-primary);
  color: var(--color-surface);
  border-color: var(--color-primary);
}

.author-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.author-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.author-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.author-info {
  flex: 1;
}

.author-name {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.author-meta {
  font-size: 1rem;
  color: var(--color-secondary);
  margin-bottom: 0.75rem;
}

.completion-badge {
  background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%);
  color: var(--color-surface);
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.completion-badge.complete {
  background: linear-gradient(135deg, #51CF66 0%, #37B24D 100%);
}

.completion-badge.almost {
  background: linear-gradient(135deg, #51CF66 0%, #37B24D 100%);
}

.completion-badge.started {
  background: linear-gradient(135deg, #6B7456 0%, #556042 100%);
}

.progress-section {
  margin-bottom: 1.5rem;
}

.progress-bar-container {
  width: 100%;
  height: 16px;
  background: var(--color-background);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #D4AF37 0%, #51CF66 100%);
  transition: width 0.6s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: var(--color-secondary);
  font-weight: 500;
}

.achievement-badges {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.achievement-badge {
  background: linear-gradient(135deg, #51CF66 0%, #37B24D 100%);
  color: var(--color-surface);
  padding: 0.375rem 0.875rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 600;
}

.missing-section {
  background: #FFF9E6;
  border-left: 4px solid #D4AF37;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.5rem;
}

.missing-title {
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.missing-list {
  color: var(--color-secondary);
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-block;
}

.action-btn.primary {
  background: var(--color-primary);
  color: var(--color-surface);
}

.action-btn.primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.action-btn.secondary {
  background: var(--color-surface);
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.action-btn.secondary:hover {
  background: var(--color-background);
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

  .author-header {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-bar {
    gap: 2rem;
  }
}
</style>

