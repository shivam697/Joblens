/**
 * Job Application API — CRUD operations and stats
 */

import api from './axiosInstance'

export const jobApi = {
  /** Create new job application */
  create: (data) => api.post('/jobs/', data),

  /** Get paginated list with optional filters */
  list: (params = {}) => api.get('/jobs/', { params }),

  /** Get dashboard stats (total, by_status, interviews_today, by_platform) */
  getStats: () => api.get('/jobs/stats'),

  /** Get single job application by ID */
  getById: (id) => api.get(`/jobs/${id}`),

  /** Update job application */
  update: (id, data) => api.put(`/jobs/${id}`, data),

  /** Soft-delete job application */
  delete: (id) => api.delete(`/jobs/${id}`),
}
