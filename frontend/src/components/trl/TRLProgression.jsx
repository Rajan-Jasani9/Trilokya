import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import Modal from '../common/Modal'
import { FiUpload, FiX, FiCheck, FiArrowRight, FiFile } from 'react-icons/fi'

const getTRLBadge = (trl) => {
  if (!trl || trl === 0) return 'bg-gray-100 text-gray-600'
  if (trl <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
  if (trl <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
  return 'bg-[#DDEEE1] text-[#2E7D32]'
}

const TRLProgression = ({ cteId, currentTRL, onTRLUpdated }) => {
  const [showProgressionModal, setShowProgressionModal] = useState(false)
  const [targetLevel, setTargetLevel] = useState(null)
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [evidenceFiles, setEvidenceFiles] = useState({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleStartProgression = async (level) => {
    setTargetLevel(level)
    setShowProgressionModal(true)
    await loadQuestions(level)
  }

  const loadQuestions = async (level) => {
    try {
      setLoading(true)
      const r = await api.get(`/trl/ctes/${cteId}/trl-assessments/${level}/questions`)
      setQuestions(r.data || [])
      try {
        const assR = await api.get(`/trl/ctes/${cteId}/trl-assessments`)
        const existing = assR.data.find(a => a.trl_level === level)
        if (existing) setResponses({})
      } catch { setResponses({}) }
    } catch (error) {
      console.error('Error loading questions:', error)
      alert('Failed to load questions')
    } finally { setLoading(false) }
  }

  const handleAnswerChange = (qId, answer) => {
    setResponses(prev => ({ ...prev, [qId]: { ...prev[qId], answer } }))
  }

  const handleEvidenceTextChange = (qId, text) => {
    setResponses(prev => ({ ...prev, [qId]: { ...prev[qId], evidence_text: text } }))
  }

  const handleFileSelect = (qId, file) => {
    if (file) setEvidenceFiles(prev => ({ ...prev, [qId]: file }))
  }

  const handleRemoveFile = (qId) => {
    setEvidenceFiles(prev => { const n = { ...prev }; delete n[qId]; return n })
  }

  const uploadEvidence = async (responseId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return (await api.post(`/evidence/upload?trl_response_id=${responseId}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })).data
  }

  const handleSubmit = async () => {
    const requiredQs = questions.filter(q => q.is_required)
    const unanswered = requiredQs.filter(q => !responses[q.id]?.answer)
    if (unanswered.length > 0) {
      alert(`Please answer all required questions. Missing: ${unanswered.map(q => q.question_text).join(', ')}`)
      return
    }

    const evidenceQs = questions.filter(q => q.evidence_required)
    const missingEv = evidenceQs.filter(q => !responses[q.id]?.evidence_text && !evidenceFiles[q.id])
    if (missingEv.length > 0) {
      alert(`Please provide evidence for: ${missingEv.map(q => q.question_text).join(', ')}`)
      return
    }

    try {
      setSubmitting(true)
      const promises = questions.map(async (question) => {
        const rd = responses[question.id]
        if (!rd) return null
        const r = await api.post(`/trl/ctes/${cteId}/trl-assessments/${targetLevel}/responses`, {
          trl_question_id: question.id, answer: rd.answer, evidence_text: rd.evidence_text || '', confidence_score: null
        })
        if (evidenceFiles[question.id]) await uploadEvidence(r.data.id, evidenceFiles[question.id])
        return r.data
      })
      await Promise.all(promises.filter(Boolean))
      await api.post(`/trl/ctes/${cteId}/advance-trl`, { target_level: targetLevel }, { headers: { 'Content-Type': 'application/json' } })
      alert(`Successfully advanced to TRL ${targetLevel}`)
      closeModal()
      if (onTRLUpdated) onTRLUpdated()
    } catch (error) {
      console.error('Error submitting TRL progression:', error)
      alert(`Error: ${error.response?.data?.detail || 'Failed to advance TRL level'}`)
    } finally { setSubmitting(false) }
  }

  const closeModal = () => {
    setShowProgressionModal(false); setTargetLevel(null); setResponses({}); setEvidenceFiles({})
  }

  const nextLevel = currentTRL ? currentTRL + 1 : 1
  const maxLevel = 9

  return (
    <div className="space-y-5">
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Current TRL Level</p>
            <div className="flex items-center gap-3 mt-2">
              <div className={`px-5 py-2.5 rounded text-2xl font-bold ${getTRLBadge(currentTRL)}`}>
                {currentTRL || '0'}
              </div>
              {currentTRL === 0 && <p className="text-sm text-gray-400">Not Started</p>}
            </div>
          </div>
          {nextLevel <= maxLevel && (
            <button onClick={() => handleStartProgression(nextLevel)} className="btn-primary">
              <FiArrowRight className="h-4 w-4" />
              <span>Advance to TRL {nextLevel}</span>
            </button>
          )}
        </div>
      </div>

      {/* Progression Modal */}
      <Modal isOpen={showProgressionModal} onClose={closeModal} title={`Advance to TRL ${targetLevel}`} size="lg">
        {loading ? <LoadingSpinner /> : (
          <div className="space-y-5">
            <div className="alert-info">
              <p className="text-sm font-medium">
                Answer all required questions and provide evidence where needed to advance to TRL {targetLevel}.
              </p>
            </div>

            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
              {questions.map((question, index) => (
                <div key={question.id} className="card p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-1.5 mb-2">
                        <span className="text-[10px] font-bold text-primary-700 bg-primary-100 px-1.5 py-0.5 rounded">
                          Q{index + 1}
                        </span>
                        {question.is_required && <span className="badge badge-danger text-[10px]">Required</span>}
                        {question.evidence_required && <span className="badge badge-warning text-[10px]">Evidence Required</span>}
                      </div>
                      <p className="text-sm text-gray-900 leading-relaxed">{question.question_text}</p>
                    </div>
                  </div>

                  {/* Answer */}
                  <div className="mb-3">
                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Answer</p>
                    <div className="flex flex-wrap gap-2">
                      {['Yes', 'No', 'Not Applicable'].map((opt) => {
                        const selected = responses[question.id]?.answer === opt
                        return (
                          <label key={opt}
                            className={`flex items-center gap-2 cursor-pointer px-3 py-2 border rounded text-sm font-medium transition-colors duration-150
                              ${selected ? 'border-primary-600 bg-primary-50 text-primary-700' : 'border-shell-border text-gray-600 hover:border-primary-300 hover:bg-primary-50/40'}
                            `}
                          >
                            <input type="radio" name={`question-${question.id}`} value={opt}
                              checked={selected} onChange={() => handleAnswerChange(question.id, opt)}
                              className="h-3.5 w-3.5 text-primary-600 focus:ring-primary-500" />
                            <span>{opt}</span>
                          </label>
                        )
                      })}
                    </div>
                  </div>

                  {/* Evidence Text */}
                  <div className="mb-3">
                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
                      Evidence / Notes {question.evidence_required && <span className="text-trl-low">*</span>}
                    </p>
                    <textarea value={responses[question.id]?.evidence_text || ''} onChange={(e) => handleEvidenceTextChange(question.id, e.target.value)}
                      rows={2} className="input resize-none text-sm" placeholder="Provide evidence, notes, or justification…" />
                  </div>

                  {/* File Upload */}
                  <div>
                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Upload Evidence (Photo/PDF)</p>
                    {evidenceFiles[question.id] ? (
                      <div className="flex items-center justify-between p-3 bg-primary-50/40 rounded border" style={{ borderColor: '#D9E2E2' }}>
                        <div className="flex items-center gap-2 min-w-0">
                          <FiFile className="h-4 w-4 text-primary-600 flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{evidenceFiles[question.id].name}</p>
                            <p className="text-[11px] text-gray-400">{(evidenceFiles[question.id].size / 1024).toFixed(1)} KB</p>
                          </div>
                        </div>
                        <button onClick={() => handleRemoveFile(question.id)}
                          className="p-1.5 text-trl-low hover:bg-red-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                          aria-label="Remove file">
                          <FiX className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <label className="flex flex-col items-center justify-center w-full px-4 py-5 border-2 border-dashed rounded cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition-colors duration-150 group"
                        style={{ borderColor: '#D9E2E2' }}>
                        <FiUpload className="h-6 w-6 text-gray-300 group-hover:text-primary-500 mb-1.5 transition-colors" />
                        <span className="text-xs text-gray-500 group-hover:text-primary-600 font-medium">Click to upload</span>
                        <span className="text-[10px] text-gray-400 mt-0.5">PDF, JPG, PNG (Max 10MB)</span>
                        <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleFileSelect(question.id, e.target.files[0])} className="hidden" />
                      </label>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-5 border-t" style={{ borderColor: '#D9E2E2' }}>
              <button onClick={closeModal} disabled={submitting} className="btn-secondary">Cancel</button>
              <button onClick={handleSubmit} disabled={submitting} className="btn-primary">
                {submitting ? <LoadingSpinner size="sm" /> : (
                  <><FiCheck className="h-4 w-4" /><span>Advance to TRL {targetLevel}</span></>
                )}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default TRLProgression
