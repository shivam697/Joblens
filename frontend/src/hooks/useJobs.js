/**
 * Jobs Hook — Fetch job list with React Query, filters, and pagination
 */

import { useQuery } from '@tanstack/react-query'
import { jobApi } from '../api/jobApi'

export function useJobs(filters = {}) {
  const { status, platform, search, page = 1, limit = 20 } = filters

  return useQuery({
    queryKey: ['jobs', { status, platform, search, page, limit }],
    queryFn: () => jobApi.list({ status, platform, search, page, limit }),
    // keepPreviousData prevents flash of empty state during pagination
    placeholderData: (previousData) => previousData,
  })
}

export function useJobStats() {
  return useQuery({
    queryKey: ['jobStats'],
    queryFn: () => jobApi.getStats(),
  })
}

export function useJobDetail(jobId) {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobApi.getById(jobId),
    enabled: !!jobId, // Don't fetch until we have an ID
  })
}
