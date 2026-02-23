import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import Modal from '../common/Modal'
import { FiPlus, FiEdit, FiTrash2, FiChevronDown, FiChevronUp } from 'react-icons/fi'

const TRLDefinitionManager = () => {
  const [definitions, setDefinitions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showDefinitionModal, setShowDefinitionModal] = useState(false)
  const [showQuestionModal, setShowQuestionModal] = useState(false)
  const [editingDefinition, setEditingDefinition] = useState(null)
  const [editingQuestion, setEditingQuestion] = useState(null)
  const [selectedDefinition, setSelectedDefinition] = useState(null)
  const [expandedDefinitions, setExpandedDefinitions] = useState(new Set())

  useEffect(() => { loadDefinitions() }, [])

  const loadDefinitions = async () => {
    try { setLoading(true); const r = await api.get('/admin/trl-definitions'); setDefinitions(r.data || []) }
    catch (error) { console.error('Error loading TRL definitions:', error); alert('Failed to load TRL definitions') }
    finally { setLoading(false) }
  }

  const toggleDefinition = (id) => {
    setExpandedDefinitions(prev => {
      const s = new Set(prev)
      s.has(id) ? s.delete(id) : s.add(id)
      return s
    })
  }

  const handleDeleteDefinition = async (id) => {
    if (!window.confirm('Delete this TRL definition and all its questions?')) return
    try { await api.delete(`/admin/trl-definitions/${id}`); loadDefinitions() }
    catch (error) { console.error('Error:', error); alert('Failed to delete') }
  }

  const handleDeleteQuestion = async (id) => {
    if (!window.confirm('Delete this question?')) return
    try { await api.delete(`/admin/trl-questions/${id}`); loadDefinitions() }
    catch (error) { console.error('Error:', error); alert('Failed to delete') }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="section-title">TRL Definitions</h2>
        <button onClick={() => { setEditingDefinition(null); setShowDefinitionModal(true) }} className="btn-primary text-sm">
          <FiPlus className="h-4 w-4" /><span>Add TRL Level</span>
        </button>
      </div>

      <div className="space-y-2">
        {definitions.map((def) => (
          <div key={def.id} className="border rounded" style={{ borderColor: '#D9E2E2' }}>
            <div
              className="flex items-center justify-between p-3.5 cursor-pointer hover:bg-primary-50/30 transition-colors duration-100"
              onClick={() => toggleDefinition(def.id)}
            >
              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                {expandedDefinitions.has(def.id)
                  ? <FiChevronUp className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  : <FiChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                }
                <div className="min-w-0">
                  <h3 className="text-sm font-medium text-gray-900">TRL {def.level}: {def.name}</h3>
                  {def.description && <p className="text-xs text-gray-500 mt-0.5 truncate">{def.description}</p>}
                </div>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0 ml-2">
                <button onClick={(e) => { e.stopPropagation(); setEditingDefinition(def); setShowDefinitionModal(true) }}
                  className="p-2 text-primary-600 hover:bg-primary-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center">
                  <FiEdit className="h-4 w-4" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); setSelectedDefinition(def); setEditingQuestion(null); setShowQuestionModal(true) }}
                  className="p-2 text-primary-600 hover:bg-primary-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center">
                  <FiPlus className="h-4 w-4" />
                </button>
                <button onClick={(e) => { e.stopPropagation(); handleDeleteDefinition(def.id) }}
                  className="p-2 text-trl-low hover:bg-red-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center">
                  <FiTrash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            {expandedDefinitions.has(def.id) && (
              <div className="border-t p-4" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2.5">
                  Questions ({def.questions?.length || 0})
                </h4>
                <div className="space-y-1.5">
                  {def.questions && def.questions.length > 0 ? (
                    def.questions.sort((a, b) => a.question_order - b.question_order).map((q) => (
                      <div key={q.id} className="flex items-start justify-between p-3 bg-white rounded border" style={{ borderColor: '#D9E2E2' }}>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold text-gray-400">Q{q.question_order}</span>
                            {q.is_required && <span className="badge badge-danger text-[10px]">Required</span>}
                            {q.evidence_required && <span className="badge badge-warning text-[10px]">Evidence</span>}
                          </div>
                          <p className="text-sm text-gray-800 mt-1">{q.question_text}</p>
                        </div>
                        <div className="flex items-center gap-1 ml-3 flex-shrink-0">
                          <button onClick={() => { setSelectedDefinition(def); setEditingQuestion(q); setShowQuestionModal(true) }}
                            className="p-1.5 text-primary-600 hover:bg-primary-50 rounded transition-colors">
                            <FiEdit className="h-3.5 w-3.5" />
                          </button>
                          <button onClick={() => handleDeleteQuestion(q.id)}
                            className="p-1.5 text-trl-low hover:bg-red-50 rounded transition-colors">
                            <FiTrash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-gray-400 text-center py-4">No questions yet</p>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Definition Modal */}
      <Modal isOpen={showDefinitionModal} onClose={() => { setShowDefinitionModal(false); setEditingDefinition(null) }}
        title={editingDefinition ? 'Edit TRL Definition' : 'Create TRL Definition'} size="md">
        <TRLDefinitionForm definition={editingDefinition}
          onSave={() => { setShowDefinitionModal(false); setEditingDefinition(null); loadDefinitions() }}
          onCancel={() => { setShowDefinitionModal(false); setEditingDefinition(null) }} />
      </Modal>

      {/* Question Modal */}
      <Modal isOpen={showQuestionModal}
        onClose={() => { setShowQuestionModal(false); setEditingQuestion(null); setSelectedDefinition(null) }}
        title={editingQuestion ? 'Edit Question' : 'Add Question'} size="md">
        <TRLQuestionForm definition={selectedDefinition} question={editingQuestion}
          onSave={() => { setShowQuestionModal(false); setEditingQuestion(null); setSelectedDefinition(null); loadDefinitions() }}
          onCancel={() => { setShowQuestionModal(false); setEditingQuestion(null); setSelectedDefinition(null) }} />
      </Modal>
    </div>
  )
}

/* ── TRL Definition Form ── */
const TRLDefinitionForm = ({ definition, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    level: definition?.level || '',
    name: definition?.name || '',
    description: definition?.description || '',
    evidence_required: definition?.evidence_required !== undefined ? definition.evidence_required : true,
    min_confidence: definition?.min_confidence || '',
    is_active: definition?.is_active !== undefined ? definition.is_active : true,
  })
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
    if (errors[name]) setErrors(prev => { const n = { ...prev }; delete n[name]; return n })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.level || !formData.name) { setErrors({ submit: 'Level and name are required' }); return }
    setLoading(true)
    try {
      const payload = { ...formData, level: parseInt(formData.level), min_confidence: formData.min_confidence ? parseFloat(formData.min_confidence) : null }
      if (definition) await api.patch(`/admin/trl-definitions/${definition.id}`, payload)
      else await api.post('/admin/trl-definitions', payload)
      onSave()
    } catch (error) {
      setErrors({ submit: error.response?.data?.detail || 'Failed to save definition' })
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.submit && <div className="alert-error text-sm">{errors.submit}</div>}

      <div>
        <label className="form-label">TRL Level <span className="text-trl-low">*</span></label>
        <input type="number" name="level" value={formData.level} onChange={handleChange} min="1" max="9" disabled={!!definition}
          className={`input ${definition ? '' : ''}`} required />
      </div>
      <div>
        <label className="form-label">Name <span className="text-trl-low">*</span></label>
        <input type="text" name="name" value={formData.name} onChange={handleChange} className="input" required />
      </div>
      <div>
        <label className="form-label">Description</label>
        <textarea name="description" value={formData.description} onChange={handleChange} rows={3} className="input resize-none" />
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" name="evidence_required" checked={formData.evidence_required} onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
        <label className="text-sm text-gray-700">Evidence Required</label>
      </div>
      <div>
        <label className="form-label">Minimum Confidence (0–1)</label>
        <input type="number" name="min_confidence" value={formData.min_confidence} onChange={handleChange}
          min="0" max="1" step="0.1" className="input" />
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
        <label className="text-sm text-gray-700">Active</label>
      </div>
      <div className="flex justify-end gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button type="button" onClick={onCancel} disabled={loading} className="btn-secondary">Cancel</button>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? <LoadingSpinner size="sm" /> : 'Save'}
        </button>
      </div>
    </form>
  )
}

/* ── TRL Question Form ── */
const TRLQuestionForm = ({ definition, question, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    question_text: question?.question_text || '',
    question_order: question?.question_order || (definition?.questions?.length || 0) + 1,
    is_required: question?.is_required !== undefined ? question.is_required : true,
    evidence_required: question?.evidence_required !== undefined ? question.evidence_required : true,
    weight: question?.weight || 1.0,
  })
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.question_text) { setErrors({ submit: 'Question text is required' }); return }
    setLoading(true)
    try {
      const payload = { ...formData, trl_definition_id: definition.id }
      if (question) await api.patch(`/admin/trl-questions/${question.id}`, payload)
      else await api.post('/admin/trl-questions', payload)
      onSave()
    } catch (error) {
      setErrors({ submit: error.response?.data?.detail || 'Failed to save question' })
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.submit && <div className="alert-error text-sm">{errors.submit}</div>}

      <div>
        <label className="form-label">Question Text <span className="text-trl-low">*</span></label>
        <textarea name="question_text" value={formData.question_text} onChange={handleChange} rows={3} className="input resize-none" required />
      </div>
      <div>
        <label className="form-label">Order</label>
        <input type="number" name="question_order" value={formData.question_order} onChange={handleChange} min="1" className="input" />
      </div>
      <div>
        <label className="form-label">Weight</label>
        <input type="number" name="weight" value={formData.weight} onChange={handleChange} min="0" step="0.1" className="input" />
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" name="is_required" checked={formData.is_required} onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
        <label className="text-sm text-gray-700">Required</label>
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" name="evidence_required" checked={formData.evidence_required} onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
        <label className="text-sm text-gray-700">Evidence Required</label>
      </div>
      <div className="flex justify-end gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button type="button" onClick={onCancel} disabled={loading} className="btn-secondary">Cancel</button>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? <LoadingSpinner size="sm" /> : 'Save'}
        </button>
      </div>
    </form>
  )
}

export default TRLDefinitionManager
