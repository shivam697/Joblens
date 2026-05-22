import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { useATSPolling } from '../../hooks/useATSPolling'
import ATSScoreRing from '../../components/shared/ATSScoreRing'
import Badge from '../../components/ui/Badge'
import Card from '../../components/ui/Card'
import PageWrapper from '../../components/layout/PageWrapper'
import { formatDateTime } from '../../utils/formatters'

export default function ATSReport() {
  const { reportId } = useParams()
  const navigate = useNavigate()
  const { report, isPolling, isComplete, isFailed } = useATSPolling(reportId)

  // Loading/pending state
  if (!report || isPolling) {
    return (
      <PageWrapper>
        <div className="max-w-lg mx-auto text-center py-20">
          <Loader2 className="w-12 h-12 text-indigo-400 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-display font-bold text-slate-100 mb-2">Analyzing your resume...</h2>
          <p className="text-slate-500">This usually takes 15-30 seconds</p>
        </div>
      </PageWrapper>
    )
  }

  if (isFailed) {
    return (
      <PageWrapper>
        <div className="max-w-lg mx-auto text-center py-20">
          <p className="text-rose-400 text-lg font-medium mb-2">Analysis Failed</p>
          <p className="text-slate-400 text-sm">{report.error_message || 'Something went wrong. Please try again.'}</p>
          <button onClick={() => navigate(-1)} className="text-indigo-400 mt-4 hover:underline">Go Back</button>
        </div>
      </PageWrapper>
    )
  }

  const r = report.report || {}
  const score = report.overall_score || 0

  const getScoreLabel = () => {
    if (score >= 71) return { text: 'Strong Match — Well aligned with job requirements', color: 'text-emerald-400' }
    if (score >= 41) return { text: 'Moderate Match — Good foundation with room to improve', color: 'text-amber-400' }
    return { text: 'Low Match — Significant improvements needed', color: 'text-rose-400' }
  }
  const scoreLabel = getScoreLabel()

  return (
    <PageWrapper>
      <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-slate-200 flex items-center gap-1 mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">ATS Analysis Report</h1>
          <div className="flex items-center gap-2 mt-2">
            <Badge color={report.ats_source === 'quick_check' ? 'violet' : 'indigo'}>
              {report.ats_source === 'quick_check' ? 'Quick Check' : 'Job-Linked'}
            </Badge>
            <span className="text-slate-500 text-sm">{formatDateTime(report.generated_at)}</span>
          </div>
        </div>
      </div>

      {/* Score Hero */}
      <Card className="p-8 text-center mb-8">
        <ATSScoreRing score={score} size="lg" />
        <p className={`text-sm font-medium mt-4 ${scoreLabel.color}`}>{scoreLabel.text}</p>
      </Card>

      <div className="space-y-6">
        {/* Keyword Analysis */}
        {r.keyword_analysis && (
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Keyword Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm text-emerald-400 font-medium mb-2">Matched Keywords ({r.keyword_analysis.matched_keywords?.length || 0})</h3>
                <div className="flex flex-wrap gap-2">
                  {(r.keyword_analysis.matched_keywords || []).map((kw, i) => (
                    <span key={i} className="bg-emerald-500/20 text-emerald-400 rounded-full px-3 py-1 text-xs font-medium">{kw}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm text-rose-400 font-medium mb-2">Missing Keywords ({r.keyword_analysis.missing_keywords?.length || 0})</h3>
                <div className="flex flex-wrap gap-2">
                  {(r.keyword_analysis.missing_keywords || []).map((kw, i) => (
                    <span key={i} className="bg-rose-500/20 text-rose-400 rounded-full px-3 py-1 text-xs font-medium">{kw}</span>
                  ))}
                </div>
              </div>
            </div>
            {r.keyword_analysis.match_percentage != null && (
              <div className="mt-4">
                <div className="flex justify-between text-xs text-slate-400 mb-1"><span>Match</span><span>{r.keyword_analysis.match_percentage}%</span></div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full transition-all duration-1000" style={{ width: `${r.keyword_analysis.match_percentage}%` }} />
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Skills Gap */}
        {r.skills_gap && (
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Skills Gap</h2>
            {(r.skills_gap.hard_skills_missing?.length || 0) === 0 && (r.skills_gap.soft_skills_missing?.length || 0) === 0 ? (
              <p className="text-emerald-400">✓ No significant skills gap found!</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {r.skills_gap.hard_skills_missing?.length > 0 && (
                  <div>
                    <h3 className="text-sm text-rose-400 font-medium mb-2">Hard Skills Missing</h3>
                    <div className="flex flex-wrap gap-2">{r.skills_gap.hard_skills_missing.map((s, i) => <span key={i} className="bg-rose-500/15 text-rose-400 rounded-lg px-2.5 py-1 text-xs">{s}</span>)}</div>
                  </div>
                )}
                {r.skills_gap.soft_skills_missing?.length > 0 && (
                  <div>
                    <h3 className="text-sm text-amber-400 font-medium mb-2">Soft Skills Missing</h3>
                    <div className="flex flex-wrap gap-2">{r.skills_gap.soft_skills_missing.map((s, i) => <span key={i} className="bg-amber-500/15 text-amber-400 rounded-lg px-2.5 py-1 text-xs">{s}</span>)}</div>
                  </div>
                )}
              </div>
            )}
          </Card>
        )}

        {/* Grammar Issues */}
        {r.grammar_issues?.length > 0 && (
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Grammar & Language</h2>
            <div className="space-y-4">
              {r.grammar_issues.map((issue, i) => (
                <div key={i} className="bg-slate-800/50 rounded-xl p-4">
                  <p className="text-rose-400 text-sm line-through mb-1">{issue.original}</p>
                  <p className="text-emerald-400 text-sm font-medium mb-1">{issue.suggestion}</p>
                  <p className="text-slate-500 text-xs italic">{issue.reason}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Action Verb Suggestions */}
        {r.action_verb_suggestions?.length > 0 && (
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Action Verbs to Replace</h2>
            <div className="space-y-3">
              {r.action_verb_suggestions.map((v, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-rose-400 text-sm line-through flex-1">{v.weak}</span>
                  <span className="text-slate-500">→</span>
                  <span className="text-emerald-400 text-sm font-medium flex-1">{v.strong}</span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Section Feedback */}
        {r.section_feedback && (
          <Card className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">Section Feedback</h2>
            <div className="space-y-3">
              {Object.entries(r.section_feedback).map(([section, feedback]) => (
                <div key={section} className="border-l-2 border-indigo-500/30 pl-4">
                  <h3 className="text-sm font-medium text-indigo-400 capitalize mb-1">{section}</h3>
                  <p className="text-slate-300 text-sm">{feedback}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Format + Quantification + Tailoring Suggestions */}
        {[
          { key: 'format_suggestions', title: 'Format Suggestions' },
          { key: 'quantification_suggestions', title: 'Quantification Suggestions' },
          { key: 'tailoring_suggestions', title: 'Tailoring Suggestions' },
        ].map(({ key, title }) => r[key]?.length > 0 && (
          <Card key={key} className="p-6">
            <h2 className="font-display font-semibold text-slate-100 mb-4">{title}</h2>
            <ul className="space-y-2">
              {r[key].map((item, i) => <li key={i} className="text-slate-300 text-sm flex gap-2"><span className="text-indigo-400 shrink-0">{i + 1}.</span>{item}</li>)}
            </ul>
          </Card>
        ))}

        {/* Top 5 Recommendations */}
        {r.top_5_recommendations?.length > 0 && (
          <Card className="p-6 border-indigo-500/20">
            <h2 className="font-display font-semibold text-slate-100 mb-4">🎯 Top 5 Recommendations</h2>
            <div className="space-y-3">
              {r.top_5_recommendations.map((rec, i) => (
                <div key={i} className="flex gap-3 bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-4">
                  <span className="shrink-0 w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white">P{i + 1}</span>
                  <p className="text-slate-200 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </PageWrapper>
  )
}
