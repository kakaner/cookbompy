<template>
  <div class="container">
    <div class="page-header">
      <h2 class="page-title">Edit Book</h2>
      <p class="page-subtitle">Update book information</p>
    </div>

    <div v-if="booksStore.loading && !booksStore.currentBook" class="loading">
      Loading boko...
    </div>

    <div v-else-if="booksStore.currentBook" class="form-section card">
      <form @submit.prevent="handleSubmit">
        <div v-if="error" class="error">
          {{ error }}
        </div>

        <!-- Core Information -->
        <div class="form-section-inner">
          <h4 class="section-heading">Core Information</h4>
          <div class="form-grid">
            <div class="form-field full-width">
              <label class="form-label">Title <span class="required">*</span></label>
              <input
                v-model="formData.title"
                type="text"
                required
                class="form-input"
                placeholder="Book title"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Author <span class="required">*</span></label>
              <input
                v-model="formData.author"
                type="text"
                required
                class="form-input"
                placeholder="Author name"
              />
            </div>

            <div class="form-field">
              <label class="form-label">ISBN-13</label>
              <input
                v-model="formData.isbn_13"
                type="text"
                class="form-input"
                placeholder="ISBN-13"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Publication Date</label>
              <input
                v-model="formData.publication_date"
                type="date"
                class="form-input"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Publisher</label>
              <input
                v-model="formData.publisher"
                type="text"
                class="form-input"
                placeholder="Publisher name"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Page Count</label>
              <input
                v-model.number="formData.page_count"
                type="number"
                class="form-input"
                placeholder="Number of pages"
                min="0"
              />
            </div>

            <div class="form-field">
              <label class="form-label">Language</label>
              <select v-model="formData.language" class="form-select">
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
            />

            <div class="form-field">
              <label class="form-label">Book Type <span class="required">*</span></label>
              <select v-model="formData.book_type" class="form-select" required>
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
            </div>

            <GenreInput v-model="formData.genres" />

            <div class="form-field full-width">
              <label class="form-label">Synopsis</label>
              <textarea
                v-model="formData.description"
                class="form-textarea"
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

        <!-- Reading Sessions -->
        <div class="form-section-inner">
          <div class="section-header-with-action">
            <h4 class="section-heading">Reading Sessions</h4>
            <button type="button" @click="addNewRead" class="btn btn-secondary btn-sm">
              + Add Read
            </button>
          </div>
          
          <div v-if="reads.length === 0" class="empty-reads">
            <p>No reading sessions yet. Click "Add Read" to record your first reading of this boko.</p>
          </div>
          
          <div v-else class="reads-list">
            <div
              v-for="(read, index) in reads"
              :key="read.id || `new-${index}`"
              class="read-section"
              :class="{ 'is-editing': editingReadIndex === index }"
            >
              <div class="read-header" @click="toggleReadEdit(index)">
                <div class="read-header-info">
                  <h5 class="read-title">
                    Read #{{ index + 1 }}
                    <span v-if="read.is_reread" class="reread-badge">Re-read</span>
                    <span v-if="read.is_memorable" class="memorable-badge-small">⭐</span>
                  </h5>
                  <div class="read-dates">
                    <span v-if="read.date_finished">{{ formatDate(read.date_finished) }}</span>
                    <span v-else-if="read.date_started">Started: {{ formatDate(read.date_started) }}</span>
                    <span v-else class="text-muted">Not started</span>
                  </div>
                </div>
                <div class="read-header-actions">
                  <span class="read-status-badge" :class="`status-${read.read_status?.toLowerCase()}`">
                    {{ read.read_status || 'UNREAD' }}
                  </span>
                  <span class="collapse-icon">{{ editingReadIndex === index ? '▲' : '▼' }}</span>
                </div>
              </div>
              
              <div v-if="editingReadIndex === index" class="read-edit-form">
                <div class="form-grid">
                  <div class="form-field">
                    <label class="form-label">Status</label>
                    <select v-model="read.read_status" class="form-select">
                      <option value="UNREAD">Unread</option>
                      <option value="READING">Reading</option>
                      <option value="READ">Read</option>
                      <option value="DNF">Did Not Finish</option>
                    </select>
                  </div>
                  
                  <div class="form-field">
                    <label class="form-label">Date Started</label>
                    <input
                      v-model="read.date_started"
                      type="date"
                      class="form-input"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label class="form-label">Date Finished</label>
                    <input
                      v-model="read.date_finished"
                      type="date"
                      class="form-input"
                    />
                  </div>
                  
                  <div class="form-field">
                    <label class="checkbox-label">
                      <input v-model="read.is_reread" type="checkbox" />
                      This is a re-read
                    </label>
                  </div>
                  
                  <div class="form-field">
                    <label class="checkbox-label">
                      <input v-model="read.is_memorable" type="checkbox" />
                      Mark as memorable (featured in semester timeline)
                    </label>
                  </div>
                </div>
                
                <!-- Points Calculator for this read -->
                <div v-if="read.read_status === 'READ' && formData.book_type" class="points-calculator-read">
                  <h5>Points for this read:</h5>
                  <div class="points-display-read">
                    <div class="points-row">
                      <span>Bompyallegory:</span>
                      <span class="points-value">{{ calculateReadPoints(read).allegory.toFixed(2) }}</span>
                    </div>
                    <div class="points-row">
                      <span>Bompyreasonable:</span>
                      <span class="points-value">{{ calculateReadPoints(read).reasonable.toFixed(2) }}</span>
                    </div>
                    <div class="form-field">
                      <label class="checkbox-label">
                        <input v-model="read.overrideBasePoints" type="checkbox" />
                        Override Base Points
                      </label>
                      <input
                        v-if="read.overrideBasePoints"
                        v-model.number="read.base_points"
                        type="number"
                        step="0.01"
                        class="form-input"
                        placeholder="e.g., 1.0"
                      />
                    </div>
                  </div>
                </div>
                
                <!-- Review -->
                <div class="form-field full-width">
                  <label class="form-label">Review / Notes</label>
                  <textarea
                    v-model="read.review"
                    class="form-input"
                    rows="4"
                    placeholder="Your thoughts, notes, or review for this reading..."
                  ></textarea>
                </div>
                
                <!-- Read Vibe Photo -->
                <div class="form-field full-width">
                  <label class="form-label">Read Vibe Photo</label>
                  <div class="vibe-photo-section">
                    <div v-if="read.read_vibe_photo_url" class="vibe-photo-preview">
                      <img :src="read.read_vibe_photo_url" alt="Read vibe" />
                      <button type="button" @click="removeVibePhoto(index)" class="remove-btn">×</button>
                    </div>
                    <div v-else class="vibe-photo-upload">
                      <input
                        :ref="el => vibePhotoInputs[index] = el"
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        @change="(e) => handleVibePhotoSelect(e, index)"
                        style="display: none"
                      />
                      <button type="button" @click="vibePhotoInputs[index]?.click()" class="btn btn-secondary">
                        Upload Photo
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- Read Actions -->
                <div class="read-actions">
                  <button type="button" @click="saveRead(index)" class="btn btn-primary btn-sm">
                    Save Read
                  </button>
                  <button
                    v-if="read.id"
                    type="button"
                    @click="deleteRead(read.id, index)"
                    class="btn btn-danger btn-sm"
                  >
                    Delete Read
                  </button>
                  <button type="button" @click="cancelReadEdit" class="btn btn-sm">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Details -->
        <div class="form-section-inner collapsible" :class="{ expanded: showAdditionalDetails }">
          <div class="collapsible-header" @click="showAdditionalDetails = !showAdditionalDetails">
            <h4 class="section-heading">Additional Details (Optional)</h4>
            <span class="collapse-icon">{{ showAdditionalDetails ? '▲' : '▼' }}</span>
          </div>
          <div v-if="showAdditionalDetails" class="collapsible-content">
            <div class="form-grid">
              <div class="form-field">
                <label class="form-label">Series</label>
                <input v-model="formData.series" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Series Number</label>
                <input v-model.number="formData.series_number" type="number" class="form-input" min="0" />
              </div>
              <div class="form-field">
                <label class="form-label">Original Title</label>
                <input v-model="formData.original_title" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Translator</label>
                <input v-model="formData.translator" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Illustrator</label>
                <input v-model="formData.illustrator" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Awards</label>
                <input v-model="formData.awards" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Acquisition Date</label>
                <input v-model="formData.acquisition_date" type="date" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Acquisition Source</label>
                <input v-model="formData.acquisition_source" type="text" class="form-input" />
              </div>
              <div class="form-field">
                <label class="form-label">Physical Location</label>
                <input v-model="formData.physical_location" type="text" class="form-input" />
              </div>
            </div>
          </div>
        </div>

        <!-- Cover Upload -->
        <div class="form-section-inner">
          <h4 class="section-heading">Cover Image</h4>
          <div class="cover-upload-section">
            <div v-if="coverPreview || formData.cover_image_url" class="cover-preview">
              <img :src="coverPreview || formData.cover_image_url" alt="Cover" />
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
              <button type="button" @click="$refs.coverInput?.click()" class="upload-cover-btn">
                Upload Cover Image
              </button>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading || !isFormValid">
            {{ loading ? 'Updating...' : 'Update Boko' }}
          </button>
          <button type="button" @click="handleDelete" class="btn" style="background: var(--color-error); color: white;">
            Delete Boko
          </button>
          <router-link :to="`/books/${booksStore.currentBook.id}`" class="btn">Cancel</router-link>
        </div>
      </form>
    </div>

    <!-- Delete Confirmation Modal -->
    <DeleteConfirmModal
      v-if="showDeleteModal"
      :book-title="booksStore.currentBook?.title"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '../stores/books'
import FormatSelect from '../components/FormatSelect.vue'
import GenreInput from '../components/GenreInput.vue'
import DeleteConfirmModal from '../components/DeleteConfirmModal.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()

const showAdditionalDetails = ref(false)
const loading = ref(false)
const error = ref(null)
const coverFile = ref(null)
const coverPreview = ref(null)
const showDeleteModal = ref(false)
const overrideBasePoints = ref(false)
const reads = ref([])
const editingReadIndex = ref(null)
const vibePhotoInputs = ref({})

const formData = ref({
  title: '',
  author: '',
  isbn_13: '',
  isbn_10: '',
  publication_date: null,
  publisher: '',
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
  format: 'PAPERBACK'
})

const isFormValid = computed(() => {
  return formData.value.title.trim() &&
         formData.value.author.trim() &&
         formData.value.format &&
         formData.value.book_type
})

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

// Point calculation
const calculatedPoints = computed(() => {
  if (!formData.value.book_type || formData.value.read_status !== 'READ') {
    return {
      base: 0,
      lengthAddons: 0,
      allegory: 0,
      reasonable: 0
    }
  }
  
  // Base points by book type
  const basePointsMap = {
    'FICTION': 1.0,
    'NONFICTION': 1.5,
    'YA': 0.75,
    'CHILDRENS': 0.5,
    'COMIC': 0.5,
    'NOVELLA': 0.5,
    'SHORT_STORY': 0.1,
    'OTHER': 1.0
  }
  
  const base = formData.value.base_points || basePointsMap[formData.value.book_type] || 1.0
  
  // Length add-ons
  let lengthAddons = 0
  if (formData.value.page_count) {
    const effectivePages = formData.value.page_count + 13 // Grace buffer
    if (effectivePages >= 500) {
      lengthAddons = 1.0
      const pagesOverFirst = effectivePages - 500
      lengthAddons += Math.floor(pagesOverFirst / 100) * 1.0
    }
  }
  
  // Calculate totals
  const total = base + lengthAddons
  const allegory = formData.value.is_reread ? total * 0.5 : total
  const reasonable = total
  
  return {
    base,
    lengthAddons,
    allegory,
    reasonable
  }
})

const handleOverrideToggle = () => {
  if (!overrideBasePoints.value) {
    formData.value.base_points = null
  }
}

const loadBookData = async () => {
  const book = booksStore.currentBook
  if (book) {
    formData.value = {
      title: book.title || '',
      author: book.author || '',
      isbn_13: book.isbn_13 || '',
      isbn_10: book.isbn_10 || '',
      publication_date: book.publication_date || null,
      publisher: book.publisher || '',
      page_count: book.page_count || null,
      language: book.language || 'en',
      cover_image_url: book.cover_image_url || null,
      description: book.description || '',
      description_source: book.description_source || null,
      genres: book.genres || [],
      book_type: book.book_type || '',
      series: book.series || '',
      series_number: book.series_number || null,
      original_title: book.original_title || '',
      translator: book.translator || '',
      illustrator: book.illustrator || '',
      awards: book.awards || '',
      acquisition_date: book.acquisition_date || null,
      acquisition_source: book.acquisition_source || '',
      physical_location: book.physical_location || '',
      format: book.format || 'PAPERBACK'
    }
    
    // Load reads for this book
    try {
      const response = await api.get(`/reads/book/${book.id}`)
      reads.value = (response.data || []).map(read => ({
        ...read,
        overrideBasePoints: read.base_points_overridden || false,
        base_points: read.base_points ? read.base_points / 100.0 : null
      }))
    } catch (err) {
      console.error('Error loading reads:', err)
      reads.value = []
    }
  }
}

// Read management functions
const addNewRead = () => {
  const newRead = {
    read_status: 'UNREAD',
    date_started: null,
    date_finished: null,
    is_reread: false,
    is_memorable: false,
    review: null,
    read_vibe_photo_url: null,
    base_points: null,
    overrideBasePoints: false
  }
  reads.value.push(newRead)
  editingReadIndex.value = reads.value.length - 1
}

const toggleReadEdit = (index) => {
  if (editingReadIndex.value === index) {
    editingReadIndex.value = null
  } else {
    editingReadIndex.value = index
  }
}

const cancelReadEdit = () => {
  editingReadIndex.value = null
  // Reload reads to discard changes
  loadBookData()
}

const saveRead = async (index) => {
  const read = reads.value[index]
  if (!read) return
  
  loading.value = true
  error.value = null
  
  try {
    const bookId = parseInt(route.params.id)
    const readData = {
      read_status: read.read_status || 'UNREAD',
      date_started: read.date_started || null,
      date_finished: read.date_finished || null,
      is_reread: read.is_reread || false,
      is_memorable: read.is_memorable || false,
      review: read.review || null,
      read_vibe_photo_url: read.read_vibe_photo_url || null,
      base_points: read.overrideBasePoints ? read.base_points : null
    }
    
    if (read.id) {
      // Update existing read
      await api.put(`/reads/${read.id}`, readData)
    } else {
      // Create new read
      await api.post(`/reads?book_id=${bookId}`, readData)
    }
    
    editingReadIndex.value = null
    await loadBookData() // Reload to get updated reads
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save read'
    console.error('Error saving read:', err)
  } finally {
    loading.value = false
  }
}

const deleteRead = async (readId, index) => {
  if (!confirm('Are you sure you want to delete this read?')) {
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    await api.delete(`/reads/${readId}`)
    reads.value.splice(index, 1)
    editingReadIndex.value = null
    await loadBookData() // Reload to refresh
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete read'
    console.error('Error deleting read:', err)
  } finally {
    loading.value = false
  }
}

const handleVibePhotoSelect = async (event, index) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Photo must be less than 5MB'
    return
  }
  
  loading.value = true
  try {
    const bookId = parseInt(route.params.id)
    const formData = new FormData()
    formData.append('file', file)
    
    // Upload to read vibe endpoint (we'll need to create this or use existing)
    const response = await api.post(`/books/${bookId}/read-vibe`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    reads.value[index].read_vibe_photo_url = response.data.read_vibe_photo_url
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to upload photo'
    console.error('Error uploading vibe photo:', err)
  } finally {
    loading.value = false
  }
}

const removeVibePhoto = (index) => {
  reads.value[index].read_vibe_photo_url = null
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

watch(() => booksStore.currentBook, () => {
  loadBookData()
}, { immediate: true })

onMounted(async () => {
  const bookId = parseInt(route.params.id)
  if (bookId) {
    await booksStore.fetchBook(bookId)
    loadBookData()
  }
})

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
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const bookId = parseInt(route.params.id)
    
    // Prepare update data (no reading fields - those are in reads)
    const updateData = {
      ...formData.value,
      publication_date: formData.value.publication_date || null,
      acquisition_date: formData.value.acquisition_date || null,
      page_count: formData.value.page_count || null,
      series_number: formData.value.series_number || null,
      genres: formData.value.genres.length > 0 ? formData.value.genres : null
    }
    
    // Remove reading-related fields
    delete updateData.date_started
    delete updateData.date_finished
    delete updateData.is_reread
    delete updateData.is_memorable
    delete updateData.read_status
    delete updateData.base_points
    
    await booksStore.updateBook(bookId, updateData)
    
    // Upload cover if new file provided
    if (coverFile.value) {
      await booksStore.uploadCover(bookId, coverFile.value)
    }
    
    router.push(`/books/${bookId}`)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update book. Please try again.'
    console.error('Update book error:', err)
  } finally {
    loading.value = false
  }
}

const handleDelete = () => {
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  showDeleteModal.value = false
  loading.value = true
  
  try {
    const bookId = parseInt(route.params.id)
    await booksStore.deleteBook(bookId)
    router.push('/library')
  } catch (err) {
    error.value = 'Failed to delete boko. Please try again.'
    console.error('Delete book error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Reuse styles from AddBook.vue */
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

.form-section {
  margin-bottom: 2rem;
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
}

.required {
  color: var(--color-error);
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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
  padding: 0.75rem 0;
  margin-bottom: 0;
  border-bottom: 1px solid var(--color-border);
  transition: all var(--transition-fast);
}

.collapsible-header:hover {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.collapsible-header .section-heading {
  margin: 0;
  font-size: 1rem;
}

.collapse-icon {
  font-size: 0.875rem;
  color: var(--color-text-light);
  transition: transform var(--transition-fast);
}

.collapsible.expanded .collapse-icon {
  transform: rotate(180deg);
}

.collapsible-content {
  margin-top: 1rem;
  padding-top: 1rem;
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

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

/* Reading Sessions Styles */
.section-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.empty-reads {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-light);
  background: var(--color-surface);
  border-radius: var(--radius-sm);
}

.reads-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.read-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  transition: all var(--transition-fast);
}

.read-section.is-editing {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(155, 72, 25, 0.1);
}

.read-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  user-select: none;
  transition: background var(--transition-fast);
}

.read-header:hover {
  background: var(--color-background);
}

.read-header-info {
  flex: 1;
}

.read-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.read-dates {
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.read-header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.read-status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.read-status-badge.status-unread {
  background: rgba(128, 128, 128, 0.15);
  color: #666;
}

.read-status-badge.status-reading {
  background: rgba(33, 150, 243, 0.15);
  color: #2196F3;
}

.read-status-badge.status-read {
  background: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
}

.read-status-badge.status-dnf {
  background: rgba(244, 67, 54, 0.15);
  color: #F44336;
}

.reread-badge {
  padding: 0.125rem 0.5rem;
  background: rgba(212, 175, 55, 0.15);
  color: var(--color-accent);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.memorable-badge-small {
  font-size: 0.875rem;
}

.read-edit-form {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-background);
}

.points-calculator-read {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.points-calculator-read h5 {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-primary);
}

.points-display-read {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.points-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.points-value {
  font-weight: 600;
  color: var(--color-primary);
}

.read-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.vibe-photo-section {
  margin-top: 0.5rem;
}

.vibe-photo-preview {
  position: relative;
  width: 200px;
  max-height: 300px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.vibe-photo-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.vibe-photo-preview .remove-btn {
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

.vibe-photo-upload {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.text-muted {
  color: var(--color-text-light);
  font-style: italic;
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
}
</style>

