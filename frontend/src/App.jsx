import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import LandingPage from './pages/LandingPage'
import Login from './components/auth/Login'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Layout from './components/common/Layout'
import Dashboard from './pages/Dashboard'
import ProjectsPage from './pages/ProjectsPage'
import CTEsPage from './pages/CTEsPage'
import ApprovalsPage from './pages/ApprovalsPage'
import AdminPage from './pages/AdminPage'
import UsersPage from './pages/UsersPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="ctes" element={<CTEsPage />} />
            <Route path="approvals" element={<ApprovalsPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="admin" element={<AdminPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
