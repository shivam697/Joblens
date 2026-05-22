/**
 * ATS Analysis API — Quick check (Flow 1), job-linked (Flow 2), and polling
 */

import api from './axiosInstance'

export const atsApi = {
  /**
   * Flow 1 — Quick ATS Check: upload resume + paste JD
   * Accepts FormData with file/resume_id and job_description
   */
  quickAnalyze: (formData) => {
    return api.post('/ats/quick-analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /**
   * Flow 2 — Job-Linked ATS Analysis
   * Sends job_application_id, backend fetches resume and JD automatically
   */
  jobLinkedAnalyze: (jobApplicationId) => {
    const formData = new FormData()
    formData.append('job_application_id', jobApplicationId)
    return api.post('/ats/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** Get ATS report by ID — used for polling during analysis */
  getReport: (reportId) => api.get(`/ats/report/${reportId}`),

  /** Get user's ATS analysis history */
  getHistory: () => api.get('/ats/history'),
}
