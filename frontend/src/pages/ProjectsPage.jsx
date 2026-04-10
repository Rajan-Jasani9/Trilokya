import React, { useState, useEffect } from 'react'
import api from '../services/api'
import ProjectList from '../components/projects/ProjectList'
import ProjectDetail from '../components/projects/ProjectDetail'
import ProjectForm from '../components/projects/ProjectForm'
import ProjectMemberAssignment from '../components/projects/ProjectMemberAssignment'
import CTEForm from '../components/ctes/CTEForm'
import Modal from '../components/common/Modal'
import { FiArrowLeft } from 'react-icons/fi'

const ProjectsPage = () => {
  const [selectedProject, setSelectedProject] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showCTEModal, setShowCTEModal] = useState(false)
  const [showAssignMembersModal, setShowAssignMembersModal] = useState(false)
  const [projectForMembers, setProjectForMembers] = useState(null)
  const [editingProject, setEditingProject] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [cteRefreshTrigger, setCteRefreshTrigger] = useState(0)

  useEffect(() => {
    const projectId = sessionStorage.getItem('selectedProjectId')
    if (projectId) {
      sessionStorage.removeItem('selectedProjectId')
      loadAndSelectProject(parseInt(projectId))
    }
  }, [])

  const loadAndSelectProject = async (projectId) => {
    try {
      const response = await api.get(`/projects/${projectId}`)
      setSelectedProject(response.data)
    } catch (error) {
      console.error('Error loading project:', error)
    }
  }

  const handleProjectSelect = (project) => setSelectedProject(project)
  const handleCreateProject = () => setShowCreateModal(true)
  const handleBackToList = () => { setSelectedProject(null); setEditingProject(null) }
  const handleEditProject = (project) => { setEditingProject(project); setSelectedProject(null) }
  const handleAssignMembers = (project) => { setProjectForMembers(project); setShowAssignMembersModal(true) }

  const handleDeleteProject = async (project) => {
    if (!window.confirm(`Delete project "${project.name}" (${project.code})? This cannot be undone.`)) return
    try {
      await api.delete(`/projects/${project.id}`)
      if (selectedProject?.id === project.id) setSelectedProject(null)
      setRefreshTrigger((p) => p + 1)
    } catch (error) {
      console.error('Error deleting project:', error)
      alert(error.response?.data?.detail || 'Failed to delete project')
    }
  }

  if (selectedProject && !editingProject) {
    return (
      <>
        <ProjectDetail
          projectId={selectedProject.id}
          onBack={handleBackToList}
          onEdit={(project) => setEditingProject(project)}
          onAddCTE={() => setShowCTEModal(true)}
          refreshTrigger={cteRefreshTrigger}
          onProjectDeleted={() => { handleBackToList(); setRefreshTrigger((p) => p + 1) }}
        />
        <Modal isOpen={showCTEModal} onClose={() => setShowCTEModal(false)} title="Create New CTE" size="md">
          <CTEForm
            projectId={selectedProject.id}
            onSave={() => { setShowCTEModal(false); setCteRefreshTrigger(prev => prev + 1) }}
            onCancel={() => setShowCTEModal(false)}
          />
        </Modal>
      </>
    )
  }

  if (editingProject) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => setEditingProject(null)}
          className="btn-ghost text-sm"
        >
          <FiArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>
        <div className="card p-5 md:p-6">
          <h1 className="text-lg font-semibold text-gray-900 mb-5">Edit Project</h1>
          <ProjectForm
            project={editingProject}
            onSave={() => { setEditingProject(null); setSelectedProject(null); setRefreshTrigger(prev => prev + 1) }}
            onCancel={() => setEditingProject(null)}
          />
        </div>
      </div>
    )
  }

  return (
    <>
      <ProjectList
        onProjectSelect={handleProjectSelect}
        onCreateProject={handleCreateProject}
        onEditProject={handleEditProject}
        onAssignMembers={handleAssignMembers}
        onDeleteProject={handleDeleteProject}
        refreshTrigger={refreshTrigger}
      />
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Project" size="lg">
        <ProjectForm
          onSave={() => { setShowCreateModal(false); setRefreshTrigger(prev => prev + 1) }}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>
      <Modal
        isOpen={showAssignMembersModal}
        onClose={() => { setShowAssignMembersModal(false); setProjectForMembers(null) }}
        title={`Assign Members — ${projectForMembers?.name || ''}`}
        size="md"
      >
        {projectForMembers && (
          <ProjectMemberAssignment
            projectId={projectForMembers.id}
            onClose={() => { setShowAssignMembersModal(false); setProjectForMembers(null); setRefreshTrigger(prev => prev + 1) }}
          />
        )}
      </Modal>
    </>
  )
}

export default ProjectsPage
