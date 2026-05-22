import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Lightbulb, Loader2, Upload, ExternalLink, RefreshCw } from 'lucide-react'
import { recommendationApi } from '../../api/recommendationApi'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import { PageSpinner } from '../../components/ui/Spinner'
import PageWrapper from '../../components/layout/PageWrapper'
import toast from 'react-hot-toast'

export default function Recommendations() {
  const [generating, setGenerating] = useState(false)
  const queryClient = useQueryClient()

  const { data: response, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => recommendationApi.get(),
  })

  const data = response?.data

  const handleGenerate = async (force = false) => {
    setGenerating(true)
    try {
      await recommendationApi.generate(force)
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
      toast.success('Recommendations generated!')
    } catch (err) {
      toast.error(err?.message || 'Failed to generate recommendations')
    } finally {
      setGenerating(false)
    }
  }

  if (isLoading) return <PageWrapper><PageSpinner /></PageWrapper>

  // No recommendations yet
  if (!data) {
    return (
      <PageWrapper>
        <h1 className="page-title mb-2">AI Job Recommendations</h1>
        <p className="text-slate-400 text-sm mb-8">Get AI-powered role suggestions based on your resume</p>
        <Card className="p-8 text-center max-w-lg mx-auto">
          <Lightbulb className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
          <h3 className="text-slate-100 font-display font-semibold text-lg mb-2">Generate Recommendations</h3>
          <p className="text-slate-400 text-sm mb-6">Upload and activate a resume first, then let Gemini AI find the best roles for you</p>
          <Button onClick={handleGenerate} loading={generating} size="lg">
            <Lightbulb className="w-4 h-4" /> Generate Now
          </Button>
          <p className="text-slate-500 text-xs mt-3">Takes about 20-30 seconds</p>
        </Card>
      </PageWrapper>
    )
  }

  const recs = data.recommendations || []

  const getMatchColor = (pct) => {
    if (pct >= 80) return 'emerald'
    if (pct >= 60) return 'amber'
    return 'rose'
  }

  return (
    <PageWrapper>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">AI Job Recommendations</h1>
          <p className="text-slate-400 text-sm mt-1">Based on your resume analysis</p>
        </div>
        <Button variant="secondary" onClick={() => handleGenerate(true)} loading={generating}>
          <RefreshCw className="w-4 h-4" /> Regenerate
        </Button>
      </div>

      {/* Candidate level + top skills */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <Badge color="indigo">Level: {data.candidate_level || 'Fresher'}</Badge>
        {(data.strongest_skills || []).map((skill, i) => (
          <Badge key={i} color="violet">{skill}</Badge>
        ))}
      </div>

      {/* Generating overlay */}
      {generating && (
        <div className="text-center py-12">
          <Loader2 className="w-10 h-10 text-indigo-400 animate-spin mx-auto mb-3" />
          <p className="text-slate-300">Gemini AI is analyzing your resume...</p>
        </div>
      )}

      {/* Recommendation cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {recs.map((rec, i) => (
          <Card key={i} className="p-6 hover:border-slate-600 transition-colors">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-display font-semibold text-slate-100">{rec.job_title}</h3>
              <Badge color={getMatchColor(rec.match_percentage)}>{rec.match_percentage}% Match</Badge>
            </div>
            <p className="text-slate-400 text-sm mb-4">{rec.why_it_fits}</p>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <p className="text-xs text-slate-500 mb-1.5">Skills You Have</p>
                <div className="flex flex-wrap gap-1">
                  {(rec.skills_you_have || []).map((s, j) => <span key={j} className="bg-emerald-500/15 text-emerald-400 rounded px-2 py-0.5 text-xs">{s}</span>)}
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1.5">Skills to Learn</p>
                <div className="flex flex-wrap gap-1">
                  {(rec.skills_to_learn || []).map((s, j) => <span key={j} className="bg-indigo-500/15 text-indigo-400 rounded px-2 py-0.5 text-xs">{s}</span>)}
                </div>
              </div>
            </div>

            {rec.salary_range_india && (
              <p className="text-emerald-400 text-sm font-medium mb-3">💰 {rec.salary_range_india}</p>
            )}

            <div className="flex gap-2">
              {(rec.search_keywords || []).slice(0, 2).map((kw, j) => (
                <a key={j} href={`https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(kw)}`} target="_blank" rel="noopener" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                  Search: {kw} <ExternalLink className="w-3 h-3" />
                </a>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </PageWrapper>
  )
}
