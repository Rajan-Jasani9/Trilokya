import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import ResponsiveTable from '../common/Table'
import LoadingSpinner from '../common/LoadingSpinner'

const getTRLBadge = (trl) => {
  if (!trl || trl === 0) return 'bg-gray-100 text-gray-600'
  if (trl <= 3) return 'bg-[#F4E0DD] text-[#C44536]'
  if (trl <= 6) return 'bg-[#F4E8D2] text-[#D4A017]'
  return 'bg-[#DDEEE1] text-[#2E7D32]'
}

const CTEList = ({ projectId, onCTESelect, searchQuery = '' }) => {
  const [ctes, setCtes] = useState([])
  const [cteTRLs, setCteTRLs] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => { if (projectId) loadCTEs() }, [projectId])

  const loadCTEs = async () => {
    try {
      const response = await api.get(`/ctes/projects/${projectId}/ctes`)
      const ctesData = response.data
      setCtes(ctesData)

      const trlResults = await Promise.all(
        ctesData.map(async (cte) => {
          try {
            const r = await api.get(`/trl/ctes/${cte.id}/current-trl`).catch(() => ({ data: { current_trl: 0 } }))
            return { cteId: cte.id, trl: r.data.current_trl || 0 }
          } catch { return { cteId: cte.id, trl: 0 } }
        })
      )
      const trlMap = {}
      trlResults.forEach(({ cteId, trl }) => { trlMap[cteId] = trl })
      setCteTRLs(trlMap)
    } catch (error) { console.error('Error loading CTEs:', error) }
    finally { setLoading(false) }
  }

  if (loading) return <LoadingSpinner />

  const columns = [
    { header: 'Code', key: 'code' },
    { header: 'Name', key: 'name' },
    { header: 'Category', key: 'category' },
    { header: 'Current TRL', key: 'trl' },
    { header: 'Actions', key: 'actions' },
  ]

  const normalizedQuery = (searchQuery || '').trim().toLowerCase()
  const filteredCtes = normalizedQuery
    ? ctes.filter((cte) =>
        [cte.code, cte.name, cte.category, cte.description]
          .filter(Boolean)
          .some((field) => String(field).toLowerCase().includes(normalizedQuery))
      )
    : ctes

  return (
    <div className="space-y-4">
      {filteredCtes.length === 0 ? (
        <div className="card p-10 text-center">
          <p className="text-gray-500 font-medium text-sm">
            {ctes.length === 0 ? 'No CTEs found for this project' : 'No CTEs match your search'}
          </p>
          <p className="text-gray-400 text-xs mt-1">
            {ctes.length === 0 ? 'Create a new CTE to get started' : 'Try a different keyword'}
          </p>
        </div>
      ) : (
        <ResponsiveTable
          columns={columns}
          data={filteredCtes}
          renderRow={(cte) => (
            <>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm font-mono font-medium text-gray-900">{cte.code}</td>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm font-medium text-gray-900">{cte.name}</td>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm text-gray-600">{cte.category || '—'}</td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold ${getTRLBadge(cteTRLs[cte.id])}`}>
                  TRL {cteTRLs[cte.id] || 'N/A'}
                </span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <button onClick={() => onCTESelect(cte)} className="btn-ghost text-xs py-1 px-2 min-h-[36px]">
                  View
                </button>
              </td>
            </>
          )}
          renderCard={(cte) => (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900 truncate">{cte.name}</h3>
                <span className="text-xs font-mono text-gray-400">{cte.code}</span>
              </div>
              <div className="flex items-center justify-between">
                {cte.category && <p className="text-xs text-gray-500">{cte.category}</p>}
                <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold ${getTRLBadge(cteTRLs[cte.id])}`}>
                  TRL {cteTRLs[cte.id] || 'N/A'}
                </span>
              </div>
              <button onClick={() => onCTESelect(cte)} className="w-full btn-primary text-xs mt-2">
                View Details
              </button>
            </div>
          )}
        />
      )}
    </div>
  )
}

export default CTEList
