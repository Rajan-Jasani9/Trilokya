import React, { useState, useEffect } from 'react'
import api from '../services/api'
import CTEList from '../components/ctes/CTEList'
import CTEDetail from '../components/ctes/CTEDetail'
import CTEForm from '../components/ctes/CTEForm'
import Modal from '../components/common/Modal'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { FiPlus, FiArrowLeft, FiFolder } from 'react-icons/fi'
import { useLocation } from 'react-router-dom'

const CTEsPage = () => {
  const location = useLocation()
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const [selectedCTE, setSelectedCTE] = useState(null)
  const [editingCTE, setEditingCTE] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => { loadProjects() }, [])
  useEffect(() => {
    const cteId = new URLSearchParams(location.search).get('cteId')
    if (!cteId || !projects.length) return
    openCTEDetailFromQuery(parseInt(cteId, 10))
  }, [location.search, projects])

  const loadProjects = async () => {
    try {
      const r = await api.get('/projects')
      setProjects(r.data)
      if (r.data.length > 0 && !selectedProject) setSelectedProject(r.data[0])
    } catch (error) { console.error('Error loading projects:', error) }
    finally { setLoading(false) }
  }

  const openCTEDetailFromQuery = async (cteId) => {
    if (!Number.isFinite(cteId)) return
    try {
      const cteResponse = await api.get(`/ctes/${cteId}`)
      const cte = cteResponse.data
      setSelectedCTE(cte)
      const project = projects.find((p) => p.id === cte.project_id)
      if (project) setSelectedProject(project)
    } catch (error) {
      console.error('Error opening CTE detail from query param:', error)
    }
  }

  const handleCTESelect = (cte) => setSelectedCTE(cte)
  const handleBackToList = () => { setSelectedCTE(null); setEditingCTE(null) }

  if (loading) return <LoadingSpinner fullScreen />

  if (selectedCTE && !editingCTE) {
    return <CTEDetail cteId={selectedCTE.id} onBack={handleBackToList} onEdit={(cte) => setEditingCTE(cte)} />
  }

  if (editingCTE) {
    return (
      <div className="space-y-4">
        <button onClick={() => setEditingCTE(null)} className="btn-ghost text-sm">
          <FiArrowLeft className="h-4 w-4" /><span>Back</span>
        </button>
        <div className="card p-5 md:p-6">
          <h1 className="text-lg font-semibold text-gray-900 mb-5">Edit CTE</h1>
          <CTEForm
            cte={editingCTE}
            projectId={editingCTE.project_id}
            onSave={() => { setEditingCTE(null); setSelectedCTE(null); loadProjects() }}
            onCancel={() => setEditingCTE(null)}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="page-header">
        <h1 className="page-title">Critical Technology Elements</h1>
        {selectedProject && (
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            <FiPlus className="h-4 w-4" /><span>New CTE</span>
          </button>
        )}
      </div>

      {/* Project Selector */}
      <div className="card p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="project-select" className="form-label">Project Filter</label>
          <select
            id="project-select"
            value={selectedProject?.id || ''}
            onChange={(e) => {
              const p = projects.find(p => p.id === parseInt(e.target.value))
              setSelectedProject(p); setSelectedCTE(null)
            }}
            className="input w-full"
          >
            <option value="">Select a project…</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name} ({p.code})</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="cte-search" className="form-label">Search CTEs</label>
          <input
            id="cte-search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by code, name, category, description..."
            className="input w-full"
          />
        </div>
      </div>

      {/* CTE List */}
      {selectedProject ? (
        <CTEList projectId={selectedProject.id} onCTESelect={handleCTESelect} searchQuery={search} />
      ) : (
        <div className="card p-12 text-center">
          <FiFolder className="h-10 w-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Please select a project to view CTEs</p>
        </div>
      )}

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New CTE" size="md">
        <CTEForm
          projectId={selectedProject?.id}
          onSave={() => { setShowCreateModal(false); loadProjects() }}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>
    </div>
  )
}

export default CTEsPage
