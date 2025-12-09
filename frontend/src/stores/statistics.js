import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useStatisticsStore = defineStore('statistics', () => {
  // State
  const summary = ref(null)
  const readingStats = ref({})
  const pointsStats = ref({})
  const formatBreakdown = ref({})
  const bookTypeBreakdown = ref({})
  const genreBreakdown = ref({})
  const authorFrequency = ref(null)
  const viewnerRate = ref({})
  const commentuRate = ref({})
  const communityStats = ref(null)
  const currentTimeDimension = ref('alltime')
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const hasSummary = computed(() => summary.value !== null)

  // Actions
  async function fetchSummary() {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/summary')
      summary.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch statistics summary'
      console.error('Error fetching statistics summary:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchReadingStats(timeDimension = 'alltime') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/reading', {
        params: { time_dimension: timeDimension }
      })
      readingStats.value[timeDimension] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch reading statistics'
      console.error('Error fetching reading statistics:', err)
      throw err
    } finally {
      loading.value = false
    }
  }


  async function fetchPointsStats(timeDimension = 'alltime', algorithm = 'allegory') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/points', {
        params: { 
          time_dimension: timeDimension,
          algorithm: algorithm
        }
      })
      const key = `${timeDimension}_${algorithm}`
      pointsStats.value[key] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch points statistics'
      console.error('Error fetching points statistics:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchFormatBreakdown(timeDimension = 'alltime') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/format-breakdown', {
        params: { time_dimension: timeDimension }
      })
      formatBreakdown.value[timeDimension] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch format breakdown'
      console.error('Error fetching format breakdown:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBookTypeBreakdown(timeDimension = 'alltime') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/book-type-breakdown', {
        params: { time_dimension: timeDimension }
      })
      bookTypeBreakdown.value[timeDimension] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch book type breakdown'
      console.error('Error fetching book type breakdown:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchGenreBreakdown(timeDimension = 'alltime', limit = 10) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/genre-breakdown', {
        params: { 
          time_dimension: timeDimension,
          limit: limit
        }
      })
      const key = `${timeDimension}_${limit}`
      genreBreakdown.value[key] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch genre breakdown'
      console.error('Error fetching genre breakdown:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAuthorFrequency(limit = 10) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/author-frequency', {
        params: { limit: limit }
      })
      authorFrequency.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch author frequency'
      console.error('Error fetching author frequency:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchViewnerRate(timeDimension = 'alltime') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/viewner-rate', {
        params: { time_dimension: timeDimension }
      })
      viewnerRate.value[timeDimension] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch viewner rate'
      console.error('Error fetching viewner rate:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCommentuRate(timeDimension = 'alltime') {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/commentu-rate', {
        params: { time_dimension: timeDimension }
      })
      commentuRate.value[timeDimension] = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch commentu rate'
      console.error('Error fetching commentu rate:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCommunityStats(minUserCount = 2, conjugationLimit = 10) {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/statistics/community', {
        params: { 
          min_user_count: minUserCount,
          conjugation_limit: conjugationLimit
        }
      })
      communityStats.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch community statistics'
      console.error('Error fetching community statistics:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function setTimeDimension(dimension) {
    currentTimeDimension.value = dimension
  }

  function     clearCache() {
    summary.value = null
    readingStats.value = {}
    pointsStats.value = {}
    formatBreakdown.value = {}
    bookTypeBreakdown.value = {}
    genreBreakdown.value = {}
    authorFrequency.value = null
    viewnerRate.value = {}
    commentuRate.value = {}
    communityStats.value = null
  }

  return {
    // State
    summary,
    readingStats,
    pointsStats,
    formatBreakdown,
    bookTypeBreakdown,
    genreBreakdown,
    authorFrequency,
    viewnerRate,
    commentuRate,
    communityStats,
    currentTimeDimension,
    loading,
    error,
    // Computed
    hasSummary,
    // Actions
    fetchSummary,
    fetchReadingStats,
    fetchPointsStats,
    fetchFormatBreakdown,
    fetchBookTypeBreakdown,
    fetchGenreBreakdown,
    fetchAuthorFrequency,
    fetchViewnerRate,
    fetchCommentuRate,
    fetchCommunityStats,
    setTimeDimension,
    clearCache
  }
})

