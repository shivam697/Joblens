import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { jobApi } from '../../api/jobApi'
import { resumeApi } from '../../api/resumeApi'
import { PLATFORMS, STATUSES, INTERVIEW_MODES } from '../../utils/constants'
import Button from '../../components/ui/Button'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function JobEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState(null)

  const { data: jobRes, isLoading } = useQuery({ queryKey: ['job', id], queryFn: () => jobApi.getById(id) })
  const { data: resumesRes } = useQuery({ queryKey: ['resumes'], queryFn: () => resumeApi.list() })
  const resumes = resumesRes?.data || []

  useEffect(() => {
    if (jobRes?.data) {
      const j = jobRes.data
      setFormData({
        company_name: j.company_name || '', platform: j.platform || 'linkedin',
        job_link: j.job_link || '', job_description: j.job_description || '',
        hr_name: j.hr_name || '', hr_contact: j.hr_contact || '', hr_email: j.hr_email || '',
        status: j.status || 'saved',
        interview_datetime: j.interview_datetime ? new Date(j.interview_datetime).toISOString().slice(0, 16) : '',
        interview_mode: j.interview_mode || '', interview_platform: j.interview_platform || '',
        interview_link: j.interview_link || '', interview_notes: j.interview_notes || '',
        salary_offered: j.salary_offered || '', notes: j.notes || '', resume_id: j.resume_id || '',
      })
    }
  }, [jobRes])

  const handleChange = (e) => setFormData(p => ({ ...p, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true)
    try {
      const payload = { ...formData }
      Object.keys(payload).forEach(k => { if (payload[k] === '') payload[k] = null })
      if (payload.salary_offered) payload.salary_offered = parseFloat(payload.salary_offered)
      if (payload.interview_datetime) payload.interview_datetime = new Date(payload.interview_datetime).toISOString()
      await jobApi.update(id, payload)
      queryClient.invalidateQueries({ queryKey: ['job', id] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Updated!'); navigate(`/jobs/${id}`)
    } catch (err) { toast.error(err?.message || 'Failed to update') } finally { setLoading(false) }
  }

  if (isLoading || !formData) return <PageWrapper><PageSpinner /></PageWrapper>

  return (
    <PageWrapper>
      <div className="max-w-3xl mx-auto">
        <h1 className="page-title mb-8">Edit Application</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="card p-6 grid grid-cols-1 md:grid-cols-2 gap-5">
            <div><label className="form-label">Company *</label><input name="company_name" value={formData.company_name} onChange={handleChange} className="input-field" required /></div>
            <div><label className="form-label">Platform</label><select name="platform" value={formData.platform} onChange={handleChange} className="select-field">{PLATFORMS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}</select></div>
            <div><label className="form-label">Status</label><select name="status" value={formData.status} onChange={handleChange} className="select-field">{STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}</select></div>
            <div><label className="form-label">Job Link</label><input name="job_link" value={formData.job_link} onChange={handleChange} className="input-field" /></div>
            <div><label className="form-label">HR Name</label><input name="hr_name" value={formData.hr_name} onChange={handleChange} className="input-field" /></div>
            <div><label className="form-label">HR Phone</label><input name="hr_contact" value={formData.hr_contact} onChange={handleChange} className="input-field" /></div>
            <div><label className="form-label">HR Email</label><input name="hr_email" value={formData.hr_email} onChange={handleChange} className="input-field" /></div>
            <div><label className="form-label">Resume</label><select name="resume_id" value={formData.resume_id} onChange={handleChange} className="select-field"><option value="">None</option>{resumes.map(r => <option key={r.id} value={r.id}>{r.file_name}</option>)}</select></div>
            <div><label className="form-label">Salary (₹)</label><input name="salary_offered" type="number" value={formData.salary_offered} onChange={handleChange} className="input-field" /></div>
          </div>
          <div className="card p-6"><label className="form-label">Job Description</label><textarea name="job_description" value={formData.job_description} onChange={handleChange} className="input-field min-h-[120px]" /></div>
          {formData.status === 'interview_scheduled' && (
            <div className="card p-6 grid grid-cols-1 md:grid-cols-2 gap-5">
              <div><label className="form-label">Interview Date</label><input name="interview_datetime" type="datetime-local" value={formData.interview_datetime} onChange={handleChange} className="input-field" /></div>
              <div><label className="form-label">Mode</label><select name="interview_mode" value={formData.interview_mode} onChange={handleChange} className="select-field"><option value="">Select</option>{INTERVIEW_MODES.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}</select></div>
              <div><label className="form-label">Platform</label><input name="interview_platform" value={formData.interview_platform} onChange={handleChange} className="input-field" /></div>
              <div><label className="form-label">Link</label><input name="interview_link" value={formData.interview_link} onChange={handleChange} className="input-field" /></div>
              <div className="md:col-span-2"><label className="form-label">Notes</label><textarea name="interview_notes" value={formData.interview_notes} onChange={handleChange} className="input-field min-h-[80px]" /></div>
            </div>
          )}
          <div className="card p-6"><label className="form-label">Personal Notes</label><textarea name="notes" value={formData.notes} onChange={handleChange} className="input-field min-h-[80px]" /></div>
          <div className="flex gap-3">
            <Button type="submit" loading={loading} className="flex-1" size="lg">Save Changes</Button>
            <Button variant="secondary" type="button" onClick={() => navigate(`/jobs/${id}`)} size="lg">Cancel</Button>
          </div>
        </form>
      </div>
    </PageWrapper>
  )
}
