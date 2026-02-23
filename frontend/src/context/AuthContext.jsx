import React, { createContext, useContext, useState, useEffect } from 'react'
import { getCurrentUser, logout as logoutService } from '../services/auth'
import { isAuthenticated } from '../services/storage'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isAuthenticated()) {
      loadUser()
    } else {
      setLoading(false)
    }
  }, [])

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser()
      // Get user roles from token or make a separate call
      // For now, we'll decode the token to get roles
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          const payload = JSON.parse(atob(token.split('.')[1]))
          userData.roles = payload.roles || []
        }
      } catch (e) {
        // If we can't get roles from token, set empty array
        userData.roles = []
      }
      setUser(userData)
    } catch (error) {
      console.error('Error loading user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = (userData) => {
    setUser(userData)
  }

  const logout = () => {
    logoutService()
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
