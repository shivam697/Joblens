/**
 * Navbar — Top navigation bar with user avatar and logout
 */

import { useNavigate } from 'react-router-dom'
import { LogOut, Search, Menu } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function Navbar({ onMenuToggle }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
      toast.success('Logged out successfully')
      navigate('/login')
    } catch {
      toast.error('Failed to logout')
    }
  }

  // Get user initials for avatar fallback
  const initials = user?.full_name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?'

  return (
    <nav className="h-16 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 flex items-center justify-between px-6 sticky top-0 z-40">
      {/* Left: Logo and menu toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="lg:hidden text-slate-400 hover:text-slate-100"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1
          className="text-xl font-display font-bold text-indigo-400 cursor-pointer"
          onClick={() => navigate('/dashboard')}
        >
          Job<span className="text-slate-100">Lense</span>
        </h1>
      </div>

      {/* Right: User info and logout */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.full_name}
              className="w-8 h-8 rounded-full border border-slate-600"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-semibold text-white">
              {initials}
            </div>
          )}
          <span className="text-sm text-slate-300 hidden sm:block">
            {user?.full_name}
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="text-slate-400 hover:text-rose-400 transition-colors p-2 rounded-lg hover:bg-slate-800"
          title="Logout"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </nav>
  )
}
