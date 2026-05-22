/**
 * App — Root component with all routes and ProtectedRoute wrapper
 * 
 * Public routes: /login, /register, /auth/callback
 * Protected routes: everything else (redirects to /login if not authenticated)
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { PageSpinner } from './components/ui/Spinner'

// Auth pages
import Login from './pages/Auth/Login'
import Register from './pages/Auth/Register'
import OAuthCallback from './pages/Auth/OAuthCallback'

// Protected pages
import Dashboard from './pages/Dashboard/Dashboard'
import ResumeUpload from './pages/Resume/ResumeUpload'
import ResumeList from './pages/Resume/ResumeList'
import ATSQuickCheck from './pages/ATS/ATSQuickCheck'
import ATSReport from './pages/ATS/ATSReport'
import JobList from './pages/Jobs/JobList'
import JobCreate from './pages/Jobs/JobCreate'
import JobEdit from './pages/Jobs/JobEdit'
import JobDetail from './pages/Jobs/JobDetail'
import Recommendations from './pages/Recommendations/Recommendations'

/**
 * ProtectedRoute — Redirects unauthenticated users to login
 * Shows loading spinner during initial auth check (prevents flash of login page)
 */
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  // Still checking auth status — show loading instead of redirecting
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-app">
        <PageSpinner />
      </div>
    )
  }

  // Not authenticated — redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

/**
 * PublicRoute — Redirects authenticated users away from login/register
 */
function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-app">
        <PageSpinner />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default function App() {
  return (
    <Routes>
      {/* Public routes — login, register, OAuth callback */}
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      <Route path="/auth/callback" element={<OAuthCallback />} />

      {/* Protected routes — require authentication */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/resume" element={<ProtectedRoute><ResumeList /></ProtectedRoute>} />
      <Route path="/resume/upload" element={<ProtectedRoute><ResumeUpload /></ProtectedRoute>} />
      <Route path="/ats/check" element={<ProtectedRoute><ATSQuickCheck /></ProtectedRoute>} />
      <Route path="/ats/report/:reportId" element={<ProtectedRoute><ATSReport /></ProtectedRoute>} />
      <Route path="/jobs" element={<ProtectedRoute><JobList /></ProtectedRoute>} />
      <Route path="/jobs/new" element={<ProtectedRoute><JobCreate /></ProtectedRoute>} />
      <Route path="/jobs/:id" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
      <Route path="/jobs/:id/edit" element={<ProtectedRoute><JobEdit /></ProtectedRoute>} />
      <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />

      {/* Default redirect — go to dashboard if authenticated, login if not */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
