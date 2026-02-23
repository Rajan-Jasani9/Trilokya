import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import ResponsiveTable from '../common/Table'
import LoadingSpinner from '../common/LoadingSpinner'
import Dropdown, { DropdownItem } from '../common/Dropdown'
import { FiPlus, FiSearch, FiFilter, FiEdit, FiUsers, FiEye } from 'react-icons/fi'

const ProjectList = ({ onProjectSelect, onCreateProject, onEditProject, onAssignMembers, refreshTrigger }) => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterOpen, setFilterOpen] = useState(false)

  useEffect(() => { loadProjects() }, [refreshTrigger])

  const loadProjects = async () => {
    try {
      const response = await api.get('/projects')
      setProjects(response.data)
    } catch (error) {
      console.error('Error loading projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.code.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) return <LoadingSpinner fullScreen />

  const columns = [
    { header: 'Code', key: 'code' },
    { header: 'Name', key: 'name' },
    { header: 'Category', key: 'category' },
    { header: 'Target TRL', key: 'target_trl' },
    { header: 'Actions', key: 'actions' },
  ]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">Projects</h1>
        <button onClick={onCreateProject} className="btn-primary">
          <FiPlus className="h-4 w-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search projects by name or code…"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-9"
            />
          </div>
          <button
            onClick={() => setFilterOpen(!filterOpen)}
            className={`btn-secondary ${filterOpen ? 'bg-primary-50' : ''}`}
          >
            <FiFilter className="h-4 w-4" />
            <span className="hidden sm:inline">Filters</span>
          </button>
        </div>
      </div>

      {/* Table / Cards */}
      {filteredProjects.length === 0 ? (
        <div className="card p-12 text-center">
          <FiEye className="h-10 w-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No projects found</p>
        </div>
      ) : (
        <ResponsiveTable
          columns={columns}
          data={filteredProjects}
          renderRow={(project) => (
            <>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className="text-sm font-mono font-medium text-gray-900">{project.code}</span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className="text-sm font-medium text-gray-900">{project.name}</span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className="badge badge-gray">{project.category}</span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className="text-sm text-gray-700 font-medium">
                  {project.target_trl ? `TRL ${project.target_trl}` : '—'}
                </span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => onProjectSelect(project)}
                    className="btn-ghost text-xs py-1 px-2 min-h-[36px]"
                  >
                    View
                  </button>
                  <Dropdown>
                    <DropdownItem icon={FiEye} onClick={() => onProjectSelect(project)}>View Details</DropdownItem>
                    <DropdownItem icon={FiEdit} onClick={() => onEditProject && onEditProject(project)}>Edit Project</DropdownItem>
                    <DropdownItem icon={FiUsers} onClick={() => onAssignMembers && onAssignMembers(project)}>Assign Members</DropdownItem>
                  </Dropdown>
                </div>
              </td>
            </>
          )}
          renderCard={(project) => (
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900 truncate">{project.name}</h3>
                  <p className="text-xs font-mono text-gray-400 mt-0.5">{project.code}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <span className="badge badge-gray">{project.category}</span>
                {project.target_trl && <span className="badge badge-info">Target TRL {project.target_trl}</span>}
              </div>
              <div className="flex gap-2 pt-2 border-t" style={{ borderColor: '#D9E2E2' }}>
                <button onClick={() => onProjectSelect(project)} className="flex-1 btn-primary text-xs">
                  <FiEye className="h-3.5 w-3.5" />
                  <span>View Details</span>
                </button>
                <Dropdown>
                  <DropdownItem icon={FiEdit} onClick={() => onEditProject && onEditProject(project)}>Edit</DropdownItem>
                  <DropdownItem icon={FiUsers} onClick={() => onAssignMembers && onAssignMembers(project)}>Assign Members</DropdownItem>
                </Dropdown>
              </div>
            </div>
          )}
        />
      )}
    </div>
  )
}

export default ProjectList
