import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { getTechnologyAssetSrc } from '../utils/technologyAssets'
import { FiFolder, FiTarget, FiArrowLeft, FiSearch, FiGrid, FiLayers } from 'react-icons/fi'
import { useToast } from '../components/common/ToastProvider'

const TechnologiesPage = () => {
  const { showToast } = useToast()
  const [technologies, setTechnologies] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTech, setSelectedTech] = useState(null)
  const [techProjects, setTechProjects] = useState([])
  const [projectsLoading, setProjectsLoading] = useState(false)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadTechnologies()
  }, [])

  const loadTechnologies = async () => {
    try {
      const response = await api.get('/technologies')
      setTechnologies(response.data || [])
    } catch (error) {
      console.error('Error loading technologies:', error)
      showToast('Failed to load technologies.', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleTechClick = async (tech) => {
    setSelectedTech(tech)
    setProjectsLoading(true)
    try {
      const response = await api.get(`/technologies/${tech.id}/projects`)
      setTechProjects(response.data || [])
    } catch (error) {
      console.error('Error loading projects for technology:', error)
      setTechProjects([])
      showToast('Failed to load projects for selected technology.', 'error')
    } finally {
      setProjectsLoading(false)
    }
  }

  const handleProjectClick = (project) => {
    navigate('/app/projects')
    sessionStorage.setItem('selectedProjectId', project.id.toString())
  }

  const handleBackToGrid = () => {
    setSelectedTech(null)
    setTechProjects([])
  }

  const filteredTechnologies = technologies.filter((tech) =>
    tech.name.toLowerCase().includes(search.toLowerCase())
  )

  const getTRLBadge = (trl) => {
    if (!trl || trl === 0) return 'bg-gray-100 text-gray-600'
    if (trl <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
    if (trl <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
    return 'bg-[#DDEEE1] text-[#2E7D32]'
  }

  if (loading) return <LoadingSpinner fullScreen />

  // ─── Project list view for a selected technology ───
  if (selectedTech) {
    return (
      <div className="space-y-5">
        <div className="page-header">
          <div className="flex items-center gap-3">
            <button onClick={handleBackToGrid} className="btn-ghost text-sm !px-2 !min-h-[36px]">
              <FiArrowLeft className="h-4 w-4" />
            </button>
            <div>
              <h1 className="page-title !mb-0">{selectedTech.name}</h1>
              {selectedTech.description && (
                <p className="text-sm text-gray-500 mt-1">{selectedTech.description}</p>
              )}
            </div>
          </div>
        </div>

        {projectsLoading ? (
          <LoadingSpinner />
        ) : techProjects.length === 0 ? (
          <div className="card p-12 text-center">
            <FiFolder className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium text-lg">No projects under this technology</p>
            <p className="text-gray-400 text-sm mt-2">
              Projects tagged with "{selectedTech.name}" will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <span className="badge badge-info">
                {techProjects.length} {techProjects.length === 1 ? 'Project' : 'Projects'}
              </span>
            </div>
            {techProjects.map((project) => {
              const currentTRL = project.current_trl || 0
              const currentIRL = project.current_irl || 0
              const currentMRL = project.current_mrl || 0
              const currentSRL = project.current_srl || 0
              const targetTRL = project.target_trl || 0
              const progress = targetTRL > 0 ? Math.max(0, Math.min(100, (currentTRL / targetTRL) * 100)) : 0
              const gap = targetTRL - currentTRL

              return (
                <div
                  key={project.id}
                  onClick={() => handleProjectClick(project)}
                  className="card card-hover p-4 cursor-pointer group"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="h-9 w-9 rounded bg-primary-50 flex items-center justify-center flex-shrink-0 group-hover:bg-primary-100 transition-colors">
                        <FiFolder className="h-4 w-4 text-primary-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-semibold text-gray-900 truncate group-hover:text-primary-700 transition-colors">
                          {project.name}
                        </h3>
                        <p className="text-xs font-mono text-gray-400 mt-0.5">{project.code}</p>
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          <span className="badge badge-gray">{project.category}</span>
                          {project.target_trl > 0 && (
                            <span className="badge badge-info">
                              <FiTarget className="h-3 w-3 mr-1" />
                              Target TRL {project.target_trl}
                            </span>
                          )}
                        </div>
                        {targetTRL > 0 && (
                          <div className="mt-2.5">
                            <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
                              <span>Progress to Target</span>
                              <span>{progress.toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary-600 rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <div className="text-right">
                        <div className={`px-3 py-1.5 rounded text-xs font-bold ${getTRLBadge(currentTRL)}`}>
                          TRL {currentTRL || 'N/A'}
                        </div>
                        <p className="text-[10px] text-gray-500 mt-1">IRL {currentIRL} · MRL {currentMRL} · SRL {currentSRL}</p>
                        {gap > 0 && (
                          <p className="text-[10px] text-gray-400 mt-1">Gap: {gap}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  // ─── Technology grid view ───
  return (
    <div className="space-y-5">
      <div className="page-header">
        <div>
          <h1 className="page-title">Technology Domains</h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse projects by technology area — click a card to view associated projects
          </p>
        </div>
      </div>

      {/* Search bar */}
      <div className="relative max-w-md">
        <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search technologies..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input !pl-10"
        />
      </div>

      {filteredTechnologies.length === 0 ? (
        <div className="card p-12 text-center">
          <FiLayers className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">No technologies found</p>
          <p className="text-gray-400 text-sm mt-1">
            {search ? 'Try a different search term' : 'Technologies will appear here once added.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {filteredTechnologies.map((tech) => (
            <TechnologyCard key={tech.id} tech={tech} onClick={() => handleTechClick(tech)} />
          ))}
        </div>
      )}
    </div>
  )
}

const TechnologyCard = ({ tech, onClick }) => {
  const iconSrc = getTechnologyAssetSrc(tech.icon_filename)

  return (
    <div
      onClick={onClick}
      className="group cursor-pointer rounded-md border bg-[#e8f4f4] hover:bg-[#d5ecec] transition-all duration-200 flex flex-col items-center justify-center p-5 text-center"
      style={{ borderColor: '#c8dede', minHeight: '160px' }}
    >
      {/* Icon from frontend/src/assets (see utils/technologyAssets.js) */}
      <div className="h-16 w-16 mb-3 flex items-center justify-center">
        {iconSrc ? (
          <img
            src={iconSrc}
            alt={tech.name}
            className="w-full h-full object-contain"
          />
        ) : (
          <FiGrid className="h-10 w-10 text-gray-800 group-hover:text-primary-700 transition-colors" />
        )}
      </div>

      {/* Name */}
      <p className="text-xs font-semibold text-gray-800 group-hover:text-primary-700 transition-colors leading-tight">
        {tech.name}
      </p>

      {/* Project count badge */}
      {tech.project_count > 0 && (
        <span className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-primary-100 text-primary-700">
          {tech.project_count} {tech.project_count === 1 ? 'project' : 'projects'}
        </span>
      )}
    </div>
  )
}

export default TechnologiesPage
