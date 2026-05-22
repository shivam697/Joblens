/**
 * Card — Reusable card container with consistent dark styling
 */

export default function Card({ children, className = '', ...props }) {
  return (
    <div
      className={`bg-slate-900 border border-slate-700 rounded-2xl shadow-lg ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
