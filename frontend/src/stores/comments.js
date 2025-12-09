import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useCommentsStore = defineStore('comments', () => {
  // State: comments organized by read_id or semester_id
  const commentsByRead = ref({}) // { readId: { items: [], pagination: {} } }
  const commentsBySemester = ref({}) // { semesterId: { items: [], pagination: {} } }
  const loading = ref(false)
  const reactionUsers = ref({}) // { commentId_reactionType: { items: [], pagination: {} } }

  // Getters
  const getCommentsForRead = computed(() => {
    return (readId) => {
      return commentsByRead.value[readId]?.items || []
    }
  })

  const getCommentsForSemester = computed(() => {
    return (semesterId) => {
      return commentsBySemester.value[semesterId]?.items || []
    }
  })

  const getTotalCommentCount = computed(() => {
    return (readId, semesterId) => {
      if (readId) {
        return commentsByRead.value[readId]?.pagination?.total || 0
      } else if (semesterId) {
        return commentsBySemester.value[semesterId]?.pagination?.total || 0
      }
      return 0
    }
  })

  const getPagination = computed(() => {
    return (readId, semesterId) => {
      if (readId) {
        return commentsByRead.value[readId]?.pagination || {
          page: 1,
          page_size: 20,
          total: 0,
          total_pages: 0
        }
      } else if (semesterId) {
        return commentsBySemester.value[semesterId]?.pagination || {
          page: 1,
          page_size: 20,
          total: 0,
          total_pages: 0
        }
      }
      return {
        page: 1,
        page_size: 20,
        total: 0,
        total_pages: 0
      }
    }
  })

  // Actions
  const fetchComments = async (readId = null, semesterId = null, page = 1, pageSize = 20) => {
    loading.value = true
    try {
      let response
      if (readId) {
        response = await api.get(`/comments/read/${readId}`, {
          params: { page, page_size: pageSize }
        })
        
        // Initialize if needed
        if (!commentsByRead.value[readId]) {
          commentsByRead.value[readId] = { items: [], pagination: {} }
        }
        
        // Update comments
        commentsByRead.value[readId].items = response.data.items
        commentsByRead.value[readId].pagination = {
          page: response.data.page,
          page_size: response.data.page_size,
          total: response.data.total,
          total_pages: response.data.total_pages
        }
      } else if (semesterId) {
        response = await api.get(`/comments/semester/${semesterId}`, {
          params: { page, page_size: pageSize }
        })
        
        // Initialize if needed
        if (!commentsBySemester.value[semesterId]) {
          commentsBySemester.value[semesterId] = { items: [], pagination: {} }
        }
        
        // Update comments
        commentsBySemester.value[semesterId].items = response.data.items
        commentsBySemester.value[semesterId].pagination = {
          page: response.data.page,
          page_size: response.data.page_size,
          total: response.data.total,
          total_pages: response.data.total_pages
        }
      } else {
        throw new Error('Either readId or semesterId must be provided')
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to fetch comments:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createComment = async (readId = null, semesterId = null, content, parentCommentId = null) => {
    loading.value = true
    try {
      const payload = {
        content: content.trim(),
        parent_comment_id: parentCommentId
      }
      if (readId) {
        payload.read_id = readId
      } else if (semesterId) {
        payload.semester_id = semesterId
      } else {
        throw new Error('Either readId or semesterId must be provided')
      }
      
      const response = await api.post('/comments', payload)
      
      // Refresh comments
      if (readId) {
        await fetchComments(readId, null, 1, 20)
      } else if (semesterId) {
        await fetchComments(null, semesterId, 1, 20)
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to create comment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteComment = async (commentId, readId = null, semesterId = null) => {
    loading.value = true
    try {
      await api.delete(`/comments/${commentId}`)
      
      // Refresh comments
      if (readId) {
        await fetchComments(readId, null, 1, 20)
      } else if (semesterId) {
        await fetchComments(null, semesterId, 1, 20)
      }
    } catch (error) {
      console.error('Failed to delete comment:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const toggleReaction = async (commentId, reactionType, readId = null, semesterId = null) => {
    try {
      const response = await api.post(`/comments/${commentId}/reactions`, {
        reaction_type: reactionType
      })
      
      // Update the comment's reactions in local state
      const updateCommentReactions = (comments) => {
        for (const comment of comments) {
          if (comment.id === commentId) {
            comment.reactions = response.data.reactions
            comment.current_user_reactions = response.data.current_user_reactions
            return
          }
          if (comment.replies && comment.replies.length > 0) {
            updateCommentReactions(comment.replies)
          }
        }
      }
      
      if (readId && commentsByRead.value[readId]?.items) {
        updateCommentReactions(commentsByRead.value[readId].items)
      } else if (semesterId && commentsBySemester.value[semesterId]?.items) {
        updateCommentReactions(commentsBySemester.value[semesterId].items)
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to toggle reaction:', error)
      throw error
    }
  }

  const fetchReactionUsers = async (commentId, reactionType, page = 1, pageSize = 20) => {
    const key = `${commentId}_${reactionType}`
    try {
      const response = await api.get(`/comments/${commentId}/reactions`, {
        params: {
          reaction_type: reactionType,
          page,
          page_size: pageSize
        }
      })
      
      if (!reactionUsers.value[key]) {
        reactionUsers.value[key] = { items: [], pagination: {} }
      }
      
      reactionUsers.value[key].items = response.data.items
      reactionUsers.value[key].pagination = {
        page: response.data.page,
        page_size: response.data.page_size,
        total: response.data.total,
        total_pages: response.data.total_pages
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to fetch reaction users:', error)
      throw error
    }
  }

  const searchComments = async (params) => {
    loading.value = true
    try {
      const response = await api.get('/comments/search', { params })
      return response.data
    } catch (error) {
      console.error('Failed to search comments:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearComments = (readId = null, semesterId = null) => {
    if (readId) {
      delete commentsByRead.value[readId]
    } else if (semesterId) {
      delete commentsBySemester.value[semesterId]
    } else {
      commentsByRead.value = {}
      commentsBySemester.value = {}
    }
  }

  return {
    // State
    commentsByRead,
    commentsBySemester,
    loading,
    reactionUsers,
    
    // Getters
    getCommentsForRead,
    getCommentsForSemester,
    getTotalCommentCount,
    getPagination,
    
    // Actions
    fetchComments,
    createComment,
    deleteComment,
    toggleReaction,
    fetchReactionUsers,
    searchComments,
    clearComments
  }
})

