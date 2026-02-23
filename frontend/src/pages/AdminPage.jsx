import React, { useState, useEffect } from 'react'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import TRLDefinitionManager from '../components/admin/TRLDefinitionManager'
import { FiSettings, FiLayers } from 'react-icons/fi'

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('trl')
  const [loading, setLoading] = useState(false)
  const [orgUnits, setOrgUnits] = useState([])

  useEffect(() => {
    if (activeTab === 'org') loadOrgUnits()
  }, [activeTab])

  const loadOrgUnits = async () => {
    try { setLoading(true); const r = await api.get('/admin/org-units'); setOrgUnits(r.data || []) }
    catch (error) { console.error('Error loading org units:', error); alert('Failed to load organization units') }
    finally { setLoading(false) }
  }

  const tabs = [
    { id: 'trl', label: 'TRL Definitions', icon: FiSettings },
    { id: 'org', label: 'Organization Units', icon: FiLayers },
  ]

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
            {activeTab === 'trl' && <TRLDefinitionManager />}
            {activeTab === 'org' && (
              <div className="space-y-4">
                <div>
                  <h2 className="section-title mb-1">Organization Units</h2>
                  <p className="text-sm text-gray-500 mb-4">View and manage organization units.</p>
                  {orgUnits.length === 0 ? (
                    <p className="text-gray-400 text-center py-8 text-sm">No organization units found</p>
                  ) : (
                    <div className="space-y-2">
                      {orgUnits.map((org) => (
                        <div key={org.id} className="border rounded p-4" style={{ borderColor: '#D9E2E2' }}>
                          <h4 className="text-sm font-medium text-gray-900">{org.name}</h4>
                          <p className="text-xs text-gray-500 mt-0.5">Code: {org.code} · Type: {org.org_type}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default AdminPage
