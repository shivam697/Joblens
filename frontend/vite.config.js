import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config for JobLense frontend
// React plugin enables Fast Refresh for instant dev feedback
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy API calls to FastAPI backend during development
    // This avoids CORS issues when running frontend and backend on different ports
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
