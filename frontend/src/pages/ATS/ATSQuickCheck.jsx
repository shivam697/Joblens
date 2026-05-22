import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ScanSearch, Loader2 } from 'lucide-react'
import { atsApi } from '../../api/atsApi'
import { resumeApi } from '../../api/resumeApi'
import { useATSPolling } from '../../hooks/useATSPolling'
import ResumeDropzone from '../../components/shared/ResumeDropzone'
import Button from '../../components/ui/Button'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function ATSQuickCheck() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedResumeId, setSelectedResumeId] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [reportId, setReportId] = useState(null)

  const { data: resumesRes } = useQuery({ queryKey: ['resumes'], queryFn: () => resumeApi.list() })
  const resumes = resumesRes?.data || []

  const { report, isPolling, isComplete, isFailed } = useATSPolling(reportId)

  const canSubmit = (activeTab === 'upload' ? !!selectedFile : !!selectedResumeId) && jobDescription.length >= 50

  const handleAnalyze = async () => {
    setSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('job_description', jobDescription)
      if (activeTab === 'upload' && selectedFile) {
        formData.append('file', selectedFile)
      } else if (activeTab === 'saved' && selectedResumeId) {
        formData.append('resume_id', selectedResumeId)
      }
      const res = await atsApi.quickAnalyze(formData)
      if (!res?.success || !res?.data?.report_id) {
        throw new Error(res?.message || 'Failed to start analysis')
      }
      setReportId(res.data.report_id)
    } catch (err) {
      toast.error(err?.message || 'Failed to start analysis')
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (isComplete && report?.report_id) {
      navigate(`/ats/report/${report.report_id}`, { replace: true })
    }
  }, [isComplete, report?.report_id, navigate])

  useEffect(() => {
    if (isFailed) {
      toast.error(report?.error_message || 'Analysis failed. Please try again.')
      setReportId(null)
      setSubmitting(false)
    }
  }, [isFailed, report?.error_message])

  if (reportId && (isPolling || submitting)) {
    return (
      <PageWrapper>
        <div className="max-w-lg mx-auto text-center py-20">
          <AnalyzingView />
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <div className="max-w-5xl mx-auto">
        <h1 className="page-title mb-1">ATS Quick Check</h1>
        <p className="text-slate-400 text-sm mb-8">Upload your resume and paste a job description to get instant ATS analysis</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="card p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Your Resume</h2>
            <div className="flex gap-2 mb-4">
              <button type="button" onClick={() => setActiveTab('upload')} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'upload' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>Upload New</button>
              <button type="button" onClick={() => setActiveTab('saved')} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${activeTab === 'saved' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>Use Saved</button>
            </div>
            {activeTab === 'upload' ? (
              <ResumeDropzone selectedFile={selectedFile} onFileSelected={setSelectedFile} onRemove={() => setSelectedFile(null)} />
            ) : resumes.length > 0 ? (
              <select value={selectedResumeId} onChange={(e) => setSelectedResumeId(e.target.value)} className="select-field">
                <option value="">Select a resume</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>{r.file_name}{r.is_active ? ' ★ Active' : ''}</option>
                ))}
              </select>
            ) : (
              <p className="text-slate-500 text-sm py-4">No resumes uploaded yet. Switch to Upload New tab.</p>
            )}
          </div>

          <div className="card p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Job Description</h2>
            <textarea value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} className="input-field min-h-[200px] resize-none" placeholder="Paste the complete job description here..." />
            <JdCharCount jobDescription={jobDescription} />
          </div>
        </div>

        <Button onClick={handleAnalyze} loading={submitting} disabled={!canSubmit} className="w-full" size="lg">
          <ScanSearch className="w-5 h-5" /> Analyze Now
        </Button>
      </div>
    </PageWrapper>
  )
}

function JdCharCount({ jobDescription }) {
  return (
    <div className="flex justify-between mt-2">
      <p className="text-slate-500 text-xs">Paste from Naukri, LinkedIn, or any job board</p>
      <p className={`text-xs ${jobDescription.length >= 50 ? 'text-emerald-400' : 'text-slate-500'}`}>{jobDescription.length}/50 min</p>
    </div>
  )
}

function AnalyzingView() {
  return (
    <>
      <div className="animate-pulse-ring inline-block mb-6">
        <ScanSearch className="w-16 h-16 text-indigo-400 animate-spin-slow" />
      </div>
      <h2 className="text-xl font-display font-bold text-slate-100 mb-2">AI is analyzing your resume...</h2>
      <div className="space-y-3 mt-6 text-left max-w-xs mx-auto">
        <div className="flex items-center gap-2 text-emerald-400 text-sm"><span>✓</span> Resume processed</div>
        <div className="flex items-center gap-2 text-indigo-400 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" /> Comparing with job requirements...
        </div>
        <div className="flex items-center gap-2 text-slate-500 text-sm"><span>○</span> Generating detailed report...</div>
      </div>
      <p className="text-slate-500 text-sm mt-6">This usually takes 15-30 seconds</p>
    </>
  )
}
