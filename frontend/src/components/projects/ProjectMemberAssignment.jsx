import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import LoadingSpinner from '../common/LoadingSpinner'
import { FiX, FiPlus } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext'

const ProjectMemberAssignment = ({ projectId, onClose }) => {
  const [members, setMembers] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [addingMember, setAddingMember] = useState(false)
  const { user } = useAuth()

  const userRoles = user?.roles || []
  const canAssignMembers = Array.isArray(userRoles)
    ? (userRoles.includes('Manager') || userRoles.includes('Assistant Manager'))
    : (userRoles === 'Manager' || userRoles === 'Assistant Manager' ||
       (typeof userRoles === 'string' && (userRoles.includes('Manager') || userRoles.includes('Assistant Manager'))))

  useEffect(() => {
    if (projectId) { loadMembers(); if (canAssignMembers) loadAllUsers() }
  }, [projectId])

  const loadMembers = async () => {
    try {
      setLoading(true)
      const r = await api.get(`/projects/${projectId}/members`)
      setMembers(r.data || [])
    } catch (error) {
      console.error('Error loading members:', error)
      try { const pr = await api.get(`/projects/${projectId}`); if (pr.data.members) setMembers(pr.data.members) } catch {}
    } finally { setLoading(false) }
  }

  const loadAllUsers = async () => {
    try {
      const r = await api.get('/users/accessible').catch(() => api.get('/users'))
      setAllUsers(r.data || [])
    } catch (error) { console.error('Error loading users:', error) }
  }

  const handleAddMember = async (userId) => {
    try {
      setAddingMember(true)
      await api.post(`/projects/${projectId}/members`, { user_id: userId, role_in_project: null })
      await loadMembers()
    } catch (error) {
      console.error('Error adding member:', error)
      alert(error.response?.data?.detail || 'Failed to add member')
    } finally { setAddingMember(false) }
  }

  const handleRemoveMember = async (memberId) => {
    if (!window.confirm('Are you sure you want to remove this member?')) return
    try { await api.delete(`/projects/${projectId}/members/${memberId}`); loadMembers() }
    catch (error) { console.error('Error removing member:', error); alert('Failed to remove member') }
  }

  if (loading) return <LoadingSpinner />

  const availableUsers = allUsers.filter(u => !members.some(m => m.user_id === u.id))

  return (
    <div className="space-y-5">
      {/* Current Members */}
      <div>
        <h3 className="form-label mb-2">Current Members</h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {members.length === 0 ? (
            <p className="text-gray-400 text-center py-4 text-sm">No members assigned</p>
          ) : (
            members.map((member) => (
              <div key={member.id} className="flex items-center justify-between border rounded p-3" style={{ borderColor: '#D9E2E2' }}>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {member.user?.full_name || member.user?.username || `User ${member.user_id}`}
                  </p>
                  <p className="text-xs text-gray-400">{member.user?.email || ''}</p>
                </div>
                {canAssignMembers && (
                  <button onClick={() => handleRemoveMember(member.id)}
                    className="p-2 text-trl-low hover:bg-red-50 rounded transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                    aria-label="Remove member">
                    <FiX className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Members */}
      {canAssignMembers && (
        <div>
          <h3 className="form-label mb-2">Add Members</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {availableUsers.length === 0 ? (
              <p className="text-gray-400 text-center py-4 text-sm">All users are already assigned</p>
            ) : (
              availableUsers.map((u) => (
                <button key={u.id} onClick={() => handleAddMember(u.id)} disabled={addingMember}
                  className="w-full text-left p-3 border rounded hover:bg-primary-50 transition-colors min-h-[44px] disabled:opacity-50"
                  style={{ borderColor: '#D9E2E2' }}>
                  <p className="text-sm font-medium text-gray-900">{u.full_name}</p>
                  <p className="text-xs text-gray-400">{u.email}</p>
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button onClick={onClose} className="btn-primary text-sm">Done</button>
      </div>
    </div>
  )
}

export default ProjectMemberAssignment
