/**
 * ResumeDropzone — Drag-and-drop resume upload component
 * 
 * Reusable — used in both ResumeUpload page and ATS Quick Check page.
 * Accepts PDF and .txt files, validates size, shows preview after selection.
 */

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X } from 'lucide-react'
import { MAX_FILE_SIZE_MB } from '../../utils/constants'

export default function ResumeDropzone({ onFileSelected, selectedFile, onRemove }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileSelected(acceptedFiles[0])
    }
  }, [onFileSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxSize: MAX_FILE_SIZE_MB * 1024 * 1024,
    multiple: false,
  })

  // Show file preview if selected
  if (selectedFile) {
    return (
      <div className="border border-slate-600 rounded-xl p-4 bg-slate-950 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <File className="w-8 h-8 text-indigo-400" />
          <div>
            <p className="text-slate-100 font-medium text-sm">{selectedFile.name}</p>
            <p className="text-slate-500 text-xs">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
        <button
          onClick={onRemove}
          className="text-slate-400 hover:text-rose-400 transition-colors p-1"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    )
  }

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
        isDragActive
          ? 'border-indigo-500 bg-indigo-500/10'
          : 'border-slate-600 hover:border-indigo-500/50 hover:bg-slate-950'
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="w-10 h-10 text-slate-500 mx-auto mb-3" />
      <p className="text-slate-300 font-medium mb-1">
        {isDragActive ? 'Drop your resume here' : 'Drag and drop your resume here'}
      </p>
      <p className="text-slate-500 text-sm">
        or <span className="text-indigo-400 underline">click to browse</span>
      </p>
      <p className="text-slate-600 text-xs mt-2">PDF or TXT — Max {MAX_FILE_SIZE_MB}MB</p>
    </div>
  )
}
