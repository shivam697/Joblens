/**
 * Recommendations API — Generate and fetch AI job recommendations
 */

import api from './axiosInstance'

export const recommendationApi = {
  /** Generate new recommendations from active resume */
  generate: (force = false) =>
    api.post('/recommendations/', null, { params: force ? { force: true } : {} }),

  /** Get most recent recommendations */
  get: () => api.get('/recommendations/'),
}
