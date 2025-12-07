<template>
  <div class="container">
    <div class="section-header">
      <h2 class="section-title">Library</h2>
      <p class="section-subtitle">Your personal boko collection</p>
    </div>

    <!-- Search and Filters -->
    <div class="library-controls">
      <div class="search-container">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search books by title, author..."
          @input="handleSearch"
        />
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
        <router-link to="/books/add" class="btn btn-primary">
          + Add Boko
        </router-link>
      </div>
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
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import BookCard from '../components/BookCard.vue'
import { FORMAT_OPTIONS } from '../utils/formats'

const router = useRouter()
const booksStore = useBooksStore()

const viewMode = ref('grid')
const searchQuery = ref('')
const formatOptions = FORMAT_OPTIONS

// Debounce search
let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    booksStore.setFilter('search', searchQuery.value || null)
    booksStore.fetchBooks({ page: 1 })
  }, 500)
}

const goToPage = (page) => {
  booksStore.fetchBooks({ page })
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
  padding: 0.875rem 1.25rem;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
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

