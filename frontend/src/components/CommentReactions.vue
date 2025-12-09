<template>
  <div class="comment-reactions">
    <div class="reactions-list">
      <button
        v-for="reaction in reactionTypes"
        :key="reaction.type"
        @click="handleReactionClick(reaction.type)"
        :class="[
          'reaction-btn',
          { 'reaction-active': isActive(reaction.type) }
        ]"
        :aria-label="`${reaction.emoji} ${reaction.label}`"
        :title="reaction.label"
      >
        <span class="reaction-emoji">{{ reaction.emoji }}</span>
        <span
          v-if="getCount(reaction.type) > 0"
          class="reaction-count"
          @click.stop="showUsers(reaction.type)"
        >
          {{ getCount(reaction.type) }}
        </span>
      </button>
    </div>
    
    <!-- Reaction users modal/popover (simplified - can be enhanced) -->
    <div v-if="showUsersModal" class="reaction-users-modal" @click="closeUsersModal">
      <div class="modal-content" @click.stop>
        <h4>Users who reacted with {{ getReactionEmoji(selectedReactionType) }}</h4>
        <div v-if="loadingUsers" class="loading">Loading...</div>
        <div v-else-if="reactionUsers.length === 0" class="empty">No users yet</div>
        <ul v-else class="users-list">
          <li v-for="user in reactionUsers" :key="user.id" class="user-item">
            <span class="user-avatar">
              {{ user.user.profile_photo_url ? '👤' : (user.user.display_name || user.user.username).charAt(0).toUpperCase() }}
            </span>
            <span class="user-name">{{ user.user.display_name || user.user.username }}</span>
          </li>
        </ul>
        <button @click="closeUsersModal" class="btn btn-secondary btn-sm">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCommentsStore } from '../stores/comments'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

const commentsStore = useCommentsStore()

const reactionTypes = [
  { type: 'heart', emoji: '❤️', label: 'Love' },
  { type: 'thumbs_up', emoji: '👍', label: 'Like' },
  { type: 'laugh', emoji: '😂', label: 'Funny' },
  { type: 'think', emoji: '🤔', label: 'Interesting' },
  { type: 'target', emoji: '🎯', label: 'Spot on' },
  { type: 'book', emoji: '📚', label: 'Relevant' },
  { type: 'clap', emoji: '👏', label: 'Well said' }
]

const showUsersModal = ref(false)
const selectedReactionType = ref(null)
const reactionUsers = ref([])
const loadingUsers = ref(false)

const isActive = (reactionType) => {
  return props.comment.current_user_reactions?.includes(reactionType) || false
}

const getCount = (reactionType) => {
  return props.comment.reactions?.[reactionType]?.count || 0
}

const getReactionEmoji = (type) => {
  return reactionTypes.find(r => r.type === type)?.emoji || ''
}

const handleReactionClick = async (reactionType) => {
  try {
    await commentsStore.toggleReaction(
      props.comment.id,
      reactionType,
      props.comment.read_id
    )
  } catch (error) {
    console.error('Error toggling reaction:', error)
  }
}

const showUsers = async (reactionType) => {
  if (getCount(reactionType) === 0) return
  
  selectedReactionType.value = reactionType
  showUsersModal.value = true
  loadingUsers.value = true
  
  try {
    const data = await commentsStore.fetchReactionUsers(
      props.comment.id,
      reactionType,
      1,
      20
    )
    reactionUsers.value = data.items
  } catch (error) {
    console.error('Error fetching reaction users:', error)
  } finally {
    loadingUsers.value = false
  }
}

const closeUsersModal = () => {
  showUsersModal.value = false
  selectedReactionType.value = null
  reactionUsers.value = []
}

</script>

<style scoped>
.comment-reactions {
  position: relative;
  margin-top: 0.5rem;
}

.reactions-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.reaction-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 44px;
  min-height: 44px;
  justify-content: center;
  touch-action: manipulation;
}

.reaction-btn:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  transform: scale(1.05);
}

.reaction-btn:active {
  transform: scale(0.95);
}

.reaction-btn.reaction-active {
  background: rgba(155, 72, 25, 0.1);
  border-color: var(--color-primary);
  animation: reactionPulse 0.3s ease-out;
}

@keyframes reactionPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.reaction-emoji {
  font-size: 1rem;
}

.reaction-count {
  font-weight: 500;
  color: var(--color-text);
  cursor: pointer;
}

.reaction-users-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h4 {
  margin-bottom: 1rem;
  font-family: var(--font-heading);
  color: var(--color-primary);
}

.users-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

.user-item:last-child {
  border-bottom: none;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.user-name {
  font-weight: 500;
  color: var(--color-text);
}

.empty {
  text-align: center;
  color: var(--color-text-light);
  padding: 1rem;
}

.loading {
  text-align: center;
  color: var(--color-text-light);
  padding: 1rem;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .reactions-list {
    gap: 0.25rem;
  }
  
  .reaction-btn {
    min-width: 40px;
    min-height: 40px;
    padding: 0.2rem 0.4rem;
    font-size: 0.8rem;
  }
  
  .modal-content {
    width: 95%;
    padding: 1rem;
  }
}
</style>

