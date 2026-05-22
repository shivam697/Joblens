/**
 * OAuthCallback — Handles OAuth redirect completion
 * 
 * After Google/Facebook OAuth, the user is redirected here.
 * We call GET /auth/me to load the user from the cookie that was set by the backend.
 */

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function OAuthCallback() {
  const { checkAuth } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false

    const handleCallback = async () => {
      // Brief pause so the browser applies the httpOnly cookie from the OAuth redirect
      await new Promise((resolve) => setTimeout(resolve, 300))
      if (cancelled) return

      try {
        const user = await checkAuth({ throwOnFailure: true })
        if (!user) {
          throw new Error('No session')
        }
        toast.success('Welcome to JobLense!')
        navigate('/dashboard', { replace: true })
      } catch {
        toast.error('Login failed. Please try again.')
        navigate('/login', { replace: true })
      }
    }

    handleCallback()
    return () => { cancelled = true }
  }, [checkAuth, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-app">
      <div className="text-center">
        <Loader2 className="w-10 h-10 animate-spin text-indigo-500 mx-auto mb-4" />
        <p className="text-slate-300 text-lg font-medium">Completing your login...</p>
        <p className="text-slate-500 text-sm mt-1">Please wait a moment</p>
      </div>
    </div>
  )
}
