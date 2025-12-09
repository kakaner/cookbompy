<template>
  <div class="book-filters">
    <div class="filters-header">
      <h4 class="filters-title">Filters & Sort</h4>
      <button 
        class="toggle-filters"
        @click="expanded = !expanded"
        :aria-expanded="expanded"
      >
        {{ expanded ? '−' : '+' }}
      </button>
    </div>

    <div v-if="expanded" class="filters-content">
      <!-- Sort -->
      <div class="filter-group">
        <label class="filter-label">Sort By</label>
        <select v-model="localSort" @change="onSortChange" class="filter-select">
          <option value="date_read_desc">Most Recently Read</option>
          <option value="date_read_asc">Oldest Read</option>
          <option value="title_asc">Title (A-Z)</option>
          <option value="title_desc">Title (Z-A)</option>
          <option value="author_asc">Author (A-Z)</option>
          <option value="author_desc">Author (Z-A)</option>
          <option value="date_added_desc">Date Added (Newest)</option>
          <option value="date_added_asc">Date Added (Oldest)</option>
          <option value="publication_date_desc">Publication Date (Newest)</option>
          <option value="publication_date_asc">Publication Date (Oldest)</option>
          <option value="format">Format</option>
          <option value="semester_desc">Semester (Most Recent)</option>
          <option value="semester_asc">Semester (Oldest)</option>
        </select>
      </div>

      <!-- Format Filter (Multi-select) -->
      <div class="filter-group">
        <label class="filter-label">Format</label>
        <div class="filter-checkboxes">
          <label v-for="fmt in formatOptions" :key="fmt.value" class="checkbox-label">
            <input
              type="checkbox"
              :value="fmt.value"
              v-model="localFormats"
              @change="onFormatChange"
            />
            <span>{{ fmt.icon }} {{ fmt.label }}</span>
          </label>
        </div>
      </div>

      <!-- Book Type Filter (Multi-select) -->
      <div class="filter-group">
        <label class="filter-label">Book Type</label>
        <div class="filter-checkboxes">
          <label v-for="type in bookTypes" :key="type.value" class="checkbox-label">
            <input
              type="checkbox"
              :value="type.value"
              v-model="localBookTypes"
              @change="onBookTypeChange"
            />
            <span>{{ type.label }}</span>
          </label>
        </div>
      </div>

      <!-- Read Status Filter -->
      <div class="filter-group">
        <label class="filter-label">Read Status</label>
        <select v-model="localReadStatus" @change="onReadStatusChange" class="filter-select">
          <option :value="null">All</option>
          <option value="READ">Read</option>
          <option value="READING">Currently Reading</option>
          <option value="UNREAD">Unread</option>
          <option value="DNF">Did Not Finish</option>
        </select>
      </div>

      <!-- Review Status Filter -->
      <div class="filter-group">
        <label class="filter-label">Review Status</label>
        <select v-model="localHasReview" @change="onHasReviewChange" class="filter-select">
          <option :value="null">All</option>
          <option :value="true">Has Review</option>
          <option :value="false">No Review</option>
        </select>
      </div>

      <!-- Language Filter -->
      <div class="filter-group">
        <label class="filter-label">Language</label>
        <input
          v-model="localLanguage"
          type="text"
          class="filter-input"
          placeholder="e.g., en, es, fr"
          @input="onLanguageChange"
        />
      </div>

      <!-- Author Filter -->
      <div class="filter-group">
        <label class="filter-label">Author</label>
        <input
          v-model="localAuthor"
          type="text"
          class="filter-input"
          placeholder="Filter by author"
          @input="onAuthorChange"
        />
      </div>

      <!-- Clear Filters -->
      <div class="filter-actions">
        <button @click="clearAllFilters" class="btn-clear">Clear All Filters</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { FORMAT_OPTIONS } from '../utils/formats'

const props = defineProps({
  sort: {
    type: String,
    default: 'date_read_desc'
  },
  formats: {
    type: Array,
    default: () => []
  },
  bookTypes: {
    type: Array,
    default: () => []
  },
  readStatus: {
    type: String,
    default: null
  },
  hasReview: {
    type: Boolean,
    default: null
  },
  language: {
    type: String,
    default: null
  },
  author: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:sort', 'update:formats', 'update:bookTypes', 'update:readStatus', 'update:hasReview', 'update:language', 'update:author', 'clear'])

const expanded = ref(false)
const localSort = ref(props.sort)
const localFormats = ref([...props.formats])
const localBookTypes = ref([...props.bookTypes])
const localReadStatus = ref(props.readStatus)
const localHasReview = ref(props.hasReview)
const localLanguage = ref(props.language || '')
const localAuthor = ref(props.author || '')

const formatOptions = FORMAT_OPTIONS

const bookTypes = [
  { value: 'FICTION', label: 'Fiction' },
  { value: 'NONFICTION', label: 'Non-fiction' },
  { value: 'YA', label: 'Young Adult' },
  { value: 'CHILDRENS', label: "Children's" },
  { value: 'COMIC', label: 'Comic' },
  { value: 'NOVELLA', label: 'Novella' },
  { value: 'SHORT_STORY', label: 'Short Story' },
  { value: 'OTHER', label: 'Other' }
]

const onSortChange = () => {
  emit('update:sort', localSort.value)
}

const onFormatChange = () => {
  emit('update:formats', [...localFormats.value])
}

const onBookTypeChange = () => {
  emit('update:bookTypes', [...localBookTypes.value])
}

const onReadStatusChange = () => {
  emit('update:readStatus', localReadStatus.value)
}

const onHasReviewChange = () => {
  emit('update:hasReview', localHasReview.value)
}

const onLanguageChange = () => {
  emit('update:language', localLanguage.value || null)
}

const onAuthorChange = () => {
  emit('update:author', localAuthor.value || null)
}

const clearAllFilters = () => {
  localSort.value = 'date_read_desc'
  localFormats.value = []
  localBookTypes.value = []
  localReadStatus.value = null
  localHasReview.value = null
  localLanguage.value = ''
  localAuthor.value = ''
  emit('clear')
}

watch(() => props.sort, (newVal) => {
  localSort.value = newVal
})

watch(() => props.formats, (newVal) => {
  localFormats.value = [...newVal]
}, { deep: true })

watch(() => props.bookTypes, (newVal) => {
  localBookTypes.value = [...newVal]
}, { deep: true })

watch(() => props.readStatus, (newVal) => {
  localReadStatus.value = newVal
})

watch(() => props.hasReview, (newVal) => {
  localHasReview.value = newVal
})

watch(() => props.language, (newVal) => {
  localLanguage.value = newVal || ''
})

watch(() => props.author, (newVal) => {
  localAuthor.value = newVal || ''
})
</script>

<style scoped>
.book-filters {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.filters-title {
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.toggle-filters {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.25rem;
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.toggle-filters:hover {
  background: var(--color-background);
  border-color: var(--color-primary);
}

.filters-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.filter-select,
.filter-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.95rem;
  background: var(--color-background);
  color: var(--color-text);
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.filter-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.25rem 0;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.filter-actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.btn-clear {
  padding: 0.5rem 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-light);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-clear:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .filters-content {
    grid-template-columns: 1fr;
  }
}
</style>

