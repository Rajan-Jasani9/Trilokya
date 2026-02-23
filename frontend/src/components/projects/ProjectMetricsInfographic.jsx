import React, { useMemo } from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts'
import { FiTarget, FiAlertTriangle, FiCheckCircle, FiClock } from 'react-icons/fi'

const MAX_LEVEL = 9

const ProjectMetricsInfographic = ({ project, ctes }) => {
  const currentTRL = typeof project?.current_trl === 'number' ? project.current_trl : 0
  const targetTRL = typeof project?.target_trl === 'number' ? project.target_trl : null

  const effectiveTarget = targetTRL && targetTRL > 0 ? targetTRL : MAX_LEVEL
  const safeCurrent = Math.max(0, Math.min(currentTRL, MAX_LEVEL))
  const gap = effectiveTarget - safeCurrent
  const journeyProgress = effectiveTarget
    ? Math.max(0, Math.min(100, Math.round((safeCurrent / effectiveTarget) * 100)))
    : 0

  const today = new Date()
  const endDate = project?.end_date ? new Date(project.end_date) : null
  const msPerDay = 1000 * 60 * 60 * 24
  const daysRemaining =
    endDate && !Number.isNaN(endDate.getTime())
      ? Math.ceil((endDate.getTime() - today.getTime()) / msPerDay)
      : null

  const riskLevel = useMemo(() => {
    if (!effectiveTarget || effectiveTarget <= 0) return 'Unknown'
    if (daysRemaining === null) {
      if (gap <= 1) return 'Low'
      if (gap <= 3) return 'Medium'
      return 'High'
    }

    if (daysRemaining <= 0) {
      return gap > 0 ? 'Critical' : 'Complete'
    }

    if (gap <= 0) return 'Complete'
    if (gap >= 3 && daysRemaining <= 90) return 'High'
    if (gap >= 2 && daysRemaining <= 180) return 'Medium'
    return 'Low'
  }, [effectiveTarget, gap, daysRemaining])

  const radarData = useMemo(() => {
    const clamp = (value) => {
      if (typeof value !== 'number' || value < 0) return 0
      return Math.min(value, MAX_LEVEL)
    }

    return [
      { axis: 'TRL', value: clamp(project?.current_trl) || 0 },
      { axis: 'IRL', value: clamp(project?.current_irl) || 0 },
      { axis: 'MRL', value: clamp(project?.current_mrl) || 0 },
      { axis: 'SRL', value: clamp(project?.current_srl) || 0 },
    ]
  }, [project])

  const cteHeatmapRows = useMemo(() => {
    if (!Array.isArray(ctes)) return []
    const clamp = (value) => {
      if (typeof value !== 'number' || value < 0) return 0
      return Math.min(value, MAX_LEVEL)
    }

    return ctes.map((cte) => ({
      id: cte.id,
      name: cte.name,
      code: cte.code,
      trl: clamp(cte.current_trl ?? cte.trl ?? 0),
      irl: clamp(cte.current_irl ?? 0),
      mrl: clamp(cte.current_mrl ?? 0),
      srl: clamp(cte.current_srl ?? 0),
    }))
  }, [ctes])

  const valueToHeatClass = (value) => {
    if (!value || value === 0) return 'bg-gray-100 text-gray-400'
    if (value <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
    if (value <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
    return 'bg-[#DDEEE1] text-[#2E7D32]'
  }

  const valueLabel = (value) => {
    if (!value || value === 0) return '—'
    return value
  }

  const getTRLColor = (level) => {
    if (!level || level === 0) return '#9E9E9E'
    if (level <= 3) return '#C44536'
    if (level <= 6) return '#D4A017'
    return '#2E7D32'
  }

  const riskBadgeClass = (() => {
    switch (riskLevel) {
      case 'Critical':
        return 'badge-danger'
      case 'High':
        return 'badge-danger'
      case 'Medium':
        return 'badge-warning'
      case 'Low':
        return 'badge-success'
      case 'Complete':
        return 'badge-success'
      default:
        return 'badge-gray'
    }
  })()

  return (
    <div className="space-y-5">
      {/* Section 1: Hero TRL Ladder */}
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-5">
          <div>
            <h2 className="section-title">Project TRL Journey</h2>
            <p className="text-xs text-gray-500 mt-1">
              Current TRL vs target, with gap analysis and risk assessment
            </p>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <div className={`px-3 py-1.5 rounded text-xs font-bold ${valueToHeatClass(safeCurrent)}`}>
              Current TRL {safeCurrent || 'N/A'}
            </div>
            {targetTRL && targetTRL > 0 && (
              <div className="flex items-center gap-1.5 text-xs text-gray-600">
                <FiTarget className="h-3.5 w-3.5 text-primary-600" />
                <span className="font-medium">Target: TRL {targetTRL}</span>
              </div>
            )}
          </div>
        </div>

        {/* TRL Ladder 1-9 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-[11px] text-gray-500">
            <span className="font-semibold uppercase tracking-wide">TRL Progression</span>
            <span>
              Progress: <span className="font-bold text-gray-900">{journeyProgress}%</span>
            </span>
          </div>
          
          <div className="relative">
            <div className="flex items-center gap-1">
              {[...Array(MAX_LEVEL)].map((_, idx) => {
                const level = idx + 1
                const isCurrent = level === safeCurrent
                const isTarget = targetTRL && level === targetTRL
                const isBehind = safeCurrent > 0 && level <= safeCurrent
                const isAhead = safeCurrent > 0 && level > safeCurrent && (!targetTRL || level <= targetTRL)

                let baseClass = 'flex-1 h-10 rounded border text-xs font-bold flex items-center justify-center transition-all duration-150'
                
                if (!safeCurrent) {
                  baseClass += ' bg-gray-50 border-gray-200 text-gray-400'
                } else if (isBehind) {
                  baseClass += ' text-white border-transparent'
                  baseClass += ` bg-primary-600`
                } else if (isAhead) {
                  baseClass += ' bg-primary-50 border-primary-200 text-primary-700'
                } else {
                  baseClass += ' bg-gray-50 border-gray-200 text-gray-400'
                }

                return (
                  <div key={level} className="relative flex-1">
                    <div className={baseClass}>{level}</div>
                    {isCurrent && (
                      <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex flex-col items-center">
                        <span className="text-[10px] font-bold text-primary-700">Current</span>
                        <div className="h-2 w-2 rounded-full bg-primary-600 mt-0.5" />
                      </div>
                    )}
                    {isTarget && (
                      <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex flex-col items-center">
                        <div className="h-2 w-2 rounded-full bg-trl-high mb-0.5" />
                        <span className="text-[10px] font-bold text-trl-high">Target</span>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded bg-primary-50 flex items-center justify-center flex-shrink-0">
                <FiTarget className="h-4 w-4 text-primary-600" />
              </div>
              <div>
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">TRL Gap</p>
                <p className="text-sm font-bold text-gray-900">
                  {gap > 0 ? `${gap} level${gap > 1 ? 's' : ''}` : 'None'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded bg-primary-50 flex items-center justify-center flex-shrink-0">
                <FiClock className="h-4 w-4 text-primary-600" />
              </div>
              <div>
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Days Remaining</p>
                <p className="text-sm font-bold text-gray-900">
                  {daysRemaining === null
                    ? 'N/A'
                    : daysRemaining >= 0
                    ? `${daysRemaining} day${daysRemaining === 1 ? '' : 's'}`
                    : `${Math.abs(daysRemaining)} over`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className={`h-8 w-8 rounded flex items-center justify-center flex-shrink-0 ${
                riskLevel === 'Complete' || riskLevel === 'Low' ? 'bg-[#DDEEE1]' :
                riskLevel === 'Medium' ? 'bg-[#F4E8D2]' : 'bg-[#F4E0DD]'
              }`}>
                {riskLevel === 'Complete' || riskLevel === 'Low' ? (
                  <FiCheckCircle className="h-4 w-4 text-trl-high" />
                ) : riskLevel === 'Medium' ? (
                  <FiAlertTriangle className="h-4 w-4 text-trl-mid" />
                ) : (
                  <FiAlertTriangle className="h-4 w-4 text-trl-low" />
                )}
              </div>
              <div>
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Risk Level</p>
                <span className={`badge ${riskBadgeClass} text-xs`}>
                  {riskLevel}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Radar Chart & Risk Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Radar Chart */}
        <div className="card p-5">
          <div className="mb-4">
            <h3 className="section-title text-base">Readiness Profile</h3>
            <p className="text-xs text-gray-500 mt-1">
              Multi-dimensional maturity across TRL, IRL, MRL, and SRL
            </p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#E5ECEC" />
                <PolarAngleAxis
                  dataKey="axis"
                  tick={{ fontSize: 11, fill: '#4b5563', fontWeight: 500 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, MAX_LEVEL]}
                  tick={{ fontSize: 10, fill: '#9ca3af' }}
                />
                <Radar
                  name="Readiness"
                  dataKey="value"
                  stroke="#146c6c"
                  fill="#146c6c"
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 pt-3 border-t" style={{ borderColor: '#D9E2E2' }}>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {radarData.map((item) => (
                <div key={item.axis} className="flex items-center justify-between">
                  <span className="text-gray-600 font-medium">{item.axis}:</span>
                  <span className="font-bold text-gray-900">{item.value || 0}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Risk & Velocity Panel */}
        <div className="card p-5">
          <div className="mb-4">
            <h3 className="section-title text-base">Risk & Velocity</h3>
            <p className="text-xs text-gray-500 mt-1">
              Project health indicators and timeline analysis
            </p>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">
                  TRL Gap
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {gap > 0 ? gap : 0}
                  <span className="text-xs font-medium text-gray-500 ml-1">levels</span>
                </p>
              </div>
              <div className="p-3 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">
                  Time Pressure
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {daysRemaining === null
                    ? '—'
                    : daysRemaining >= 0
                    ? daysRemaining
                    : Math.abs(daysRemaining)}
                  {daysRemaining !== null && (
                    <span className="text-xs font-medium text-gray-500 ml-1">
                      {daysRemaining >= 0 ? 'days' : 'over'}
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="p-3 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-2">
                Assessment Summary
              </p>
              <p className="text-xs text-gray-600 leading-relaxed">
                With a gap of{' '}
                <span className="font-semibold text-gray-900">
                  {gap > 0 ? gap : 0} TRL level{gap === 1 ? '' : 's'}
                </span>{' '}
                {daysRemaining !== null && (
                  <>
                    and{' '}
                    <span className="font-semibold text-gray-900">
                      {daysRemaining >= 0
                        ? `${daysRemaining} day${daysRemaining === 1 ? '' : 's'} remaining`
                        : `${Math.abs(daysRemaining)} day${Math.abs(daysRemaining) === 1 ? '' : 's'} over target`}
                    </span>
                    {', '}
                  </>
                )}
                this project is classified as{' '}
                <span className={`font-semibold ${riskBadgeClass.includes('danger') ? 'text-trl-low' : riskBadgeClass.includes('warning') ? 'text-trl-mid' : 'text-trl-high'}`}>
                  {riskLevel} risk
                </span>.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: CTE Contribution Heatmap */}
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <div>
            <h3 className="section-title text-base">CTE Contribution Matrix</h3>
            <p className="text-xs text-gray-500 mt-1">
              Readiness levels across all Critical Technology Elements
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-[10px] text-gray-500">
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-6 rounded" style={{ backgroundColor: '#F4E0DD' }} />
              <span className="font-medium">1–3 (High Risk)</span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-6 rounded" style={{ backgroundColor: '#F4E8D2' }} />
              <span className="font-medium">4–6 (Moderate)</span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-6 rounded" style={{ backgroundColor: '#DDEEE1' }} />
              <span className="font-medium">7–9 (Mature)</span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-6 rounded bg-gray-100" />
              <span className="font-medium">Not Assessed</span>
            </span>
          </div>
        </div>

        {cteHeatmapRows.length === 0 ? (
          <div className="flex items-center justify-center rounded border border-dashed py-10" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
            <p className="text-sm text-gray-500">
              No CTEs yet. Add CTEs to see contribution across readiness dimensions.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border-separate border-spacing-y-1">
              <thead>
                <tr className="text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wide">
                  <th className="px-3 py-2.5">CTE</th>
                  <th className="px-3 py-2.5">Code</th>
                  <th className="px-2 py-2.5 text-center">TRL</th>
                  <th className="px-2 py-2.5 text-center">IRL</th>
                  <th className="px-2 py-2.5 text-center">MRL</th>
                  <th className="px-2 py-2.5 text-center">SRL</th>
                </tr>
              </thead>
              <tbody>
                {cteHeatmapRows.map((row) => (
                  <tr key={row.id} className="bg-white rounded border" style={{ borderColor: '#D9E2E2' }}>
                    <td className="px-3 py-2.5 font-medium text-gray-800 rounded-l text-sm whitespace-nowrap max-w-xs truncate">
                      {row.name}
                    </td>
                    <td className="px-3 py-2.5 text-gray-500 font-mono text-xs whitespace-nowrap">
                      {row.code}
                    </td>
                    {['trl', 'irl', 'mrl', 'srl'].map((key) => (
                      <td key={key} className="px-2 py-2.5 text-center">
                        <div
                          className={`inline-flex items-center justify-center h-7 w-12 rounded text-[11px] font-bold ${valueToHeatClass(
                            row[key]
                          )}`}
                        >
                          {valueLabel(row[key])}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProjectMetricsInfographic
