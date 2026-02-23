import React, { useState, useEffect } from 'react'
import api from '../services/api'
import ResponsiveTable from '../components/common/Table'
import Modal from '../components/common/Modal'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { FiPlus, FiEdit, FiTrash2, FiSearch, FiUsers } from 'react-icons/fi'

const UsersPage = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => { loadUsers() }, [])

  const loadUsers = async () => {
    try {
      setLoading(true); setError(null)
      const r = await api.get('/users'); setUsers(r.data || [])
    } catch (error) {
      console.error('Error loading users:', error)
      setError(error.response?.data?.detail || 'Failed to load users')
      setUsers([])
    } finally { setLoading(false) }
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return
    try { await api.delete(`/users/${userId}`); loadUsers() }
    catch (error) { console.error('Error:', error); alert('Failed to delete user') }
  }

  const filteredUsers = users.filter((u) =>
    u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) return <LoadingSpinner fullScreen />

  const columns = [
    { header: 'Username', key: 'username' },
    { header: 'Full Name', key: 'full_name' },
    { header: 'Email', key: 'email' },
    { header: 'Status', key: 'status' },
    { header: 'Actions', key: 'actions' },
  ]

  return (
    <div className="space-y-5">
      <div className="page-header">
        <h1 className="page-title">Users</h1>
        <button onClick={() => { setEditingUser(null); setShowModal(true) }} className="btn-primary">
          <FiPlus className="h-4 w-4" /><span>New User</span>
        </button>
      </div>

      <div className="card p-4">
        <div className="relative">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input type="text" placeholder="Search users by name, username, or email…" value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} className="input pl-9" />
        </div>
      </div>

      {error && (
        <div className="alert-error">
          <p className="font-medium text-sm">Error loading users</p>
          <p className="text-xs mt-1">{error}</p>
        </div>
      )}

      {!loading && !error && filteredUsers.length === 0 && (
        <div className="card p-12 text-center">
          <FiUsers className="h-10 w-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium text-sm">
            {searchTerm ? 'No users found matching your search' : 'No users found'}
          </p>
          {!searchTerm && <p className="text-gray-400 text-xs mt-1">Create your first user to get started</p>}
        </div>
      )}

      {filteredUsers.length > 0 && (
        <ResponsiveTable columns={columns} data={filteredUsers}
          renderRow={(user) => (
            <>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm font-mono font-medium text-gray-900">{user.username}</td>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm text-gray-700">{user.full_name}</td>
              <td className="px-5 py-3.5 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-5 py-3.5 whitespace-nowrap">
                <div className="flex items-center gap-1">
                  <button onClick={() => { setEditingUser(user); setShowModal(true) }}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                    aria-label="Edit user">
                    <FiEdit className="h-4 w-4" />
                  </button>
                  <button onClick={() => handleDelete(user.id)}
                    className="p-2 text-trl-low hover:bg-red-50 rounded transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center"
                    aria-label="Delete user">
                    <FiTrash2 className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </>
          )}
          renderCard={(user) => (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900 truncate">{user.full_name}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{user.username}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{user.email}</p>
                </div>
                <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex gap-2 pt-2 border-t" style={{ borderColor: '#D9E2E2' }}>
                <button onClick={() => { setEditingUser(user); setShowModal(true) }} className="flex-1 btn-secondary text-xs">
                  <FiEdit className="h-3.5 w-3.5" /><span>Edit</span>
                </button>
                <button onClick={() => handleDelete(user.id)} className="flex-1 btn-danger text-xs">
                  <FiTrash2 className="h-3.5 w-3.5" /><span>Delete</span>
                </button>
              </div>
            </div>
          )}
        />
      )}

      <Modal isOpen={showModal} onClose={() => { setShowModal(false); setEditingUser(null) }}
        title={editingUser ? 'Edit User' : 'Create User'} size="md">
        <UserForm user={editingUser}
          onSave={() => { setShowModal(false); setEditingUser(null); loadUsers() }}
          onCancel={() => { setShowModal(false); setEditingUser(null) }} />
      </Modal>
    </div>
  )
}

/* ── User Form ── */
const UserForm = ({ user, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    full_name: user?.full_name || '',
    password: '',
    is_active: user?.is_active !== undefined ? user.is_active : true,
  })
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
    if (errors[name]) setErrors(prev => { const n = { ...prev }; delete n[name]; return n })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!user && !formData.password) { setErrors({ password: 'Password is required for new users' }); return }
    setLoading(true)
    try {
      if (user) {
        const payload = { ...formData }
        if (!payload.password) delete payload.password
        await api.patch(`/users/${user.id}`, payload)
      } else { await api.post('/users', formData) }
      onSave()
    } catch (error) {
      setErrors({ submit: error.response?.data?.detail || 'Failed to save user' })
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errors.submit && <div className="alert-error text-sm">{errors.submit}</div>}

      <div>
        <label htmlFor="username" className="form-label">Username <span className="text-trl-low">*</span></label>
        <input type="text" id="username" name="username" value={formData.username} onChange={handleChange} disabled={!!user}
          className={`input ${errors.username ? 'input-error' : ''}`} required />
      </div>
      <div>
        <label htmlFor="email" className="form-label">Email <span className="text-trl-low">*</span></label>
        <input type="email" id="email" name="email" value={formData.email} onChange={handleChange}
          className={`input ${errors.email ? 'input-error' : ''}`} required />
      </div>
      <div>
        <label htmlFor="full_name" className="form-label">Full Name <span className="text-trl-low">*</span></label>
        <input type="text" id="full_name" name="full_name" value={formData.full_name} onChange={handleChange}
          className={`input ${errors.full_name ? 'input-error' : ''}`} required />
      </div>
      <div>
        <label htmlFor="password" className="form-label">Password {!user && <span className="text-trl-low">*</span>}</label>
        <input type="password" id="password" name="password" value={formData.password} onChange={handleChange}
          className={`input ${errors.password ? 'input-error' : ''}`} required={!user} />
        {errors.password && <p className="text-trl-low text-xs mt-1">{errors.password}</p>}
        {user && <p className="text-xs text-gray-400 mt-1">Leave blank to keep current password</p>}
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" id="is_active" name="is_active" checked={formData.is_active} onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 rounded border-gray-300" />
        <label htmlFor="is_active" className="text-sm text-gray-700">Active</label>
      </div>

      <div className="flex gap-3 pt-4 border-t" style={{ borderColor: '#D9E2E2' }}>
        <button type="submit" disabled={loading} className="flex-1 btn-primary">
          {loading ? <LoadingSpinner size="sm" /> : (user ? 'Update' : 'Create')}
        </button>
        <button type="button" onClick={onCancel} disabled={loading} className="flex-1 btn-secondary">Cancel</button>
      </div>
    </form>
  )
}

export default UsersPage
