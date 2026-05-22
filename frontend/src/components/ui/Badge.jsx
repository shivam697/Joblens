/**
 * Badge — Small label with color variants for status, platform, etc.
 */

export default function Badge({ children, color = 'slate', className = '' }) {
  const colors = {
    slate: 'bg-slate-700 text-slate-300',
    blue: 'bg-blue-500/20 text-blue-400',
    amber: 'bg-amber-500/20 text-amber-400',
    violet: 'bg-violet-500/20 text-violet-400',
    indigo: 'bg-indigo-500/20 text-indigo-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    rose: 'bg-rose-500/20 text-rose-400',
    green: 'bg-green-500/20 text-green-400',
    gray: 'bg-gray-500/20 text-gray-400',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[color] || colors.slate} ${className}`}>
      {children}
    </span>
  )
}
