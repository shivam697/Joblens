/**
 * Resume API — Upload, list, delete, and activate resumes
 */

import api from './axiosInstance'

export const resumeApi = {
  /** Upload resume file (PDF or text) */
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** List all user's resumes */
  list: () => api.get('/resume/'),

  /** Delete a resume by ID */
  delete: (id) => api.delete(`/resume/${id}`),

  /** Set a resume as active */
  activate: (id) => api.patch(`/resume/${id}/activate`),
}
