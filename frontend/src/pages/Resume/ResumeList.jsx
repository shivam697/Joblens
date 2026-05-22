/**
 * ResumeList — List all uploaded resumes with activate and delete
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Upload, FileText } from 'lucide-react'
import { resumeApi } from '../../api/resumeApi'
import ResumeCard from '../../components/shared/ResumeCard'
import Button from '../../components/ui/Button'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function ResumeList() {
  const [loadingAction, setLoadingAction] = useState(null)
  const queryClient = useQueryClient()

  const { data: response, isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => resumeApi.list(),
  })

  const resumes = response?.data || []

  const handleActivate = async (resumeId) => {
    setLoadingAction(`activate-${resumeId}`)
    try {
      await resumeApi.activate(resumeId)
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume activated')
    } catch (error) {
      toast.error(error?.message || 'Failed to activate resume')
    } finally {
      setLoadingAction(null)
    }
  }

  const handleDelete = async (resumeId) => {
    if (!confirm('Delete this resume? This cannot be undone.')) return
    setLoadingAction(`delete-${resumeId}`)
    try {
      await resumeApi.delete(resumeId)
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume deleted')
    } catch (error) {
      toast.error(error?.message || 'Failed to delete resume')
    } finally {
      setLoadingAction(null)
    }
  }

  if (isLoading) return <PageWrapper><PageSpinner /></PageWrapper>

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="page-title">My Resumes</h1>
          <p className="text-slate-400 text-sm mt-1">{resumes.length} resume{resumes.length !== 1 ? 's' : ''} uploaded</p>
        </div>
        <Link to="/resume/upload">
          <Button><Upload className="w-4 h-4" /> Upload New</Button>
        </Link>
      </div>

      {resumes.length === 0 ? (
        <div className="text-center py-16">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-slate-300 font-medium mb-2">No resumes uploaded yet</h3>
          <p className="text-slate-500 text-sm mb-6">Upload your resume to start using ATS analysis</p>
          <Link to="/resume/upload">
            <Button><Upload className="w-4 h-4" /> Upload Your Resume</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {resumes.map(resume => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              onActivate={handleActivate}
              onDelete={handleDelete}
              isLoading={loadingAction}
            />
          ))}
        </div>
      )}
    </PageWrapper>
  )
}
