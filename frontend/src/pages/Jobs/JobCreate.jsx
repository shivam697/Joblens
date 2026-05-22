/**
 * JobCreate — Form to add a new job application
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { jobApi } from '../../api/jobApi'
import { resumeApi } from '../../api/resumeApi'
import { PLATFORMS, STATUSES, INTERVIEW_MODES } from '../../utils/constants'
import Button from '../../components/ui/Button'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function JobCreate() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    company_name: '',
    platform: 'linkedin',
    job_link: '',
    job_description: '',
    hr_name: '',
    hr_contact: '',
    hr_email: '',
    status: 'saved',
    interview_datetime: '',
    interview_mode: '',
    interview_platform: '',
    interview_link: '',
    interview_notes: '',
    salary_offered: '',
    notes: '',
    resume_id: '',
  })

  const { data: resumesResponse } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => resumeApi.list(),
  })
  const resumes = resumesResponse?.data || []

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Clean data — remove empty strings, convert types
      const payload = { ...formData }
      Object.keys(payload).forEach(key => {
        if (payload[key] === '') payload[key] = null
      })
      if (payload.salary_offered) payload.salary_offered = parseFloat(payload.salary_offered)
      if (payload.interview_datetime) payload.interview_datetime = new Date(payload.interview_datetime).toISOString()

      await jobApi.create(payload)
      toast.success('Job application added!')
      navigate('/jobs')
    } catch (error) {
      toast.error(error?.message || 'Failed to create application')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = (e) => {
    const status = e.target.value
    setFormData((prev) => ({
      ...prev,
      status,
      ...(status === 'interview_scheduled' && !prev.interview_datetime
        ? { interview_datetime: new Date().toISOString().slice(0, 16) }
        : {}),
    }))
  }

  return (
    <PageWrapper>
      <div className="max-w-3xl mx-auto">
        <h1 className="page-title mb-8">Add New Application</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Section 1: Job Information */}
          <div className="card p-6">
            <h2 className="text-lg font-display font-semibold text-slate-100 mb-5">Job Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="form-label">Company Name *</label>
                <input name="company_name" value={formData.company_name} onChange={handleChange} className="input-field" required placeholder="e.g. Google" />
              </div>
              <div>
                <label className="form-label">Platform *</label>
                <select name="platform" value={formData.platform} onChange={handleChange} className="select-field">
                  {PLATFORMS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                </select>
              </div>
              <div>
                <label className="form-label">Job Link</label>
                <input name="job_link" value={formData.job_link} onChange={handleChange} className="input-field" placeholder="https://..." />
              </div>
              <div>
                <label className="form-label">Status</label>
                <select name="status" value={formData.status} onChange={handleStatusChange} className="select-field">
                  {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Contact */}
          <div className="card p-6">
            <h2 className="text-lg font-display font-semibold text-slate-100 mb-5">HR Contact</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div><label className="form-label">HR Name</label><input name="hr_name" value={formData.hr_name} onChange={handleChange} className="input-field" /></div>
              <div><label className="form-label">Phone</label><input name="hr_contact" value={formData.hr_contact} onChange={handleChange} className="input-field" /></div>
              <div><label className="form-label">Email</label><input name="hr_email" value={formData.hr_email} onChange={handleChange} className="input-field" type="email" /></div>
            </div>
          </div>

          {/* Section 3: Job Description */}
          <div className="card p-6">
            <h2 className="text-lg font-display font-semibold text-slate-100 mb-5">Job Description</h2>
            <label className="form-label">Paste the job description (ATS analysis only)</label>
            <textarea name="job_description" value={formData.job_description} onChange={handleChange} className="input-field min-h-[150px]" placeholder="Paste the full job description here..." />
          </div>

          {/* Section 4: Interview Details */}
          <div className="card p-6">
              <h2 className="text-lg font-display font-semibold text-slate-100 mb-2">Interview Details</h2>
              <p className="text-slate-500 text-sm mb-5">For Today&apos;s Interviews and email reminders — not parsed from job description.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div><label className="form-label">Interview Date &amp; Time</label><input name="interview_datetime" type="datetime-local" value={formData.interview_datetime} onChange={handleChange} className="input-field" /></div>
                <div>
                  <label className="form-label">Mode</label>
                  <select name="interview_mode" value={formData.interview_mode} onChange={handleChange} className="select-field">
                    <option value="">Select mode</option>
                    {INTERVIEW_MODES.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div><label className="form-label">Platform</label><input name="interview_platform" value={formData.interview_platform} onChange={handleChange} className="input-field" placeholder="Zoom, Google Meet..." /></div>
                <div><label className="form-label">Meeting Link</label><input name="interview_link" value={formData.interview_link} onChange={handleChange} className="input-field" placeholder="https://..." /></div>
              </div>
              <div className="mt-5"><label className="form-label">Interview Notes</label><textarea name="interview_notes" value={formData.interview_notes} onChange={handleChange} className="input-field min-h-[80px]" placeholder="Preparation notes..." /></div>
            </div>

          {/* Section 5: Additional */}
          <div className="card p-6">
            <h2 className="text-lg font-display font-semibold text-slate-100 mb-5">Additional</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="form-label">Link Resume</label>
                <select name="resume_id" value={formData.resume_id} onChange={handleChange} className="select-field">
                  <option value="">None</option>
                  {resumes.map(r => <option key={r.id} value={r.id}>{r.file_name}{r.is_active ? ' ★' : ''}</option>)}
                </select>
              </div>
              <div><label className="form-label">Salary Offered (₹)</label><input name="salary_offered" type="number" value={formData.salary_offered} onChange={handleChange} className="input-field" placeholder="e.g. 800000" /></div>
            </div>
            <div className="mt-5"><label className="form-label">Personal Notes</label><textarea name="notes" value={formData.notes} onChange={handleChange} className="input-field min-h-[80px]" placeholder="Any notes about this application..." /></div>
          </div>

          <div className="flex gap-3">
            <Button type="submit" loading={loading} className="flex-1" size="lg">Add Application</Button>
            <Button variant="secondary" type="button" onClick={() => navigate('/jobs')} size="lg">Cancel</Button>
          </div>
        </form>
      </div>
    </PageWrapper>
  )
}
