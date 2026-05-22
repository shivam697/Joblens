/**
 * ResumeUpload — Drag and drop resume upload page
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeApi } from '../../api/resumeApi'
import ResumeDropzone from '../../components/shared/ResumeDropzone'
import Button from '../../components/ui/Button'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function ResumeUpload() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const navigate = useNavigate()

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    try {
      await resumeApi.upload(selectedFile)
      toast.success('Resume uploaded successfully!')
      navigate('/resume')
    } catch (error) {
      toast.error(error?.message || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto">
        <h1 className="page-title mb-2">Upload Resume</h1>
        <p className="text-slate-400 text-sm mb-8">
          Upload your resume to use for ATS analysis and job recommendations
        </p>

        <ResumeDropzone
          onFileSelected={setSelectedFile}
          selectedFile={selectedFile}
          onRemove={() => setSelectedFile(null)}
        />

        {selectedFile && (
          <div className="mt-6 flex gap-3">
            <Button onClick={handleUpload} loading={uploading} className="flex-1">
              Upload Resume
            </Button>
            <Button variant="secondary" onClick={() => setSelectedFile(null)}>
              Cancel
            </Button>
          </div>
        )}
      </div>
    </PageWrapper>
  )
}
