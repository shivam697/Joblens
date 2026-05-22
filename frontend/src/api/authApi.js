/**
 * Auth API — Login, register, logout, and session management calls
 */

import api from './axiosInstance'

export const authApi = {
  /** Register new user with name, email, password */
  register: (data) => api.post('/auth/register', data),

  /** Login with email and password */
  login: (data) => api.post('/auth/login', data),

  /** Logout — clears httpOnly cookie */
  logout: () => api.post('/auth/logout'),

  /** Get current user from cookie session */
  me: () => api.get('/auth/me'),
}
