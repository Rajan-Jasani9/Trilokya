import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import Modal from '../common/Modal'
import ProjectMemberAssignment from './ProjectMemberAssignment'
import ProjectMetricsInfographic from './ProjectMetricsInfographic'
import { FiEdit, FiUsers, FiPlus, FiArrowLeft, FiFolder, FiTrash2 } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const ProjectDetail = ({ projectId, onBack, onEdit, onAddCTE, onCTECreated, refreshTrigger, onProjectDeleted }) => {
  const [project, setProject] = useState(null)
  const [ctes, setCtes] = useState([])
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showMemberModal, setShowMemberModal] = useState(false)
  const { user } = useAuth()
  const navigate = useNavigate()

  const userRoles = user?.roles || []
  const canAssignMembers = Array.isArray(userRoles)
    ? (userRoles.includes('Manager') || userRoles.includes('Assistant Manager'))
    : (userRoles === 'Manager' || userRoles === 'Assistant Manager' ||
       (typeof userRoles === 'string' && (userRoles.includes('Manager') || userRoles.includes('Assistant Manager'))))

  const canDeleteProjectOrCTE = Array.isArray(userRoles)
    ? (userRoles.includes('Manager') || userRoles.includes('SuperAdmin'))
    : (userRoles === 'Manager' || userRoles === 'SuperAdmin' ||
       (typeof userRoles === 'string' && (userRoles.includes('Manager') || userRoles.includes('SuperAdmin'))))

  useEffect(() => { loadProject(); loadCTEs(); loadMembers() }, [projectId, refreshTrigger])

  const loadProject = async () => {
    try { const r = await api.get(`/projects/${projectId}`); setProject(r.data) }
    catch (error) { console.error('Error loading project:', error) }
    finally { setLoading(false) }
  }

  const loadCTEs = async () => {
    try {
      const response = await api.get(`/ctes/projects/${projectId}/ctes`)
      const ctesData = response.data || []
      const trlPromises = ctesData.map(async (cte) => {
        try {
          const trlResponse = await api.get(`/trl/ctes/${cte.id}/current-trl`).catch(() => ({ data: { current_trl: 0 } }))
          return { ...cte, current_trl: trlResponse.data?.current_trl ?? 0 }
        } catch { return { ...cte, current_trl: 0 } }
      })
      setCtes(await Promise.all(trlPromises))
    } catch (error) { console.error('Error loading CTEs:', error) }
  }

  const loadMembers = async () => {
    try { const r = await api.get(`/projects/${projectId}/members`); setMembers(r.data) }
    catch (error) {
      console.error('Error loading members:', error)
      try { const pr = await api.get(`/projects/${projectId}`); if (pr.data.members) setMembers(pr.data.members) } catch {}
    }
  }

  const handleDeleteProject = async () => {
    if (!window.confirm(`Delete project "${project?.name}" (${project?.code})? This cannot be undone.`)) return
    try {
      await api.delete(`/projects/${projectId}`)
      onProjectDeleted?.()
    } catch (error) {
      console.error('Error deleting project:', error)
      alert(error.response?.data?.detail || 'Failed to delete project')
    }
  }

  const handleDeleteCTE = async (e, cte) => {
    e.stopPropagation()
    if (!window.confirm(`Delete CTE "${cte.name}" (${cte.code})? This cannot be undone.`)) return
    try {
      await api.delete(`/ctes/${cte.id}`)
      loadCTEs()
      loadProject()
    } catch (error) {
      console.error('Error deleting CTE:', error)
      alert(error.response?.data?.detail || 'Failed to delete CTE')
    }
  }

  if (loading) return <LoadingSpinner fullScreen />
  if (!project) return <div className="text-gray-500">Project not found</div>

  return (
    <div className="space-y-5">
      {/* Back button */}
      {onBack && (
        <button onClick={onBack} className="btn-ghost text-sm">
          <FiArrowLeft className="h-4 w-4" />
          <span>Back to Projects</span>
        </button>
      )}

      {/* Project Hero Header */}
      <div className="card p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-5 border-b" style={{ borderColor: '#D9E2E2' }}>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{project.name}</h1>
            <p className="text-xs font-mono text-gray-400 mt-1">{project.code}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => onEdit(project)} className="btn-secondary text-sm">
              <FiEdit className="h-4 w-4" /><span>Edit</span>
            </button>
            {canAssignMembers && (
              <button onClick={() => setShowMemberModal(true)} className="btn-secondary text-sm">
                <FiUsers className="h-4 w-4" /><span>Assign Members</span>
              </button>
            )}
            <button onClick={() => onAddCTE(project.id)} className="btn-primary text-sm">
              <FiPlus className="h-4 w-4" /><span>Add CTE</span>
            </button>
            {canDeleteProjectOrCTE && (
              <button
                type="button"
                onClick={handleDeleteProject}
                className="btn-secondary text-sm border-red-200 text-red-700 hover:bg-red-50"
              >
                <FiTrash2 className="h-4 w-4" /><span>Delete project</span>
              </button>
            )}
          </div>
        </div>

        {/* Project Info Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-5">
          {[
            { label: 'Category', value: project.category },
            { label: 'Target TRL', value: project.target_trl ? `TRL ${project.target_trl}` : '—' },
            { label: 'Start Date', value: new Date(project.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) },
            { label: 'End Date', value: project.end_date ? new Date(project.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '—' },
          ].map((item) => (
            <div key={item.label}>
              <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">{item.label}</p>
              <p className="text-sm font-medium text-gray-900 mt-1">{item.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Metrics Infographic */}
      <ProjectMetricsInfographic project={project} ctes={ctes} />

      {/* Members Section */}
      {canAssignMembers && (
        <div className="card p-5">
          <div className="section-header">
            <h2 className="section-title">Project Members</h2>
            <button onClick={() => setShowMemberModal(true)} className="btn-ghost text-xs">
              <FiUsers className="h-3.5 w-3.5" /><span>Manage</span>
            </button>
          </div>
          {members.length === 0 ? (
            <div className="text-center py-8">
              <FiUsers className="h-8 w-8 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500 text-sm font-medium">No members assigned</p>
              <p className="text-gray-400 text-xs mt-1">Click "Manage" to assign members</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {members.map((member) => (
                <div key={member.id} className="card p-3">
                  <p className="text-sm font-medium text-gray-900">
                    {member.user?.full_name || member.user?.username || `User ${member.user_id}`}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">{member.user?.email || ''}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* CTEs Section */}
      <div className="card p-5">
        <div className="section-header">
          <h2 className="section-title">Critical Technology Elements</h2>
          <span className="badge badge-info">{ctes.length} {ctes.length === 1 ? 'CTE' : 'CTEs'}</span>
        </div>
        {ctes.length === 0 ? (
          <div className="text-center py-10">
            <FiPlus className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium text-sm">No CTEs found</p>
            <p className="text-gray-400 text-xs mt-1">Click "Add CTE" to create one</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {ctes.map((cte) => (
              <div
                key={cte.id}
                className="card card-hover p-4 cursor-pointer"
                onClick={() => navigate(`/app/ctes?cteId=${cte.id}`)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-gray-900 truncate">{cte.name}</h3>
                    <p className="text-xs font-mono text-gray-400 mt-0.5">{cte.code}</p>
                    {cte.description && (
                      <p className="text-xs text-gray-500 mt-1.5 line-clamp-2">{cte.description}</p>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    {cte.target_trl && (
                      <span className="badge badge-info text-[10px]">
                        Target TRL {cte.target_trl}
                      </span>
                    )}
                    {canDeleteProjectOrCTE && (
                      <button
                        type="button"
                        title="Delete CTE"
                        className="p-1.5 rounded text-red-600 hover:bg-red-50"
                        onClick={(e) => handleDeleteCTE(e, cte)}
                      >
                        <FiTrash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Member Modal */}
      <Modal isOpen={showMemberModal} onClose={() => setShowMemberModal(false)} title={`Assign Members — ${project.name}`} size="md">
        <ProjectMemberAssignment projectId={project.id} onClose={() => { setShowMemberModal(false); loadMembers() }} />
      </Modal>
    </div>
  )
}

export default ProjectDetail
