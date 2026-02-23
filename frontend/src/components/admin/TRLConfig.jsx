import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'

const TRLConfig = () => {
  const [definitions, setDefinitions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDefinitions()
  }, [])

  const loadDefinitions = async () => {
    try {
      const response = await api.get('/admin/trl-definitions')
      setDefinitions(response.data)
    } catch (error) {
      console.error('Error loading TRL definitions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">TRL Definitions</h2>
      <div className="space-y-4">
        {definitions.map((def) => (
          <div key={def.id} className="bg-white rounded-lg shadow p-4 md:p-6">
            <h3 className="font-medium text-gray-900">
              TRL {def.level}: {def.name}
            </h3>
            {def.description && (
              <p className="text-sm text-gray-600 mt-2">{def.description}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default TRLConfig
