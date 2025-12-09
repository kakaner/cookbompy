<template>
  <div class="comment-section">
    <div class="comment-section-header">
      <h3 class="comment-section-title">
        Comments
        <span v-if="totalCount > 0" class="comment-count-badge">
          {{ totalCount }}
        </span>
      </h3>
      <button
        v-if="totalCount > 0"
        @click="toggleCollapsed"
        class="comment-toggle-btn"
        :class="{ 'expanded': !isCollapsed }"
      >
        <span v-if="isCollapsed">Show Comments</span>
        <span v-else>Hide Comments</span>
      </button>
    </div>
    
    <!-- Comment form - only show when expanded OR when there are 0 comments -->
    <CommentForm
      v-if="!isCollapsed || totalCount === 0"
      :read-id="readId"
      :semester-id="semesterId"
      :placeholder="totalCount === 0 ? 'senpai... you could be the first commentu!' : 'Write a comment...'"
      @submit="handleCommentSubmit"
    />
    
    <!-- Collapsed state - just show count -->
    <div v-if="isCollapsed && totalCount > 0" class="comment-collapsed">
      <p>{{ totalCount }} comment{{ totalCount !== 1 ? 's' : '' }}</p>
    </div>
    
    <!-- Expanded content -->
    <div v-else>
      <!-- Loading state -->
      <div v-if="loading && comments.length === 0" class="comment-loading">
        <div class="loading-spinner"></div>
        <span>Loading comments...</span>
      </div>
      
      <!-- Empty state -->
      <div v-else-if="!loading && comments.length === 0" class="comment-empty">
        <p>No comments yet. Be the first to comment!</p>
      </div>
      
      <!-- Comments list -->
      <div v-else class="comments-list">
        <CommentItem
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :read-author-id="targetAuthorId"
          :semester-author-id="semesterAuthorId"
          :current-user-id="currentUserId"
          @deleted="handleCommentDeleted"
        />
      </div>
      
      <!-- Load more button -->
      <div v-if="hasMorePages" class="comment-load-more">
        <button
          @click="loadMoreComments"
          :disabled="loading"
          class="btn btn-secondary"
        >
          <span v-if="loading">Loading...</span>
          <span v-else>Load More Comments</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCommentsStore } from '../stores/comments'
import { useAuthStore } from '../stores/auth'
import CommentForm from './CommentForm.vue'
import CommentItem from './CommentItem.vue'

const props = defineProps({
  readId: {
    type: Number,
    default: null
  },
  semesterId: {
    type: Number,
    default: null
  },
  readAuthorId: {
    type: Number,
    default: null
  },
  semesterAuthorId: {
    type: Number,
    default: null
  },
  collapsed: {
    type: Boolean,
    default: true
  }
})

const isCollapsed = ref(props.collapsed)

const toggleCollapsed = () => {
  isCollapsed.value = !isCollapsed.value
  // Load comments when expanding if not already loaded
  if (!isCollapsed.value && comments.value.length === 0) {
    loadComments(1)
  }
}

const commentsStore = useCommentsStore()
const authStore = useAuthStore()

const currentUserId = computed(() => authStore.user?.id || 0)
const loading = computed(() => commentsStore.loading)
const comments = computed(() => {
  if (props.readId) {
    return commentsStore.getCommentsForRead(props.readId)
  } else if (props.semesterId) {
    return commentsStore.getCommentsForSemester(props.semesterId)
  }
  return []
})
const pagination = computed(() => commentsStore.getPagination(props.readId, props.semesterId))

// Count all comments including nested replies
const totalCount = computed(() => {
  const countComments = (commentList) => {
    let count = 0
    for (const comment of commentList) {
      count++ // Count this comment
      if (comment.replies && comment.replies.length > 0) {
        count += countComments(comment.replies) // Recursively count replies
      }
    }
    return count
  }
  return countComments(comments.value)
})

const hasMorePages = computed(() => {
  return pagination.value.page < pagination.value.total_pages
})

const loadComments = async (page = 1) => {
  try {
    await commentsStore.fetchComments(props.readId, props.semesterId, page, 20)
  } catch (error) {
    console.error('Error loading comments:', error)
  }
}

const loadMoreComments = async () => {
  const nextPage = pagination.value.page + 1
  await loadComments(nextPage)
}

const handleCommentSubmit = async (data) => {
  try {
    // Use props directly if data doesn't have the IDs (fallback)
    // Handle both null and undefined
    const readId = (data.readId !== null && data.readId !== undefined) ? data.readId : props.readId
    const semesterId = (data.semesterId !== null && data.semesterId !== undefined) ? data.semesterId : props.semesterId
    
    // Debug logging
    console.log('Comment submit data:', { data, props: { readId: props.readId, semesterId: props.semesterId }, final: { readId, semesterId } })
    
    await commentsStore.createComment(readId, semesterId, data.content, data.parentCommentId)
    // Comments are automatically refreshed after creation in the store
    // Reload to ensure we have the latest
    await loadComments(1)
  } catch (error) {
    console.error('Error submitting comment:', error)
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to post comment. Please try again.'
    alert(errorMessage)
  }
}

const handleCommentDeleted = () => {
  // Refresh comments after deletion
  loadComments(1)
}

const targetAuthorId = computed(() => props.readAuthorId || props.semesterAuthorId)

// Load comments on mount
onMounted(() => {
  loadComments(1)
})

// Reload if readId or semesterId changes
watch(() => [props.readId, props.semesterId], ([newReadId, newSemesterId], [oldReadId, oldSemesterId]) => {
  if (newReadId !== oldReadId || newSemesterId !== oldSemesterId) {
    loadComments(1)
  }
})
</script>

<style scoped>
.comment-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid var(--color-border);
}

.comment-section-header {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.comment-section-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-count-badge {
  background: var(--color-primary);
  color: var(--color-background);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: 600;
}

.comment-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  color: var(--color-text-light);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.comment-empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  font-style: italic;
}

.comments-list {
  margin-top: 1rem;
}

.comment-load-more {
  margin-top: 1.5rem;
  text-align: center;
}

.comment-load-more .btn {
  min-width: 150px;
}

.comment-load-more .btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comment-toggle-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.comment-toggle-btn:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.comment-toggle-btn.expanded {
  background: var(--color-primary);
  color: var(--color-background);
  border-color: var(--color-primary);
}

.comment-collapsed {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-light);
  font-style: italic;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  border: 1px dashed var(--color-border);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .comment-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
  }
  
  .comment-section-title {
    font-size: 1.25rem;
  }
  
  .comment-load-more .btn {
    width: 100%;
  }
}
</style>

