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
      navigate('/app/technologies')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-shell-background">
      <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
        <section className="relative min-h-[320px] lg:min-h-screen">
          <img
            src="/branding/drdo.jpg"
            alt="DRDO Headquarters"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-slate-900/55" />
          <div className="absolute inset-0 p-8 md:p-12 flex flex-col justify-end text-white">
            <img
              src="/branding/trilokya.png"
              alt="TRILOKYA"
              className="h-16 w-16 object-contain mb-5"
            />
            <h1 className="text-3xl md:text-4xl font-bold tracking-wide">
              TRILOKYA by DRDO
            </h1>
            <p className="mt-2 text-base md:text-lg text-slate-100">
              3rd Vision of Technology Management
            </p>
          </div>
        </section>

        <section className="p-6 sm:p-10 lg:p-12 flex items-center min-h-screen">
          <div className="w-full">
            <div className="text-center mb-8">
              <img
                src="/branding/trilokya.png"
                alt="TRILOKYA"
                className="h-14 w-14 object-contain mx-auto mb-4"
              />
              <h2 className="text-2xl font-semibold text-gray-900 tracking-tight">
                TRILOKYA
              </h2>
              <p className="text-sm font-medium text-gray-700 mt-1">
                by DRDO
              </p>
              <p className="mt-1.5 text-sm text-gray-500">
                Project Monitoring System - Sign in to continue
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
        </section>
      </div>
    </div>
  )
}

export default Login
