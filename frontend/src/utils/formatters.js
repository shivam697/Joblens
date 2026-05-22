/**
 * Display Formatters — Human-readable formatting for dates, money, and status
 */

import { format, formatDistanceToNow, isValid } from 'date-fns'

/**
 * Format a date string into a readable format like "Jan 15, 2024"
 */
export function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  if (!isValid(date)) return '—'
  return format(date, 'MMM d, yyyy')
}

/**
 * Format a datetime string like "Jan 15, 2024 at 10:30 AM"
 */
export function formatDateTime(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  if (!isValid(date)) return '—'
  return format(date, "MMM d, yyyy 'at' h:mm a")
}

/**
 * Format a date as relative time like "3 days ago"
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (!isValid(date)) return ''
  return formatDistanceToNow(date, { addSuffix: true })
}

/**
 * Format salary with Indian Rupee symbol and comma formatting
 * 500000 → ₹5,00,000
 */
export function formatSalary(amount) {
  if (!amount) return '—'
  return `₹${Number(amount).toLocaleString('en-IN')}`
}

/**
 * Get a human-readable label for a status value
 * "interview_scheduled" → "Interview Scheduled"
 */
export function formatStatus(status) {
  if (!status) return '—'
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Get a human-readable label for a platform value
 * "linkedin" → "LinkedIn"
 */
export function formatPlatform(platform) {
  const labels = {
    naukri: 'Naukri',
    linkedin: 'LinkedIn',
    instahire: 'InstaHire',
    foundit: 'Foundit',
    indeed: 'Indeed',
    glassdoor: 'Glassdoor',
    internshala: 'Internshala',
    wellfound: 'Wellfound',
    other: 'Other',
  }
  return labels[platform] || platform || '—'
}

/**
 * Format time remaining until a datetime
 * Returns { days, hours, minutes } object
 */
export function getTimeUntil(dateString) {
  if (!dateString) return null
  const target = new Date(dateString)
  const now = new Date()
  const diff = target - now

  if (diff <= 0) return null

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  return { days, hours, minutes, totalMs: diff }
}
