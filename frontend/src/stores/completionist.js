import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useCompletionistStore = defineStore('completionist', () => {
  const authors = ref([])
  const loading = ref(false)
  const stats = ref({
    authors_100_percent: 0,
    authors_75_plus: 0,
    total_tracked: 0,
    overall_completion_rate: 0
  })
  const currentAuthor = ref(null)
  const achievements = ref([])
  const leaderboard = ref([])

  const fetchAuthorProgress = async (params = {}) => {
    loading.value = true
    try {
      const response = await api.get('/completionist/authors', { params })
      authors.value = response.data.authors || []
      return response.data
    } catch (error) {
      console.error('Error fetching author progress:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchAuthorDetail = async (authorCanonId) => {
    loading.value = true
    try {
      const response = await api.get(`/completionist/authors/${authorCanonId}`)
      currentAuthor.value = response.data
      return response.data
    } catch (error) {
      console.error('Error fetching author detail:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchAchievements = async () => {
    try {
      const response = await api.get('/completionist/achievements')
      achievements.value = response.data.achievements || []
      return response.data
    } catch (error) {
      console.error('Error fetching achievements:', error)
      throw error
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const response = await api.get('/completionist/leaderboard')
      leaderboard.value = response.data.entries || []
      return response.data
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      throw error
    }
  }

  const setGoal = async (authorCanonId, deadline, notify = false) => {
    try {
      const response = await api.post('/completionist/goals', {
        author_canon_id: authorCanonId,
        deadline,
        notify
      })
      // Refresh author progress
      await fetchAuthorProgress()
      return response.data
    } catch (error) {
      console.error('Error setting goal:', error)
      throw error
    }
  }

  // Computed stats
  const computedStats = computed(() => {
    if (authors.value.length === 0) {
      return {
        authors_100_percent: 0,
        authors_75_plus: 0,
        total_tracked: 0,
        overall_completion_rate: 0
      }
    }

    const completed = authors.value.filter(a => a.completion_percentage >= 100).length
    const almost = authors.value.filter(a => a.completion_percentage >= 75).length
    const total = authors.value.length
    const avgCompletion = authors.value.reduce((sum, a) => sum + a.completion_percentage, 0) / total

    return {
      authors_100_percent: completed,
      authors_75_plus: almost,
      total_tracked: total,
      overall_completion_rate: avgCompletion / 100
    }
  })

  return {
    authors,
    loading,
    stats,
    currentAuthor,
    achievements,
    leaderboard,
    computedStats,
    fetchAuthorProgress,
    fetchAuthorDetail,
    fetchAchievements,
    fetchLeaderboard,
    setGoal
  }
})

