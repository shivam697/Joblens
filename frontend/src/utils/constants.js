/**
 * Application Constants — Single source of truth for all magic values
 * 
 * Using constants prevents typos and makes changes easy —
 * update once here, reflected everywhere.
 */

// Polling interval for ATS report status checks (milliseconds)
export const POLL_INTERVAL_MS = 3000

// Maximum resume file size in MB
export const MAX_FILE_SIZE_MB = 5

// Job application platforms — must match backend ENUM values
export const PLATFORMS = [
  { value: 'naukri', label: 'Naukri' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'instahire', label: 'InstaHire' },
  { value: 'foundit', label: 'Foundit' },
  { value: 'indeed', label: 'Indeed' },
  { value: 'glassdoor', label: 'Glassdoor' },
  { value: 'internshala', label: 'Internshala' },
  { value: 'wellfound', label: 'Wellfound' },
  { value: 'other', label: 'Other' },
]

// Job application statuses — ordered by lifecycle stage
export const STATUSES = [
  { value: 'saved', label: 'Saved', color: 'slate' },
  { value: 'applied', label: 'Applied', color: 'blue' },
  { value: 'screening', label: 'Screening', color: 'amber' },
  { value: 'interview_scheduled', label: 'Interview Scheduled', color: 'violet' },
  { value: 'interview_done', label: 'Interview Done', color: 'indigo' },
  { value: 'offered', label: 'Offered', color: 'emerald' },
  { value: 'rejected', label: 'Rejected', color: 'rose' },
  { value: 'accepted', label: 'Accepted', color: 'green' },
  { value: 'withdrawn', label: 'Withdrawn', color: 'gray' },
]

// Interview modes
export const INTERVIEW_MODES = [
  { value: 'online', label: 'Online' },
  { value: 'in_person', label: 'In Person' },
  { value: 'phone', label: 'Phone' },
]

// Backend API base URL
export const API_BASE_URL = 'http://localhost:8000/api/v1'

// Backend base URL (non-API routes like OAuth)
export const BACKEND_URL = import.meta.env.VITE_API_URL
