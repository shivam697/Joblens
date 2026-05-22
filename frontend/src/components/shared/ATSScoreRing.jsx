/**
 * ATSScoreRing — Animated SVG circular progress ring
 * 
 * Uses SVG circle with strokeDasharray and strokeDashoffset for progress.
 * Arc color changes based on score: rose (<40), amber (40-70), emerald (>70)
 */

import { useEffect, useState } from 'react'

export default function ATSScoreRing({ score = 0, size = 'md', showLabel = true }) {
  const [animatedScore, setAnimatedScore] = useState(0)

  // Animate the score from 0 to target value
  useEffect(() => {
    if (score <= 0) return
    let current = 0
    const step = score / 40 // Complete animation in ~40 frames
    const timer = setInterval(() => {
      current += step
      if (current >= score) {
        setAnimatedScore(score)
        clearInterval(timer)
      } else {
        setAnimatedScore(Math.round(current))
      }
    }, 25)
    return () => clearInterval(timer)
  }, [score])

  // Size configurations
  const sizes = {
    sm: { width: 80, strokeWidth: 6, fontSize: 'text-xl', labelSize: 'text-[10px]' },
    md: { width: 140, strokeWidth: 8, fontSize: 'text-4xl', labelSize: 'text-xs' },
    lg: { width: 200, strokeWidth: 10, fontSize: 'text-5xl', labelSize: 'text-sm' },
  }

  const config = sizes[size]
  const radius = (config.width - config.strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = (animatedScore / 100) * circumference
  const offset = circumference - progress

  // Color based on score thresholds
  const getColor = () => {
    if (animatedScore >= 71) return { stroke: '#10B981', text: 'text-emerald-400' } // Strong match
    if (animatedScore >= 41) return { stroke: '#F59E0B', text: 'text-amber-400' }   // Moderate
    return { stroke: '#F43F5E', text: 'text-rose-400' }                              // Low match
  }

  const color = getColor()

  return (
    <div className="inline-flex flex-col items-center">
      <svg width={config.width} height={config.width} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={config.width / 2}
          cy={config.width / 2}
          r={radius}
          fill="none"
          stroke="#334155"
          strokeWidth={config.strokeWidth}
        />
        {/* Progress arc — animated via strokeDashoffset */}
        <circle
          cx={config.width / 2}
          cy={config.width / 2}
          r={radius}
          fill="none"
          stroke={color.stroke}
          strokeWidth={config.strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      {/* Score number centered over the ring */}
      <div className="relative" style={{ marginTop: -config.width / 2 - (size === 'sm' ? 12 : size === 'md' ? 20 : 28), height: 0 }}>
        <div className="flex flex-col items-center" style={{ transform: `translateY(-${size === 'sm' ? 8 : size === 'md' ? 14 : 20}px)` }}>
          <span className={`font-display font-bold ${config.fontSize} ${color.text}`}>
            {animatedScore}
          </span>
          {showLabel && (
            <span className={`${config.labelSize} text-slate-400 mt-0.5`}>ATS Score</span>
          )}
        </div>
      </div>
      {/* Spacer to account for overlapping text */}
      <div style={{ height: size === 'sm' ? 12 : size === 'md' ? 24 : 36 }} />
    </div>
  )
}
