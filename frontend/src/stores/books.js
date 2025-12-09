import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useBooksStore = defineStore('books', () => {
  const books = ref([])
  const currentBook = ref(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    page_size: 50,
    total: 0,
    total_pages: 0
  })
  const filters = ref({
    format: null,
    book_type: null,
    read_status: null,
    search: null,
    sort: 'date_read_desc',
    language: null,
    has_review: null,
    author: null,
    publisher: null,
    series: null,
    genre: null,
    semester: null
  })

  const fetchBooks = async (params = {}) => {
    loading.value = true
    try {
      const queryParams = {
        page: params.page || pagination.value.page,
        page_size: params.page_size || pagination.value.page_size,
        ...filters.value,
        ...params
      }
      
      // Remove null/undefined values and handle arrays
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === null || queryParams[key] === undefined) {
          delete queryParams[key]
        } else if (Array.isArray(queryParams[key]) && queryParams[key].length === 0) {
          delete queryParams[key]
        }
      })
      
      const response = await api.get('/books', { params: queryParams })
      books.value = response.data.items
      pagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total: response.data.total,
        total_pages: response.data.total_pages
      }
      return response.data
    } catch (error) {
      console.error('Failed to fetch books:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchBook = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/books/${id}`)
      currentBook.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch book:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createBook = async (bookData) => {
    loading.value = true
    try {
      const response = await api.post('/books', bookData)
      // Refresh books list
      await fetchBooks()
      return response.data
    } catch (error) {
      console.error('Failed to create book:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateBook = async (id, bookData) => {
    loading.value = true
    try {
      const response = await api.put(`/books/${id}`, bookData)
      // Update current book if it's the one being updated
      if (currentBook.value && currentBook.value.id === id) {
        currentBook.value = response.data
      }
      // Refresh books list
      await fetchBooks()
      return response.data
    } catch (error) {
      console.error('Failed to update book:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteBook = async (id) => {
    loading.value = true
    try {
      await api.delete(`/books/${id}`)
      // Remove from local state
      books.value = books.value.filter(book => book.id !== id)
      if (currentBook.value && currentBook.value.id === id) {
        currentBook.value = null
      }
      // Refresh books list
      await fetchBooks()
    } catch (error) {
      console.error('Failed to delete book:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const searchExternal = async (query, isbn = null) => {
    loading.value = true
    try {
      const params = { q: query }
      if (isbn) {
        params.isbn = isbn
      }
      const response = await api.get('/books/search/external', { params })
      return response.data
    } catch (error) {
      console.error('Failed to search external:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const uploadCover = async (bookId, file) => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post(`/books/${bookId}/cover`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // Update current book if it's the one being updated
      if (currentBook.value && currentBook.value.id === bookId) {
        currentBook.value = response.data
      }
      
      // Update in books list
      const bookIndex = books.value.findIndex(b => b.id === bookId)
      if (bookIndex !== -1) {
        books.value[bookIndex] = response.data
      }
      
      return response.data
    } catch (error) {
      console.error('Failed to upload cover:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const setFilter = (key, value) => {
    filters.value[key] = value
    pagination.value.page = 1 // Reset to first page when filter changes
  }

  const clearFilters = () => {
    filters.value = {
      format: null,
      book_type: null,
      read_status: null,
      search: null,
      sort: 'date_read_desc',
      language: null,
      has_review: null,
      author: null,
      publisher: null,
      series: null,
      genre: null,
      semester: null
    }
    pagination.value.page = 1
  }

  return {
    books,
    currentBook,
    loading,
    pagination,
    filters,
    fetchBooks,
    fetchBook,
    createBook,
    updateBook,
    deleteBook,
    searchExternal,
    uploadCover,
    setFilter,
    clearFilters
  }
})

