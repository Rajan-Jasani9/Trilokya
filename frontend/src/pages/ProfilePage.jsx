import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'

const ProfilePage = () => {
  const { user, loading: authLoading } = useAuth()

  const [profileForm, setProfileForm] = useState({ full_name: '', email: '' })
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' })

  const [savingProfile, setSavingProfile] = useState(false)
  const [changingPassword, setChangingPassword] = useState(false)

  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')

  useEffect(() => {
    if (user) setProfileForm({ full_name: user.full_name || '', email: user.email || '' })
  }, [user])

  const handleProfileChange = (e) => {
    const { name, value } = e.target
    setProfileForm(prev => ({ ...prev, [name]: value }))
    setProfileError(''); setProfileSuccess('')
  }

  const handlePasswordChange = (e) => {
    const { name, value } = e.target
    setPasswordForm(prev => ({ ...prev, [name]: value }))
    setPasswordError(''); setPasswordSuccess('')
  }

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setProfileError(''); setProfileSuccess(''); setSavingProfile(true)
    try {
      const payload = {}
      if (profileForm.full_name !== user.full_name) payload.full_name = profileForm.full_name
      if (profileForm.email !== user.email) payload.email = profileForm.email
      if (Object.keys(payload).length === 0) { setProfileSuccess('Your profile is already up to date.'); return }
      await api.patch('/auth/me', payload)
      setProfileSuccess('Profile updated successfully.')
    } catch (error) {
      setProfileError(error.response?.data?.detail || 'Failed to update profile.')
    } finally { setSavingProfile(false) }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setPasswordError(''); setPasswordSuccess('')
    if (!passwordForm.current_password || !passwordForm.new_password) { setPasswordError('Current and new password are required.'); return }
    if (passwordForm.new_password.length < 8) { setPasswordError('New password must be at least 8 characters.'); return }
    if (passwordForm.new_password !== passwordForm.confirm_password) { setPasswordError('Passwords do not match.'); return }
    setChangingPassword(true)
    try {
      await api.post('/auth/change-password', { current_password: passwordForm.current_password, new_password: passwordForm.new_password })
      setPasswordSuccess('Password changed successfully.')
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' })
    } catch (error) {
      setPasswordError(error.response?.data?.detail || 'Failed to change password.')
    } finally { setChangingPassword(false) }
  }

  if (authLoading && !user) return <LoadingSpinner fullScreen />

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="page-header">
        <div>
          <h1 className="page-title">Profile</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your personal information and keep your account secure.
          </p>
        </div>
      </div>

      {/* Account Details */}
      <div className="card p-5 md:p-6">
        <div className="mb-5">
          <h2 className="text-base font-semibold text-gray-900">Account details</h2>
          <p className="text-xs text-gray-500 mt-0.5">Your basic account information visible to system admins.</p>
        </div>

        {profileError && <div className="alert-error mb-4">{profileError}</div>}
        {profileSuccess && <div className="alert-success mb-4">{profileSuccess}</div>}

        <form onSubmit={handleProfileSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="username" className="form-label">Username</label>
              <input id="username" type="text" value={user?.username || ''} disabled className="input" />
            </div>
            <div>
              <label htmlFor="email" className="form-label">Work email</label>
              <input id="email" name="email" type="email" value={profileForm.email} onChange={handleProfileChange}
                className="input" placeholder="name@organization.in" required />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="full_name" className="form-label">Full name</label>
              <input id="full_name" name="full_name" type="text" value={profileForm.full_name} onChange={handleProfileChange}
                className="input" placeholder="Your full name" required />
            </div>
            <div>
              <label className="form-label">Status</label>
              <div className="mt-1">
                <span className={`badge ${user?.is_active ? 'badge-success' : 'badge-gray'}`}>
                  {user?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
          <div className="pt-4 border-t flex justify-end" style={{ borderColor: '#D9E2E2' }}>
            <button type="submit" disabled={savingProfile} className="btn-primary text-sm">
              {savingProfile ? <LoadingSpinner size="sm" /> : 'Save changes'}
            </button>
          </div>
        </form>
      </div>

      {/* Password */}
      <div className="card p-5 md:p-6">
        <div className="mb-5">
          <h2 className="text-base font-semibold text-gray-900">Password & security</h2>
          <p className="text-xs text-gray-500 mt-0.5">Use a strong, unique password to protect access to sensitive project data.</p>
        </div>

        {passwordError && <div className="alert-error mb-4">{passwordError}</div>}
        {passwordSuccess && <div className="alert-success mb-4">{passwordSuccess}</div>}

        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="current_password" className="form-label">Current password</label>
              <input id="current_password" name="current_password" type="password" value={passwordForm.current_password}
                onChange={handlePasswordChange} className="input" placeholder="Enter current password" required />
            </div>
            <div>
              <label htmlFor="new_password" className="form-label">New password</label>
              <input id="new_password" name="new_password" type="password" value={passwordForm.new_password}
                onChange={handlePasswordChange} className="input" placeholder="At least 8 characters" required />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="confirm_password" className="form-label">Confirm new password</label>
              <input id="confirm_password" name="confirm_password" type="password" value={passwordForm.confirm_password}
                onChange={handlePasswordChange} className="input" placeholder="Re-enter new password" required />
            </div>
            <div className="flex items-end text-xs text-gray-400 pb-2">
              <ul className="list-disc list-inside space-y-0.5">
                <li>At least 8 characters</li>
                <li>Combine letters, numbers, symbols</li>
                <li>Avoid reusing passwords</li>
              </ul>
            </div>
          </div>
          <div className="pt-4 border-t flex justify-end" style={{ borderColor: '#D9E2E2' }}>
            <button type="submit" disabled={changingPassword} className="btn-primary text-sm">
              {changingPassword ? <LoadingSpinner size="sm" /> : 'Update password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProfilePage
