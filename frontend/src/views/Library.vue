<template>
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Libbery</h2>
      <p class="section-subtitle">Your personal boko collection</p>
    </div>

    <!-- Statistics Summary -->
    <StatisticsSummary />

    <!-- Search and Controls -->
    <div class="library-controls">
      <div class="search-container">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search books by title, author, ISBN... (try: author:Morrison, type:FICTION, format:audiobook, S42)"
          @input="handleSearch"
        />
        <div v-if="searchQuery" class="search-hint">
          <small>Tip: Use <code>author:</code>, <code>type:</code>, <code>format:</code>, <code>S42</code> for advanced search</small>
        </div>
      </div>
      
      <div class="controls-right">
        <div class="view-toggle">
          <button
            :class="['view-btn', { active: viewMode === 'grid' }]"
            @click="viewMode = 'grid'"
            title="Grid view"
          >
            ⬜
          </button>
          <button
            :class="['view-btn', { active: viewMode === 'list' }]"
            @click="viewMode = 'list'"
            title="List view"
          >
            ☰
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <BookFilters
      :sort="currentSort"
      :formats="currentFormats"
      :bookTypes="currentBookTypes"
      :readStatus="currentReadStatus"
      :hasReview="currentHasReview"
      :language="currentLanguage"
      :author="currentAuthor"
      @update:sort="onSortChange"
      @update:formats="onFormatsChange"
      @update:bookTypes="onBookTypesChange"
      @update:readStatus="onReadStatusChange"
      @update:hasReview="onHasReviewChange"
      @update:language="onLanguageChange"
      @update:author="onAuthorChange"
      @clear="clearAllFilters"
    />

    <!-- Active Filters Description -->
    <div v-if="activeFiltersDescription" class="active-filters-description">
      {{ activeFiltersDescription }}
    </div>

    <!-- Loading State -->
    <div v-if="booksStore.loading" class="loading">
      Loading books...
    </div>

    <!-- Empty State -->
    <div v-else-if="booksStore.books.length === 0" class="empty-state">
      <p>No bokos found. <router-link to="/books/add">Add your first boko</router-link></p>
    </div>

    <!-- Book Grid/List -->
    <div v-else :class="['book-container', viewMode]">
      <BookCard
        v-for="book in booksStore.books"
        :key="book.id"
        :book="book"
      />
    </div>

    <!-- Pagination -->
    <div v-if="booksStore.pagination.total_pages > 1" class="pagination">
      <button
        :disabled="booksStore.pagination.page === 1"
        @click="goToPage(booksStore.pagination.page - 1)"
        class="pagination-btn"
      >
        Previous
      </button>
      
      <span class="pagination-info">
        Page {{ booksStore.pagination.page }} of {{ booksStore.pagination.total_pages }}
        ({{ booksStore.pagination.total }} bokos)
      </span>
      
      <button
        :disabled="booksStore.pagination.page >= booksStore.pagination.total_pages"
        @click="goToPage(booksStore.pagination.page + 1)"
        class="pagination-btn"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import BookCard from '../components/BookCard.vue'
import StatisticsSummary from '../components/StatisticsSummary.vue'
import BookFilters from '../components/BookFilters.vue'
import { FORMAT_OPTIONS, getFormatDisplayName } from '../utils/formats'

const router = useRouter()
const booksStore = useBooksStore()

const viewMode = ref('grid')
const searchQuery = ref('')
const formatOptions = FORMAT_OPTIONS

// Filter state
const currentSort = ref('date_read_desc')
const currentFormats = ref([])
const currentBookTypes = ref([])
const currentReadStatus = ref(null)
const currentHasReview = ref(null)
const currentLanguage = ref(null)
const currentAuthor = ref(null)

// Debounce search
let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

const onSortChange = (sort) => {
  currentSort.value = sort
  applyFilters()
}

const onFormatsChange = (formats) => {
  currentFormats.value = formats
  applyFilters()
}

const onBookTypesChange = (bookTypes) => {
  currentBookTypes.value = bookTypes
  applyFilters()
}

const onReadStatusChange = (readStatus) => {
  currentReadStatus.value = readStatus
  applyFilters()
}

const onHasReviewChange = (hasReview) => {
  currentHasReview.value = hasReview
  applyFilters()
}

const onLanguageChange = (language) => {
  currentLanguage.value = language
  applyFilters()
}

const onAuthorChange = (author) => {
  currentAuthor.value = author
  applyFilters()
}

// Human-readable filter description
const activeFiltersDescription = computed(() => {
  const parts = []
  
  // Search query
  if (searchQuery.value) {
    parts.push(`searching for "${searchQuery.value}"`)
  }
  
  // Sort
  const sortLabels = {
    'date_read_desc': 'sorted by most recently read',
    'date_read_asc': 'sorted by oldest read',
    'title_asc': 'sorted by title (A-Z)',
    'title_desc': 'sorted by title (Z-A)',
    'author_asc': 'sorted by author (A-Z)',
    'author_desc': 'sorted by author (Z-A)',
    'date_added_desc': 'sorted by date added (newest)',
    'date_added_asc': 'sorted by date added (oldest)',
    'publication_date_desc': 'sorted by publication date (newest)',
    'publication_date_asc': 'sorted by publication date (oldest)',
    'format': 'sorted by format',
    'semester_desc': 'sorted by semester (most recent)',
    'semester_asc': 'sorted by semester (oldest)'
  }
  if (currentSort.value && currentSort.value !== 'date_read_desc') {
    parts.push(sortLabels[currentSort.value] || 'sorted')
  }
  
  // Formats
  if (currentFormats.value && currentFormats.value.length > 0) {
    const formatNames = currentFormats.value.map(f => getFormatDisplayName(f))
    if (formatNames.length === 1) {
      parts.push(`format: ${formatNames[0]}`)
    } else {
      parts.push(`formats: ${formatNames.join(', ')}`)
    }
  }
  
  // Book Types
  if (currentBookTypes.value && currentBookTypes.value.length > 0) {
    const typeLabels = {
      'FICTION': 'Fiction',
      'NONFICTION': 'Non-fiction',
      'YA': 'Young Adult',
      'CHILDRENS': "Children's",
      'COMIC': 'Comic',
      'NOVELLA': 'Novella',
      'SHORT_STORY': 'Short Story',
      'OTHER': 'Other'
    }
    const typeNames = currentBookTypes.value.map(t => typeLabels[t] || t)
    if (typeNames.length === 1) {
      parts.push(`type: ${typeNames[0]}`)
    } else {
      parts.push(`types: ${typeNames.join(', ')}`)
    }
  }
  
  // Read Status
  if (currentReadStatus.value) {
    const statusLabels = {
      'READ': 'read',
      'READING': 'currently reading',
      'UNREAD': 'unread',
      'DNF': 'did not finish'
    }
    parts.push(`status: ${statusLabels[currentReadStatus.value] || currentReadStatus.value}`)
  }
  
  // Has Review
  if (currentHasReview.value === true) {
    parts.push('with reviews')
  } else if (currentHasReview.value === false) {
    parts.push('without reviews')
  }
  
  // Language
  if (currentLanguage.value) {
    parts.push(`language: ${currentLanguage.value}`)
  }
  
  // Author
  if (currentAuthor.value) {
    parts.push(`author: ${currentAuthor.value}`)
  }
  
  if (parts.length === 0) {
    return null
  }
  
  return `Showing bokos ${parts.join(', ')}`
})

const clearAllFilters = () => {
  searchQuery.value = ''
  currentSort.value = 'date_read_desc'
  currentFormats.value = []
  currentBookTypes.value = []
  currentReadStatus.value = null
  currentHasReview.value = null
  currentLanguage.value = null
  currentAuthor.value = null
  booksStore.clearFilters()
  applyFilters()
}

const applyFilters = async () => {
  const params = {
    page: 1,
    sort: currentSort.value,
    search: searchQuery.value || null
  }
  
  if (currentFormats.value.length > 0) {
    params.format = currentFormats.value
  }
  
  if (currentBookTypes.value.length > 0) {
    params.book_type = currentBookTypes.value
  }
  
  if (currentReadStatus.value) {
    params.read_status = currentReadStatus.value
  }
  
  if (currentHasReview.value !== null) {
    params.has_review = currentHasReview.value
  }
  
  if (currentLanguage.value) {
    params.language = currentLanguage.value
  }
  
  if (currentAuthor.value) {
    params.author = currentAuthor.value
  }
  
  await booksStore.fetchBooks(params)
}

const goToPage = (page) => {
  const params = { page }
  if (currentSort.value) params.sort = currentSort.value
  if (currentFormats.value.length > 0) params.format = currentFormats.value
  if (currentBookTypes.value.length > 0) params.book_type = currentBookTypes.value
  if (currentReadStatus.value) params.read_status = currentReadStatus.value
  if (currentHasReview.value !== null) params.has_review = currentHasReview.value
  if (currentLanguage.value) params.language = currentLanguage.value
  if (currentAuthor.value) params.author = currentAuthor.value
  if (searchQuery.value) params.search = searchQuery.value
  
  booksStore.fetchBooks(params)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await booksStore.fetchBooks()
})
</script>

<style scoped>
.section-header {
  margin-bottom: 2.5rem;
}

.section-title {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.section-subtitle {
  color: var(--color-secondary);
  font-size: 0.95rem;
  letter-spacing: 0.3px;
}

.library-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-container {
  flex: 1;
  min-width: 200px;
  max-width: 500px;
}

.search-input {
  width: 100%;
  padding: 1rem 1.5rem;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: 1.05rem;
  font-family: var(--font-body);
  background: var(--color-background);
  box-shadow: 0 2px 8px rgba(155, 72, 25, 0.15);
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(155, 72, 25, 0.25);
  transform: translateY(-1px);
}

.search-hint {
  margin-top: 0.5rem;
  color: var(--color-text-light);
  font-size: 0.75rem;
}

.search-hint code {
  background: var(--color-background);
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-size: 0.7rem;
}

.controls-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.25rem;
}

.view-btn {
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  transition: all var(--transition-fast);
  font-size: 1rem;
}

.view-btn:hover {
  background: var(--color-background);
}

.view-btn.active {
  background: var(--color-primary);
  color: var(--color-background);
}

.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-chip {
  padding: 0.625rem 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 500;
  font-family: var(--font-body);
}

.filter-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.filter-chip.active {
  background: var(--color-primary);
  color: var(--color-background);
  border-color: var(--color-primary);
}

.filter-chip.clear-filter {
  background: var(--color-background);
  color: var(--color-text-light);
}

.book-container {
  margin-bottom: 2rem;
}

.book-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.book-container.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text-light);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.pagination-btn {
  padding: 0.75rem 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: var(--color-background);
  border-color: var(--color-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.95rem;
  color: var(--color-text-light);
}

.active-filters-description {
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text);
  font-style: italic;
}

@media (max-width: 768px) {
  .library-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-container {
    max-width: 100%;
  }

  .controls-right {
    justify-content: space-between;
  }

  .book-container.grid {
    grid-template-columns: 1fr;
  }
}
</style>

