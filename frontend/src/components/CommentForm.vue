<template>
  <div class="comment-form">
    <textarea
      v-model="content"
      :placeholder="placeholder"
      :maxlength="1000"
      rows="4"
      class="comment-input"
      @input="handleInput"
    ></textarea>
    <div class="comment-form-footer">
      <div class="char-counter" :class="{ 'char-counter-warning': remainingChars < 50 }">
        {{ remainingChars }} characters remaining
        <span v-if="isDevelopment" style="margin-left: 10px; font-size: 0.7rem; color: #999;">
          (canSubmit: {{ canSubmit }}, submitting: {{ submitting }}, contentLen: {{ content.trim().length }})
        </span>
      </div>
      <div class="comment-form-actions">
        <button
          v-if="content.trim()"
          @click="handleCancel"
          class="btn btn-secondary btn-sm"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="handleSubmit"
          :disabled="!canSubmit"
          :class="['btn', 'btn-primary', 'btn-sm', { 'btn-disabled': !canSubmit }]"
          :title="!canSubmit ? 'Type a comment to enable' : 'Post comment'"
        >
          <span v-if="submitting">Posting...</span>
          <span v-else>{{ parentCommentId ? 'Reply' : 'Post Comment' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Check if we're in development mode (Vite uses import.meta.env)
const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

const props = defineProps({
  readId: {
    type: Number,
    default: null
  },
  semesterId: {
    type: Number,
    default: null
  },
  parentCommentId: {
    type: Number,
    default: null
  },
  placeholder: {
    type: String,
    default: 'Write a comment...'
  },
  autoFocus: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const content = ref('')
const submitting = ref(false)

const remainingChars = computed(() => 1000 - content.value.length)
const canSubmit = computed(() => {
  if (submitting.value) return false
  if (!content.value) return false
  const trimmed = content.value.trim()
  return trimmed.length >= 1 && trimmed.length <= 1000
})

const handleInput = () => {
  // Auto-save draft to localStorage (optional enhancement)
  if (content.value) {
    const targetId = props.readId || props.semesterId
    const targetType = props.readId ? 'read' : 'semester'
    const key = `comment_draft_${targetType}_${targetId}_${props.parentCommentId || 'top'}`
    localStorage.setItem(key, content.value)
  }
}

const handleSubmit = () => {
  if (!canSubmit.value) {
    console.log('Cannot submit:', { canSubmit: canSubmit.value, contentLength: content.value.trim().length, submitting: submitting.value })
    return
  }
  
  const trimmedContent = content.value.trim()
  submitting.value = true
  
  // Emit the event (emit is synchronous, parent handles async)
  // Only include readId or semesterId if they are actually set (not null)
  const submitData = {
    content: trimmedContent,
    parentCommentId: props.parentCommentId
  }
  if (props.readId !== null && props.readId !== undefined) {
    submitData.readId = props.readId
  }
  if (props.semesterId !== null && props.semesterId !== undefined) {
    submitData.semesterId = props.semesterId
  }
  emit('submit', submitData)
  
  // Clear form
  content.value = ''
  submitting.value = false
  
  // Clear draft
  const targetId = props.readId || props.semesterId
  const targetType = props.readId ? 'read' : 'semester'
  const key = `comment_draft_${targetType}_${targetId}_${props.parentCommentId || 'top'}`
  localStorage.removeItem(key)
}

const handleCancel = () => {
  content.value = ''
  emit('cancel')
  // Clear draft
  const targetId = props.readId || props.semesterId
  const targetType = props.readId ? 'read' : 'semester'
  const key = `comment_draft_${targetType}_${targetId}_${props.parentCommentId || 'top'}`
  localStorage.removeItem(key)
}

// Load draft on mount
const loadDraft = () => {
  const targetId = props.readId || props.semesterId
  const targetType = props.readId ? 'read' : 'semester'
  const key = `comment_draft_${targetType}_${targetId}_${props.parentCommentId || 'top'}`
  const draft = localStorage.getItem(key)
  if (draft) {
    content.value = draft
  }
}

// Auto-focus if requested
watch(() => props.autoFocus, (newVal) => {
  if (newVal) {
    // Focus textarea after mount
    setTimeout(() => {
      const textarea = document.querySelector('.comment-input')
      if (textarea) textarea.focus()
    }, 100)
  }
})

// Load draft on mount
import { onMounted } from 'vue'
onMounted(() => {
  loadDraft()
})
</script>

<style scoped>
.comment-form {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}

.comment-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.95rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  background: var(--color-background);
  color: var(--color-text);
  transition: border-color var(--transition-fast);
}

.comment-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(155, 72, 25, 0.1);
}

.comment-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}

.char-counter {
  font-size: 0.8rem;
  color: var(--color-text-light);
}

.char-counter-warning {
  color: var(--color-error);
  font-weight: 500;
}

.comment-form-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn:disabled,
.btn.btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .comment-form {
    padding: 0.75rem;
  }
  
  .comment-input {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  .comment-form-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .comment-form-actions {
    justify-content: stretch;
  }
  
  .comment-form-actions .btn {
    flex: 1;
  }
}
</style>

