import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { login } from '../../services/auth'
import LoadingSpinner from '../common/LoadingSpinner'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login: setAuthUser } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await login(username, password)
      setAuthUser(response.user || { username })
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-shell-background px-4">
      <div className="max-w-md w-full">
        <div className="card p-8">
          {/* Brand header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center h-14 w-14 bg-primary-700 rounded-md mb-4">
              <span className="text-white font-bold text-lg tracking-wide">TRI</span>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 tracking-tight">
              Trilokya
            </h2>
            <p className="mt-1.5 text-sm text-gray-500">
              Project Monitoring System — Sign in to continue
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="alert-error">
                <p className="font-medium text-sm">Authentication Error</p>
                <p className="text-xs mt-1">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
              />
            </div>

            <div>
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? <LoadingSpinner size="sm" /> : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login
