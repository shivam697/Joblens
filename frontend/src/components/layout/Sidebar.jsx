/**
 * Sidebar — Side navigation with all route links and icons
 */

import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Upload,
  ScanSearch,
  Lightbulb,
  X,
} from 'lucide-react'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/jobs', label: 'Applications', icon: Briefcase },
  { path: '/resume', label: 'My Resumes', icon: FileText },
  { path: '/resume/upload', label: 'Upload Resume', icon: Upload },
  { path: '/ats/check', label: 'ATS Quick Check', icon: ScanSearch },
  { path: '/recommendations', label: 'AI Recommendations', icon: Lightbulb },
]

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-16 bottom-0 w-64 bg-slate-900 border-r border-slate-800
        transform transition-transform duration-300 z-50
        lg:translate-x-0 lg:static lg:z-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Mobile close button */}
        <div className="flex justify-end p-3 lg:hidden">
          <button onClick={onClose} className="text-slate-400 hover:text-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation links */}
        <nav className="px-3 py-2 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                }`
              }
            >
              <Icon className="w-4.5 h-4.5" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Bottom branding */}
        <div className="absolute bottom-6 left-0 right-0 px-6">
          <div className="bg-gradient-to-r from-indigo-600/10 to-violet-600/10 border border-indigo-500/10 rounded-xl p-4 text-center">
            <p className="text-xs text-slate-500">Powered by</p>
            <p className="text-sm font-display font-semibold text-indigo-400 mt-0.5">
              Gemini AI ✦
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
