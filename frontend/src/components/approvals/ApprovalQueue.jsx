import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import ResponsiveTable from '../common/Table'
import LoadingSpinner from '../common/LoadingSpinner'

const ApprovalQueue = () => {
  const [approvals, setApprovals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadApprovals()
  }, [])

  const loadApprovals = async () => {
    try {
      const response = await api.get('/approvals/pending')
      setApprovals(response.data)
    } catch (error) {
      console.error('Error loading approvals:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  const columns = [
    { header: 'Assessment', key: 'assessment' },
    { header: 'Level', key: 'level' },
    { header: 'Actions', key: 'actions' },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Pending Approvals</h1>
      <ResponsiveTable
        columns={columns}
        data={approvals}
        renderRow={(approval) => (
          <>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              Assessment #{approval.cte_trl_assessment_id}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
              Level {approval.approval_level}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm">
              <button className="text-primary-600 hover:text-primary-900 mr-4">
                Approve
              </button>
              <button className="text-red-600 hover:text-red-900">
                Reject
              </button>
            </td>
          </>
        )}
        renderCard={(approval) => (
          <div className="space-y-2">
            <h3 className="font-semibold text-gray-900">
              Assessment #{approval.cte_trl_assessment_id}
            </h3>
            <p className="text-sm text-gray-600">Level {approval.approval_level}</p>
            <div className="flex gap-2 mt-4">
              <button className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm min-h-[44px]">
                Approve
              </button>
              <button className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm min-h-[44px]">
                Reject
              </button>
            </div>
          </div>
        )}
      />
    </div>
  )
}

export default ApprovalQueue
