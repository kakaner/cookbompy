<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <h3 class="modal-title">Delete Book</h3>
      <p class="modal-message">
        Are you sure you want to delete <strong>{{ bookTitle }}</strong>? This action cannot be undone.
      </p>
      <div class="modal-actions">
        <button @click="$emit('cancel')" class="btn">Cancel</button>
        <button @click="$emit('confirm')" class="btn btn-danger">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  bookTitle: {
    type: String,
    default: 'this book'
  }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.modal-overlay {
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
  padding: 1rem;
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}

.modal-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.modal-message {
  font-size: 1rem;
  color: var(--color-text);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.modal-message strong {
  color: var(--color-primary);
  font-weight: 600;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-danger {
  background: var(--color-error);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #a00;
}
</style>

