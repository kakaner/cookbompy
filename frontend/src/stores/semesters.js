import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useSemestersStore = defineStore('semesters', () => {
  const semesters = ref([])
  const currentSemester = ref(null)
  const loading = ref(false)
  const hasMore = ref(true)
  const total = ref(0)
  const offset = ref(0)

  /**
   * Fetch semesters (loads 4 at a time from current backwards)
   */
  const fetchSemesters = async (reset = false) => {
    if (loading.value) return
    
    loading.value = true
    
    try {
      if (reset) {
        offset.value = 0
        semesters.value = []
      }
      
      const response = await api.get('/semesters', {
        params: {
          limit: 4,
          offset: offset.value
        }
      })
      
      semesters.value = [...semesters.value, ...response.data.items]
      hasMore.value = response.data.has_more
      total.value = response.data.total
      currentSemester.value = response.data.current_semester
      offset.value += 4
      
      return response.data
    } catch (error) {
      console.error('Failed to fetch semesters:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch the current semester info only
   */
  const fetchCurrentSemester = async () => {
    try {
      const response = await api.get('/semesters/current')
      currentSemester.value = response.data.semester_number
      return response.data
    } catch (error) {
      console.error('Failed to fetch current semester:', error)
      throw error
    }
  }

  /**
   * Get a single semester with its books
   */
  const fetchSemester = async (semesterNumber) => {
    loading.value = true
    try {
      const response = await api.get(`/semesters/${semesterNumber}`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch semester:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a semester's custom name
   */
  const updateSemesterName = async (semesterNumber, customName) => {
    try {
      const response = await api.put(`/semesters/${semesterNumber}`, {
        custom_name: customName || null
      })
      
      // Update in local state
      const index = semesters.value.findIndex(s => s.semester_number === semesterNumber)
      if (index !== -1) {
        semesters.value[index] = response.data
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to update semester name:', error)
      throw error
    }
  }

  /**
   * Load more semesters (for infinite scroll / "View More")
   */
  const loadMore = async () => {
    if (!hasMore.value || loading.value) return
    await fetchSemesters()
  }

  /**
   * Reset and reload semesters
   */
  const refresh = async () => {
    await fetchSemesters(true)
  }

  return {
    semesters,
    currentSemester,
    loading,
    hasMore,
    total,
    fetchSemesters,
    fetchCurrentSemester,
    fetchSemester,
    updateSemesterName,
    loadMore,
    refresh
  }
})

