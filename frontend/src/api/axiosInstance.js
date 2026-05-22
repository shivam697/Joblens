/**
 * Axios Instance — Configured HTTP client for all API calls
 * 
 * withCredentials: true is CRITICAL — it sends the httpOnly cookie
 * with every request so the backend can authenticate the user.
 * Without this, the cookie stays in the browser but never gets sent.
 */

import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // CRITICAL — sends httpOnly cookie with every request
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor — auto-redirect to login on 401 (unauthorized)
axiosInstance.interceptors.response.use(
  (response) => {
    // Return response.data directly for cleaner API calls
    // Instead of: const result = (await api.get('/jobs')).data
    // We can write: const result = await api.get('/jobs')
    return response.data
  },
  (error) => {
    // If server returns 401, user's session has expired
    // Redirect to login page automatically
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname
      const publicPaths = ['/login', '/register', '/auth/callback']
      if (!publicPaths.includes(currentPath)) {
        window.location.href = '/login'
      }
    }

    const data = error.response?.data
    const message =
      data?.message ||
      (typeof data?.detail === 'string' ? data.detail : null) ||
      (Array.isArray(data?.detail) ? data.detail[0]?.msg : null) ||
      'Network error'

    return Promise.reject({ ...data, message })
  }
)

export default axiosInstance
