import React, { useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import Modal from '../common/Modal'
import { FiCheck, FiArrowRight, FiAlertTriangle } from 'react-icons/fi'
import { useToast } from '../common/ToastProvider'

const getLevelBadge = (level) => {
  if (!level || level === 0) return 'bg-gray-100 text-gray-600'
  if (level <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
  if (level <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
  return 'bg-[#DDEEE1] text-[#2E7D32]'
}

const ReadinessProgression = ({ cteId, domain, currentLevel, onUpdated }) => {
  const DOMAIN = domain.toUpperCase()
  const { showToast } = useToast()
  const [showModal, setShowModal] = useState(false)
  const [targetLevel, setTargetLevel] = useState(null)
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [couplingResult, setCouplingResult] = useState(null)
  const [validationErrors, setValidationErrors] = useState([])

  const nextLevel = currentLevel ? currentLevel + 1 : 1
  const maxLevel = 9

  const start = async (level) => {
    setTargetLevel(level)
    setShowModal(true)
    setResponses({})
    setValidationErrors([])
    setCouplingResult(null)
    try {
      setLoading(true)
      const r = await api.get(`/${domain}/ctes/${cteId}/${domain}-assessments/${level}/questions`)
      setQuestions(r.data || [])
      if (domain === 'trl') {
        const coupling = await api.get(`/trl/ctes/${cteId}/coupling-status/${level}`)
        setCouplingResult(coupling.data)
      }
    } catch (error) {
      showToast(`Failed to load ${DOMAIN} questions`, 'error')
      setShowModal(false)
    } finally {
      setLoading(false)
    }
  }

  const submit = async () => {
    const required = questions.filter((q) => q.is_required)
    const unanswered = required.filter((q) => !responses[q.id]?.answer)
    const missingEvidence = questions.filter((q) => q.evidence_required && !responses[q.id]?.evidence_text)
    const reasons = []

    if (unanswered.length) {
      reasons.push(`Answer all required questions (${unanswered.length} missing).`)
    }
    if (missingEvidence.length) {
      reasons.push(`Provide evidence for required fields (${missingEvidence.length} missing).`)
    }
    if (reasons.length) {
      const preview = [
        ...unanswered.map((q) => `Q${questions.findIndex((item) => item.id === q.id) + 1}: required answer missing`),
        ...missingEvidence.map((q) => `Q${questions.findIndex((item) => item.id === q.id) + 1}: required evidence missing`),
      ]
      setValidationErrors(preview)
      showToast(`Cannot submit ${DOMAIN} advancement yet.`, 'error')
      return
    }

    try {
      setSubmitting(true)
      setValidationErrors([])
      await Promise.all(questions.map(async (q) => {
        if (!responses[q.id]) return
        const payload = {
          [`${domain}_question_id`]: q.id,
          answer: responses[q.id].answer,
          evidence_text: responses[q.id].evidence_text || '',
          confidence_score: null,
        }
        await api.post(`/${domain}/ctes/${cteId}/${domain}-assessments/${targetLevel}/responses`, payload)
      }))
      const result = await api.post(`/${domain}/ctes/${cteId}/advance-${domain}`, { target_level: targetLevel })
      if (domain === 'trl') setCouplingResult(result.data.coupling || null)
      showToast(result.data.message || `Advanced to ${DOMAIN} ${targetLevel}`, 'success')
      setShowModal(false)
      setResponses({})
      setQuestions([])
      setValidationErrors([])
      if (onUpdated) onUpdated()
    } catch (error) {
      const message = error.response?.data?.detail || `Failed to advance ${DOMAIN}`
      showToast(message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-5">
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Current {DOMAIN} Level</p>
            <div className="flex items-center gap-3 mt-2">
              <div className={`px-5 py-2.5 rounded text-2xl font-bold ${getLevelBadge(currentLevel)}`}>{currentLevel || '0'}</div>
            </div>
          </div>
          {nextLevel <= maxLevel && <button onClick={() => start(nextLevel)} className="btn-primary"><FiArrowRight className="h-4 w-4" /><span>Advance to {DOMAIN} {nextLevel}</span></button>}
        </div>
      </div>
      {domain === 'trl' && couplingResult && (
        <div className={`card p-4 ${couplingResult.satisfied ? 'border-green-200' : 'border-amber-200'}`}>
          <div className="flex items-center gap-2 text-sm">
            <FiAlertTriangle className="h-4 w-4" />
            <span>Coupling ({couplingResult.strict_mode ? 'Strict' : 'Soft'}): Required IRL {couplingResult.required_min_irl} / MRL {couplingResult.required_min_mrl}, Current IRL {couplingResult.current_irl} / MRL {couplingResult.current_mrl}</span>
          </div>
        </div>
      )}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={`Advance to ${DOMAIN} ${targetLevel}`} size="lg">
        {loading ? <LoadingSpinner /> : (
          <div className="space-y-4">
            {validationErrors.length > 0 && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2">
                <p className="text-xs font-semibold text-red-700 mb-1">Why it is not submitting:</p>
                <ul className="text-xs text-red-700 space-y-0.5">
                  {validationErrors.slice(0, 8).map((err, idx) => (
                    <li key={`${err}-${idx}`}>• {err}</li>
                  ))}
                </ul>
              </div>
            )}
            {domain === 'trl' && couplingResult && (
              <div className={`card p-3 ${couplingResult.satisfied ? 'border-green-200' : 'border-amber-200'}`}>
                <p className="text-xs text-gray-700">
                  Mode: <strong>{couplingResult.strict_mode ? 'Strict' : 'Soft'}</strong> | Required IRL {couplingResult.required_min_irl} (Current {couplingResult.current_irl}) | Required MRL {couplingResult.required_min_mrl} (Current {couplingResult.current_mrl})
                </p>
                {!couplingResult.satisfied && !couplingResult.strict_mode && <p className="text-[11px] text-amber-700 mt-1">Soft mode warning: TRL can proceed, but IRL/MRL are below recommended minimum.</p>}
                {!couplingResult.satisfied && couplingResult.strict_mode && <p className="text-[11px] text-red-700 mt-1">Strict mode active: this TRL advancement will be blocked until IRL/MRL minimums are met.</p>}
              </div>
            )}
            {questions.map((q, idx) => (
              <div key={q.id} className="card p-4">
                <p className="text-sm font-medium mb-2">
                  Q{idx + 1}. {q.question_text}
                  {q.is_required && <span className="text-red-600 ml-1">*</span>}
                </p>
                <div className="flex flex-wrap gap-2 mb-2">
                  {['Yes', 'No', 'Not Applicable'].map((opt) => (
                    <button key={opt} className={`btn-secondary text-xs ${responses[q.id]?.answer === opt ? '!bg-primary-100 !border-primary-500' : ''}`} onClick={() => setResponses((p) => ({ ...p, [q.id]: { ...p[q.id], answer: opt } }))}>{opt}</button>
                  ))}
                </div>
                <label className="text-[11px] font-medium text-gray-600 mb-1 block">
                  Evidence / notes
                  {q.evidence_required && <span className="text-red-600 ml-1">*</span>}
                </label>
                <textarea className="input resize-none text-sm" rows={2} placeholder={q.evidence_required ? 'Required evidence' : 'Optional evidence / notes'} value={responses[q.id]?.evidence_text || ''} onChange={(e) => setResponses((p) => ({ ...p, [q.id]: { ...p[q.id], evidence_text: e.target.value } }))} />
              </div>
            ))}
            <p className="text-[11px] text-gray-500">Fields marked with <span className="text-red-600">*</span> are required.</p>
            <div className="flex justify-end gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
              <button onClick={() => setShowModal(false)} className="btn-secondary" disabled={submitting}>Cancel</button>
              <button onClick={submit} className="btn-primary" disabled={submitting || (domain === 'trl' && couplingResult?.strict_mode && !couplingResult?.satisfied)}>{submitting ? <LoadingSpinner size="sm" /> : <><FiCheck className="h-4 w-4" /><span>Advance</span></>}</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ReadinessProgression
