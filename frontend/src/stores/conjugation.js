import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useConjugationStore = defineStore('conjugation', () => {
  // State
  const readsInCommon = ref([])
  const similarSentiment = ref([])
  const conjugationHighlights = ref([])
  const summaryStats = ref({
    totalReaders: 0,
    booksInCommon: 0,
    totalComments: 0,
    avgConjugation: null
  })
  const loading = ref(false)
  const minUserCount = ref(2)

  // Actions
  const fetchCommunityStats = async (minCount = 2, conjugationLimit = 10) => {
    loading.value = true
    try {
      minUserCount.value = minCount
      const response = await api.get('/statistics/community', {
        params: {
          min_user_count: minCount,
          conjugation_limit: conjugationLimit
        }
      })
      
      readsInCommon.value = response.data.reads_in_common.items || []
      similarSentiment.value = response.data.similar_sentiment.items || []
      conjugationHighlights.value = response.data.conjugation_highlights.items || []
      
      // Calculate summary stats
      summaryStats.value = {
        totalReaders: calculateTotalReaders(),
        booksInCommon: readsInCommon.value.length,
        totalComments: 0, // TODO: Get from community stats if available
        avgConjugation: calculateAvgConjugation()
      }
    } catch (error) {
      console.error('Error fetching community stats:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchReadsInCommon = async (minCount = 2) => {
    loading.value = true
    try {
      minUserCount.value = minCount
      const response = await api.get('/statistics/community', {
        params: {
          min_user_count: minCount,
          conjugation_limit: 10
        }
      })
      readsInCommon.value = response.data.reads_in_common.items || []
    } catch (error) {
      console.error('Error fetching reads in common:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchSimilarSentiment = async () => {
    loading.value = true
    try {
      const response = await api.get('/statistics/community', {
        params: {
          min_user_count: 2,
          conjugation_limit: 10
        }
      })
      similarSentiment.value = response.data.similar_sentiment.items || []
    } catch (error) {
      console.error('Error fetching similar sentiment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchConjugationHighlights = async (limit = 10) => {
    loading.value = true
    try {
      const response = await api.get('/statistics/community', {
        params: {
          min_user_count: 2,
          conjugation_limit: limit
        }
      })
      conjugationHighlights.value = response.data.conjugation_highlights.items || []
    } catch (error) {
      console.error('Error fetching conjugation highlights:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchSummaryStats = async () => {
    // Summary stats are calculated from full community stats
    await fetchCommunityStats(minUserCount.value, 10)
  }

  // Helper functions
  const calculateTotalReaders = () => {
    const allUserIds = new Set()
    readsInCommon.value.forEach(book => {
      book.users.forEach(user => allUserIds.add(user.user_id))
    })
    similarSentiment.value.forEach(book => {
      book.users.forEach(user => allUserIds.add(user.user_id))
    })
    conjugationHighlights.value.forEach(book => {
      book.users.forEach(user => allUserIds.add(user.user_id))
    })
    return allUserIds.size
  }

  const calculateAvgConjugation = () => {
    if (conjugationHighlights.value.length === 0) return null
    
    const scoreValues = { high: 3, medium: 2, low: 1 }
    const total = conjugationHighlights.value.reduce((sum, item) => {
      return sum + (scoreValues[item.conjugation_score] || 0)
    }, 0)
    
    const avg = total / conjugationHighlights.value.length
    if (avg >= 2.5) return 'High'
    if (avg >= 1.5) return 'Medium'
    return 'Low'
  }

  // Computed
  const hasData = computed(() => {
    return readsInCommon.value.length > 0 || 
           similarSentiment.value.length > 0 || 
           conjugationHighlights.value.length > 0
  })

  return {
    // State
    readsInCommon,
    similarSentiment,
    conjugationHighlights,
    summaryStats,
    loading,
    minUserCount,
    // Actions
    fetchCommunityStats,
    fetchReadsInCommon,
    fetchSimilarSentiment,
    fetchConjugationHighlights,
    fetchSummaryStats,
    // Computed
    hasData
  }
})

