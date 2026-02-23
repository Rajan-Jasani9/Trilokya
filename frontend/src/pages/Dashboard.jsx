import React, { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { FiFolder, FiUsers, FiActivity, FiTarget, FiTrendingUp, FiAlertCircle, FiCheckCircle, FiClock } from 'react-icons/fi'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'

const Dashboard = () => {
  const [projects, setProjects] = useState([])
  const [allCTEs, setAllCTEs] = useState([])
  const [stats, setStats] = useState({ totalProjects: 0, activeCTEs: 0, totalUsers: 0 })
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const projectsResponse = await api.get('/projects')
      const projectsData = projectsResponse.data || []
      setProjects(projectsData)

      // Load all CTEs with their TRLs
      const ctePromises = []
      for (const project of projectsData) {
        try {
          const ctesResponse = await api.get(`/ctes/projects/${project.id}/ctes`).catch(() => ({ data: [] }))
          for (const cte of ctesResponse.data) {
            try {
              const trlResponse = await api.get(`/trl/ctes/${cte.id}/current-trl`).catch(() => ({ data: { current_trl: 0 } }))
              ctePromises.push({ ...cte, current_trl: trlResponse.data?.current_trl || 0, project_name: project.name })
            } catch {
              ctePromises.push({ ...cte, current_trl: 0, project_name: project.name })
            }
          }
        } catch (e) { /* ignore */ }
      }
      const enrichedCTEs = await Promise.all(ctePromises)
      setAllCTEs(enrichedCTEs)

      let totalCTEs = enrichedCTEs.length

      let totalUsers = 0
      try {
        const usersResponse = await api.get('/users/accessible').catch(() => api.get('/users'))
        totalUsers = usersResponse.data?.length || 0
      } catch (e) {
        console.error('Error loading users:', e)
      }

      setStats({ totalProjects: projectsData.length, activeCTEs: totalCTEs, totalUsers })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Compute TRL distribution for projects
  const trlDistribution = useMemo(() => {
    const dist = Array(9).fill(0).map((_, i) => ({ level: i + 1, count: 0, label: `TRL ${i + 1}` }))
    projects.forEach(p => {
      const trl = p.current_trl || 0
      if (trl >= 1 && trl <= 9) dist[trl - 1].count++
    })
    return dist
  }, [projects])

  // Compute TRL distribution for CTEs
  const cteTRLDistribution = useMemo(() => {
    const dist = Array(9).fill(0).map((_, i) => ({ level: i + 1, count: 0, label: `TRL ${i + 1}` }))
    allCTEs.forEach(cte => {
      const trl = cte.current_trl || 0
      if (trl >= 1 && trl <= 9) dist[trl - 1].count++
    })
    return dist
  }, [allCTEs])

  // Project risk breakdown
  const riskBreakdown = useMemo(() => {
    let low = 0, medium = 0, high = 0, critical = 0, complete = 0
    projects.forEach(p => {
      const current = p.current_trl || 0
      const target = p.target_trl || 9
      const gap = target - current
      if (current >= target) complete++
      else if (gap > 3) critical++
      else if (gap > 1) high++
      else if (gap === 1) medium++
      else low++
    })
    return [
      { name: 'Complete', value: complete, color: '#2E7D32' },
      { name: 'Low Risk', value: low, color: '#D4A017' },
      { name: 'Medium Risk', value: medium, color: '#D4A017' },
      { name: 'High Risk', value: high, color: '#C44536' },
      { name: 'Critical', value: critical, color: '#C44536' },
    ].filter(item => item.value > 0)
  }, [projects])

  // Category breakdown
  const categoryBreakdown = useMemo(() => {
    const catMap = {}
    projects.forEach(p => {
      const cat = p.category || 'Unknown'
      catMap[cat] = (catMap[cat] || 0) + 1
    })
    return Object.entries(catMap).map(([name, value]) => ({ name, value }))
  }, [projects])

  // Average TRL across portfolio
  const avgTRL = useMemo(() => {
    if (projects.length === 0) return 0
    const sum = projects.reduce((acc, p) => acc + (p.current_trl || 0), 0)
    return (sum / projects.length).toFixed(1)
  }, [projects])

  // Projects on track vs at risk
  const onTrackCount = useMemo(() => {
    return projects.filter(p => {
      const current = p.current_trl || 0
      const target = p.target_trl || 9
      return current >= target || (target - current) <= 1
    }).length
  }, [projects])

  if (loading) return <LoadingSpinner fullScreen />

  const kpis = [
    { label: 'Total Projects', value: stats.totalProjects, icon: FiFolder, trend: null },
    { label: 'Active CTEs', value: stats.activeCTEs, icon: FiActivity, trend: null },
    { label: 'Total Users', value: stats.totalUsers, icon: FiUsers, trend: null },
    { label: 'Avg TRL', value: avgTRL, icon: FiTrendingUp, trend: null },
    { label: 'On Track', value: `${onTrackCount}/${stats.totalProjects}`, icon: FiCheckCircle, trend: null },
    { label: 'At Risk', value: `${stats.totalProjects - onTrackCount}/${stats.totalProjects}`, icon: FiAlertCircle, trend: null },
  ]

  const getTRLColor = (level) => {
    if (!level || level === 0) return '#9E9E9E'
    if (level <= 3) return '#C44536'
    if (level <= 6) return '#D4A017'
    return '#2E7D32'
  }

  return (
    <div className="space-y-5">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
      </div>

      {/* Enhanced KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon
          return (
            <div key={kpi.label} className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{kpi.label}</p>
                <div className="h-8 w-8 rounded bg-primary-50 flex items-center justify-center flex-shrink-0">
                  <Icon className="h-4 w-4 text-primary-600" />
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
            </div>
          )
        })}
      </div>

      {/* Main Infographics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* TRL Distribution - Projects */}
        <div className="card p-5">
          <div className="section-header mb-4">
            <h2 className="section-title">Project TRL Distribution</h2>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={trlDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5ECEC" />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#6B7280' }} />
              <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #D9E2E2',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {trlDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getTRLColor(entry.level)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* TRL Distribution - CTEs */}
        <div className="card p-5">
          <div className="section-header mb-4">
            <h2 className="section-title">CTE TRL Distribution</h2>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={cteTRLDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5ECEC" />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#6B7280' }} />
              <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #D9E2E2',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {cteTRLDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getTRLColor(entry.level)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Secondary Infographics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Risk Breakdown */}
        <div className="card p-5">
          <div className="section-header mb-4">
            <h2 className="section-title">Project Risk Status</h2>
          </div>
          {riskBreakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={riskBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #D9E2E2',
                    borderRadius: '4px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-gray-400 text-sm">No risk data available</div>
          )}
        </div>

        {/* Category Breakdown */}
        <div className="card p-5">
          <div className="section-header mb-4">
            <h2 className="section-title">Projects by Category</h2>
          </div>
          {categoryBreakdown.length > 0 ? (
            <div className="space-y-3">
              {categoryBreakdown.map((cat) => {
                const percentage = ((cat.value / stats.totalProjects) * 100).toFixed(0)
                return (
                  <div key={cat.name} className="space-y-1.5">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">{cat.name}</span>
                      <span className="text-gray-500">{cat.value} ({percentage}%)</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-600 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400 text-sm">No category data available</div>
          )}
        </div>
      </div>

      {/* Portfolio Health Summary */}
      <div className="card p-5">
        <div className="section-header mb-4">
          <h2 className="section-title">Portfolio Health Summary</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
            <div className="flex items-center gap-2 mb-2">
              <FiCheckCircle className="h-4 w-4 text-trl-high" />
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">On Track</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{onTrackCount}</p>
            <p className="text-xs text-gray-500 mt-1">Projects meeting targets</p>
          </div>
          <div className="p-4 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
            <div className="flex items-center gap-2 mb-2">
              <FiAlertCircle className="h-4 w-4 text-trl-mid" />
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">At Risk</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.totalProjects - onTrackCount}</p>
            <p className="text-xs text-gray-500 mt-1">Projects needing attention</p>
          </div>
          <div className="p-4 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
            <div className="flex items-center gap-2 mb-2">
              <FiTrendingUp className="h-4 w-4 text-primary-600" />
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Avg TRL</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{avgTRL}</p>
            <p className="text-xs text-gray-500 mt-1">Portfolio average</p>
          </div>
          <div className="p-4 rounded border" style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}>
            <div className="flex items-center gap-2 mb-2">
              <FiActivity className="h-4 w-4 text-primary-600" />
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Active CTEs</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.activeCTEs}</p>
            <p className="text-xs text-gray-500 mt-1">Total technology elements</p>
          </div>
        </div>
      </div>

      {/* Current Projects List */}
      <div className="card p-5">
        <div className="section-header">
          <h2 className="section-title">Current Projects</h2>
          <span className="badge badge-info">{projects.length} {projects.length === 1 ? 'Project' : 'Projects'}</span>
        </div>
        {projects.length === 0 ? (
          <div className="text-center py-12">
            <FiFolder className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No projects found</p>
            <p className="text-gray-400 text-sm mt-1">Create your first project to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} navigate={navigate} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

const getTRLBadge = (trl) => {
  if (!trl || trl === 0) return 'bg-gray-100 text-gray-600'
  if (trl <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
  if (trl <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
  return 'bg-[#DDEEE1] text-[#2E7D32]'
}

const ProjectCard = ({ project, navigate }) => {
  const currentTRL = project.current_trl || 0
  const targetTRL = project.target_trl || 0
  const gap = targetTRL - currentTRL
  const progress = targetTRL > 0 ? Math.max(0, Math.min(100, (currentTRL / targetTRL) * 100)) : 0

  const handleProjectClick = () => {
    navigate('/app/projects')
    sessionStorage.setItem('selectedProjectId', project.id.toString())
  }

  return (
    <div
      onClick={handleProjectClick}
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
              {project.target_trl && (
                <span className="badge badge-info">
                  <FiTarget className="h-3 w-3 mr-1" />
                  Target TRL {project.target_trl}
                </span>
              )}
            </div>
            {/* Progress bar */}
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
            {gap > 0 && (
              <p className="text-[10px] text-gray-400 mt-1">Gap: {gap}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
