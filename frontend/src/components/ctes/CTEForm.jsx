import React, { useState } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'

const CTEForm = ({ cte, projectId, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    code: cte?.code || '',
    name: cte?.name || '',
    description: cte?.description || '',
    category: cte?.category || '',
    target_trl: cte?.target_trl || '',
  })
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors(prev => { const n = { ...prev }; delete n[name]; return n })
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.code.trim()) newErrors.code = 'CTE code is required'
    if (!formData.name.trim()) newErrors.name = 'CTE name is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const payload = { ...formData, target_trl: formData.target_trl ? parseInt(formData.target_trl) : null }
      if (cte) { await api.patch(`/ctes/${cte.id}`, payload) }
      else { await api.post(`/ctes/projects/${projectId}/ctes`, { ...payload, project_id: projectId }) }
      onSave()
    } catch (error) {
      console.error('Error saving CTE:', error)
      let errorMessage = 'Failed to save CTE'
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) { errorMessage = detail.map(e => { const f = Array.isArray(e.loc) ? e.loc.slice(1).join('.') : ''; return f ? `${f}: ${e.msg}` : e.msg }).join(' | ') }
      else if (typeof detail === 'string') { errorMessage = detail }
      else if (detail?.msg) { errorMessage = detail.msg }
      setErrors({ submit: errorMessage })
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {errors.submit && (
        <div className="alert-error">
          <p className="font-medium text-sm">Error</p>
          <p className="text-xs mt-1">{typeof errors.submit === 'string' ? errors.submit : 'Failed to save CTE'}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="code" className="form-label">CTE Code <span className="text-trl-low">*</span></label>
          <input type="text" id="code" name="code" value={formData.code} onChange={handleChange} disabled={!!cte}
            className={`input ${errors.code ? 'input-error' : ''}`} required />
          {errors.code && <p className="text-trl-low text-xs mt-1">{errors.code}</p>}
        </div>
        <div>
          <label htmlFor="name" className="form-label">CTE Name <span className="text-trl-low">*</span></label>
          <input type="text" id="name" name="name" value={formData.name} onChange={handleChange}
            className={`input ${errors.name ? 'input-error' : ''}`} required />
          {errors.name && <p className="text-trl-low text-xs mt-1">{errors.name}</p>}
        </div>
      </div>

      <div>
        <label htmlFor="description" className="form-label">Description</label>
        <textarea id="description" name="description" value={formData.description} onChange={handleChange}
          rows={3} className="input resize-none" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="category" className="form-label">Category</label>
          <input type="text" id="category" name="category" value={formData.category} onChange={handleChange}
            className="input" placeholder="e.g. Hardware, Software, AI" />
        </div>
        <div>
          <label htmlFor="target_trl" className="form-label">Target TRL</label>
          <input type="number" id="target_trl" name="target_trl" value={formData.target_trl} onChange={handleChange}
            min="1" max="9" className="input" placeholder="1–9" />
          <p className="text-xs text-gray-400 mt-1">Project Target TRL = min(all CTE Target TRLs)</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 pt-5 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button type="submit" disabled={loading} className="btn-primary flex-1 sm:flex-none">
          {loading ? <LoadingSpinner size="sm" /> : (cte ? 'Update CTE' : 'Create CTE')}
        </button>
        <button type="button" onClick={onCancel} disabled={loading} className="btn-secondary flex-1 sm:flex-none">
          Cancel
        </button>
      </div>
    </form>
  )
}

export default CTEForm
