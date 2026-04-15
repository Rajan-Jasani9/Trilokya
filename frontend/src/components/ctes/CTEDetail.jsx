import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import TRLProgression from '../trl/TRLProgression'
import IRLProgression from '../irl/IRLProgression'
import MRLProgression from '../mrl/MRLProgression'
import { FiArrowLeft, FiEdit, FiCheckCircle } from 'react-icons/fi'
import { useToast } from '../common/ToastProvider'

const getTRLBadge = (trl) => {
  if (!trl || trl === 0) return 'bg-gray-100 text-gray-600'
  if (trl <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
  if (trl <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
  return 'bg-[#DDEEE1] text-[#2E7D32]'
}

const CTEDetail = ({ cteId, onBack, onEdit }) => {
  const { showToast } = useToast()
  const [cte, setCte] = useState(null)
  const [currentTRL, setCurrentTRL] = useState(0)
  const [currentIRL, setCurrentIRL] = useState(0)
  const [currentMRL, setCurrentMRL] = useState(0)
  const [currentSRL, setCurrentSRL] = useState(0)
  const [assessments, setAssessments] = useState([])
  const [activeTab, setActiveTab] = useState('trl')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadCTE() }, [cteId])

  const loadCTE = async () => {
    try {
      const [cteR, summaryR, assR] = await Promise.all([
        api.get(`/ctes/${cteId}`),
        api.get(`/ctes/${cteId}/readiness-summary`).catch(() => ({ data: { current_trl: 0, current_irl: 0, current_mrl: 0, current_srl: 0 } })),
        api.get(`/trl/ctes/${cteId}/trl-assessments`).catch(() => ({ data: [] }))
      ])
      setCte(cteR.data)
      setCurrentTRL(summaryR.data.current_trl || 0)
      setCurrentIRL(summaryR.data.current_irl || 0)
      setCurrentMRL(summaryR.data.current_mrl || 0)
      setCurrentSRL(summaryR.data.current_srl || 0)
      setAssessments(assR.data || [])
    } catch (error) {
      console.error('Error loading CTE:', error)
      showToast('Failed to load CTE details.', 'error')
    }
    finally { setLoading(false) }
  }

  if (loading) return <LoadingSpinner />
  if (!cte) return <div className="text-gray-500">CTE not found</div>

  return (
    <div className="space-y-5">
      {/* Back */}
      {onBack && (
        <button onClick={onBack} className="btn-ghost text-sm">
          <FiArrowLeft className="h-4 w-4" /><span>Back to CTEs</span>
        </button>
      )}

      {/* CTE Header */}
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-5 border-b" style={{ borderColor: '#D9E2E2' }}>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{cte.name}</h1>
            <p className="text-xs font-mono text-gray-400 mt-1">{cte.code}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1.5 rounded text-xs font-bold ${getTRLBadge(currentTRL)}`}>
              TRL {currentTRL || 'N/A'}
            </div>
            <div className="px-3 py-1.5 rounded text-xs font-bold bg-blue-50 text-blue-700">IRL {currentIRL || 0}</div>
            <div className="px-3 py-1.5 rounded text-xs font-bold bg-purple-50 text-purple-700">MRL {currentMRL || 0}</div>
            <div className="px-3 py-1.5 rounded text-xs font-bold bg-teal-50 text-teal-700">SRL {currentSRL || 0}</div>
            {onEdit && (
              <button onClick={() => onEdit(cte)} className="btn-secondary text-sm">
                <FiEdit className="h-4 w-4" /><span>Edit</span>
              </button>
            )}
          </div>
        </div>

        {/* Info grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-5">
          {cte.description && (
            <div className="sm:col-span-2">
              <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Description</p>
              <p className="text-sm text-gray-700 mt-1 leading-relaxed">{cte.description}</p>
            </div>
          )}
          {cte.category && (
            <div>
              <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Category</p>
              <p className="text-sm font-medium text-gray-900 mt-1">{cte.category}</p>
            </div>
          )}
          {cte.target_trl && (
            <div>
              <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Target TRL</p>
              <p className="text-sm font-medium text-gray-900 mt-1">TRL {cte.target_trl}</p>
            </div>
          )}
        </div>
      </div>

      <div className="card p-3">
        <div className="flex gap-2">
          {['trl', 'irl', 'mrl', 'srl'].map((tab) => (
            <button key={tab} className={`btn-secondary text-xs ${activeTab === tab ? '!bg-primary-100 !border-primary-500' : ''}`} onClick={() => setActiveTab(tab)}>{tab.toUpperCase()}</button>
          ))}
        </div>
      </div>

      {activeTab === 'trl' && <TRLProgression cteId={cteId} currentTRL={currentTRL} onTRLUpdated={loadCTE} />}
      {activeTab === 'irl' && <IRLProgression cteId={cteId} currentIRL={currentIRL} onIRLUpdated={loadCTE} />}
      {activeTab === 'mrl' && <MRLProgression cteId={cteId} currentMRL={currentMRL} onMRLUpdated={loadCTE} />}
      {activeTab === 'srl' && (
        <div className="card p-5">
          <h2 className="section-title">Derived SRL</h2>
          <p className="text-sm text-gray-600 mt-2">SRL is derived as min(TRL, IRL, MRL).</p>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div className="card p-3">TRL: {currentTRL}</div>
            <div className="card p-3">IRL: {currentIRL}</div>
            <div className="card p-3">MRL: {currentMRL}</div>
            <div className="card p-3 font-semibold">SRL: {currentSRL}</div>
          </div>
        </div>
      )}

      <div className="card p-5">
        <h2 className="section-title">Milestone Viewer</h2>
        <div className="mt-4 space-y-2 text-sm">
          {[['TRL', currentTRL], ['IRL', currentIRL], ['MRL', currentMRL], ['SRL', currentSRL]].map(([name, value]) => (
            <div key={name} className="flex items-center gap-3">
              <span className="w-10 font-medium">{name}</span>
              <div className="h-2 bg-gray-100 rounded-full flex-1 overflow-hidden">
                <div className="h-full bg-primary-600 rounded-full" style={{ width: `${Math.min(100, (value / 9) * 100)}%` }} />
              </div>
              <span className="w-6 text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Assessment History */}
      <div className="card p-5">
        <div className="section-header">
          <h2 className="section-title">TRL Assessment History</h2>
          <span className="badge badge-info">{assessments.length} {assessments.length === 1 ? 'Assessment' : 'Assessments'}</span>
        </div>
        {assessments && assessments.length > 0 ? (
          <div className="space-y-2">
            {assessments.map((a) => (
              <div key={a.id} className="card p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-sm font-semibold text-gray-900">TRL Level {a.trl_level}</h3>
                      <span className={`badge text-[10px] ${
                        a.status === 'approved' ? 'badge-success' :
                        a.status === 'submitted' ? 'badge-warning' :
                        a.status === 'rejected' ? 'badge-danger' : 'badge-gray'
                      }`}>
                        {a.status.charAt(0).toUpperCase() + a.status.slice(1)}
                      </span>
                    </div>
                    {a.notes && <p className="text-xs text-gray-500 mt-1">{a.notes}</p>}
                    {a.assessment_date && (
                      <p className="text-[11px] text-gray-400 mt-1.5">
                        Assessed: {new Date(a.assessment_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  {a.status === 'approved' && (
                    <FiCheckCircle className="h-5 w-5 text-trl-high flex-shrink-0 ml-3" />
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-10">
            <FiCheckCircle className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium text-sm">No TRL assessments yet</p>
            <p className="text-gray-400 text-xs mt-1">Start a TRL progression to begin assessments</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CTEDetail
