<template>
  <div class="form-group">
    <label v-if="label" :for="id">{{ label }}</label>
    <div class="tags-input-container">
      <span
        v-for="(genre, index) in genres"
        :key="index"
        class="tag-item"
      >
        {{ genre }}
        <span class="tag-remove" @click="removeGenre(index)">×</span>
      </span>
      <input
        :id="id"
        v-model="inputValue"
        type="text"
        class="tag-input"
        :placeholder="placeholder"
        @keydown.enter.prevent="addGenre"
        @keydown.comma.prevent="addGenre"
        @blur="addGenre"
        :disabled="disabled"
      />
    </div>
    <div v-if="hint" class="field-hint">{{ hint }}</div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  label: {
    type: String,
    default: 'Genres/Categories'
  },
  id: {
    type: String,
    default: 'genres'
  },
  placeholder: {
    type: String,
    default: 'Add genre...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const genres = ref([...props.modelValue])
const inputValue = ref('')

watch(() => props.modelValue, (newValue) => {
  genres.value = [...newValue]
}, { deep: true })

const addGenre = () => {
  const trimmed = inputValue.value.trim()
  if (trimmed && !genres.value.includes(trimmed)) {
    genres.value.push(trimmed)
    emit('update:modelValue', [...genres.value])
    inputValue.value = ''
  }
}

const removeGenre = (index) => {
  genres.value.splice(index, 1)
  emit('update:modelValue', [...genres.value])
}
</script>

<style scoped>
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--color-text);
}

.tags-input-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  min-height: 48px;
  align-items: center;
}

.tags-input-container:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: var(--color-background);
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.tag-remove {
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.8;
  transition: opacity var(--transition-fast);
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input {
  flex: 1;
  min-width: 120px;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 1rem;
  color: var(--color-text);
  padding: 0.25rem;
}

.tag-input:disabled {
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-top: 0.25rem;
}
</style>

