/**
 * Format icons and display utilities
 */

export const FORMAT_ICONS = {
  HARDCOVER: '📖',
  PAPERBACK: '📕',
  MASS_MARKET_PAPERBACK: '📕',
  TRADE_PAPERBACK: '📕',
  LEATHER_BOUND: '📖',
  KINDLE: '📘',
  PDF: '📄',
  EPUB: '📄',
  OTHER_DIGITAL: '📄',
  AUDIOBOOK_AUDIBLE: '🎧',
  AUDIOBOOK_OTHER: '🎧',
  AUDIOBOOK_CD: '🎧',
  ANTHOLOGY: '📚',
  MAGAZINE: '📄',
  OTHER: '📄'
}

export const FORMAT_DISPLAY_NAMES = {
  HARDCOVER: 'Hardcover',
  PAPERBACK: 'Paperback',
  MASS_MARKET_PAPERBACK: 'Mass Market Paperback',
  TRADE_PAPERBACK: 'Trade Paperback',
  LEATHER_BOUND: 'Leather Bound',
  KINDLE: 'Kindle/E-book',
  PDF: 'PDF',
  EPUB: 'EPUB',
  OTHER_DIGITAL: 'Other Digital',
  AUDIOBOOK_AUDIBLE: 'Audiobook (Audible)',
  AUDIOBOOK_OTHER: 'Audiobook (Other)',
  AUDIOBOOK_CD: 'Audiobook (CD)',
  ANTHOLOGY: 'Anthology',
  MAGAZINE: 'Magazine',
  OTHER: 'Other'
}

export const FORMAT_OPTIONS = [
  { value: 'HARDCOVER', label: 'Hardcover', icon: '📖' },
  { value: 'PAPERBACK', label: 'Paperback', icon: '📕' },
  { value: 'MASS_MARKET_PAPERBACK', label: 'Mass Market Paperback', icon: '📕' },
  { value: 'TRADE_PAPERBACK', label: 'Trade Paperback', icon: '📕' },
  { value: 'LEATHER_BOUND', label: 'Leather Bound', icon: '📖' },
  { value: 'KINDLE', label: 'Kindle/E-book', icon: '📘' },
  { value: 'PDF', label: 'PDF', icon: '📄' },
  { value: 'EPUB', label: 'EPUB', icon: '📄' },
  { value: 'OTHER_DIGITAL', label: 'Other Digital', icon: '📄' },
  { value: 'AUDIOBOOK_AUDIBLE', label: 'Audiobook (Audible)', icon: '🎧' },
  { value: 'AUDIOBOOK_OTHER', label: 'Audiobook (Other)', icon: '🎧' },
  { value: 'AUDIOBOOK_CD', label: 'Audiobook (CD)', icon: '🎧' },
  { value: 'ANTHOLOGY', label: 'Anthology', icon: '📚' },
  { value: 'MAGAZINE', label: 'Magazine', icon: '📄' },
  { value: 'OTHER', label: 'Other', icon: '📄' }
]

export function getFormatIcon(format) {
  return FORMAT_ICONS[format] || '📄'
}

export function getFormatDisplayName(format) {
  return FORMAT_DISPLAY_NAMES[format] || format
}

