import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'

const ProjectForm = ({ project, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false)
  const [orgUnits, setOrgUnits] = useState([])
  const [technologies, setTechnologies] = useState([])
  const [formData, setFormData] = useState({
    code: project?.code || '',
    name: project?.name || '',
    description: project?.description || '',
    category: project?.category || 'Hardware',
    target_trl: project?.target_trl || '',
    start_date: project?.start_date ? project.start_date.split('T')[0] : '',
    end_date: project?.end_date ? project.end_date.split('T')[0] : '',
    org_unit_ids: project?.org_unit_ids || [],
    technology_ids: project?.technology_ids || [],
  })
  const [errors, setErrors] = useState({})

  useEffect(() => {
    loadOrgUnits()
    loadTechnologies()
  }, [])

  const loadOrgUnits = async () => {
    try {
      const response = await api.get('/admin/org-units').catch(() => ({ data: [] }))
      setOrgUnits(response.data || [])
    } catch (error) {
      console.error('Error loading org units:', error)
    }
  }

  const loadTechnologies = async () => {
    try {
      const response = await api.get('/technologies').catch(() => ({ data: [] }))
      setTechnologies(response.data || [])
    } catch (error) {
      console.error('Error loading technologies:', error)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors(prev => { const n = { ...prev }; delete n[name]; return n })
  }

  const handleOrgUnitChange = (orgUnitId) => {
    const id = parseInt(orgUnitId)
    setFormData(prev => ({
      ...prev,
      org_unit_ids: prev.org_unit_ids.includes(id)
        ? prev.org_unit_ids.filter(oid => oid !== id)
        : [...prev.org_unit_ids, id]
    }))
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.code.trim()) newErrors.code = 'Project code is required'
    if (!formData.name.trim()) newErrors.name = 'Project name is required'
    if (!formData.start_date) newErrors.start_date = 'Start date is required'
    if (formData.end_date && formData.start_date && formData.end_date < formData.start_date) newErrors.end_date = 'End date must be after start date'
    if (formData.target_trl && (formData.target_trl < 1 || formData.target_trl > 9)) newErrors.target_trl = 'Target TRL must be between 1 and 9'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleTechnologyChange = (e) => {
    const selectedId = parseInt(e.target.value)
    if (selectedId) {
      setFormData(prev => ({ ...prev, technology_ids: [selectedId] }))
    } else {
      setFormData(prev => ({ ...prev, technology_ids: [] }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const payload = { ...formData, target_trl: formData.target_trl ? parseInt(formData.target_trl) : null }
      if (project) {
        const { target_trl, ...updatePayload } = payload
        await api.patch(`/projects/${project.id}`, updatePayload)
      } else {
        await api.post('/projects', payload)
      }
      onSave()
    } catch (error) {
      console.error('Error saving project:', error)
      let errorMessage = 'Failed to save project'
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        errorMessage = detail.map(e => { const f = Array.isArray(e.loc) ? e.loc.slice(1).join('.') : ''; return f ? `${f}: ${e.msg}` : e.msg }).join(' | ')
      } else if (typeof detail === 'string') { errorMessage = detail }
      else if (detail?.msg) { errorMessage = detail.msg }
      setErrors({ submit: errorMessage })
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {errors.submit && (
        <div className="alert-error">
          <p className="font-medium text-sm">Error</p>
          <p className="text-xs mt-1">{typeof errors.submit === 'string' ? errors.submit : 'Failed to save project'}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="code" className="form-label">Project Code <span className="text-trl-low">*</span></label>
          <input type="text" id="code" name="code" value={formData.code} onChange={handleChange} disabled={!!project}
            className={`input ${errors.code ? 'input-error' : ''}`} required />
          {errors.code && <p className="text-trl-low text-xs mt-1">{errors.code}</p>}
        </div>
        <div>
          <label htmlFor="name" className="form-label">Project Name <span className="text-trl-low">*</span></label>
          <input type="text" id="name" name="name" value={formData.name} onChange={handleChange}
            className={`input ${errors.name ? 'input-error' : ''}`} required />
          {errors.name && <p className="text-trl-low text-xs mt-1">{errors.name}</p>}
        </div>
      </div>

      <div>
        <label htmlFor="description" className="form-label">Description</label>
        <textarea id="description" name="description" value={formData.description} onChange={handleChange}
          rows={3} className="input resize-none" placeholder="Enter project description…" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="category" className="form-label">Category <span className="text-trl-low">*</span></label>
          <select id="category" name="category" value={formData.category} onChange={handleChange} className="input" required>
            <option value="Hardware">Hardware</option>
            <option value="Software">Software</option>
            <option value="AI">AI</option>
            <option value="Mixed">Mixed</option>
          </select>
        </div>
        <div>
          <label htmlFor="target_trl" className="form-label">Target TRL <span className="text-xs text-gray-400 font-normal ml-1">(computed from CTEs)</span></label>
          <input type="number" id="target_trl" name="target_trl" value={formData.target_trl} onChange={handleChange}
            min="1" max="9" disabled className="input" title="Target TRL is automatically computed as min of all CTE Target TRLs" />
          <p className="text-xs text-gray-400 mt-1">Auto-calculated: min(all CTE Target TRLs)</p>
          {errors.target_trl && <p className="text-trl-low text-xs mt-1">{errors.target_trl}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="start_date" className="form-label">Start Date <span className="text-trl-low">*</span></label>
          <input type="date" id="start_date" name="start_date" value={formData.start_date} onChange={handleChange}
            className={`input ${errors.start_date ? 'input-error' : ''}`} required />
          {errors.start_date && <p className="text-trl-low text-xs mt-1">{errors.start_date}</p>}
        </div>
        <div>
          <label htmlFor="end_date" className="form-label">End Date</label>
          <input type="date" id="end_date" name="end_date" value={formData.end_date} onChange={handleChange}
            min={formData.start_date} className={`input ${errors.end_date ? 'input-error' : ''}`} />
          {errors.end_date && <p className="text-trl-low text-xs mt-1">{errors.end_date}</p>}
        </div>
      </div>

      {orgUnits.length > 0 && (
        <div>
          <label className="form-label">Organization Units</label>
          <div className="space-y-2 max-h-40 overflow-y-auto border rounded p-3" style={{ borderColor: '#D9E2E2' }}>
            {orgUnits.map((org) => (
              <label key={org.id} className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={formData.org_unit_ids.includes(org.id)} onChange={() => handleOrgUnitChange(org.id)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
                <span className="text-sm text-gray-700">{org.name} ({org.code})</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {technologies.length > 0 && (
        <div>
          <label htmlFor="technology" className="form-label">Technology Domain</label>
          <select
            id="technology"
            value={formData.technology_ids.length > 0 ? formData.technology_ids[0] : ''}
            onChange={handleTechnologyChange}
            className="input"
          >
            <option value="">— Select a technology —</option>
            {technologies.map((tech) => (
              <option key={tech.id} value={tech.id}>{tech.name}</option>
            ))}
          </select>
          <p className="text-xs text-gray-400 mt-1">Assign this project to a technology domain</p>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 pt-5 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button type="submit" disabled={loading} className="btn-primary flex-1 sm:flex-none">
          {loading ? <LoadingSpinner size="sm" /> : (project ? 'Update Project' : 'Create Project')}
        </button>
        <button type="button" onClick={onCancel} disabled={loading} className="btn-secondary flex-1 sm:flex-none">
          Cancel
        </button>
      </div>
    </form>
  )
}

export default ProjectForm
