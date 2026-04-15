import React, { useState, useEffect } from 'react'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ReadinessDefinitionManager from '../components/admin/ReadinessDefinitionManager'
import OrganizationUnitManager from '../components/admin/OrganizationUnitManager'
import { FiSettings, FiLayers } from 'react-icons/fi'

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('trl')
  const [loading, setLoading] = useState(false)
  const [strictModeDefault, setStrictModeDefault] = useState(false)
  const [couplingRows, setCouplingRows] = useState([])

  useEffect(() => {
    if (activeTab === 'readiness') loadReadinessConfig()
  }, [activeTab])

  const tabs = [
    { id: 'trl', label: 'TRL Definitions', icon: FiSettings },
    { id: 'irl', label: 'IRL Definitions', icon: FiSettings },
    { id: 'mrl', label: 'MRL Definitions', icon: FiSettings },
    { id: 'org', label: 'Organization Units', icon: FiLayers },
    { id: 'readiness', label: 'Readiness Config', icon: FiSettings },
  ]

  const loadReadinessConfig = async () => {
    try {
      setLoading(true)
      const [settingsR, couplingR] = await Promise.all([
        api.get('/admin/readiness-settings'),
        api.get('/admin/trl-coupling-config'),
      ])
      setStrictModeDefault(settingsR.data.strict_mode_default || false)
      setCouplingRows(couplingR.data?.length ? couplingR.data : Array.from({ length: 9 }, (_, i) => ({ trl_level: i + 1, min_irl: Math.max(1, i), min_mrl: Math.max(1, i) })))
    } catch (error) {
      console.error('Error loading readiness config:', error)
      alert('Failed to load readiness config')
    } finally {
      setLoading(false)
    }
  }

  const saveReadinessConfig = async () => {
    try {
      await api.put('/admin/readiness-settings', { strict_mode_default: strictModeDefault })
      await api.put('/admin/trl-coupling-config', { items: couplingRows.map((r) => ({ trl_level: Number(r.trl_level), min_irl: Number(r.min_irl), min_mrl: Number(r.min_mrl) })) })
      alert('Readiness config updated')
    } catch (error) {
      console.error('Error saving readiness config:', error)
      alert('Failed to save readiness config')
    }
  }

  return (
    <div className="space-y-5">
      <div className="page-header">
        <h1 className="page-title">Admin Panel</h1>
      </div>

      {/* Tabs */}
      <div className="card p-0 overflow-hidden">
        <nav className="flex border-b" style={{ borderColor: '#D9E2E2' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon
            const active = activeTab === tab.id
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-3 px-5 border-b-2 text-sm font-medium min-h-[44px] transition-colors duration-150
                  ${active
                    ? 'border-primary-600 text-primary-700 bg-primary-50/50'
                    : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                  }`}
              >
                <Icon className="h-4 w-4" /><span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="card p-5">
        {loading && activeTab !== 'trl' ? <LoadingSpinner /> : (
          <>
            {activeTab === 'trl' && <ReadinessDefinitionManager domain="trl" />}
            {activeTab === 'irl' && <ReadinessDefinitionManager domain="irl" />}
            {activeTab === 'mrl' && <ReadinessDefinitionManager domain="mrl" />}
            {activeTab === 'org' && <OrganizationUnitManager />}
            {activeTab === 'readiness' && (
              <div className="space-y-4">
                <h2 className="section-title">TRL Coupling & Strict Mode</h2>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={strictModeDefault} onChange={(e) => setStrictModeDefault(e.target.checked)} />
                  Strict mode default (global)
                </label>
                <div className="space-y-2">
                  {couplingRows.map((row, index) => (
                    <div key={row.trl_level} className="grid grid-cols-3 gap-2 items-center text-sm">
                      <div>TRL {row.trl_level}</div>
                      <input type="number" className="input" min="1" max="9" value={row.min_irl} onChange={(e) => setCouplingRows((prev) => prev.map((r, i) => i === index ? { ...r, min_irl: e.target.value } : r))} />
                      <input type="number" className="input" min="1" max="9" value={row.min_mrl} onChange={(e) => setCouplingRows((prev) => prev.map((r, i) => i === index ? { ...r, min_mrl: e.target.value } : r))} />
                    </div>
                  ))}
                </div>
                <button className="btn-primary" onClick={saveReadinessConfig}>Save Readiness Config</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default AdminPage
