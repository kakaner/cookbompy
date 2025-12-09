<template>
  <div :class="commentClasses">
    <div class="comment-header">
      <div class="comment-author">
        <div class="comment-avatar">
          <img
            v-if="comment.user.profile_photo_url"
            :src="comment.user.profile_photo_url"
            :alt="comment.user.display_name || comment.user.username"
          />
          <span v-else>
            {{ (comment.user.display_name || comment.user.username).charAt(0).toUpperCase() }}
          </span>
        </div>
        <div class="comment-author-info">
          <span class="comment-author-name">
            {{ comment.user.display_name || comment.user.username }}
          </span>
          <span class="comment-timestamp">{{ formatTimestamp(comment.created_at) }}</span>
        </div>
      </div>
      <div v-if="canDelete" class="comment-actions">
        <button
          @click="handleDelete"
          class="btn-icon"
          :aria-label="'Delete comment'"
          title="Delete comment"
        >
          🗑️
        </button>
      </div>
    </div>
    
    <div class="comment-content">
      <p v-if="comment.is_deleted" class="comment-deleted">[deleted]</p>
      <p v-else class="comment-text">{{ comment.content }}</p>
    </div>
    
    <div v-if="!comment.is_deleted" class="comment-footer">
      <button
        v-if="!isReply"
        @click="toggleReplyForm"
        class="btn-link"
      >
        Reply
      </button>
      
      <CommentReactions
        v-if="!comment.is_deleted"
        :comment="comment"
        :current-user-id="currentUserId"
      />
    </div>
    
    <!-- Reply form (shown when replying) -->
    <div v-if="showReplyForm && !comment.is_deleted && !isReply" class="comment-reply-form">
      <CommentForm
        :read-id="comment.read_id"
        :parent-comment-id="comment.id"
        placeholder="Write a reply..."
        @submit="handleReplySubmit"
        @cancel="showReplyForm = false"
      />
    </div>
    
    <!-- Nested replies -->
    <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :read-author-id="readAuthorId"
        :current-user-id="currentUserId"
        :is-reply="true"
        @deleted="handleReplyDeleted"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCommentsStore } from '../stores/comments'
import CommentForm from './CommentForm.vue'
import CommentReactions from './CommentReactions.vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  readAuthorId: {
    type: Number,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  },
  isReply: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['deleted'])

const commentsStore = useCommentsStore()
const showReplyForm = ref(false)

const commentClasses = computed(() => {
  return {
    'comment-item': true,
    'comment-reply': props.isReply
  }
})

const canDelete = computed(() => {
  return props.comment.user_id === props.currentUserId ||
         props.readAuthorId === props.currentUserId
})

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  
  // Format as date
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const toggleReplyForm = () => {
  showReplyForm.value = !showReplyForm.value
}

const handleReplySubmit = async (data) => {
  try {
    await commentsStore.createComment(data.readId, data.semesterId, data.content, data.parentCommentId)
    showReplyForm.value = false
    // Refresh comments to show new reply
    await commentsStore.fetchComments(props.comment.read_id, props.comment.semester_id, 1, 20)
  } catch (error) {
    console.error('Error submitting reply:', error)
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this comment?')) {
    return
  }
  
  try {
    await commentsStore.deleteComment(props.comment.id, props.comment.read_id, props.comment.semester_id)
    emit('deleted', props.comment.id)
  } catch (error) {
    console.error('Error deleting comment:', error)
  }
}

const handleReplyDeleted = () => {
  // Refresh comments when a reply is deleted
  commentsStore.fetchComments(props.comment.read_id, props.comment.semester_id, 1, 20)
}
</script>

<style scoped>
.comment-item {
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.comment-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.comment-reply {
  margin-left: 2rem;
  border-left: 3px solid var(--color-primary);
  background: rgba(155, 72, 25, 0.02);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  overflow: hidden;
  flex-shrink: 0;
}

.comment-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comment-author-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.comment-author-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9rem;
}

.comment-timestamp {
  font-size: 0.8rem;
  color: var(--color-text-light);
}

.comment-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.btn-icon:hover {
  opacity: 1;
}

.comment-content {
  margin-bottom: 0.75rem;
}

.comment-text {
  color: var(--color-text);
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.comment-deleted {
  color: var(--color-text-light);
  font-style: italic;
}

.comment-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  text-decoration: underline;
  transition: opacity var(--transition-fast);
}

.btn-link:hover {
  opacity: 0.8;
}

.comment-reply-form {
  margin-top: 1rem;
  margin-left: 1rem;
}

.comment-replies {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid var(--color-border);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .comment-item {
    padding: 0.75rem;
  }
  
  .comment-reply {
    margin-left: 1rem;
  }
  
  .comment-reply-form {
    margin-left: 0.5rem;
  }
  
  .comment-replies {
    padding-left: 0.5rem;
  }
  
  .comment-avatar {
    width: 32px;
    height: 32px;
    font-size: 0.75rem;
  }
  
  .comment-author-name {
    font-size: 0.85rem;
  }
  
  .comment-timestamp {
    font-size: 0.75rem;
  }
}
</style>

