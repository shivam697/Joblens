/**
 * Dashboard — Stats cards, recent jobs, today's interviews, quick actions
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Briefcase, Calendar, Trophy, TrendingUp, Plus, ScanSearch, Lightbulb, ChevronRight } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { jobApi } from '../../api/jobApi'
import Card from '../../components/ui/Card'
import JobStatusBadge from '../../components/shared/JobStatusBadge'
import InterviewCountdown from '../../components/shared/InterviewCountdown'
import { formatRelativeTime, formatPlatform, formatDateTime } from '../../utils/formatters'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'

export default function Dashboard() {
  const navigate = useNavigate()

  // Fetch stats and recent jobs
  const { data: statsResponse, isLoading: statsLoading } = useQuery({
    queryKey: ['jobStats'],
    queryFn: () => jobApi.getStats(),
  })

  const { data: jobsResponse, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs', { page: 1, limit: 5 }],
    queryFn: () => jobApi.list({ page: 1, limit: 5 }),
  })

  const stats = statsResponse?.data
  const recentJobs = jobsResponse?.data?.items || []
  const todaysInterviews = stats?.interviews_today_list || []

  if (statsLoading) return <PageWrapper><PageSpinner /></PageWrapper>

  // Calculate response rate
  const totalApplied = (stats?.total || 0)
  const rejected = stats?.by_status?.rejected || 0
  const responseRate = totalApplied > 0
    ? Math.round(((totalApplied - rejected) / totalApplied) * 100)
    : 0

  const statCards = [
    { label: 'Total Applications', value: stats?.total || 0, icon: Briefcase, color: 'from-indigo-600 to-indigo-800' },
    { label: 'Interviews Scheduled', value: stats?.by_status?.interview_scheduled || 0, icon: Calendar, color: 'from-amber-600 to-amber-800' },
    { label: 'Offers Received', value: stats?.by_status?.offered || 0, icon: Trophy, color: 'from-emerald-600 to-emerald-800' },
    { label: 'Response Rate', value: `${responseRate}%`, icon: TrendingUp, color: 'from-violet-600 to-violet-800' },
  ]

  return (
    <PageWrapper>
      {/* Page heading */}
      <div className="mb-8">
        <h1 className="page-title">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Your job search at a glance</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className={`bg-gradient-to-br ${color} rounded-2xl p-5 shadow-lg`}>
            <div className="flex items-center justify-between mb-3">
              <Icon className="w-5 h-5 text-white/80" />
            </div>
            <p className="text-3xl font-display font-bold text-white">{value}</p>
            <p className="text-white/70 text-sm mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Recent Applications */}
        <div className="lg:col-span-3">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-display font-semibold text-slate-100">Recent Applications</h2>
              <Link to="/jobs" className="text-indigo-400 text-sm hover:text-indigo-300 flex items-center gap-1">
                View all <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {recentJobs.length === 0 ? (
              <div className="text-center py-8">
                <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">No applications yet</p>
                <p className="text-slate-500 text-sm mt-1">Start tracking your job search</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentJobs.map(job => (
                  <div
                    key={job.id}
                    onClick={() => navigate(`/jobs/${job.id}`)}
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-sm font-semibold text-indigo-400">
                        {job.company_name?.[0]?.toUpperCase()}
                      </div>
                      <div>
                        <p className="text-slate-100 text-sm font-medium">{job.company_name}</p>
                        <p className="text-slate-500 text-xs">{formatPlatform(job.platform)} · {formatRelativeTime(job.created_at)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {job.status === 'interview_scheduled' && job.interview_datetime && (
                        <InterviewCountdown interviewDatetime={job.interview_datetime} />
                      )}
                      <JobStatusBadge status={job.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right: Quick Actions + Today's Interviews */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Interviews */}
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Today's Interviews</h2>
            {todaysInterviews.length === 0 ? (
              <div className="text-center py-4">
                <Calendar className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-400 text-sm">No interviews today</p>
                <p className="text-slate-500 text-xs mt-2">
                  Set status to Interview Scheduled and use the Date &amp; Time field (not the job description).
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-amber-400 text-sm font-medium">
                  {todaysInterviews.length} interview{todaysInterviews.length > 1 ? 's' : ''} today
                </p>
                {todaysInterviews.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => navigate(`/jobs/${job.id}`)}
                    className="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 cursor-pointer transition-colors border border-slate-700/50"
                  >
                    <p className="text-slate-100 font-medium text-sm">{job.company_name}</p>
                    <p className="text-slate-400 text-xs mt-1">{formatDateTime(job.interview_datetime)}</p>
                    {job.interview_link && (
                      <p className="text-indigo-400 text-xs mt-1 truncate">Meeting link saved</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Quick Actions */}
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => navigate('/jobs/new')}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors text-left"
              >
                <div className="p-2 bg-indigo-500/20 rounded-lg">
                  <Plus className="w-4 h-4 text-indigo-400" />
                </div>
                <span className="text-sm text-slate-200">Add New Application</span>
              </button>
              <button
                onClick={() => navigate('/ats/check')}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors text-left"
              >
                <div className="p-2 bg-violet-500/20 rounded-lg">
                  <ScanSearch className="w-4 h-4 text-violet-400" />
                </div>
                <span className="text-sm text-slate-200">Quick ATS Check</span>
              </button>
              <button
                onClick={() => navigate('/recommendations')}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition-colors text-left"
              >
                <div className="p-2 bg-emerald-500/20 rounded-lg">
                  <Lightbulb className="w-4 h-4 text-emerald-400" />
                </div>
                <span className="text-sm text-slate-200">Get AI Recommendations</span>
              </button>
            </div>
          </Card>
        </div>
      </div>
    </PageWrapper>
  )
}
