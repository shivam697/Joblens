import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Pencil, Trash2, ExternalLink, ScanSearch, Eye, ArrowLeft } from 'lucide-react'
import { jobApi } from '../../api/jobApi'
import { atsApi } from '../../api/atsApi'
import { useATSPolling } from '../../hooks/useATSPolling'
import { formatDateTime, formatSalary, formatPlatform, formatStatus } from '../../utils/formatters'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import JobStatusBadge from '../../components/shared/JobStatusBadge'
import InterviewCountdown from '../../components/shared/InterviewCountdown'
import ATSScoreRing from '../../components/shared/ATSScoreRing'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function JobDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [analyzing, setAnalyzing] = useState(false)
  const [reportId, setReportId] = useState(null)

  const { data: response, isLoading } = useQuery({ queryKey: ['job', id], queryFn: () => jobApi.getById(id) })
  const job = response?.data

  // Poll for ATS report when analyzing
  const { report: atsReport, isPolling, isComplete } = useATSPolling(reportId)

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const res = await atsApi.jobLinkedAnalyze(id)
      setReportId(res.data.report_id)
    } catch (err) {
      toast.error(err?.message || 'Failed to start analysis')
      setAnalyzing(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Remove this application?')) return
    try {
      await jobApi.delete(id)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Removed'); navigate('/jobs')
    } catch { toast.error('Failed to remove') }
  }

  if (isLoading) return <PageWrapper><PageSpinner /></PageWrapper>
  if (!job) return <PageWrapper><p className="text-slate-400">Application not found</p></PageWrapper>

  const existingReportId = job.ats_report_id

  return (
    <PageWrapper>
      <button onClick={() => navigate('/jobs')} className="text-slate-400 hover:text-slate-200 flex items-center gap-1 mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Applications
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-3 space-y-6">
          {/* Header */}
          <Card className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-2xl font-display font-bold text-slate-100">{job.company_name}</h1>
                <p className="text-slate-400 text-sm mt-1">via {formatPlatform(job.platform)}</p>
              </div>
              <JobStatusBadge status={job.status} />
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              {job.job_link && (
                <div><span className="text-slate-500">Job Link</span><br />
                  <a href={job.job_link} target="_blank" rel="noopener" className="text-indigo-400 hover:underline flex items-center gap-1">View Posting <ExternalLink className="w-3 h-3" /></a>
                </div>
              )}
              {job.hr_name && <div><span className="text-slate-500">HR Contact</span><br /><span className="text-slate-200">{job.hr_name}</span></div>}
              {job.hr_email && <div><span className="text-slate-500">HR Email</span><br /><span className="text-slate-200">{job.hr_email}</span></div>}
              {job.hr_contact && <div><span className="text-slate-500">Phone</span><br /><span className="text-slate-200">{job.hr_contact}</span></div>}
              {job.salary_offered && <div><span className="text-slate-500">Salary</span><br /><span className="text-emerald-400 font-medium">{formatSalary(job.salary_offered)}</span></div>}
              <div><span className="text-slate-500">Applied</span><br /><span className="text-slate-200">{formatDateTime(job.created_at)}</span></div>
            </div>
          </Card>

          {/* Job Description */}
          {job.job_description && (
            <Card className="p-6">
              <h2 className="font-display font-semibold text-slate-100 mb-3">Job Description</h2>
              <div className="text-slate-300 text-sm whitespace-pre-wrap max-h-64 overflow-y-auto pr-2 leading-relaxed">{job.job_description}</div>
            </Card>
          )}

          {/* ATS Analysis Section */}
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">ATS Analysis</h2>

            {/* Show existing report score */}
            {existingReportId && !reportId && (
              <div className="flex items-center gap-6">
                <ATSScoreRing score={75} size="sm" />
                <div>
                  <Link to={`/ats/report/${existingReportId}`}>
                    <Button variant="secondary" size="sm"><Eye className="w-4 h-4" /> View Full Report</Button>
                  </Link>
                  <Button variant="ghost" size="sm" className="ml-2" onClick={handleAnalyze} loading={analyzing}>Re-analyze</Button>
                </div>
              </div>
            )}

            {/* Analyzing state */}
            {(isPolling || (analyzing && reportId)) && (
              <div className="text-center py-6 animate-pulse-ring">
                <ScanSearch className="w-10 h-10 text-indigo-400 mx-auto mb-3 animate-spin-slow" />
                <p className="text-slate-200 font-medium">AI is analyzing your resume...</p>
                <p className="text-slate-500 text-sm mt-1">This usually takes 15-30 seconds</p>
              </div>
            )}

            {/* Completed inline */}
            {isComplete && atsReport && (
              <div className="flex items-center gap-6">
                <ATSScoreRing score={atsReport.overall_score || 0} size="sm" />
                <Link to={`/ats/report/${atsReport.report_id}`}>
                  <Button><Eye className="w-4 h-4" /> View Full Report</Button>
                </Link>
              </div>
            )}

            {/* No report yet — show analyze button */}
            {!existingReportId && !reportId && !analyzing && (
              <>
                {job.job_description && job.resume_id ? (
                  <div className="border-2 border-dashed border-indigo-500/30 rounded-xl p-6 text-center">
                    <ScanSearch className="w-8 h-8 text-indigo-400 mx-auto mb-3" />
                    <p className="text-slate-200 font-medium mb-1">Analyze this resume against the job description</p>
                    <p className="text-slate-500 text-sm mb-4">Get AI-powered feedback on keyword match, skills gap, and improvements</p>
                    <Button onClick={handleAnalyze} loading={analyzing}><ScanSearch className="w-4 h-4" /> Analyze with AI</Button>
                  </div>
                ) : (
                  <div className="border border-amber-500/20 bg-amber-500/5 rounded-xl p-4">
                    <p className="text-amber-400 text-sm font-medium mb-1">
                      {!job.job_description ? 'Add a job description to enable ATS analysis' : 'Link a resume to enable ATS analysis'}
                    </p>
                    <Button variant="secondary" size="sm" className="mt-2" onClick={() => navigate(`/jobs/${id}/edit`)}>
                      <Pencil className="w-3.5 h-3.5" /> Edit Application
                    </Button>
                  </div>
                )}
              </>
            )}
          </Card>

          {job.notes && (
            <Card className="p-6">
              <h2 className="font-display font-semibold text-slate-100 mb-3">Personal Notes</h2>
              <p className="text-slate-300 text-sm whitespace-pre-wrap">{job.notes}</p>
            </Card>
          )}
        </div>

        {/* Right Column */}
        <div className="lg:col-span-2 space-y-6">
          {job.status === 'interview_scheduled' && job.interview_datetime && (
            <Card className="p-6">
              <h2 className="font-display font-semibold text-slate-100 mb-4">Interview</h2>
              <InterviewCountdown interviewDatetime={job.interview_datetime} />
              <div className="mt-4 space-y-2 text-sm">
                <p><span className="text-slate-500">Time:</span> <span className="text-slate-200">{formatDateTime(job.interview_datetime)}</span></p>
                {job.interview_mode && <p><span className="text-slate-500">Mode:</span> <span className="text-slate-200">{formatStatus(job.interview_mode)}</span></p>}
                {job.interview_platform && <p><span className="text-slate-500">Platform:</span> <span className="text-slate-200">{job.interview_platform}</span></p>}
                {job.interview_link && <a href={job.interview_link} target="_blank" className="text-indigo-400 hover:underline flex items-center gap-1 mt-2">Join Meeting <ExternalLink className="w-3 h-3" /></a>}
              </div>
            </Card>
          )}

          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Actions</h2>
            <div className="space-y-2">
              <Button variant="secondary" className="w-full" onClick={() => navigate(`/jobs/${id}/edit`)}><Pencil className="w-4 h-4" /> Edit Application</Button>
              <Button variant="danger" className="w-full" onClick={handleDelete}><Trash2 className="w-4 h-4" /> Delete Application</Button>
            </div>
          </Card>
        </div>
      </div>
    </PageWrapper>
  )
}
