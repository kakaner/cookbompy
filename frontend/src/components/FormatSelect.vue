<template>
  <div class="form-group">
    <label v-if="label" :for="id">{{ label }} <span v-if="required">*</span></label>
    <select
      :id="id"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="form-select"
      :required="required"
      :disabled="disabled"
    >
      <option value="">{{ placeholder || 'Select format...' }}</option>
      <option
        v-for="format in formatOptions"
        :key="format.value"
        :value="format.value"
      >
        {{ format.icon }} {{ format.label }}
      </option>
    </select>
    <div v-if="hint" class="field-hint">{{ hint }}</div>
  </div>
</template>

<script setup>
import { FORMAT_OPTIONS } from '../utils/formats'

defineProps({
  modelValue: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: 'Format'
  },
  id: {
    type: String,
    default: 'format'
  },
  placeholder: {
    type: String,
    default: null
  },
  required: {
    type: Boolean,
    default: false
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

defineEmits(['update:modelValue'])

const formatOptions = FORMAT_OPTIONS
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

.form-select {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 1rem;
  background: var(--color-surface);
  color: var(--color-text);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.form-select:disabled {
  background: var(--color-background);
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-top: 0.25rem;
}
</style>

