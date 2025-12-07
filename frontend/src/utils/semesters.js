// Semester calculation utilities for frontend

// The epoch: first semester starts May 15, 2005
const EPOCH_YEAR = 2005
const EPOCH_MONTH = 5
const EPOCH_DAY = 15

/**
 * Calculate semester number from a date
 * @param {Date} checkDate - The date to check
 * @returns {number} Semester number (1-based)
 */
export function calculateSemesterNumber(checkDate) {
  if (!(checkDate instanceof Date)) {
    checkDate = new Date(checkDate)
  }
  
  const epoch = new Date(EPOCH_YEAR, EPOCH_MONTH - 1, EPOCH_DAY)
  
  if (checkDate < epoch) {
    return null // Date before epoch
  }
  
  // Calculate years since epoch
  const yearDiff = checkDate.getFullYear() - EPOCH_YEAR
  
  // Determine which half of the year we're in
  const month = checkDate.getMonth() + 1 // getMonth() is 0-based
  const day = checkDate.getDate()
  
  let semesterNumber
  
  if (month < 5 || (month === 5 && day < 15)) {
    // Before May 15 of this year - we're in the second half of a semester
    // that started in November of the previous year
    const semesterYearOffset = (yearDiff - 1) * 2
    semesterNumber = semesterYearOffset + 2 // Even semester
  } else if (month < 11 || (month === 11 && day < 15)) {
    // May 15 to November 14 - odd semester
    const semesterYearOffset = yearDiff * 2
    semesterNumber = semesterYearOffset + 1 // Odd semester
  } else {
    // November 15 onwards - even semester
    const semesterYearOffset = yearDiff * 2
    semesterNumber = semesterYearOffset + 2 // Even semester
  }
  
  return semesterNumber
}

/**
 * Get current semester number
 * @returns {number} Current semester number
 */
export function getCurrentSemester() {
  return calculateSemesterNumber(new Date())
}

/**
 * Format semester display name (e.g., "Semester 42")
 * @param {number} semesterNumber - Semester number
 * @returns {string} Display name
 */
export function getSemesterDisplayName(semesterNumber) {
  if (!semesterNumber) return null
  return `Semester ${semesterNumber}`
}

