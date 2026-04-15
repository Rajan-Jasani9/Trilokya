import React, { useEffect, useMemo, useState } from 'react'
import { FiEdit, FiPlus, FiTrash2 } from 'react-icons/fi'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import Modal from '../common/Modal'

const ORG_TYPES = ['Directorate', 'Division', 'Lab']

const OrganizationUnitManager = () => {
  const [orgUnits, setOrgUnits] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [editingOrgUnit, setEditingOrgUnit] = useState(null)
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    parent_id: '',
    org_type: ORG_TYPES[0],
  })

  const parentOptions = useMemo(
    () => orgUnits.filter((ou) => ou.id !== editingOrgUnit?.id),
    [orgUnits, editingOrgUnit]
  )

  useEffect(() => {
    loadOrgUnits()
  }, [])

  const loadOrgUnits = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/org-units')
      setOrgUnits(response.data || [])
    } catch (error) {
      console.error('Error loading org units:', error)
      alert('Failed to load organization units')
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setEditingOrgUnit(null)
    setFormData({ code: '', name: '', parent_id: '', org_type: ORG_TYPES[0] })
    setShowModal(true)
  }

  const openEditModal = (orgUnit) => {
    setEditingOrgUnit(orgUnit)
    setFormData({
      code: orgUnit.code || '',
      name: orgUnit.name || '',
      parent_id: orgUnit.parent_id || '',
      org_type: orgUnit.org_type || ORG_TYPES[0],
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingOrgUnit(null)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      const payload = {
        code: formData.code.trim(),
        name: formData.name.trim(),
        org_type: formData.org_type,
        parent_id: formData.parent_id ? Number(formData.parent_id) : null,
      }

      if (editingOrgUnit) {
        await api.patch(`/admin/org-units/${editingOrgUnit.id}`, payload)
      } else {
        await api.post('/admin/org-units', payload)
      }

      closeModal()
      await loadOrgUnits()
    } catch (error) {
      console.error('Error saving org unit:', error)
      alert(error?.response?.data?.detail || 'Failed to save organization unit')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (orgUnit) => {
    if (!window.confirm(`Delete organization unit "${orgUnit.name}"?`)) return
    try {
      await api.delete(`/admin/org-units/${orgUnit.id}`)
      await loadOrgUnits()
    } catch (error) {
      console.error('Error deleting org unit:', error)
      alert(error?.response?.data?.detail || 'Failed to delete organization unit')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="section-title mb-0">Organization Units</h2>
        <button onClick={openCreateModal} className="btn-primary text-sm">
          <FiPlus className="h-4 w-4" />
          <span>Add Unit</span>
        </button>
      </div>

      {orgUnits.length === 0 ? (
        <p className="text-gray-400 text-center py-8 text-sm">No organization units found</p>
      ) : (
        <div className="space-y-2">
          {orgUnits.map((org) => (
            <div key={org.id} className="border rounded p-4 flex items-start justify-between gap-3" style={{ borderColor: '#D9E2E2' }}>
              <div className="min-w-0">
                <h4 className="text-sm font-medium text-gray-900">{org.name}</h4>
                <p className="text-xs text-gray-500 mt-0.5">Code: {org.code} | Type: {org.org_type}</p>
                {org.parent_id && <p className="text-xs text-gray-500 mt-0.5">Parent ID: {org.parent_id}</p>}
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                <button onClick={() => openEditModal(org)} className="p-2 text-primary-600 hover:bg-primary-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center">
                  <FiEdit className="h-4 w-4" />
                </button>
                <button onClick={() => handleDelete(org)} className="p-2 text-trl-low hover:bg-red-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center">
                  <FiTrash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editingOrgUnit ? 'Edit Organization Unit' : 'Create Organization Unit'}
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Code</label>
            <input
              type="text"
              name="code"
              value={formData.code}
              onChange={handleChange}
              className="input"
              required
            />
          </div>
          <div>
            <label className="form-label">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="input"
              required
            />
          </div>
          <div>
            <label className="form-label">Type</label>
            <select
              name="org_type"
              value={formData.org_type}
              onChange={handleChange}
              className="input"
              required
            >
              {ORG_TYPES.map((orgType) => (
                <option key={orgType} value={orgType}>
                  {orgType}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Parent Unit (Optional)</label>
            <select
              name="parent_id"
              value={formData.parent_id}
              onChange={handleChange}
              className="input"
            >
              <option value="">None</option>
              {parentOptions.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.code} - {org.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
            <button type="button" onClick={closeModal} className="btn-secondary" disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? <LoadingSpinner size="sm" /> : 'Save'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default OrganizationUnitManager
