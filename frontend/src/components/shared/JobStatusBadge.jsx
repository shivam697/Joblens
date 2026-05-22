/**
 * JobStatusBadge — Color-coded badge for all job application statuses
 * 
 * Interview Scheduled gets a special animated pulse dot to draw attention.
 */

import Badge from '../ui/Badge'
import { formatStatus } from '../../utils/formatters'
import { STATUSES } from '../../utils/constants'

export default function JobStatusBadge({ status }) {
  // Find the color mapping for this status
  const statusInfo = STATUSES.find(s => s.value === status)
  const color = statusInfo?.color || 'slate'

  return (
    <Badge color={color}>
      {/* Animated pulse dot for interview_scheduled — draws attention */}
      {status === 'interview_scheduled' && (
        <span className="relative flex h-2 w-2 mr-1">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-400" />
        </span>
      )}
      {formatStatus(status)}
    </Badge>
  )
}
