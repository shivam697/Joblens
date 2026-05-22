/**
 * ResumeCard — Resume display card with active indicator and actions
 */

import { FileText, Star, Trash2 } from 'lucide-react'
import { formatDate } from '../../utils/formatters'
import Button from '../ui/Button'

export default function ResumeCard({ resume, onActivate, onDelete, isLoading }) {
  return (
    <div className={`bg-slate-900 border rounded-2xl p-5 transition-all duration-200 ${
      resume.is_active 
        ? 'border-indigo-500 ring-1 ring-indigo-500/20' 
        : 'border-slate-700 hover:border-slate-600'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl ${resume.is_active ? 'bg-indigo-500/20' : 'bg-slate-800'}`}>
            <FileText className={`w-5 h-5 ${resume.is_active ? 'text-indigo-400' : 'text-slate-400'}`} />
          </div>
          <div>
            <h3 className="text-slate-100 font-medium text-sm">{resume.file_name}</h3>
            <p className="text-slate-500 text-xs mt-0.5">
              {resume.file_type.toUpperCase()} · Uploaded {formatDate(resume.uploaded_at)}
            </p>
          </div>
        </div>

        {resume.is_active && (
          <span className="flex items-center gap-1 text-indigo-400 text-xs font-medium bg-indigo-500/10 px-2 py-1 rounded-full">
            <Star className="w-3 h-3 fill-indigo-400" />
            Active
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 mt-4">
        {!resume.is_active && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onActivate(resume.id)}
            loading={isLoading === `activate-${resume.id}`}
          >
            <Star className="w-3.5 h-3.5" />
            Set Active
          </Button>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(resume.id)}
          loading={isLoading === `delete-${resume.id}`}
          className="text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Delete
        </Button>
      </div>
    </div>
  )
}
