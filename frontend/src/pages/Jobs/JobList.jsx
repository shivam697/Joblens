/**
 * JobList — Job applications with table view and filters
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Search, Briefcase, Eye, Pencil, Trash2, X } from 'lucide-react'
import { useJobs } from '../../hooks/useJobs'
import { PLATFORMS, STATUSES } from '../../utils/constants'
import { formatDate, formatPlatform, formatRelativeTime } from '../../utils/formatters'
import Button from '../../components/ui/Button'
import JobStatusBadge from '../../components/shared/JobStatusBadge'
import InterviewCountdown from '../../components/shared/InterviewCountdown'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'
import { jobApi } from '../../api/jobApi'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'

export default function JobList() {
  const [filters, setFilters] = useState({
    status: '',
    platform: '',
    search: '',
    page: 1,
  })
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: response, isLoading } = useJobs({
    status: filters.status || undefined,
    platform: filters.platform || undefined,
    search: filters.search || undefined,
    page: filters.page,
  })

  const jobs = response?.data?.items || []
  const total = response?.data?.total || 0
  const totalPages = response?.data?.total_pages || 1

  const hasFilters = filters.status || filters.platform || filters.search

  const handleDelete = async (e, jobId) => {
    e.stopPropagation()
    if (!confirm('Remove this application?')) return
    try {
      await jobApi.delete(jobId)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['jobStats'] })
      toast.success('Application removed')
    } catch {
      toast.error('Failed to remove application')
    }
  }

  if (isLoading) return <PageWrapper><PageSpinner /></PageWrapper>

  return (
    <PageWrapper>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">Job Applications</h1>
          <p className="text-slate-400 text-sm mt-1">{total} application{total !== 1 ? 's' : ''}</p>
        </div>
        <Link to="/jobs/new">
          <Button><Plus className="w-4 h-4" /> Add New</Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters(f => ({ ...f, search: e.target.value, page: 1 }))}
            className="input-field pl-10"
            placeholder="Search by company..."
          />
        </div>
        <select
          value={filters.status}
          onChange={(e) => setFilters(f => ({ ...f, status: e.target.value, page: 1 }))}
          className="select-field w-48"
        >
          <option value="">All Statuses</option>
          {STATUSES.map(s => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        <select
          value={filters.platform}
          onChange={(e) => setFilters(f => ({ ...f, platform: e.target.value, page: 1 }))}
          className="select-field w-44"
        >
          <option value="">All Platforms</option>
          {PLATFORMS.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={() => setFilters({ status: '', platform: '', search: '', page: 1 })}>
            <X className="w-4 h-4" /> Clear
          </Button>
        )}
      </div>

      {/* Job list */}
      {jobs.length === 0 ? (
        <div className="text-center py-16">
          <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-slate-300 font-medium mb-2">
            {hasFilters ? 'No matching applications' : 'No applications yet'}
          </h3>
          <p className="text-slate-500 text-sm mb-6">
            {hasFilters ? 'Try adjusting your filters' : 'Start tracking your job search journey'}
          </p>
          {!hasFilters && (
            <Link to="/jobs/new">
              <Button><Plus className="w-4 h-4" /> Add Your First Application</Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map(job => (
            <div
              key={job.id}
              onClick={() => navigate(`/jobs/${job.id}`)}
              className="card p-4 flex items-center justify-between cursor-pointer hover:border-slate-600 transition-colors"
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-sm font-bold text-indigo-400 shrink-0">
                  {job.company_name?.[0]?.toUpperCase()}
                </div>
                <div className="min-w-0">
                  <h3 className="text-slate-100 font-medium text-sm truncate">{job.company_name}</h3>
                  <p className="text-slate-500 text-xs">
                    {formatPlatform(job.platform)} · {formatRelativeTime(job.created_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {job.status === 'interview_scheduled' && job.interview_datetime && (
                  <InterviewCountdown interviewDatetime={job.interview_datetime} />
                )}
                <JobStatusBadge status={job.status} />
                <div className="flex items-center gap-1 ml-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); navigate(`/jobs/${job.id}/edit`) }}
                    className="p-1.5 text-slate-500 hover:text-slate-300 rounded-lg hover:bg-slate-800"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => handleDelete(e, job.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <Button
            variant="secondary"
            size="sm"
            disabled={filters.page <= 1}
            onClick={() => setFilters(f => ({ ...f, page: f.page - 1 }))}
          >
            Previous
          </Button>
          <span className="text-slate-400 text-sm px-4">
            Page {filters.page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            disabled={filters.page >= totalPages}
            onClick={() => setFilters(f => ({ ...f, page: f.page + 1 }))}
          >
            Next
          </Button>
        </div>
      )}
    </PageWrapper>
  )
}
