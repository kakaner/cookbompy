/**
 * Time dimension utilities for statistics
 */

export const TIME_DIMENSIONS = [
  { value: 'day', label: 'Day' },
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
  { value: 'year', label: 'Year' },
  { value: 'semester', label: 'Semester' },
  { value: 'alltime', label: 'All Time' }
]

export function getTimeDimensionOptions() {
  return TIME_DIMENSIONS
}

export function formatTimeLabel(dimension, dateString) {
  if (dimension === 'alltime') {
    return 'All Time'
  }
  
  if (!dateString) {
    return ''
  }
  
  const date = new Date(dateString)
  
  if (dimension === 'day') {
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } else if (dimension === 'week') {
    // Format as "2024-W01"
    const year = date.getFullYear()
    const week = getWeekNumber(date)
    return `${year}-W${week.toString().padStart(2, '0')}`
  } else if (dimension === 'month') {
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
  } else if (dimension === 'year') {
    return date.getFullYear().toString()
  } else if (dimension === 'semester') {
    // Semester labels come from backend as "S42" format
    return dateString
  }
  
  return dateString
}

export function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
}

export function getSemesterLabel(semesterNumber, customName) {
  if (customName) {
    return customName
  }
  return `Semester ${semesterNumber}`
}

export function groupDataByDimension(data, dimension) {
  // Data is already grouped by backend, this is just for frontend processing if needed
  return data
}

export function formatPercentage(value, decimals = 1) {
  return `${value.toFixed(decimals)}%`
}

export function formatNumber(value, decimals = 0) {
  return value.toFixed(decimals)
}

