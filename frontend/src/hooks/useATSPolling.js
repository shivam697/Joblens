/**
 * ATS Polling Hook — Polls report status every 3 seconds until complete
 * 
 * Used by both ATSQuickCheck (Flow 1) and JobDetail (Flow 2) pages.
 * Automatically stops polling when status becomes 'completed' or 'failed'.
 * Cleans up interval on component unmount to prevent memory leaks.
 */

import { useState, useEffect, useCallback } from 'react'
import { atsApi } from '../api/atsApi'
import { POLL_INTERVAL_MS } from '../utils/constants'

export function useATSPolling(reportId) {
  const [report, setReport] = useState(null)
  const [isPolling, setIsPolling] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [isFailed, setIsFailed] = useState(false)

  useEffect(() => {
    // Don't start polling without a report ID
    if (!reportId) return

    setIsPolling(true)
    setIsComplete(false)
    setIsFailed(false)

    // Poll immediately on first call, then every 3 seconds
    const fetchReport = async () => {
      try {
        const response = await atsApi.getReport(reportId)
        const data = response.data

        setReport(data)

        if (data.status === 'completed') {
          setIsComplete(true)
          setIsPolling(false)
          return true // Signal to stop polling
        }

        if (data.status === 'failed') {
          setIsFailed(true)
          setIsPolling(false)
          return true // Signal to stop polling
        }

        return false // Keep polling
      } catch (error) {
        console.error('Polling error:', error)
        setIsFailed(true)
        setIsPolling(false)
        setReport({ error_message: error?.message || 'Failed to fetch report' })
        return true
      }
    }

    // Fetch immediately
    fetchReport()

    // Then poll every POLL_INTERVAL_MS
    const interval = setInterval(async () => {
      const shouldStop = await fetchReport()
      if (shouldStop) {
        clearInterval(interval)
      }
    }, POLL_INTERVAL_MS)

    // Cleanup on unmount — prevents polling after navigation
    return () => clearInterval(interval)
  }, [reportId])

  return { report, isPolling, isComplete, isFailed }
}
