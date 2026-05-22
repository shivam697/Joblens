/**
 * InterviewCountdown — Live countdown timer to interview datetime
 * 
 * Updates every minute. Returns null if interview is in the past.
 * Color changes from normal → amber (<24hr) → rose (<2hr) for urgency.
 */

import { useState, useEffect } from 'react'
import { Clock } from 'lucide-react'
import { getTimeUntil } from '../../utils/formatters'

export default function InterviewCountdown({ interviewDatetime }) {
  const [timeLeft, setTimeLeft] = useState(null)

  useEffect(() => {
    if (!interviewDatetime) return

    // Update immediately and then every 60 seconds
    const update = () => setTimeLeft(getTimeUntil(interviewDatetime))
    update()
    const interval = setInterval(update, 60000)
    return () => clearInterval(interval)
  }, [interviewDatetime])

  // Don't render if interview is in the past or no datetime
  if (!timeLeft) return null

  // Color based on urgency
  const getUrgencyColor = () => {
    const hoursLeft = timeLeft.days * 24 + timeLeft.hours
    if (hoursLeft < 2) return 'text-rose-400 border-rose-500/30 bg-rose-500/10'
    if (hoursLeft < 24) return 'text-amber-400 border-amber-500/30 bg-amber-500/10'
    return 'text-indigo-400 border-indigo-500/30 bg-indigo-500/10'
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-sm font-medium ${getUrgencyColor()}`}>
      <Clock className="w-4 h-4" />
      <span className="font-display">
        {timeLeft.days > 0 && `${timeLeft.days}d `}
        {timeLeft.hours}h {timeLeft.minutes}m
      </span>
    </div>
  )
}
