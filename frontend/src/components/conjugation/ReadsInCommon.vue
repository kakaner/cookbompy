<template>
  <div v-if="loading" class="loading">Loading reads in common...</div>
  <div v-else-if="books.length === 0" class="empty-state">
    <p>No books read in common yet.</p>
  </div>
  <div v-else class="books-grid">
    <div
      v-for="book in books"
      :key="book.book_id"
      class="community-book-card"
      @click="goToBookDetail(book.book_id)"
    >
      <div class="book-header">
        <div class="small-cover">
          <img
            v-if="getBookCover(book.book_id)"
            :src="getBookCover(book.book_id)"
            :alt="book.title"
          />
          <div v-else class="cover-placeholder">
            {{ book.title.charAt(0) }}
          </div>
        </div>
        <div class="book-header-info">
          <div class="book-title-small">{{ book.title }}</div>
          <div class="book-author-small">{{ book.author }}</div>
        </div>
      </div>
      
      <div class="readers-count">
        <div class="readers-avatars">
          <div
            v-for="(user, index) in book.users.slice(0, 4)"
            :key="user.user_id"
            class="reader-avatar"
            :style="getAvatarStyle(user, index)"
            :title="user.display_name"
          >
            <img
              v-if="user.profile_photo_url"
              :src="user.profile_photo_url"
              :alt="user.display_name"
            />
            <span v-else>{{ getUserInitials(user) }}</span>
          </div>
          <div
            v-if="book.users.length > 4"
            class="reader-avatar more-avatars"
            :title="`${book.users.length - 4} more readers`"
          >
            +{{ book.users.length - 4 }}
          </div>
        </div>
        <span>Read by {{ book.user_count }} {{ book.user_count === 1 ? 'user' : 'users' }}</span>
      </div>
      
      <div v-if="book.formats && book.formats.length > 0" class="formats">
        <span
          v-for="format in book.formats"
          :key="format"
          class="format-badge"
          :title="format"
        >
          {{ getFormatIcon(format) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { getFormatIcon } from '../../utils/formats'
import { useBooksStore } from '../../stores/books'

const props = defineProps({
  books: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const booksStore = useBooksStore()

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

const getUserInitials = (user) => {
  const name = user.display_name || user.username
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

const getAvatarStyle = (user, index) => {
  const colors = ['#9B4819', '#6B7456', '#D4AF37', '#8B4513']
  return {
    backgroundColor: user.profile_photo_url ? 'transparent' : colors[index % colors.length],
    marginLeft: index > 0 ? '-8px' : '0'
  }
}

const getBookCover = (bookId) => {
  // Try to get cover from books store if available
  const book = booksStore.books.find(b => b.id === bookId)
  return book?.cover_image_url || null
}
</script>

<style scoped>
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.75rem;
}

.community-book-card {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(44, 44, 44, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
}

.community-book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(155, 72, 25, 0.15);
}

.book-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.small-cover {
  width: 50px;
  height: 75px;
  background: linear-gradient(135deg, #E0DCD4 0%, #C5BFB5 100%);
  border-radius: 3px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  flex-shrink: 0;
}

.small-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
}

.book-header-info {
  flex: 1;
  min-width: 0;
}

.book-title-small {
  font-family: var(--font-heading);
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--color-text);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.book-author-small {
  font-size: 0.8rem;
  color: var(--color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.readers-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.readers-avatars {
  display: flex;
  align-items: center;
}

.reader-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.65rem;
  font-weight: 600;
  overflow: hidden;
}

.reader-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reader-avatar.more-avatars {
  background: var(--color-secondary);
  font-size: 0.6rem;
}

.formats {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.format-badge {
  font-size: 1rem;
  opacity: 0.8;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

.loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
}
</style>

