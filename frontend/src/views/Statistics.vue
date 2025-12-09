<template>
  <div class="container">
    <div class="page-header">
      <h2>Statistics</h2>
      <p class="page-subtitle">Comprehensive reading analytics and insights</p>
    </div>

    <!-- Time Dimension Selector -->
    <div class="time-dimension-selector">
      <label for="time-dimension">Time Period:</label>
      <select 
        id="time-dimension"
        v-model="selectedTimeDimension"
        @change="onTimeDimensionChange"
        class="dimension-select"
      >
        <option v-for="dim in timeDimensions" :key="dim.value" :value="dim.value">
          {{ dim.label }}
        </option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="statisticsStore.loading" class="loading">
      Loading statistics...
    </div>

    <!-- Statistics Content -->
    <div v-else class="statistics-content">
      <!-- Reading Statistics Section -->
      <section class="stat-section">
        <h3 class="section-title">Reading Statistics</h3>
        <div v-if="selectedTimeDimension === 'alltime'" class="summary-numbers">
          <div class="summary-item">
            <div class="summary-value">{{ totalReads }}</div>
            <div class="summary-label">Total Reads</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ totalPointsAllegory.toFixed(2) }}</div>
            <div class="summary-label">Total Points (bompyallegory)</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ totalPointsReasonable.toFixed(2) }}</div>
            <div class="summary-label">Total Points (bompyreasonable)</div>
          </div>
        </div>
        <div v-else>
          <!-- Metric Selection Checkboxes -->
          <div class="metric-selector">
            <label class="metric-checkbox">
              <input
                type="checkbox"
                v-model="selectedMetrics.reads"
                @change="updateCombinedChart"
              />
              <span>Total Reads</span>
            </label>
            <label class="metric-checkbox">
              <input
                type="checkbox"
                v-model="selectedMetrics.bompyallegory"
                @change="updateCombinedChart"
              />
              <span>Points (bompyallegory)</span>
            </label>
            <label class="metric-checkbox">
              <input
                type="checkbox"
                v-model="selectedMetrics.bompyreasonable"
                @change="updateCombinedChart"
              />
              <span>Points (bompyreasonable)</span>
            </label>
          </div>
          
          <!-- Combined Chart -->
          <div class="chart-card">
            <LineChart
              :datasets="combinedChartData"
              title="Reading Statistics Over Time"
            />
          </div>
        </div>
      </section>

      <!-- Engagement Metrics Section -->
      <section class="stat-section">
        <h3 class="section-title">Engagement Metrics</h3>
        <div v-if="selectedTimeDimension === 'alltime'" class="summary-numbers">
          <div class="summary-item">
            <div class="summary-value">{{ formatPercentage(viewnerRateOverall) }}</div>
            <div class="summary-label">Viewner Rate</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ formatPercentage(commentuRateOverall) }}</div>
            <div class="summary-label">Commentu Rate</div>
          </div>
        </div>
        <div v-else class="charts-grid">
          <div class="chart-card">
            <LineChart
              :data="viewnerRateData"
              title="Viewner Rate Over Time"
              label="Percentage"
              color="#9B4819"
            />
            <div v-if="viewnerRateOverall" class="overall-rate">
              Overall Viewner Rate: {{ formatPercentage(viewnerRateOverall) }}
            </div>
          </div>
          <div class="chart-card">
            <LineChart
              :data="commentuRateData"
              title="Commentu Rate Over Time"
              label="Percentage"
              color="#6B7456"
            />
            <div v-if="commentuRateOverall" class="overall-rate">
              Overall Commentu Rate: {{ formatPercentage(commentuRateOverall) }}
            </div>
          </div>
        </div>
      </section>

      <!-- Collection Analytics Section -->
      <section class="stat-section">
        <h3 class="section-title">Collection Analytics</h3>
        <div class="charts-grid">
          <div class="chart-card">
            <PieChart
              :data="formatBreakdownData"
              title="Format Distribution"
            />
          </div>
          <div class="chart-card">
            <BarChart
              :data="bookTypeBreakdownData"
              title="Book Type Distribution"
              label="Reads"
              color="#9B4819"
            />
          </div>
          <div class="chart-card">
            <BarChart
              :data="genreBreakdownData"
              title="Genre Distribution (Top 10)"
              label="Reads"
              color="#6B7456"
              horizontal
            />
          </div>
        </div>
      </section>

      <!-- Author Frequency -->
      <section class="stat-section">
        <h3 class="section-title">Most-Read Authors</h3>
        <div class="author-list">
          <div 
            v-for="(author, index) in authorFrequencyData" 
            :key="author.author"
            class="author-item"
          >
            <span class="author-rank">#{{ index + 1 }}</span>
            <div class="author-info">
              <span class="author-name">{{ author.author }}</span>
              <span class="author-stats">
                {{ author.read_count }} reads across {{ author.unique_books }} book{{ author.unique_books !== 1 ? 's' : '' }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Community Statistics Section -->
      <section class="stat-section">
        <h3 class="section-title">Community Statistics</h3>
        <div v-if="communityStatsData" class="community-stats">
          <div class="community-section">
            <h4>Reads in Common</h4>
            <div v-if="communityStatsData.reads_in_common.items.length > 0" class="reads-common-list">
              <div 
                v-for="item in communityStatsData.reads_in_common.items.slice(0, 10)" 
                :key="item.book_id"
                class="reads-common-item"
              >
                <router-link :to="`/books/${item.book_id}`" class="book-link">
                  <span class="book-title">{{ item.title }}</span>
                  <span class="book-author">by {{ item.author }}</span>
                </router-link>
                <div class="book-stats">
                  <span>{{ item.user_count }} users</span>
                  <span>{{ item.read_count }} reads</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-message">No reads in common found</div>
          </div>

          <div class="community-section">
            <h4>Conjugation Highlights</h4>
            <div v-if="communityStatsData.conjugation_highlights.items.length > 0" class="conjugation-list">
              <div 
                v-for="item in communityStatsData.conjugation_highlights.items" 
                :key="item.book_id"
                class="conjugation-item"
              >
                <router-link :to="`/books/${item.book_id}`" class="book-link">
                  <span class="book-title">{{ item.title }}</span>
                  <span class="book-author">by {{ item.author }}</span>
                </router-link>
                <div class="conjugation-score" :class="`score-${item.conjugation_score}`">
                  {{ item.conjugation_score }} conjugation
                </div>
              </div>
            </div>
            <div v-else class="empty-message">No conjugation highlights found</div>
          </div>

          <div class="community-section">
            <router-link to="/conjugation" class="view-full-link">
              View Full Conjugation Analysis →
            </router-link>
          </div>
        </div>
        <div v-else class="loading">Loading community statistics...</div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useStatisticsStore } from '../stores/statistics'
import { getTimeDimensionOptions } from '../utils/timeDimensions'
import LineChart from '../components/charts/LineChart.vue'
import BarChart from '../components/charts/BarChart.vue'
import PieChart from '../components/charts/PieChart.vue'

const statisticsStore = useStatisticsStore()
const selectedTimeDimension = ref('alltime')
const timeDimensions = getTimeDimensionOptions()

// Metric selection (all selected by default)
const selectedMetrics = ref({
  reads: true,
  bompyallegory: true,
  bompyreasonable: true
})

const formatPercentage = (value) => {
  return `${value.toFixed(1)}%`
}

const onTimeDimensionChange = async () => {
  statisticsStore.setTimeDimension(selectedTimeDimension.value)
  await loadStatistics()
}

const loadStatistics = async () => {
  const dim = selectedTimeDimension.value
  try {
    await Promise.all([
      statisticsStore.fetchReadingStats(dim),
      statisticsStore.fetchPointsStats(dim, 'allegory'),
      statisticsStore.fetchPointsStats(dim, 'reasonable'),
      statisticsStore.fetchFormatBreakdown(dim),
      statisticsStore.fetchBookTypeBreakdown(dim),
      statisticsStore.fetchGenreBreakdown(dim, 10),
      statisticsStore.fetchViewnerRate(dim),
      statisticsStore.fetchCommentuRate(dim),
      statisticsStore.fetchAuthorFrequency(10),
      statisticsStore.fetchCommunityStats(2, 10)
    ])
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
}

const readingStatsData = computed(() => {
  const data = statisticsStore.readingStats[selectedTimeDimension.value]
  return data?.data || []
})


const pointsAllegoryData = computed(() => {
  const key = `${selectedTimeDimension.value}_allegory`
  const data = statisticsStore.pointsStats[key]
  return data?.data || []
})

const pointsReasonableData = computed(() => {
  const key = `${selectedTimeDimension.value}_reasonable`
  const data = statisticsStore.pointsStats[key]
  return data?.data || []
})

const formatBreakdownData = computed(() => {
  const data = statisticsStore.formatBreakdown[selectedTimeDimension.value]
  if (!data) return []
  return data.items.map(item => ({
    label: item.format,
    value: item.count,
    percentage: item.percentage,
    icon: '' // Format icons would go here
  }))
})

const bookTypeBreakdownData = computed(() => {
  const data = statisticsStore.bookTypeBreakdown[selectedTimeDimension.value]
  if (!data) return []
  return data.items.map(item => ({
    label: item.book_type,
    value: item.count,
    percentage: item.percentage
  }))
})

const genreBreakdownData = computed(() => {
  const key = `${selectedTimeDimension.value}_10`
  const data = statisticsStore.genreBreakdown[key]
  if (!data) return []
  return data.items.map(item => ({
    label: item.genre,
    value: item.count,
    percentage: item.percentage
  }))
})

const viewnerRateData = computed(() => {
  const data = statisticsStore.viewnerRate[selectedTimeDimension.value]
  return data?.data || []
})

const viewnerRateOverall = computed(() => {
  const data = statisticsStore.viewnerRate[selectedTimeDimension.value]
  return data?.overall_rate || 0
})

const commentuRateData = computed(() => {
  const data = statisticsStore.commentuRate[selectedTimeDimension.value]
  return data?.data || []
})

const commentuRateOverall = computed(() => {
  const data = statisticsStore.commentuRate[selectedTimeDimension.value]
  return data?.overall_rate || 0
})

const authorFrequencyData = computed(() => {
  return statisticsStore.authorFrequency?.items || []
})

const communityStatsData = computed(() => {
  return statisticsStore.communityStats
})

// Combined chart data for multiple metrics
const combinedChartData = computed(() => {
  const datasets = []
  
  // Get all unique labels from all datasets
  const allLabels = new Set()
  if (selectedMetrics.value.reads && readingStatsData.value.length > 0) {
    readingStatsData.value.forEach(item => allLabels.add(item.label))
  }
  if (selectedMetrics.value.bompyallegory && pointsAllegoryData.value.length > 0) {
    pointsAllegoryData.value.forEach(item => allLabels.add(item.label))
  }
  if (selectedMetrics.value.bompyreasonable && pointsReasonableData.value.length > 0) {
    pointsReasonableData.value.forEach(item => allLabels.add(item.label))
  }
  
  const sortedLabels = Array.from(allLabels).sort()
  
  // Helper to get value for a label from a dataset
  const getValueForLabel = (data, label) => {
    const item = data.find(d => d.label === label)
    return item ? (item.value || 0) : 0
  }
  
  // Create dataset for reads
  if (selectedMetrics.value.reads) {
    datasets.push({
      label: 'Total Reads',
      data: sortedLabels.map(label => ({
        label,
        value: getValueForLabel(readingStatsData.value, label)
      })),
      color: '#9B4819',
      fill: false
    })
  }
  
  // Create dataset for bompyallegory
  if (selectedMetrics.value.bompyallegory) {
    datasets.push({
      label: 'Points (bompyallegory)',
      data: sortedLabels.map(label => ({
        label,
        value: getValueForLabel(pointsAllegoryData.value, label)
      })),
      color: '#6B7456',
      fill: false
    })
  }
  
  // Create dataset for bompyreasonable
  if (selectedMetrics.value.bompyreasonable) {
    datasets.push({
      label: 'Points (bompyreasonable)',
      data: sortedLabels.map(label => ({
        label,
        value: getValueForLabel(pointsReasonableData.value, label)
      })),
      color: '#D4AF37',
      fill: false
    })
  }
  
  return datasets
})

const updateCombinedChart = () => {
  // Chart will update automatically via computed property
}

const totalReads = computed(() => {
  if (selectedTimeDimension.value === 'alltime' && readingStatsData.value.length > 0) {
    return readingStatsData.value[0]?.value || 0
  }
  return readingStatsData.value.reduce((sum, item) => sum + (item.value || 0), 0)
})


const totalPointsAllegory = computed(() => {
  if (selectedTimeDimension.value === 'alltime' && pointsAllegoryData.value.length > 0) {
    return pointsAllegoryData.value[0]?.value || 0
  }
  return pointsAllegoryData.value.reduce((sum, item) => sum + (item.value || 0), 0)
})

const totalPointsReasonable = computed(() => {
  if (selectedTimeDimension.value === 'alltime' && pointsReasonableData.value.length > 0) {
    return pointsReasonableData.value[0]?.value || 0
  }
  return pointsReasonableData.value.reduce((sum, item) => sum + (item.value || 0), 0)
})

onMounted(async () => {
  await loadStatistics()
})

watch(() => selectedTimeDimension.value, async () => {
  await onTimeDimensionChange()
})

watch(() => selectedMetrics.value, () => {
  // Chart will update automatically via computed property
}, { deep: true })
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: var(--color-text-light);
  font-size: 0.95rem;
}

.time-dimension-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.time-dimension-selector label {
  font-weight: 500;
  color: var(--color-text);
}

.dimension-select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.95rem;
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
}

.dimension-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

.statistics-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.stat-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 2rem;
}

.section-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-border);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 1.5rem;
}

.overall-rate {
  margin-top: 1rem;
  text-align: center;
  font-weight: 600;
  color: var(--color-primary);
  font-size: 0.95rem;
}

.author-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.author-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.author-rank {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
  min-width: 40px;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.author-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: 1rem;
}

.author-stats {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.community-stats {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.community-section h4 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.reads-common-list,
.conjugation-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reads-common-item,
.conjugation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.book-link {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-decoration: none;
  flex: 1;
}

.book-title {
  font-weight: 600;
  color: var(--color-text);
}

.book-author {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.book-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.conjugation-score {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: capitalize;
}

.score-high {
  background: var(--color-success);
  color: white;
}

.score-medium {
  background: var(--color-accent);
  color: var(--color-text);
}

.score-low {
  background: var(--color-secondary-light);
  color: var(--color-secondary);
}

.empty-message {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-light);
}

.view-full-link {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  color: var(--color-background);
  text-decoration: none;
  border-radius: var(--radius-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.view-full-link:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.summary-numbers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.summary-value {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-selector {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  flex-wrap: wrap;
}

.metric-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--color-text);
  user-select: none;
}

.metric-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.metric-checkbox:hover {
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .reads-common-item,
  .conjugation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>

