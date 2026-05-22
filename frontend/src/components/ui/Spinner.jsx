/**
 * Spinner — Loading indicator in small, medium, large sizes
 */

import { Loader2 } from 'lucide-react'

export default function Spinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <Loader2 className={`animate-spin text-indigo-500 ${sizes[size]} ${className}`} />
  )
}

/**
 * Full page loading spinner — used during initial data load
 */
export function PageSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        <Loader2 className="w-10 h-10 animate-spin text-indigo-500 mx-auto mb-3" />
        <p className="text-slate-400 text-sm">Loading...</p>
      </div>
    </div>
  )
}
