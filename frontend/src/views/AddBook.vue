<template>
  <div class="container">
    <div class="page-header">
      <h2 class="page-title">Add Boko</h2>
      <p class="page-subtitle">Search external databases or enter manually</p>
    </div>

    <!-- External Search Section -->
    <div class="search-section card">
      <h3 class="search-title">Search External Databases</h3>
      <div class="search-input-group">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search by title, author, or ISBN (e.g., 'remains day ishiguro' or '978-0679731726')"
          @keydown.enter.prevent="performSearch"
          :disabled="searching"
        />
        <button
          @click="performSearch"
          class="search-btn"
          :disabled="searching || !searchQuery.trim()"
        >
          {{ searching ? 'Searching...' : 'Search' }}
        </button>
      </div>
      <p class="search-hint">
        Examples: "remains day", "kazuo ishiguro", "978-0679731726"
      </p>

      <!-- Loading Indicator -->
      <div v-if="searching" class="loading-indicator">
        <div class="spinner"></div>
        <span>Searching and loading book data...</span>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="search-results">
        <h4>Search Results</h4>
        <div class="results-grid">
          <div
            v-for="result in searchResults"
            :key="result.isbn_13 || result.isbn_10 || result.title"
            class="result-card"
            @click="selectSearchResult(result)"
          >
            <div class="result-cover">
              <img v-if="result.cover_url" :src="result.cover_url" :alt="result.title" />
              <div v-else class="cover-placeholder-small">{{ result.title.charAt(0) }}</div>
            </div>
            <div class="result-info">
              <h4>{{ result.title }}</h4>
              <p>{{ result.author }}</p>
              <p v-if="result.publication_year" class="result-meta">{{ result.publication_year }}</p>
            </div>
            <button class="select-btn">Select</button>
          </div>
        </div>
      </div>

      <!-- Search Error -->
      <div v-if="searchError" class="error">
        {{ searchError }}
      </div>
    </div>

    <!-- Manual Entry Form -->
    <div class="form-section card">
      <h3 class="form-title">Book Information</h3>
      
      <form @submit.prevent="handleSubmit">
        <div v-if="error" class="error">
          {{ error }}
        </div>

        <!-- Core Information -->
        <div class="form-section-inner">
          <h4 class="section-heading">Core Information</h4>
          <div class="form-grid">
            <div class="form-field full-width">
              <label class="form-label">
                Title <span class="required">*</span>
                <span v-if="autoLoadedFields.title" class="auto-badge">Auto-loaded</span>
              </label>
              <input
                v-model="formData.title"
                type="text"
                required
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.title }"
                placeholder="Book title"
              />
            </div>

            <div class="form-field">
              <label class="form-label">
                Author <span class="required">*</span>
                <span v-if="autoLoadedFields.author" class="auto-badge">Auto-loaded</span>
              </label>
              <input
                v-model="formData.author"
                type="text"
                required
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.author }"
                placeholder="Author name"
              />
            </div>

            <div class="form-field">
              <label class="form-label">ISBN</label>
              <input
                v-model="formData.isbn_13"
                type="text"
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.isbn_13 }"
                placeholder="ISBN-13"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Publication Date</label>
              <input
                v-model="formData.publication_date"
                type="date"
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.publication_year }"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Publisher</label>
              <input
                v-model="formData.publisher"
                type="text"
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.publisher }"
                placeholder="Publisher name"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Page Count</label>
              <input
                v-model.number="formData.page_count"
                type="number"
                class="form-input"
                :class="{ 'auto-loaded-field': autoLoadedFields.page_count }"
                placeholder="Number of pages"
                min="0"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Language</label>
              <select
                v-model="formData.language"
                class="form-select"
                :class="{ 'auto-loaded-field': autoLoadedFields.language }"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="ru">Russian</option>
                <option value="ja">Japanese</option>
                <option value="zh">Chinese</option>
                <option value="other">Other</option>
              </select>
            </div>

            <FormatSelect
              v-model="formData.format"
              label="Format"
              required
              hint="Required for point calculation"
            />

            <div class="form-field">
              <label class="form-label">
                Book Type
                <span class="required">*</span>
              </label>
              <select
                v-model="formData.book_type"
                class="form-select"
                :class="{ 'auto-loaded-field': autoLoadedFields.book_type }"
                required
              >
                <option value="">Select type...</option>
                <option value="FICTION">Fiction</option>
                <option value="NONFICTION">Nonfiction</option>
                <option value="YA">Young Adult</option>
                <option value="CHILDRENS">Children's</option>
                <option value="COMIC">Comic</option>
                <option value="NOVELLA">Novella</option>
                <option value="SHORT_STORY">Short Story</option>
                <option value="OTHER">Other</option>
              </select>
              <div class="field-hint">Required for point calculation</div>
            </div>

            <GenreInput
              v-model="formData.genres"
              label="Genres/Categories"
              :class="{ 'auto-loaded-field': autoLoadedFields.genres }"
            />

            <div class="form-field full-width">
              <label class="form-label">
                Synopsis
                <span v-if="autoLoadedFields.description" class="auto-badge">Auto-loaded</span>
              </label>
              <textarea
                v-model="formData.description"
                class="form-textarea"
                :class="{ 'auto-loaded-field': autoLoadedFields.description }"
                rows="6"
                placeholder="Book description or synopsis"
              ></textarea>
              <div v-if="formData.description_source" class="synopsis-source">
                <span class="source-icon">{{ getSourceIcon(formData.description_source) }}</span>
                <span>Synopsis from {{ formData.description_source }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Points Calculator (if read) -->
        <div class="form-section-inner" v-if="formData.read_status === 'READ' && formData.book_type">
          <h4 class="section-heading">Points Calculator</h4>
          <div class="points-calculator">
            <div class="points-breakdown">
              <div class="points-row">
                <span>Base Points:</span>
                <span>{{ calculatedPoints.base.toFixed(2) }}</span>
              </div>
              <div class="points-row" v-if="calculatedPoints.lengthAddons > 0">
                <span>Length Add-ons:</span>
                <span>+{{ calculatedPoints.lengthAddons.toFixed(2) }}</span>
              </div>
              <div class="points-row" v-if="formData.is_reread">
                <span>Reread Multiplier:</span>
                <span>× 0.5</span>
              </div>
              <div class="points-row total">
                <span>bompyallegory:</span>
                <span>{{ calculatedPoints.allegory.toFixed(2) }} pts</span>
              </div>
              <div class="points-row total">
                <span>bompyreasonable:</span>
                <span>{{ calculatedPoints.reasonable.toFixed(2) }} pts</span>
              </div>
            </div>
            <div class="override-section">
              <label class="checkbox-label">
                <input
                  v-model="overrideBasePoints"
                  type="checkbox"
                  @change="handleOverrideToggle"
                />
                Override Base Points
              </label>
              <div v-if="overrideBasePoints" class="override-input-group">
                <input
                  v-model.number="formData.base_points"
                  type="number"
                  step="0.01"
                  min="0"
                  class="override-input"
                  placeholder="Base points"
                />
                <span>points</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Reading Status -->
        <div class="form-section-inner">
          <h4 class="section-heading">Reading Status</h4>
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Status</label>
              <select v-model="formData.read_status" class="form-select">
                <option value="UNREAD">Unread</option>
                <option value="READING">Currently Reading</option>
                <option value="READ">Read</option>
                <option value="DNF">Did Not Finish</option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Date Finished</label>
              <input
                v-model="formData.date_finished"
                type="date"
                class="form-input"
              />
              <div class="field-hint">Used to assign semester</div>
            </div>

            <div class="form-field">
              <label class="form-label">Date Started (Optional)</label>
              <input
                v-model="formData.date_started"
                type="date"
                class="form-input"
              />
              <div class="field-hint">For conjugation tracking</div>
            </div>

            <div class="form-field">
              <label class="checkbox-label">
                <input
                  v-model="formData.is_reread"
                  type="checkbox"
                />
                This is a re-read
              </label>
            </div>
            <div class="form-field">
              <label class="checkbox-label">
                <input
                  v-model="formData.is_memorable"
                  type="checkbox"
                />
                Mark as memorable (featured in semester timeline)
              </label>
            </div>
          </div>
        </div>

        <!-- Additional Details (Collapsed) -->
        <div class="form-section-inner collapsible" :class="{ expanded: showAdditionalDetails }">
          <div class="collapsible-header" @click="showAdditionalDetails = !showAdditionalDetails">
            <h4 class="section-heading">Additional Details (Optional)</h4>
            <span class="collapse-icon">{{ showAdditionalDetails ? '▲' : '▼' }}</span>
          </div>
          <div v-if="showAdditionalDetails" class="collapsible-content">
            <div class="form-grid">
              <div class="form-field">
                <label class="form-label">Series</label>
                <input
                  v-model="formData.series"
                  type="text"
                  class="form-input"
                  placeholder="Series name"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Series Number</label>
                <input
                  v-model.number="formData.series_number"
                  type="number"
                  class="form-input"
                  placeholder="Book number in series"
                  min="0"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Original Title</label>
                <input
                  v-model="formData.original_title"
                  type="text"
                  class="form-input"
                  placeholder="For translations"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Translator</label>
                <input
                  v-model="formData.translator"
                  type="text"
                  class="form-input"
                  placeholder="Translator name"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Illustrator</label>
                <input
                  v-model="formData.illustrator"
                  type="text"
                  class="form-input"
                  placeholder="Illustrator name"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Awards</label>
                <input
                  v-model="formData.awards"
                  type="text"
                  class="form-input"
                  placeholder="Awards received"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Acquisition Date</label>
                <input
                  v-model="formData.acquisition_date"
                  type="date"
                  class="form-input"
                />
              </div>

              <div class="form-field">
                <label class="form-label">Acquisition Source</label>
                <input
                  v-model="formData.acquisition_source"
                  type="text"
                  class="form-input"
                  placeholder="Purchased, gift, library, etc."
                />
              </div>

              <div class="form-field">
                <label class="form-label">Physical Location</label>
                <input
                  v-model="formData.physical_location"
                  type="text"
                  class="form-input"
                  placeholder="Shelf, room, house identifier"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Cover Upload -->
        <div class="form-section-inner">
          <h4 class="section-heading">Cover Image</h4>
          <div class="cover-upload-section">
            <div v-if="coverPreview" class="cover-preview">
              <img :src="coverPreview" alt="Cover preview" />
              <button type="button" @click="removeCover" class="remove-cover-btn">×</button>
            </div>
            <div v-else class="cover-upload-placeholder">
              <input
                ref="coverInput"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                @change="handleCoverSelect"
                style="display: none"
              />
              <button
                type="button"
                @click="$refs.coverInput?.click()"
                class="upload-cover-btn"
              >
                Upload Cover Image
              </button>
              <p class="upload-hint">JPEG, PNG, or WebP (max 5MB)</p>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? 'Adding Boko...' : 'Add Boko' }}
          </button>
          <router-link to="/library" class="btn">Cancel</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import { useAuthStore } from '../stores/auth'
import FormatSelect from '../components/FormatSelect.vue'
import GenreInput from '../components/GenreInput.vue'

const router = useRouter()
const booksStore = useBooksStore()
const authStore = useAuthStore()

const searchQuery = ref('')
const searching = ref(false)
const searchResults = ref([])
const searchError = ref(null)
const showAdditionalDetails = ref(false)
const loading = ref(false)
const error = ref(null)
const coverFile = ref(null)
const coverPreview = ref(null)

const autoLoadedFields = ref({
  title: false,
  author: false,
  isbn_13: false,
  publication_year: false,
  publisher: false,
  page_count: false,
  language: false,
  book_type: false,
  genres: false,
  description: false
})

const formData = ref({
  title: '',
  author: '',
  isbn_13: '',
  isbn_10: '',
  publication_date: null,
  publisher: '',
  edition: '',
  page_count: null,
  language: 'en',
  cover_image_url: null,
  description: '',
  description_source: null,
  genres: [],
  book_type: '',
  series: '',
  series_number: null,
  original_title: '',
  translator: '',
  illustrator: '',
  awards: '',
  acquisition_date: null,
  acquisition_source: '',
  physical_location: '',
  date_started: null,
  date_finished: null,
  is_reread: false,
  is_memorable: false,
  read_status: 'UNREAD',
  format: 'PAPERBACK', // Default format, will be overridden by user preference
  base_points: null
})

// Apply user's default book format on mount
onMounted(() => {
  if (authStore.user?.default_book_format) {
    formData.value.format = authStore.user.default_book_format
  }
})

const isFormValid = computed(() => {
  return formData.value.title.trim() &&
         formData.value.author.trim() &&
         formData.value.format &&
         formData.value.book_type
})

const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  searching.value = true
  searchError.value = null
  searchResults.value = []
  
  try {
    const results = await booksStore.searchExternal(searchQuery.value)
    searchResults.value = results
    if (results.length === 0) {
      searchError.value = 'No results found. Try a different search or enter manually.'
    }
  } catch (err) {
    searchError.value = 'Search failed. Please try again or enter manually.'
    console.error('Search error:', err)
  } finally {
    searching.value = false
  }
}

const selectSearchResult = (result) => {
  // Auto-fill form with search result
  formData.value.title = result.title || formData.value.title
  formData.value.author = result.author || formData.value.author
  formData.value.isbn_13 = result.isbn_13 || formData.value.isbn_13
  formData.value.isbn_10 = result.isbn_10 || formData.value.isbn_10
  if (result.publication_year) {
    formData.value.publication_date = `${result.publication_year}-01-01`
    autoLoadedFields.value.publication_year = true
  }
  formData.value.publisher = result.publisher || formData.value.publisher
  formData.value.page_count = result.page_count || formData.value.page_count
  formData.value.description = result.description || formData.value.description
  if (result.description) {
    // Map source to enum value
    const sourceMap = {
      'google_books': 'GOOGLE_BOOKS',
      'open_library': 'GOOGLE_BOOKS', // Fallback since we don't have OPEN_LIBRARY enum
      'goodreads': 'GOODREADS'
    }
    formData.value.description_source = sourceMap[result.source] || 'GOOGLE_BOOKS'
  }
  formData.value.genres = result.genres || []
  formData.value.cover_image_url = result.cover_url || formData.value.cover_image_url
  if (result.cover_url) {
    coverPreview.value = result.cover_url
  }
  
  // Mark fields as auto-loaded
  autoLoadedFields.value = {
    title: !!result.title,
    author: !!result.author,
    isbn_13: !!result.isbn_13,
    publication_year: !!result.publication_year,
    publisher: !!result.publisher,
    page_count: !!result.page_count,
    language: false,
    book_type: false,
    genres: !!(result.genres && result.genres.length > 0),
    description: !!result.description
  }
  
  // Scroll to form
  document.querySelector('.form-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const handleCoverSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      error.value = 'Cover image must be less than 5MB'
      return
    }
    coverFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      coverPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeCover = () => {
  coverFile.value = null
  coverPreview.value = null
  formData.value.cover_image_url = null
  if (document.querySelector('input[type="file"]')) {
    document.querySelector('input[type="file"]').value = ''
  }
}

const getSourceIcon = (source) => {
  const icons = {
    'GOODREADS': 'G',
    'GOOGLE_BOOKS': 'GB',
    'AMAZON': 'A',
    'WIKIPEDIA': 'W',
    'MANUAL': 'M'
  }
  return icons[source] || '?'
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // Prepare book data (remove reading fields - they go in Read model)
    const bookData = {
      ...formData.value,
      publication_date: formData.value.publication_date || null,
      acquisition_date: formData.value.acquisition_date || null,
      page_count: formData.value.page_count || null,
      series_number: formData.value.series_number || null,
      genres: formData.value.genres.length > 0 ? formData.value.genres : null
    }
    
    // Remove reading fields from book data
    delete bookData.date_started
    delete bookData.date_finished
    delete bookData.is_reread
    delete bookData.is_memorable
    delete bookData.read_status
    delete bookData.base_points
    
    // Create book
    const book = await booksStore.createBook(bookData)
    
    // Upload cover if provided
    if (coverFile.value) {
      await booksStore.uploadCover(book.id, coverFile.value)
    }
    
    // Create initial read if reading data was provided
    if (formData.value.read_status !== 'UNREAD' || formData.value.date_started || formData.value.date_finished) {
      try {
        const readData = {
          read_status: formData.value.read_status || 'UNREAD',
          date_started: formData.value.date_started || null,
          date_finished: formData.value.date_finished || null,
          is_reread: formData.value.is_reread || false,
          is_memorable: formData.value.is_memorable || false,
          base_points: formData.value.base_points || null
        }
        await api.post(`/reads?book_id=${book.id}`, readData)
      } catch (err) {
        console.error('Error creating initial read:', err)
        // Don't fail the whole operation if read creation fails
      }
    }
    
    // Redirect to book detail
    router.push(`/books/${book.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add boko. Please try again.'
    console.error('Add book error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-family: var(--font-heading);
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: var(--color-secondary);
  font-size: 1rem;
}

.search-section {
  margin-bottom: 2rem;
}

.search-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.search-input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.search-btn {
  padding: 0.875rem 2rem;
  background: var(--color-primary);
  color: var(--color-background);
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-btn:hover:not(:disabled) {
  background: var(--color-secondary);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-hint {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-top: 0.5rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(212, 175, 55, 0.1);
  border-radius: var(--radius-sm);
  margin-top: 1rem;
  color: var(--color-primary);
  font-weight: 500;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(155, 72, 25, 0.3);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-results {
  margin-top: 1.5rem;
}

.search-results h4 {
  margin-bottom: 1rem;
  font-family: var(--font-heading);
  font-size: 1.125rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.result-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.result-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.result-cover {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 3px;
  overflow: hidden;
  background: var(--color-border);
}

.result-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-small {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--color-text-light);
  font-weight: 600;
}

.result-info h4 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-info p {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin: 0.25rem 0;
}

.result-meta {
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.select-btn {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: var(--color-background);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.select-btn:hover {
  background: var(--color-secondary);
}

.form-section {
  margin-bottom: 2rem;
}

.form-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.form-section-inner {
  margin-bottom: 2rem;
}

.section-heading {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-background);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.required {
  color: var(--color-error);
}

.auto-badge {
  background: rgba(81, 207, 102, 0.15);
  color: #2B8A3E;
  padding: 0.15rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem 1rem;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.form-textarea {
  min-height: 120px;
  resize: vertical;
}

.auto-loaded-field {
  border-color: rgba(81, 207, 102, 0.5);
  background: rgba(81, 207, 102, 0.03);
}

.synopsis-source {
  font-size: 0.8rem;
  color: var(--color-secondary);
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.source-icon {
  width: 16px;
  height: 16px;
  background: var(--color-secondary);
  color: var(--color-background);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 400;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.collapsible-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.collapse-icon {
  font-size: 0.875rem;
  color: var(--color-text-light);
  transition: transform var(--transition-fast);
}

.collapsible-content {
  margin-top: 1rem;
}

.cover-upload-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cover-preview {
  position: relative;
  width: 150px;
  aspect-ratio: 2/3;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-cover-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-upload-placeholder {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-cover-btn {
  padding: 0.75rem 1.5rem;
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
  font-size: 0.95rem;
}

.upload-cover-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-background);
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--color-text-light);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.points-calculator {
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 1.5rem;
  margin-top: 1rem;
}

.points-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.points-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--color-text);
}

.points-row.total {
  padding-top: 0.75rem;
  border-top: 2px solid var(--color-primary);
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--color-primary);
}

.override-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.override-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-top: 0.75rem;
}

.override-input {
  width: 100px;
  padding: 0.5rem;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-family: var(--font-body);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .search-input-group {
    flex-direction: column;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>

