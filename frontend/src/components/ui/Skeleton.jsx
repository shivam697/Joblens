/**
 * Skeleton — Loading placeholder for data fetching states
 */

export default function Skeleton({ className = '', ...props }) {
  return (
    <div
      className={`animate-pulse bg-slate-800 rounded-xl ${className}`}
      {...props}
    />
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">
      <Skeleton className="h-4 w-3/4 mb-3" />
      <Skeleton className="h-3 w-1/2 mb-2" />
      <Skeleton className="h-3 w-1/3" />
    </div>
  )
}
