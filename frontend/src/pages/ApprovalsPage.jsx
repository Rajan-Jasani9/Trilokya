import React from 'react'
import { FiClipboard } from 'react-icons/fi'

const ApprovalsPage = () => {
  return (
    <div className="space-y-5">
      <div className="page-header">
        <h1 className="page-title">Approvals</h1>
      </div>
      <div className="card p-10 text-center">
        <FiClipboard className="h-10 w-10 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 font-medium text-sm">Approval queue interface will be implemented here</p>
        <p className="text-gray-400 text-xs mt-1">Pending TRL advancement approvals will appear in this section</p>
      </div>
    </div>
  )
}

export default ApprovalsPage
