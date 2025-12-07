/**
 * Color theme definitions for CookBomPy
 * Each theme has a primary (accent) color and secondary color
 */

export const themes = {
  terracotta: {
    name: 'Terracotta',
    primary: '#9B4819',
    primaryLight: 'rgba(155, 72, 25, 0.1)',
    primaryDark: '#7A3A14',
    secondary: '#6B7456',
    secondaryLight: 'rgba(107, 116, 86, 0.1)',
    secondaryDark: '#545D44',
    accent: '#D4AF37'
  },
  ocean: {
    name: 'Ocean Blue',
    primary: '#1E5F8A',
    primaryLight: 'rgba(30, 95, 138, 0.1)',
    primaryDark: '#164866',
    secondary: '#4A7C6F',
    secondaryLight: 'rgba(74, 124, 111, 0.1)',
    secondaryDark: '#3A6259',
    accent: '#7CB9E8'
  },
  forest: {
    name: 'Forest Green',
    primary: '#2D5F3D',
    primaryLight: 'rgba(45, 95, 61, 0.1)',
    primaryDark: '#224830',
    secondary: '#8B6B4A',
    secondaryLight: 'rgba(139, 107, 74, 0.1)',
    secondaryDark: '#6E553A',
    accent: '#90EE90'
  },
  midnight: {
    name: 'Midnight Purple',
    primary: '#5D4E7A',
    primaryLight: 'rgba(93, 78, 122, 0.1)',
    primaryDark: '#493D60',
    secondary: '#7A8B8B',
    secondaryLight: 'rgba(122, 139, 139, 0.1)',
    secondaryDark: '#616E6E',
    accent: '#B19CD9'
  },
  gold: {
    name: 'Warm Gold',
    primary: '#B8860B',
    primaryLight: 'rgba(184, 134, 11, 0.1)',
    primaryDark: '#8B6508',
    secondary: '#6B5B4A',
    secondaryLight: 'rgba(107, 91, 74, 0.1)',
    secondaryDark: '#554838',
    accent: '#FFD700'
  },
  slate: {
    name: 'Slate',
    primary: '#4A5568',
    primaryLight: 'rgba(74, 85, 104, 0.1)',
    primaryDark: '#3A4250',
    secondary: '#718096',
    secondaryLight: 'rgba(113, 128, 150, 0.1)',
    secondaryDark: '#5A6677',
    accent: '#A0AEC0'
  }
}

export const themeList = Object.entries(themes).map(([key, value]) => ({
  key,
  ...value
}))

/**
 * Apply a theme to the document root
 * @param {string} themeKey - The theme key (e.g., 'terracotta', 'ocean')
 */
export function applyTheme(themeKey) {
  const theme = themes[themeKey] || themes.terracotta
  const root = document.documentElement

  root.style.setProperty('--color-primary', theme.primary)
  root.style.setProperty('--color-primary-light', theme.primaryLight)
  root.style.setProperty('--color-primary-dark', theme.primaryDark)
  root.style.setProperty('--color-secondary', theme.secondary)
  root.style.setProperty('--color-secondary-light', theme.secondaryLight)
  root.style.setProperty('--color-secondary-dark', theme.secondaryDark)
  root.style.setProperty('--color-accent', theme.accent)

  // Store in localStorage for persistence
  localStorage.setItem('colorTheme', themeKey)
}

/**
 * Get the current theme from localStorage or default
 * @returns {string} The current theme key
 */
export function getCurrentTheme() {
  return localStorage.getItem('colorTheme') || 'terracotta'
}

/**
 * Initialize theme on app load
 */
export function initializeTheme() {
  const savedTheme = getCurrentTheme()
  applyTheme(savedTheme)
}

